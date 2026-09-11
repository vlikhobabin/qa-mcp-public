## Context

`targetWindow(titleContains)` already dispatches `class:`, `hwnd:`, `pid:` and
plain-title selectors, and `find1CWindow()` picks the first visible
`V8TopLevelFrame…` window when the caption is blank. The gap: nothing ties the
target to the specific client the caller is driving, so a blank caption is
ambiguous with multiple clients and a fixed caption is config-specific.

## Decision

Introduce a `port:<N>` selector: resolve the PID listening on local TCP port N,
then that PID's 1C window.

- **Port → PID**: `GetExtendedTcpTable(AF_INET, TCP_TABLE_OWNER_PID_LISTENER)`.
  The fiddly `MIB_TCPTABLE_OWNER_PID` parsing lives in a platform-neutral
  `pidForListeningPort(table, port)` so it is exercised by the offline suite with
  synthetic buffers; the Windows-only `pidListeningOnPort` just supplies the real
  bytes.
- **PID → window**: `find1CWindowForPID(pid)` prefers the `V8TopLevelFrame…`
  window, else the first visible window the PID owns.
- **Wiring**: display request handlers gain `client_port`; a neutral
  `effectiveWindow(window, clientPort)` returns the explicit window if given,
  else `port:<clientPort>`, else blank. This keeps the explicit override and the
  blank→`find1CWindow` fallback intact.
- **Python**: `RemoteAgentBackend` carries `client_port` (from
  `QA_MCP_CLIENT_PORT`) and sends it on every display payload via
  `_window_fields`. The window field is unchanged, so an old host-agent ignores
  `client_port` and still resolves a blank caption via `find1CWindow` — graceful
  degradation, no version gate needed.

## Alternatives Considered

- **Resolve port→PID in Python.** The container cannot read the Windows host TCP
  table; only the host-agent can. Rejected.
- **Smuggle the port into the `window` string from Python** (send
  `window: "port:N"`). An old host-agent would treat `"port:N"` as a literal
  caption and fail to match — a regression. A separate additive `client_port`
  field degrades gracefully instead. Rejected in favor of the explicit field.
- **Keep requiring `QA_MCP_HOST_AGENT_WINDOW`.** That is the defect: it is
  config-specific and multi-client-unsafe.

## Risks

- IPv4-only table: a TestClient TPort also binds `[::]`, but the same PID owns
  the IPv4 listener, so the IPv4 table suffices. If a client ever bound IPv6
  only, resolution would fail closed (window-not-found), never mis-target.

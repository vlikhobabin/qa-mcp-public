## Why

In remote-client mode a display primitive (the F5 list refresh, screenshots,
UIA cell reads) must target the 1C window of the TestClient being driven. The
host-agent targeted a window by caption substring supplied through
`QA_MCP_HOST_AGENT_WINDOW`. That caption is configuration-specific: a value
baked for one base (e.g. demo10413's "Демонстрационное приложение") silently
mis-targets another ([redacted third-party configuration]'s "Бухгалтерия предприятия, редакция 3.0"),
producing an F5 that reaches no window and a falsely empty list
(`row_count:0, "no display backend was reachable"`). It also cannot disambiguate
when several TestClients run at once.

The driver already knows which client it is talking to — the TPort in
`QA_MCP_CLIENT_PORT`. The window it should refresh is, by definition, the one
owned by the process listening on that TPort.

## What Changes

- Host-agent: add a `port:<N>` window selector that resolves the PID listening
  on local TCP port `N` (via `GetExtendedTcpTable`) and targets that process's
  1C top-level window (class `V8TopLevelFrame…`), falling back to its first
  visible window. Display endpoints accept an optional `client_port` and, when
  no explicit `window` is given, target `port:<client_port>`.
- Python `RemoteAgentBackend`: send the driven-client TPort as `client_port`
  alongside `window` on send_keys/type/click/screenshot/visible_list_cells, so
  a port-aware host-agent auto-targets the client's own window with no
  per-configuration `QA_MCP_HOST_AGENT_WINDOW`. An explicit override still wins;
  older host-agents ignore the extra field and keep their 1C-window heuristic.
- Keep the TCP-table parsing and the window-selector resolution in
  platform-neutral, offline-tested helpers.
- Advance the host-agent version and the client's compatibility set (also
  admitting the interim `0.1.3-testclient-envblock`).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: the host-agent SHALL be able to resolve
  the display target window from the driven client's TPort, so display
  primitives target the correct TestClient without a per-configuration caption.

## Impact

- Touches the Windows host-agent Go window resolution
  (`host-agent/windows-display-agent/`) and the Python display backend
  (`src/qa_mcp/protocol/display_backend.py`).
- Adds offline Go tests (TCP-table parse, effective-window selection) and Python
  tests (client_port payload + override precedence).
- Backward compatible: no request/response field is removed; the new
  `client_port` is additive and ignored by older host-agents.
- Does not change native TestClient protocol frames, replay templates, the
  Python manager transport, MCP provider setup or runtime lab configuration.
- Live .201 confirmation of the port→window resolution is retained as evidence.

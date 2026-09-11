## 1. Planning And Preflight

- [x] 1.1 Create proposal, design, delta spec and tasks for
  `host-agent-target-window-by-client-port`.
- [x] 1.2 `openspec validate host-agent-target-window-by-client-port --strict`
  and `git diff --check`.
- [x] 1.3 Retain live .201 port→window evidence under
  `.artifacts/openspec/host-agent-target-window-by-client-port/<ts>/`.

## 2. Test-First Coverage (offline)

- [x] 2.1 Go: `pidForListeningPort` finds the LISTEN row's PID, ignores
  ESTABLISHED rows, misses cleanly on absent/short/truncated tables (synthetic
  `MIB_TCPTABLE_OWNER_PID` buffers).
- [x] 2.2 Go: `effectiveWindow` — explicit caption/selector wins, blank falls
  back to `port:<clientPort>`, blank+no-port stays blank.
- [x] 2.3 Python: `RemoteAgentBackend` sends `client_port` on the display
  payload; an explicit `target_window` still wins; no `client_port` field when
  the port is unset; `from_env` reads `QA_MCP_CLIENT_PORT`.

## 3. Implementation

- [x] 3.1 Go: neutral `pidForListeningPort`; windows `pidListeningOnPort`
  (`GetExtendedTcpTable`) + `find1CWindowForPID`; `port:<N>` case in
  `targetWindow`.
- [x] 3.2 Go: display handlers accept `client_port`; neutral
  `effectiveWindow(window, clientPort)` composes the selector.
- [x] 3.3 Python: `RemoteAgentBackend.client_port` + `_window_fields`; bump
  `HOST_AGENT_VERSION` and extend `COMPATIBLE_HOST_AGENT_VERSIONS`.

## 4. Verify

- [x] 4.1 `go test ./...` (native) GREEN incl. the new tests;
  `GOOS=windows go vet` + build clean.
- [x] 4.2 `python -m pytest -q` GREEN (796) incl. the new display-backend tests.
- [x] 4.3 Live .201: `/send_keys {keys:[F5], client_port:15385}` (no window)
  resolved `target.pid=<client>` / `class=V8TopLevelFrameSDI` / title
  "Бухгалтерия предприятия, редакция 3.0"; an idle port failed closed (HTTP 422);
  an explicit caption still won. Retained as evidence.

## 5. Sync And Archive

- [x] 5.1 Sync the delta into
  `openspec/specs/qa-mcp-windows-host-agent-security/spec.md`.
- [x] 5.2 Archive the change and update the board card at publish.

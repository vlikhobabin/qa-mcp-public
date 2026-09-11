## ADDED Requirements

### Requirement: Host-agent resolves the display target window from the driven client TPort

The Windows host-agent SHALL be able to target a display primitive (key send,
type, click, screenshot, visible-cell read) at the 1C window of the specific
TestClient a caller is driving, identified by that client's TPort, without the
caller supplying a configuration-specific window caption. Display endpoints MUST
accept an optional `client_port`. When no explicit `window` is supplied, the
host-agent MUST resolve the PID listening on that local TCP port and target that
process's 1C top-level window (window class prefixed `V8TopLevelFrame…`),
falling back to the first visible window that process owns. An explicit `window`
(caption substring or `class:`/`hwnd:`/`pid:` selector) MUST continue to take
precedence over `client_port`. When neither is usable the host-agent MUST fail
closed with its existing window-not-found response rather than target an
unrelated window. The `client_port` field MUST be additive so that a host-agent
without this capability ignores it and keeps its existing blank-caption
1C-window heuristic.

#### Scenario: Blank caption resolves the client window from its TPort
- **WHEN** an authenticated display request omits `window` and supplies
  `client_port` for a TestClient listening on that local TPort
- **THEN** the host-agent resolves the PID listening on that TCP port
- **AND** targets that process's `V8TopLevelFrame…` 1C window
- **AND** the response reports that resolved window as the target.

#### Scenario: Explicit caption overrides the client port
- **WHEN** an authenticated display request supplies both a non-empty `window`
  and a `client_port`
- **THEN** the host-agent targets the window matched by the explicit `window`
- **AND** does not resolve the target from `client_port`.

#### Scenario: Idle or unknown TPort fails closed
- **WHEN** an authenticated display request supplies only a `client_port` on
  which no process is listening
- **THEN** the host-agent returns its structured window-not-found failure
- **AND** does not target any unrelated window.

#### Scenario: client_port is additive for older host-agents
- **WHEN** a client sends `client_port` to a host-agent build that predates this
  capability
- **THEN** the host-agent ignores the unknown field
- **AND** still resolves a blank `window` via its existing 1C-window heuristic.

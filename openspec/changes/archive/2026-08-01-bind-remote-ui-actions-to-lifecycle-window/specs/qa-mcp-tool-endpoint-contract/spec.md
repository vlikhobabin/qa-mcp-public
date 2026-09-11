## ADDED Requirements

### Requirement: Remote display tools inherit the active TestClient target

When qa-mcp has an active remote TestClient launch or attachment, `capture_screenshot`, `send_keys`, `type_text`, `click`, and host-agent visible-list-cell reads SHALL send the bounded active `client_target` whenever the caller does not supply an explicit non-empty, non-wildcard window selector. The target SHALL identify the host TestClient by PID and TPort and SHALL include the opaque lifecycle id when the process is provider-owned. An explicit selector SHALL take precedence. The MCP result SHALL preserve typed target-validation and desktop-session failures and MUST NOT retry with an empty, wildcard, generic 1C, or foreground-window target.

#### Scenario: Owned launch supplies implicit display target

- **WHEN** remote `launch_test_client` returns an owned lifecycle handle and records it as the active attachment
- **AND** a caller invokes a remote display tool without an explicit window
- **THEN** qa-mcp sends a `client_target` derived from that lifecycle handle
- **AND** the request includes the same lifecycle id, PID, and TPort without exposing a raw HWND.

#### Scenario: Attach supplies a non-owning display target

- **WHEN** remote `attach_test_client` connects to an already-listening TestClient and the authenticated host-agent resolves that listener to its process-owned 1C window
- **THEN** the attach result and active attachment include a bounded non-owning `client_target`
- **AND** `owns_process` remains false.

#### Scenario: Explicit selector wins

- **WHEN** an active remote TestClient target exists
- **AND** a display tool is called with an explicit non-empty, non-wildcard window selector
- **THEN** qa-mcp sends the explicit selector as the target override
- **AND** does not replace it with the active `client_target`.

#### Scenario: Weak implicit target fails closed

- **WHEN** an active remote TestClient context exists but its `client_target` is missing, stale, mismatched, or unsupported by the host-agent
- **AND** no explicit window selector was supplied
- **THEN** the MCP result reports the typed target failure
- **AND** qa-mcp does not retry against an empty selector, wildcard, generic 1C window, or foreground application.

#### Scenario: Desktop session diagnostic is preserved

- **WHEN** the host-agent refuses a lifecycle-bound display request because the Windows session is locked, disconnected, or non-interactive
- **THEN** the MCP result preserves the corresponding distinct typed error and bounded detail
- **AND** it does not report a generic screenshot/input conflict or success.

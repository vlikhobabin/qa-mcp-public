## ADDED Requirements

### Requirement: Host-agent sends refresh keys to the target window without foreground steal
The Windows host-agent SHALL deliver authenticated `F5` and `Escape` key
requests to the resolved 1C target window without requiring that window to
become the OS foreground window. The target-window key path MUST use the same
authenticated endpoint boundary and target-window resolution contract as the
existing display bridge.

#### Scenario: F5 refresh is sent to a non-foreground target
- **WHEN** an authenticated `/send_keys` request sends key `F5`
- **AND** the requested or default target resolves to a visible
  `V8TopLevelFrame*` 1C window that is not foreground
- **THEN** the host-agent sends key-down and key-up messages for `VK_F5` to that
  target window
- **AND** it does not call `SetForegroundWindow` for that request
- **AND** the response includes `ok: true` and the resolved target metadata.

#### Scenario: Escape clean-state sweep is sent to a non-foreground target
- **WHEN** an authenticated `/send_keys` request sends key `Escape`
- **AND** the target 1C window is visible but not foreground
- **THEN** the host-agent sends key-down and key-up messages for `VK_ESCAPE` to
  that target window
- **AND** it does not call `SetForegroundWindow` for that request.

#### Scenario: Other key sequences keep foreground semantics
- **WHEN** an authenticated `/send_keys` request contains a key or chord outside
  the focus-independent refresh-key allowlist
- **THEN** the host-agent uses the existing foreground-coupled input route for
  that request
- **AND** unsupported key names still fail closed before any desktop input is
  sent.

### Requirement: Foreground denial is reported as a structured host-agent result
The host-agent SHALL return a structured `foreground-denied` result instead of
a generic primitive failure or HTTP 500 when a display primitive still requires
the real foreground window and Windows denies foreground activation.

#### Scenario: Foreground-denied is not reported as HTTP 500
- **WHEN** an authenticated display primitive requires foreground activation
- **AND** the target window is resolved
- **AND** Windows denies `SetForegroundWindow`
- **THEN** the host-agent response includes `ok: false` and
  `error: "foreground-denied"`
- **AND** the HTTP status is not `500`
- **AND** the diagnostic distinguishes foreground denial from a missing target
  window or unreachable host-agent.

### Requirement: Host-agent version declares focus-independent refresh support
The host-agent and Python remote display backend SHALL advertise and accept a
bounded version family for the focus-independent refresh-key contract. The
default Python handshake MUST accept the new host-agent version before issuing
display primitives, while exact operator overrides and SHA-256 pinning remain
strict.

#### Scenario: New focus-independent host-agent version is accepted by default
- **WHEN** qa-mcp is configured for remote-client mode without
  `QA_MCP_HOST_AGENT_EXPECTED_VERSION`
- **AND** the authenticated host-agent `/version` response reports the
  focus-independent refresh-key version
- **THEN** `RemoteAgentBackend.handshake()` succeeds
- **AND** display primitives may be attempted through the host-agent.

#### Scenario: Exact version override remains strict
- **WHEN** `QA_MCP_HOST_AGENT_EXPECTED_VERSION` is set
- **AND** the authenticated host-agent reports any other version
- **THEN** `RemoteAgentBackend.handshake()` fails with
  `host-agent-version-mismatch`
- **AND** no host-agent desktop primitive is attempted.

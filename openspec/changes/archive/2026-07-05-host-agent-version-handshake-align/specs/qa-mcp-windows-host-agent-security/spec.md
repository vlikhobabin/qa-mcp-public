## ADDED Requirements

### Requirement: Remote display backend uses bounded host-agent version compatibility
qa-mcp's remote display backend SHALL accept only explicitly supported
host-agent versions during `/version` handshake unless an operator supplies an
exact expected-version override. Unsupported versions MUST fail with a
structured `host-agent-version-mismatch` diagnostic before any desktop-control
or screenshot primitive is attempted.

#### Scenario: Current supported host-agent version is accepted by default
- **WHEN** qa-mcp is configured for remote-client mode without
  `QA_MCP_HOST_AGENT_EXPECTED_VERSION`
- **AND** the authenticated host-agent `/version` response reports a supported
  current version
- **THEN** `RemoteAgentBackend.handshake()` succeeds without requiring an
  environment override.

#### Scenario: Explicit expected-version override remains exact
- **WHEN** `QA_MCP_HOST_AGENT_EXPECTED_VERSION` is set to a specific version
- **AND** the authenticated host-agent reports a different version
- **THEN** `RemoteAgentBackend.handshake()` fails with
  `host-agent-version-mismatch`
- **AND** no host-agent desktop primitive is attempted.

#### Scenario: Unsupported default version is diagnosed honestly
- **WHEN** qa-mcp uses its default host-agent compatibility set
- **AND** the authenticated host-agent reports an unsupported version
- **THEN** the backend returns `host-agent-version-mismatch` with install
  guidance
- **AND** SHA-256 pinning, when configured, remains an exact independent check.

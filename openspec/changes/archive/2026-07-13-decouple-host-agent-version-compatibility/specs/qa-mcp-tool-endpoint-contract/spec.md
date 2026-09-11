## ADDED Requirements

### Requirement: Remote host-agent compatibility is protocol-based
The remote display backend SHALL use the authenticated host-agent display
protocol id as the default compatibility boundary instead of requiring an
exact build label. Explicit operator version and SHA-256 pins SHALL remain
exact. Known legacy build labels without a protocol field MAY remain compatible;
unknown builds without a supported protocol SHALL fail closed.

#### Scenario: Shipped image connects to a newer wire-compatible agent
- **WHEN** `/version` returns an unknown newer build label and the supported
  display protocol id
- **THEN** the handshake succeeds without an operator override
- **AND** reports `version_relationship: protocol-compatible`.

#### Scenario: Unknown agent omits or changes the protocol
- **WHEN** an unknown build returns no display protocol or an unsupported one
- **THEN** the handshake fails closed before a display primitive executes.

#### Scenario: Operator pins a build label or hash
- **WHEN** `QA_MCP_HOST_AGENT_EXPECTED_VERSION` or the expected SHA-256 is set
- **THEN** the corresponding raw value is compared exactly
- **AND** a mismatch fails closed even when the display protocol is supported.

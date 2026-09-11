## ADDED Requirements

### Requirement: TestClient relay routing is explicit and endpoint-bound

qa-mcp SHALL enable relay authentication only when both a relay endpoint and
token are configured, and SHALL apply the preface only to connections whose
host and port exactly match that endpoint.

#### Scenario: Relay endpoint matches

- **WHEN** a protocol helper connects to the configured relay host and port
- **THEN** the shared connector authenticates the relay before exposing the
  socket to protocol code.

#### Scenario: Relay is absent or endpoint differs

- **WHEN** relay configuration is absent or a helper connects to another
  address
- **THEN** the connector uses direct TCP without sending a relay preface
- **AND** existing solo/Linux/local TestClient contours remain compatible.

#### Scenario: Partial relay configuration is supplied

- **WHEN** only endpoint or token is configured
- **THEN** startup/config validation fails closed with a bounded diagnostic
- **AND** no secret value appears in the diagnostic.

#### Scenario: Relay listener and TestClient TPort differ

- **WHEN** protocol sockets use a configured relay endpoint and
  `QA_MCP_HOST_AGENT_CLIENT_PORT` names the real local TestClient TPort
- **THEN** protocol connections continue through the authenticated relay
- **AND** host-agent display/window commands target the real TestClient TPort
- **AND** omitting the override preserves the existing client-port behavior.

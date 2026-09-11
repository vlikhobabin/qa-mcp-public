## RENAMED Requirements

- FROM: `### Requirement: Wildcard HTTP binds require explicit unsafe opt-in`
- TO: `### Requirement: Wildcard HTTP binds require authentication`

## MODIFIED Requirements

### Requirement: Wildcard HTTP binds require authentication

The qa-mcp HTTP MCP transport SHALL refuse wildcard or non-loopback serving
unless project-owned authentication is configured through
`QA_MCP_BEARER_TOKEN`. The former unsafe-bind opt-in MUST NOT bypass the
authentication requirement for the standalone container.

#### Scenario: Wildcard host without authentication is rejected
- **WHEN** `QA_MCP_HTTP_HOST` is set to a wildcard or non-loopback host
- **AND** the MCP authentication secret is absent
- **THEN** the server refuses the configuration before serving requests.

#### Scenario: Wildcard host with authentication starts
- **WHEN** a wildcard listener and a valid project-owned authentication secret
  are configured
- **THEN** the server starts
- **AND** unauthenticated MCP requests are rejected before dispatch.

### Requirement: HTTP exposure documentation is explicit

Delivery documentation SHALL distinguish local loopback and authenticated
container exposure, explain token generation/storage and MUST NOT require an AI
for 1C proxy or account.

#### Scenario: Operator can distinguish local and container modes
- **WHEN** an operator reads current standalone guidance
- **THEN** loopback-only native use and authenticated Docker port publishing are
  separate examples
- **AND** no example exposes unauthenticated MCP on a non-loopback listener.

### Requirement: Standalone health is bounded and does not require MCP credentials

The project-owned `/health` route SHALL remain usable by Docker healthchecks
without an MCP Bearer token and SHALL return only bounded liveness data.

#### Scenario: Healthcheck does not disclose runtime configuration
- **WHEN** an unauthenticated client requests `/health`
- **THEN** it receives a successful bounded liveness response
- **AND** no token, target identity, credential or environment value is present.

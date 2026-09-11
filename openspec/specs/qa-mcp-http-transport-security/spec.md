# qa-mcp-http-transport-security Specification

## Purpose

Define the network exposure and authentication contract for qa-mcp Streamable
HTTP transport. Local-only access remains the native default; broader exposure
requires the project-owned Bearer boundary.

## Requirements

### Requirement: HTTP MCP transport binds locally by default

The qa-mcp streamable HTTP transport SHALL default to loopback-only access. Docker Compose and helper scripts SHALL
serve the MCP port on `127.0.0.1` unless an operator explicitly chooses a non-loopback exposure mode.

#### Scenario: Default Python server host is loopback
- **WHEN** the HTTP MCP server starts without `QA_MCP_HTTP_HOST`
- **THEN** it binds to `127.0.0.1`
- **AND** it does not listen on all network interfaces

#### Scenario: Model-A Compose is loopback scoped
- **WHEN** `docker compose -f docker/docker-compose.yml up` is used with defaults
- **THEN** the service uses host networking with `QA_MCP_HTTP_HOST=127.0.0.1`
- **AND** it does not default to wildcard bind or `QA_MCP_HTTP_ALLOW_UNSAFE_BIND=1`

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
- **WHEN** `QA_MCP_HTTP_HOST` is set to a wildcard or non-loopback host
- **AND** a valid project-owned authentication secret is configured
- **THEN** the server starts
- **AND** unauthenticated MCP requests are rejected before dispatch.

### Requirement: HTTP exposure documentation is explicit

Delivery documentation SHALL distinguish local loopback and authenticated
container exposure, explain token generation/storage and MUST NOT require an AI
for 1C proxy or account.

#### Scenario: Operator can distinguish local and container modes
- **WHEN** an operator reads the Docker or delivery runbook
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

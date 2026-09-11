## ADDED Requirements

### Requirement: HTTP MCP transport binds locally by default

The qa-mcp streamable HTTP transport SHALL default to loopback-only access. Docker Compose and helper scripts SHALL publish the MCP port on `127.0.0.1` unless an operator explicitly chooses a non-loopback exposure mode.

#### Scenario: Default Python server host is loopback
- **WHEN** the HTTP MCP server starts without `QA_MCP_HTTP_HOST`
- **THEN** it binds to `127.0.0.1`
- **AND** it does not listen on all network interfaces

#### Scenario: Compose publish is loopback scoped
- **WHEN** `docker compose -f docker/docker-compose.yml up` is used with defaults
- **THEN** host port `8000` is published on `127.0.0.1`
- **AND** it is not published on all interfaces

### Requirement: Wildcard HTTP binds require explicit unsafe opt-in

The qa-mcp HTTP MCP transport SHALL fail closed or refuse startup when configured to bind to all interfaces unless an explicit unsafe-bind opt-in is present. When unsafe bind is enabled, startup logs SHALL warn that the transport has no built-in authentication and must be protected by an auth proxy or trusted network boundary.

#### Scenario: Wildcard host without opt-in is rejected
- **WHEN** `QA_MCP_HTTP_HOST` is set to `0.0.0.0` or another wildcard host
- **AND** the unsafe-bind opt-in is absent
- **THEN** the server refuses the configuration before serving MCP requests

#### Scenario: Explicit unsafe bind warns
- **WHEN** `QA_MCP_HTTP_HOST` is set to a wildcard or non-loopback host
- **AND** the unsafe-bind opt-in is present
- **THEN** the server starts with the requested bind
- **AND** it logs a warning that unauthenticated network exposure is operator-owned

### Requirement: HTTP exposure documentation is explicit

The delivery documentation SHALL describe the default local-only HTTP transport, the unsafe-bind opt-in, and the need for an auth proxy or trusted network when exposing streamable HTTP beyond loopback.

#### Scenario: Operator can distinguish local and exposed modes
- **WHEN** an operator reads the Docker or delivery runbook
- **THEN** the local-only default command and unsafe exposed command are separate
- **AND** the exposed command carries the authentication/network-boundary warning

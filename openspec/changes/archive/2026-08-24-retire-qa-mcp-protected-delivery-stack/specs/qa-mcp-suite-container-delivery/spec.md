## MODIFIED Requirements

### Requirement: Thin image uses the suite provider base
The source-visible qa-mcp thin image SHALL use an immutable digest-pinned suite
provider base as its runtime image and SHALL install the locked Python package
without a separate compiled builder ABI.

#### Scenario: Building with an immutable suite base
- **WHEN** the thin image is built with the required suite-base argument
- **THEN** the argument is an immutable digest reference
- **AND** readable qa-mcp modules import successfully in that final image

#### Scenario: Mutable suite base is rejected
- **WHEN** a release build omits the suite-base argument or supplies a mutable tag
- **THEN** the release workflow rejects it before building or publishing

### Requirement: Thin image exposes MCP through the suite proxy
The qa-mcp source-visible thin image SHALL run `qa-native-mcp` as a stdio process
behind `ai-mcp-proxy serve-http` on container port 8080.

#### Scenario: Health endpoint is served by proxy
- **WHEN** the container is running
- **THEN** `GET /health` on port 8080 returns the proxy health contract

#### Scenario: MCP traffic is token gated
- **WHEN** `/mcp` is requested without the configured bearer token
- **THEN** the proxy rejects the request instead of forwarding it to qa-mcp

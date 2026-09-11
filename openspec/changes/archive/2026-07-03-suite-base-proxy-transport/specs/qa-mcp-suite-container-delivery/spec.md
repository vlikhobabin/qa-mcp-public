## ADDED Requirements

### Requirement: Thin image uses the suite provider base
The qa-mcp protected thin image SHALL use the suite provider base as its final
runtime image while keeping the protected build builder ABI aligned with the final
Python runtime.

#### Scenario: Building with default suite base
- **WHEN** the thin image is built with default Docker build arguments
- **THEN** the final stage uses the suite base image contract and the protected
  native modules import successfully in that final image

#### Scenario: Overriding Python ABI
- **WHEN** a release build overrides the suite base Python ABI
- **THEN** the build can override the builder Python image to the matching ABI

### Requirement: Thin image exposes MCP through the suite proxy
The qa-mcp protected thin image SHALL run `qa-native-mcp` as a stdio process behind
`ai-mcp-proxy serve-http` on container port 8080.

#### Scenario: Health endpoint is served by proxy
- **WHEN** the container is running
- **THEN** `GET /health` on port 8080 returns the proxy health contract

#### Scenario: MCP traffic is token gated
- **WHEN** `/mcp` is requested without the configured bearer token
- **THEN** the proxy rejects the request instead of forwarding it to qa-mcp

### Requirement: Model B remote TestClient defaults remain intact
The suite-proxy thin image SHALL preserve the model B defaults that connect
protocol tools to a host-side TestClient and display tools to the Windows host-agent.

#### Scenario: Container starts with model B defaults
- **WHEN** the thin image starts without per-user overrides
- **THEN** `QA_MCP_REMOTE_CLIENT=1`, `QA_MCP_CLIENT_HOST=host.docker.internal` and
  `QA_MCP_CLIENT_PORT=15381` are present in the runtime environment

# qa-mcp Independent Standalone Runtime Specification

## Purpose

Define the public-input, direct HTTP container contract for running qa-mcp
without a private AI for 1C base image, proxy or service dependency.

## Requirements

### Requirement: Standalone image builds from public inputs
The standalone Docker image SHALL build from a documented public base and
public qa-mcp repository/package inputs without a private image, binary,
package index, credential or BuildKit secret.

#### Scenario: Clean public checkout builds the image
- **WHEN** an unauthenticated clean checkout runs the documented Docker build
- **THEN** the image builds without `ai-suite-base`, `ai-mcp-proxy`, a data key
  or a private release service.

### Requirement: Standalone image serves direct Streamable HTTP MCP
The container SHALL serve project-owned `/mcp` and `/health` endpoints directly
on the documented internal port as a non-root user.

#### Scenario: Container starts with minimum standalone configuration
- **WHEN** the image starts with a generated MCP token and remote TestClient
  settings
- **THEN** `/health` reports bounded readiness
- **AND** an authenticated Streamable HTTP MCP initialization succeeds.

#### Scenario: Health response is bounded and secret-free
- **WHEN** an unauthenticated client requests `/health`
- **THEN** the runtime returns only bounded liveness data
- **AND** it discloses no token, target, credentials or environment values.

### Requirement: Network exposure fails closed
Non-loopback or wildcard MCP serving MUST require configured authentication,
and default host publication SHALL remain scoped to loopback.

#### Scenario: Missing token blocks wildcard startup
- **WHEN** the container is configured for a wildcard listener without an MCP
  authentication secret
- **THEN** it exits before accepting MCP requests.

#### Scenario: Wrong token is rejected
- **WHEN** a client sends an MCP request without the configured Bearer token or
  with a different token
- **THEN** the runtime rejects it without dispatching a tool.

### Requirement: Remote TestClient routing remains standalone
The standalone runtime SHALL reach a user-owned host TestClient and compatible
repository host boundary through documented Docker host routing without an AI
for 1C service. Final extraction and qualification of the independent public
Windows bridge remains owned by OSS-05.

#### Scenario: Windows Docker Desktop route is exercised
- **WHEN** the exact release image connects through `host.docker.internal` to
  the configured Windows target
- **THEN** safe status/read and bounded display operations route through the
  configured host boundary
- **AND** cleanup stops only release-owned TestClient state.

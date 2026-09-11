# qa-mcp Suite Container Delivery Specification

## Purpose

Define the retained model-B TestClient and diagnostic behavior for the
source-visible qa-mcp container after standalone runtime extraction.

## Requirements

### Requirement: Model B remote TestClient defaults remain intact
The independent standalone image SHALL preserve model-B defaults that connect
protocol tools to a host-side TestClient and display tools to the public Windows
bridge without importing or invoking AI for 1C services.

#### Scenario: Container starts with model B defaults
- **WHEN** the standalone image starts without per-user endpoint overrides
- **THEN** remote-client mode, `host.docker.internal` and the documented default
  TPort are selected
- **AND** the only optional host control dependency is the public bridge.

### Requirement: Model-B doctor checks HTTP reachability instead of raw port state

The qa-mcp model-B diagnostic flow SHALL verify host-agent availability through
authenticated HTTP requests rather than relying on raw port enumeration. The
diagnostic MUST treat successful HTTP responses over loopback or
`host.docker.internal` as reachability proof even when OS port-listing output
uses an IPv6 wildcard listener such as `[::]`.

#### Scenario: IPv6 wildcard listener still passes HTTP health

- **WHEN** the host-agent listens on an IPv6 wildcard address
- **AND** authenticated HTTP requests to `127.0.0.1` or `[::1]` return success
- **THEN** the doctor reports host-agent reachability as pass
- **AND** it does not fail solely because raw port enumeration did not show an
  IPv4-specific listener

#### Scenario: Container route is summarized before tool invocation

- **WHEN** qa-mcp runs in the thin container with
  `QA_MCP_CLIENT_HOST=host.docker.internal`
- **AND** the host-agent route is reachable from inside the container
- **THEN** `qa_mcp_doctor` includes a container-to-host-agent route check in
  the single diagnostic chain
- **AND** users do not need to invoke an unrelated MCP tool to learn whether the
  route works

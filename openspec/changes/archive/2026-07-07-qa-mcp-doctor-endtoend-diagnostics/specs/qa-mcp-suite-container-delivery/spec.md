## ADDED Requirements

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

### Requirement: Model-B doctor includes platform and COM doctor links
The qa-mcp diagnostic flow SHALL include platform discovery and COMConnector
doctor checks when the configured host-agent exposes those authenticated
endpoints. Unsupported or unavailable COM checks MUST be reported as explicit
skips or failures with owner/action hints, not hidden behind the overall
TestClient status.

#### Scenario: Platform and COM checks are available
- **WHEN** the host-agent health, platform discovery, and COM doctor endpoints
  are configured
- **THEN** `qa_mcp_doctor` records separate platform and COM check results
- **AND** the COM result is bounded to the existing read-only COM doctor
  contract

#### Scenario: COM doctor is unavailable on this contour
- **WHEN** the current contour cannot execute the COMConnector doctor
- **THEN** `qa_mcp_doctor` marks the COM link as skipped or failed with a
  distinct code
- **AND** the overall result remains transparent about the unverified COM link

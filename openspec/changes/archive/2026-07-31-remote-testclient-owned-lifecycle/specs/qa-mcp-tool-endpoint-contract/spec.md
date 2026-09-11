## ADDED Requirements

### Requirement: Remote-client launches create provider-owned lifecycle handles
`launch_test_client` in remote-client mode SHALL mark a host-agent-launched
TestClient as provider-owned only when the host-agent explicitly reports
`owns_process: true` for that launched process, and SHALL return enough
sanitized lifecycle handle metadata, including an opaque lifecycle id, for a
later `stop_test_client` call to clean up the same host process. Manually
attached TestClients and legacy host-agent launch results that do not
explicitly report ownership and a lifecycle id SHALL remain unowned.

#### Scenario: Host-agent launch returns an owned handle
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `launch_test_client` successfully launches a TestClient through the
  configured host-agent
- **THEN** the returned result includes `owns_process: true`
- **AND** the returned result identifies host-agent lifecycle ownership without
  exposing credentials or raw host runtime logs
- **AND** the returned lifecycle handle includes an opaque `id` that is not
  derived from the PID alone
- **AND** the active attachment keeps using the launched protocol endpoint.

#### Scenario: Manual attachment remains unowned
- **WHEN** `attach_test_client` records an already-listening TestClient endpoint
- **THEN** the returned result includes `owns_process: false`
- **AND** a later cleanup request cannot terminate that manually attached
  client through qa-mcp.

#### Scenario: Legacy host-agent launch result is not inferred as owned
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** the configured host-agent returns a successful launch result with a
  PID but without `owns_process: true`
- **THEN** qa-mcp records the endpoint as an active attachment
- **AND** the returned attachment remains `owns_process: false`
- **AND** qa-mcp does not synthesize a lifecycle handle from the PID alone.

### Requirement: Remote-client stop routes through host-agent ownership
`stop_test_client` SHALL remain local process-group cleanup for locally launched
clients, but in remote-client mode it SHALL route cleanup through the configured
host-agent only when the caller supplies the opaque lifecycle handle returned by
the provider-owned remote launch. The tool SHALL return a structured result for
stopped, already stopped, and refused states, and SHALL refuse PID-only remote
cleanup requests. Generic display protocol compatibility SHALL NOT by itself
authorize remote TestClient stop: qa-mcp MUST first prove that the host-agent
supports lifecycle-handle stop semantics through the current lifecycle-stop
version or an explicit advertised capability.

#### Scenario: Owned remote launch is stopped through the host-agent
- **WHEN** a remote-client `launch_test_client` result includes an owned
  lifecycle handle
- **AND** `stop_test_client` is called with that PID and the returned lifecycle
  handle
- **THEN** qa-mcp sends the stop request to the same host-agent lifecycle route
- **AND** the result reports a typed final state for that exact launched process.

#### Scenario: Repeated stop is idempotent
- **WHEN** `stop_test_client` has already finalized an owned remote TestClient
- **AND** the caller repeats `stop_test_client` for the same lifecycle handle
- **THEN** the result reports an already-finalized state
- **AND** no unrelated 1C process is targeted.

#### Scenario: PID-only remote cleanup is refused
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `stop_test_client` is called with a PID but without the lifecycle
  handle id returned by `launch_test_client`
- **THEN** the result is a structured `missing_lifecycle_handle` refusal
- **AND** qa-mcp does not call the host-agent stop route.

#### Scenario: Protocol-compatible legacy stop route is refused
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** the host-agent handshake reports the shared display protocol but does
  not prove lifecycle-handle TestClient stop support
- **AND** `stop_test_client` is called with an otherwise valid lifecycle handle
- **THEN** the result is a structured
  `host-agent-testclient-lifecycle-unsupported` failure
- **AND** qa-mcp does not call the host-agent stop route.

#### Scenario: Unowned remote PID is refused
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `stop_test_client` is called with a lifecycle handle id that does not
  belong to a provider-owned remote launch
- **THEN** the result is a structured refusal
- **AND** qa-mcp does not attempt local process cleanup or host-side broad
  process termination.

#### Scenario: Not-ready remote launch exposes cleanup handle when host-owned
- **WHEN** the host-agent starts a TestClient process but reports the launch as
  not ready while the process is still alive
- **AND** the host-agent response includes `owns_process: true` and a lifecycle
  handle
- **THEN** qa-mcp returns that sanitized cleanup handle in the structured launch
  failure
- **AND** it does not record the not-ready endpoint as an active attachment.

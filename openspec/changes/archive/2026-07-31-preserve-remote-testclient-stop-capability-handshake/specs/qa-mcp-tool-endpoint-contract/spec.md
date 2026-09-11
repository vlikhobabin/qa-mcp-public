## MODIFIED Requirements

### Requirement: Remote-client stop routes through host-agent ownership

`stop_test_client` SHALL remain local process-group cleanup for locally launched
clients, but in remote-client mode it SHALL route cleanup through the configured
host-agent only when the caller supplies the opaque lifecycle handle returned by
the provider-owned remote launch. The tool SHALL return a structured result for
stopped, already stopped, and refused states, and SHALL refuse PID-only remote
cleanup requests. Generic display protocol compatibility SHALL NOT by itself
authorize remote TestClient stop: qa-mcp MUST first prove that the host-agent
supports lifecycle-handle stop semantics through the current lifecycle-stop
version or an explicit advertised capability preserved by the remote
`/version` handshake. Only a capability list entry named
`testclient-lifecycle-handle-stop` or a capability mapping entry with that name
and an explicit boolean `true` SHALL authorize future protocol-compatible
host-agent stop routing.

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

#### Scenario: Future host-agent capability authorizes lifecycle stop

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** the host-agent handshake reports the shared display protocol with a
  future protocol-compatible version
- **AND** the `/version` response advertises
  `testclient-lifecycle-handle-stop` either in a capability-name list or in a
  capability mapping whose value is the boolean `true`
- **AND** `stop_test_client` is called with an owned lifecycle handle
- **THEN** qa-mcp sends `/testclient/stop` through the host-agent lifecycle
  route
- **AND** it does not require an exact version pin for that future compatible
  host-agent.

#### Scenario: Truthy non-boolean capability values do not authorize stop

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** the host-agent handshake reports the shared display protocol with a
  protocol-compatible version
- **AND** the `/version` response advertises
  `testclient-lifecycle-handle-stop` in a capability mapping whose value is not
  an explicit boolean `true`
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

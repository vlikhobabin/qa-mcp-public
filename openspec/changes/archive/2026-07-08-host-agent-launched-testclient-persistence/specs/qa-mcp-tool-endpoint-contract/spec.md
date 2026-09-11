## MODIFIED Requirements

### Requirement: Remote-client launch uses host-agent when configured

`launch_test_client` SHALL support remote-client mode by routing launch through
the configured authenticated Windows host-agent instead of failing as a
local-only tool. The tool MUST render or request the same target identity as the
local lifecycle path, preserve structured host-agent launch diagnostics, wait
for the configured TestClient TPort to become reachable from the container, and
remember the endpoint for subsequent endpoint-touching tools only after the
host-agent readiness result and the container-side TPort probe both prove the
client is usable.

#### Scenario: Remote launch establishes and remembers a host TestClient
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** host-agent launch settings are configured
- **AND** `launch_test_client` is called with a target infobase, user and TPort
- **AND** the host-agent returns `ok: true`, `alive: true` and
  `listening: true`
- **AND** the TPort is reachable from the container
- **THEN** qa-mcp returns `ok: true` with the host PID when reported, the TPort
  and a redacted command summary
- **AND** a follow-up endpoint-touching tool called without explicit `host` and
  `port` uses the launched endpoint.

#### Scenario: Dead remote endpoint can be re-established
- **WHEN** a previous remote-client attachment is stale or no longer listening
- **AND** the caller invokes `launch_test_client` again
- **THEN** qa-mcp requests a new host-agent launch or reuses an already
  listening TPort reported by the host-agent
- **AND** the remembered endpoint is updated only when the resulting endpoint is
  live from the container.

#### Scenario: Host-agent early exit is returned as a launch failure
- **WHEN** qa-mcp is in remote-client mode
- **AND** the host-agent launch response reports `ok: false` with
  `error: "testclient-exited-early"`
- **THEN** `launch_test_client` returns a structured failure result with the
  same host-agent error code and diagnostic detail
- **AND** the result includes the redacted manual host command fallback
- **AND** no active attached endpoint is recorded.

#### Scenario: Host-agent not-listening result is returned as a launch failure
- **WHEN** qa-mcp is in remote-client mode
- **AND** the host-agent launch response reports `ok: false` with
  `error: "testclient-not-listening"`
- **THEN** `launch_test_client` returns a structured failure result with the
  same host-agent error code and diagnostic detail
- **AND** no active attached endpoint is recorded.

#### Scenario: Container reachability remains required after host readiness
- **WHEN** qa-mcp is in remote-client mode
- **AND** the host-agent reports the TestClient process as ready on the host
- **AND** the TPort is not reachable from the container
- **THEN** `launch_test_client` returns `remote-testclient-port-not-listening`
- **AND** the host-agent readiness payload is preserved for diagnostics
- **AND** no active attached endpoint is recorded.

#### Scenario: Missing host-agent launch returns an exact manual command
- **WHEN** qa-mcp is in remote-client mode
- **AND** the host-agent launch route is unavailable, unreachable or too old
- **THEN** `launch_test_client` returns a structured failure result
- **AND** the result includes the exact host command an operator can run with
  the resolved connection string, user and `-TPort`
- **AND** secret values such as the TestClient password are redacted while
  `password_set` remains visible.

#### Scenario: Local launch behavior is unchanged
- **WHEN** `QA_MCP_REMOTE_CLIENT` is unset or false
- **THEN** `launch_test_client` uses the existing Linux/Xvfb lifecycle path
- **AND** no host-agent TestClient launch request is sent.

## ADDED Requirements

### Requirement: Remote-client launch uses host-agent when configured

`launch_test_client` SHALL support remote-client mode by routing launch through
the configured authenticated Windows host-agent instead of failing as a
local-only tool. The tool MUST render or request the same target identity as the
local lifecycle path, wait for the configured TestClient TPort to become
reachable from the container, and remember the endpoint for subsequent
endpoint-touching tools.

#### Scenario: Remote launch establishes and remembers a host TestClient
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** host-agent launch settings are configured
- **AND** `launch_test_client` is called with a target infobase, user and TPort
- **THEN** qa-mcp sends an authenticated host-agent TestClient launch request
- **AND** the result includes `ok: true`, the host PID when reported, the TPort
  and a redacted command summary
- **AND** a follow-up endpoint-touching tool called without explicit `host` and
  `port` uses the launched endpoint.

#### Scenario: Dead remote endpoint can be re-established
- **WHEN** a previous remote-client attachment is stale or no longer listening
- **AND** the caller invokes `launch_test_client` again
- **THEN** qa-mcp requests a new host-agent launch or reuses an already
  listening TPort reported by the host-agent
- **AND** the remembered endpoint is updated to the live host/port.

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

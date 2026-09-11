## ADDED Requirements

### Requirement: Host-agent supervises the configured workstation bsl-agent
When the workstation helper is configured, the host-agent SHALL launch `bsl-agent.exe workstation serve` using the `ai1c.bsl-agent-workstation-supervision.v1` contract, accept readiness only from loopback `/health` state `ready`, restart an exited helper after bounded backoff, and stop only the process it owns when the host-agent stops.

#### Scenario: Helper becomes ready
- **WHEN** the configured fake helper starts and returns ready health/status
- **THEN** host-agent health reports configured, ready, protocol, version, and restart count without configured paths.

#### Scenario: Helper crashes and restarts
- **WHEN** the owned helper process exits unexpectedly
- **THEN** the supervisor starts a replacement within the configured backoff interval
- **AND** the health restart count increases.

#### Scenario: Host-agent stops the owned helper
- **WHEN** the supervisor stops
- **THEN** it requests graceful termination, waits the contract timeout, and falls back only to terminating its owned process/group.

#### Scenario: Helper is not configured
- **WHEN** binary/workspace configuration is absent
- **THEN** no helper is spawned and existing display, TestClient, COM, platform, and agent-CLI paths remain available.

### Requirement: Host-agent exposes only bounded authenticated BSL routes
The host-agent SHALL expose authenticated diagnostics and resync routes that forward to the fixed loopback endpoints of the configured ready helper. It MUST reject unauthenticated calls before reading their bodies and MUST NOT accept caller-selected upstream URLs or executable paths.

#### Scenario: Diagnostic request is routed
- **WHEN** an authenticated caller sends a bounded diagnostic request while the fake helper is ready
- **THEN** the host-agent returns the helper's bounded JSON response from `/v1/diagnostics`.

#### Scenario: Helper is unavailable
- **WHEN** an authenticated caller requests diagnostics while the helper is disabled or not ready
- **THEN** the host-agent returns a structured fail-closed readiness error without spawning an arbitrary process.

#### Scenario: Resync request is routed explicitly
- **WHEN** an authenticated caller invokes the host-agent resync route
- **THEN** exactly one request is forwarded to the helper's fixed `/v1/resync` endpoint.

## ADDED Requirements

### Requirement: Public bridge exposes a versioned narrow capability set
The Windows standalone bridge SHALL advertise a versioned capability document
containing only reviewed TestClient lifecycle/relay and bounded display/UIA
operations.

#### Scenario: Compatible bridge is accepted
- **WHEN** qa-mcp reads a bridge capability document with the supported major
  version and required capabilities
- **THEN** it enables only those advertised standalone operations.

#### Scenario: Incompatible bridge fails closed
- **WHEN** the bridge reports an unsupported major version or omits a required
  capability
- **THEN** qa-mcp returns a structured compatibility error before lifecycle or
  desktop mutation.

### Requirement: Public bridge has no AI for 1C runtime dependency
The released bridge and installer MUST be built entirely from public repository
source and MUST NOT require COM worker, BSL agent, Team registry/onboarding,
agent CLI or another AI for 1C binary or service.

#### Scenario: Release executable is inspected and started
- **WHEN** the exact release executable is installed on a clean supported
  Windows host with 1C
- **THEN** it starts and reports standalone readiness without another product
  executable or account.

### Requirement: Removed product endpoints are absent
The public bridge SHALL omit COM, BSL, agent completion, Team
registration/onboarding and arbitrary platform execution routes.

#### Scenario: Removed routes are requested
- **WHEN** a client requests a retired product-specific route
- **THEN** the bridge returns not found
- **AND** the route is absent from capability and help output.

### Requirement: Standalone bridge preserves security and ownership
Every lifecycle, relay and desktop-control route MUST retain authenticated
access, target identity validation, bounded concurrency and exact owned
cleanup.

#### Scenario: Display request targets another process
- **WHEN** a request cannot bind its lifecycle/TPort identity to the selected 1C
  window
- **THEN** the bridge rejects input before desktop interaction.

#### Scenario: Explicit window hint cannot bypass lifecycle binding
- **WHEN** a display request includes an explicit selector together with an
  active TestClient target
- **THEN** the bridge requires and revalidates the exact owned lifecycle,
  PID and TPort
- **AND** it does not use the selector, foreground window or another process as
  an authority fallback.

#### Scenario: Concurrent route capacity is exhausted
- **WHEN** authenticated lifecycle or display work reaches the shared in-flight
  execution limit
- **THEN** the next request receives structured HTTP `429`
  `execution-capacity-exhausted` before handler or driver work
- **AND** capacity is released when prior work completes or fails.

#### Scenario: Owned TestClient is stopped
- **WHEN** stop is called for a bridge-owned lifecycle
- **THEN** only the exact owned process/task/relay state is removed
- **AND** unrelated 1C sessions remain running.

#### Scenario: Container reads through authenticated relay
- **WHEN** the standalone container connects to the configured relay endpoint
  with the protected bridge token
- **THEN** the relay authenticates before opening only the fixed loopback
  TestClient TPort
- **AND** a safe protocol read succeeds without exposing the token or protocol
  payload in retained evidence.

#### Scenario: Default uninstall removes configured relay firewall rule
- **WHEN** the operator uninstalls the exact owned bridge without repeating the
  optional relay address
- **THEN** the installer derives the owned relay port from persisted install
  state and removes its exact firewall rule before deleting that state.

### Requirement: Exact Windows release bytes are qualified
The release gate SHALL run Windows-native lifecycle, relay, display and recovery
tests against the exact source-bound executable that will be published.

#### Scenario: Release candidate passes Windows qualification
- **WHEN** the release executable is installed on the authorized Windows target
- **THEN** launch/read/input/screenshot/stop evidence identifies its hash and
  version
- **AND** rerun and exact cleanup evidence pass.

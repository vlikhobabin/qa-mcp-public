## ADDED Requirements

### Requirement: Host-agent self-registers its immutable bridge identity
When registry configuration is complete, the host-agent SHALL POST an `ai1c.bridge-registration.v1` envelope at startup and every configured heartbeat interval. The envelope MUST contain the startup-configured user, advertised endpoint, per-developer token, TTL, and an `ai1c.windows-host-bridge.discovery.v1` body; runtime requests MUST NOT change that user.

#### Scenario: Startup and heartbeat renew the lease
- **WHEN** the host-agent starts with complete registry configuration
- **THEN** the fixture registry receives an immediate registration and later heartbeats with the same user and endpoint
- **AND** each accepted heartbeat renews the observable lease TTL.

#### Scenario: Registry restart self-heals
- **WHEN** the registry forgets all registrations while the host-agent keeps running
- **THEN** the next heartbeat recreates the registration without operator action.

#### Scenario: Host-agent stop allows expiry
- **WHEN** the host-agent registration lifecycle stops
- **THEN** no more heartbeats are sent and the fixture registration expires within its TTL.

### Requirement: Registration failures are secret-safe and do not degrade the bridge
Registry network errors and authorization rejections SHALL update bounded registration status and be retried on the next heartbeat without terminating or disabling existing host-agent bridge endpoints. Token values MUST NOT appear in logs, health output, error details, or retained evidence.

#### Scenario: Registry rejects mismatched identity credentials
- **WHEN** the registry rejects the immutable configured user/token pair
- **THEN** registration status reports a bounded rejection without the token
- **AND** authenticated host-agent bridge health and operations remain available.

#### Scenario: Registry is unavailable
- **WHEN** a registration attempt fails due to network unavailability
- **THEN** the host-agent remains alive and retries at the next heartbeat.

### Requirement: Solo mode performs no registry I/O
When no registry URL is configured, the host-agent SHALL preserve prior solo behavior, report registration as disabled, and MUST NOT create any registry request.

#### Scenario: Registry configuration is absent
- **WHEN** the host-agent starts without a registry URL
- **THEN** the fixture request count remains zero and existing bridge endpoints behave as before.

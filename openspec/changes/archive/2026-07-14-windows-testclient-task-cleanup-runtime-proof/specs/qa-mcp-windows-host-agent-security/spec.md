## MODIFIED Requirements

### Requirement: Transient launch credentials are secret-safe

The Windows host-agent SHALL remove the exact transient launch task before
returning on success, failure or request cancellation. Production launch paths
SHALL invoke an idempotent cleanup boundary independent of the request context.
An explicit cleanup failure SHALL prevent a successful launch result and SHALL
leave an exact-name deferred retry armed.

#### Scenario: Cancellation and cleanup failure are proven on Windows

- **WHEN** the request context is canceled after an exact randomized QA-owned
  task has been registered
- **THEN** bounded cleanup independent of that context removes the exact task
- **AND** no wildcard or name-wide cleanup is used
- **AND** an injected first cleanup failure is returned as failure while the
  deferred fallback retries and removes that exact task
- **AND** the retained Windows-native result is bound to the same current source
  fingerprint as the delivered host-agent artifact and normal launch proof.

### Requirement: Solo mode performs no registry I/O

When no registry URL is configured, the host-agent SHALL keep registration
disabled even when its authenticated bridge endpoint has a host token. The
host token MAY default the bridge token only when registration is enabled by a
non-empty registry URL.

#### Scenario: Authenticated solo host-agent starts without registry URL

- **WHEN** the host-agent has an endpoint token and no registry URL
- **THEN** startup succeeds and registration health is disabled
- **AND** the endpoint token is not treated as partial registry configuration
- **AND** no registry request is created.

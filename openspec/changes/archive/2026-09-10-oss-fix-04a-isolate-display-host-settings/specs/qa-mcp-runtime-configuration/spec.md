## ADDED Requirements

### Requirement: Composed display clients use application settings
For an application built with explicit Settings, qa-mcp SHALL select local or
remote display behavior and construct host-agent clients solely from that
application's settings. Address, token, version/hash policy, window selector,
native client port and timeout MUST NOT be inherited from process environment
during a composed call. Existing documented fallback between host-agent client
port and application client port SHALL remain application-local.

#### Scenario: Conflicting factories and environment (C1)
- **WHEN** local and remote factories have distinct complete settings and execute interleaved display calls while process environment names a third host
- **THEN** each call uses its own backend, request destination, authentication, pins, window, native port and timeout
- **AND** local calls do not reach remote HTTP and remote calls do not select local X11.

### Requirement: Host lifecycle consumers share configuration and current ownership
Composed host-agent lifecycle calls SHALL use the same application-owned configuration as display calls.
This covers launch, status, stop and supported attach compatibility calls.
Each operation SHALL apply its current admitted attachment independently and
MUST retain existing target/session/generation and cleanup restrictions.

#### Scenario: Distinct applications and changing attachment (C2)
- **WHEN** two applications operate on distinct fake lifecycle identities and one changes its attachment
- **THEN** subsequent calls use the corresponding current identity and cannot retain another application's or an older session's target
- **AND** stopping one application does not signal or clear the other's session.

#### Scenario: Unproven project attach remains blocked (C2)
- **WHEN** a project-bound non-owned attach lacks the required observation
- **THEN** it remains blocked before host-agent or native invocation
- **AND** settings isolation does not create new attach authority.

### Requirement: Explicit absence cannot fall back to environment
Composed availability checks and associated mode/configuration diagnostics SHALL use the active application's settings.
Intentionally missing host-agent
configuration MUST NOT select a process-configured host or local fallback.
Configuration failures SHALL retain bounded diagnostics without credentials.

#### Scenario: Empty remote configuration and backend failure (C3)
- **WHEN** an explicit remote application lacks an agent address while process environment supplies one, or a configured fake backend fails
- **THEN** absence is reported without a request to that process host or local fallback
- **AND** the public error identifies the correct application mode without authentication tokens or private configuration values.

### Requirement: Configuration isolation preserves context and explicit legacy adapters
Application settings and backend target state MUST remain isolated under
nested, interleaved async and exceptional calls. Implementation MUST NOT mutate
process environment to route a composed operation. Explicit environment-based
backend construction outside composition SHALL retain its compatibility contract.

#### Scenario: Exceptional exit restores the caller and legacy controls (C4)
- **WHEN** calls from distinct factories interleave or raise, followed by a caller using an explicit legacy env mapping outside composition
- **THEN** application context is restored and neither factory's settings or attachment has leaked
- **AND** the legacy adapter reads only its supplied mapping with existing pin, timeout and port behavior.

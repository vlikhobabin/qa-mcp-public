## ADDED Requirements

### Requirement: Every bound native operation requires current route admission
Every project-bound native-session operation MUST validate the exact current
target, session, attachment, endpoint and binding generation independently of
positive-result schema membership. Rejection MUST produce a fixed blocked
outcome before native handlers, endpoint probes, display callbacks or protocol
sends, without changing target, session, attachment or ownership state.

#### Scenario: Native command has no current route
- **WHEN** a bound registered `click_command` or another native route has missing, stale or mismatched target, session, attachment or generation
- **THEN** it returns `runtime-target-route-blocked` before any native or display effect
- **AND** all application identities and ownership state remain unchanged.

#### Scenario: Shared entrypoint receives a schema-missing native operation
- **WHEN** a bound request reaches the common operation entrypoint without a positive-result schema
- **THEN** it cannot bypass route admission or execute an unknown route permissively.

### Requirement: Public operation classification is complete and explicit
Every registered public tool MUST have an explicit native-session-bound,
lifecycle, provider-data or pure/readiness classification. Schema presence MUST
NOT determine permission. Unknown routes in a bound application MUST fail
closed; lifecycle-specific admission and provider policies MUST remain in force.

#### Scenario: Registry completeness is checked
- **WHEN** both composed public profiles and direct/decorated registered routes are inventoried
- **THEN** every tool has one explicit classification and no unknown native route receives a permissive default.

### Requirement: Current admitted and unbound controls remain usable
An exact admitted bound route MUST retain representative read, write and display
operations using that route once. Pure tools, provider-data tools and valid
lifecycle operations MUST remain available under their own existing policies.
Explicit unbound compatibility MUST remain supported.

#### Scenario: Exact bound route executes
- **WHEN** representative read, write and display calls have the exact current admitted route
- **THEN** each native consumer receives its admitted endpoint and identity once
- **AND** there is no retargeting or cross-application state change.

#### Scenario: Independent and legacy operations execute
- **WHEN** pure/provider tools, valid lifecycle calls or explicit unbound tools are called
- **THEN** their supported behavior remains available with existing safety policies.

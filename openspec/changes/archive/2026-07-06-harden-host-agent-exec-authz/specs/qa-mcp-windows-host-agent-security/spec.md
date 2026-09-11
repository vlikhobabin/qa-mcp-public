## ADDED Requirements

### Requirement: Host-agent enforces platform argv mutation policy server-side
The Windows host-agent SHALL validate `/platform/execute` argv against the
declared `mutation_class` before resolving or spawning a 1C platform executable.
Requests declared `read_only` MUST be rejected when their executable and argv
contain known mutating 1C platform actions. Requests declared `mutating` MUST
still require operator intent through the existing platform execute policy.

#### Scenario: Read-only Designer execute is rejected before spawn
- **WHEN** an authenticated `/platform/execute` request declares
  `mutation_class: "read_only"` and supplies executable `designer` with argv
  containing `/Execute`
- **THEN** the host-agent returns a fail-closed policy error
- **AND** no platform process is spawned

#### Scenario: Read-only ibcmd probe still passes
- **WHEN** an authenticated `/platform/execute` request declares
  `mutation_class: "read_only"` and supplies a known read-only `ibcmd` argv such
  as `--version` or `config generation-id`
- **THEN** the host-agent continues through the existing allowlist, catalog
  resolution, timeout, redaction, and process result behavior

#### Scenario: Mutating platform argv requires a mutating declaration
- **WHEN** an authenticated `/platform/execute` request supplies known mutating
  platform argv
- **THEN** the request is accepted only when `mutation_class` is `mutating` and
  the existing operator-intent requirement is satisfied
- **AND** a missing or `read_only` mutation declaration is rejected before spawn

### Requirement: Host-agent bounds concurrent subprocess execution
The Windows host-agent SHALL apply a shared in-flight concurrency cap to
subprocess-spawning endpoints after authentication and request validation. The
cap MUST cover `/platform/execute`, `/com/execute`, and `/agent/complete`, and a
request that cannot acquire capacity MUST fail closed without spawning a
process.

#### Scenario: N+1 exec request is throttled before spawn
- **WHEN** the host-agent has reached its configured in-flight execution cap
- **AND** an authenticated caller sends another valid subprocess request to
  `/platform/execute`, `/com/execute`, or `/agent/complete`
- **THEN** the endpoint returns a bounded throttling error such as
  `execution-capacity-exceeded`
- **AND** no additional subprocess is spawned for that request

#### Scenario: Capacity is released after completion
- **WHEN** an execution endpoint acquires capacity and then returns success,
  failure, cancellation, or timeout
- **THEN** the in-flight slot is released
- **AND** a later valid request can acquire capacity normally

### Requirement: Host-agent failed-auth limiter evicts stale keys
The Windows host-agent SHALL remove failed-auth limiter entries whose retained
attempts have aged out of the limiter window. Eviction MUST prevent unbounded
map growth without weakening the existing wrong-token rate limit for currently
active failures.

#### Scenario: Expired failed-auth keys are removed
- **WHEN** failed-auth attempts for a client key are older than the configured
  limiter window
- **THEN** the limiter removes that key during maintenance
- **AND** the key no longer contributes to limiter map growth

#### Scenario: Active failed-auth attempts still rate limit
- **WHEN** a client key sends failed-auth attempts within the configured limiter
  window
- **THEN** the host-agent continues to reject attempts above the configured
  threshold with the existing rate-limit response

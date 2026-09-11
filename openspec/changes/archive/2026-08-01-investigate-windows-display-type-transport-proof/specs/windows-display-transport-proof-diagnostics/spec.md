## ADDED Requirements

### Requirement: Bounded typed transport evidence
The investigation proof SHALL retain the `type_text` HTTP status class and a
normalized structured error code without retaining response payloads, window or
process identities, screenshots, credentials, or host-agent logs.

#### Scenario: Error response is observed
- **WHEN** the source-bound `type_text` request returns a non-success HTTP response
- **THEN** the sanitized evidence contains its status class and allowlisted typed code and contains none of the excluded raw artifacts

### Requirement: Failure class is distinguishable
The investigation SHALL distinguish proof-client transport or parsing failure,
host-agent `foreground-denied`, typed desktop-session refusal, and unexpected
host-agent or fixture exit using bounded observable signals.

#### Scenario: Live host returns a typed refusal
- **WHEN** the host-agent and owned fixture remain live and the response exposes a recognized typed refusal
- **THEN** the result class identifies that product refusal rather than reporting an untyped transport failure

#### Scenario: An owned process exits
- **WHEN** the host-agent or owned fixture exits before the failing route completes
- **THEN** the result class identifies the unexpected process-exit boundary without recording its process identity

### Requirement: Investigation branches without widening product scope
The investigation SHALL repair and rerun an ignored proof harness when the
failure is harness-local, and SHALL create a linked implementation-card handoff
instead of editing product code when the host-agent invariant is defective.

#### Scenario: Harness parsing is defective
- **WHEN** the bounded response proves that the host returned a usable typed result which the proof client lost
- **THEN** the ignored harness is repaired and the full S50-120 Windows matrix is rerun

#### Scenario: Product invariant is defective
- **WHEN** a live source-bound host violates the expected typed route contract
- **THEN** a linked product-fix card records the exact invariant and complete verification floor before any product edit

### Requirement: Authorized execution and exact cleanup
The proof SHALL run only on the authorized Windows target with owned fixtures
and SHALL remove only its exact task, stage, processes, screenshots, token, and
logs.

#### Scenario: Proof finishes or fails
- **WHEN** the bounded proof reaches any terminal outcome
- **THEN** sanitized cleanup evidence confirms the exact owned resources are absent and no infobase or business data was accessed

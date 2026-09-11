## ADDED Requirements

### Requirement: Investigation preserves the exact published and runtime identity
I14 MUST bind its findings to the unchanged five published-I11 blobs and the
same operator-authorized Windows principal, host, platform, target, candidate,
fixtures and candidate argv identity used by the failed I13 row. It MUST NOT
substitute a host, identity, platform, target, fixture or candidate build.

#### Scenario: Every identity matches
- **WHEN** the five Git blobs and every runtime identity/hash match the I13
  evidence and authorized contour
- **THEN** bounded investigation may proceed.

#### Scenario: Any identity differs
- **WHEN** any bound source or runtime identity differs
- **THEN** I14 stops fail-closed without accepting evidence from that contour.

### Requirement: S4 failure evidence is bounded and typed
I14 SHALL isolate at most one investigation-owned S4 attempt using the exact
candidate arguments and inputs and SHALL retain only a closed failure class,
stage, exit code, duration, counts, hashes and booleans. It MUST retain no raw
UI, screenshot, credential, connection string or broad output and MUST NOT
claim that the attempt certifies I13.

#### Scenario: Failure is reproduced
- **WHEN** the candidate exits before its observation receipt
- **THEN** the decision identifies the earliest evidenced boundary and assigns
  a contour, harness or published-behavior classification.

#### Scenario: Failure is not reproduced
- **WHEN** the one bounded probe reaches a different terminal state
- **THEN** the decision records contour variance without starting another row
  or treating the probe as certification.

### Requirement: Protected task-topology drift is attributed without mutation
I14 MUST compare unrelated scheduled-task topology through hashed identities
and bounded counts and SHOULD correlate changes with narrowly bounded scheduler
events. It MUST classify the finding as deterministic harness behavior,
independent system drift or ownership violation only when bounded evidence
distinguishes the class; otherwise it MUST retain `NOT-VERIFIABLE` and infer no
cause. It MUST NOT stop, alter, unregister or expose unrelated tasks.

#### Scenario: Foreign task changes independently
- **WHEN** a non-I14 hashed task identity changes without an I14 action targeting
  it and bounded scheduler evidence attributes the change outside the owned
  task lifecycle
- **THEN** the decision classifies the finding as independent system drift.

#### Scenario: Owned action targets foreign state
- **WHEN** retained evidence shows an I14 cleanup or harness action selected a
  non-I14 task
- **THEN** the decision classifies an ownership violation and blocks publish.

#### Scenario: Started-route attribution is unavailable
- **WHEN** the historical started route and scheduler attribution are
  unavailable, so harness/start behavior and external drift remain
  observationally indistinguishable
- **THEN** the decision remains `NOT-VERIFIABLE`, rules out only causes directly
  excluded by retained evidence and infers no topology cause.

### Requirement: Exact restoration and double cleanup gate the decision
I14 MUST restore exact configuration bytes, ACL and retained metadata, remove
only exact-owned task, stage, process/job/desktop and transport state, and prove
the second cleanup pass performs no work. Any foreign target or residual owned
state SHALL block completion. Any unavailable initial continuity or typed
zero-state evidence SHALL be recorded as `NOT-VERIFIABLE` and MUST NOT be
reported as cleanup acceptance.

#### Scenario: Cleanup is exact and rerun-safe
- **WHEN** configuration state equals the before-image, owned residue is zero
  and the repeated cleanup reports zero removals
- **THEN** cleanup acceptance passes.

#### Scenario: Cleanup is incomplete or foreign
- **WHEN** configuration differs, owned residue remains or an unrelated target
  was selected
- **THEN** I14 stops fail-closed and is not publishable.

#### Scenario: Cleanup continuity is not evidenced
- **WHEN** an initial metadata value or typed job/desktop/transport zero-state
  was not retained
- **THEN** the decision identifies that exact gap as `NOT-VERIFIABLE` and does
  not infer restoration or zero-state for that surface.

### Requirement: Decision scopes correction and recertification separately
I14 MUST classify every finding as contour, harness, published behavior,
independent system drift, ownership violation or `not_verifiable` and MUST name
a separately authorized successor when correction or a fresh certification
attempt is needed. It SHALL NOT modify product/test source or archive/complete
I13.

#### Scenario: A correction is indicated
- **WHEN** evidence identifies a correctable harness or published-behavior
  defect
- **THEN** the decision names a separate correction card with its required
  verification and fresh review floor.

#### Scenario: A fresh certification attempt is indicated
- **WHEN** the investigation closes without modifying published behavior but
  I13 remains incomplete
- **THEN** the decision names a separate certification successor and leaves
  I13 `NOT-VERIFIABLE` and unarchived.

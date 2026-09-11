## ADDED Requirements

### Requirement: Safe UI action scope is explicitly gated
The protocol lab SHALL define the allowed safe UI action families and excluded
mutation semantics before accepting any action protocol case.

#### Scenario: Candidate action is selected
- **WHEN** a safe UI action candidate is added to the protocol case matrix
- **THEN** the candidate records its action family, UI target, pre-state,
  expected post-state and recovery or cleanup expectation
- **AND** the candidate is limited to focus or element activation, existing
  window activation, tab or page switching, or menu expansion that does not
  execute a command

#### Scenario: Candidate action would mutate business data
- **WHEN** a candidate requires text input, command execution, checkbox
  toggling, table editing, save/post/delete behavior or another persisted data
  mutation
- **THEN** the candidate is excluded from the safe UI action matrix
- **AND** the exclusion records that a separate mutation-specific card is
  required before capture

### Requirement: Safe UI actions preserve unresolved read-only evidence gates
The protocol lab SHALL keep controlled fixture and read-only element hash
outcomes visible when choosing safe UI action targets.

#### Scenario: Read-only prerequisite is unresolved or deferred
- **WHEN** a safe UI action target depends on a read-only fixture family or
  element request shape with non-accepted evidence
- **THEN** the action candidate records the unresolved status, owner route and
  residual risk
- **AND** the candidate is not accepted as protocol knowledge until later
  capture and replay or probe evidence satisfies the safe action contract

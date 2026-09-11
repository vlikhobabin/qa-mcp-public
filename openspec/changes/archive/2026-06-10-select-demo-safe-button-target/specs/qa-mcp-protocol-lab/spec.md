## ADDED Requirements

### Requirement: Demo button target selection is read-only and explicit
The protocol lab SHALL select a demo real-button pilot target through a
read-only target-selection record before any safety classification or runtime
action is attempted.

#### Scenario: Demo button target is selected
- **WHEN** a demo button is selected for the pilot
- **THEN** the selection record includes the demo form path, element path,
  visible caption or marker, enabled and visible state, target owner, source
  evidence route and planned evidence bundle path
- **AND** the selected target is not clicked by the selection step

#### Scenario: No eligible target is found
- **WHEN** read-only discovery cannot identify a concrete button without
  ambiguity
- **THEN** the selection result records `blocked`, `unsupported` or `deferred`
  with reason, owner route and residual risk
- **AND** downstream classification and capture steps do not invent a target

### Requirement: Rejected demo button candidates remain visible
The protocol lab SHALL preserve rejected or deferred demo button candidates in
compact planning evidence instead of silently omitting them.

#### Scenario: Demo button candidate is rejected
- **WHEN** a candidate appears to be a business command, write action, external
  side effect or otherwise unsafe target
- **THEN** the selection evidence records the candidate caption or marker,
  rejection reason, owner route and residual risk
- **AND** the candidate is not passed to runtime execution

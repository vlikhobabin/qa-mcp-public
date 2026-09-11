## ADDED Requirements

### Requirement: V3 mutation cases retain before/action/post/reset evidence

The protocol lab SHALL retain a recovery-proof sequence for each V3 mutation
case.

#### Scenario: Mutation proof includes the full recovery path

- **WHEN** a V3 mutation case is captured for review
- **THEN** the evidence bundle contains before, action, post and reset
  observations
- **AND** the bundle records the expected recovery path for the case

### Requirement: V3 mutation cases reset to the baseline after failure

The protocol lab SHALL restore the V1 baseline after a failed or completed V3
mutation case.

#### Scenario: Reset returns the fixture to baseline after failure

- **WHEN** a V3 mutation attempt fails before acceptance
- **THEN** the fixture can be reset to the same baseline state used before the
  attempt
- **AND** the remaining marker set matches the documented recovery expectation

### Requirement: V3 mutation evidence isolates action frames

The protocol lab SHALL keep the candidate action frame range separate from
bootstrap, background refresh and cleanup traffic.

#### Scenario: Evidence separates action and background traffic

- **WHEN** a V3 mutation proof is reviewed
- **THEN** the candidate action range is distinct from background and cleanup
  frames
- **AND** the reviewed evidence can explain any residual traffic that remains
  outside the action range

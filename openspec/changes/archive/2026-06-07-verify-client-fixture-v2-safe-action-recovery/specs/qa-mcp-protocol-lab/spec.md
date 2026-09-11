## ADDED Requirements

### Requirement: V2 safe-action cases include recovery evidence

The protocol lab SHALL verify that each safe-action case can return the
fixture to baseline after execution.

#### Scenario: Recovery is proven

- **WHEN** a safe action is run in the fixture
- **THEN** the evidence records before, action, post and recovery markers plus
  the reset result
- **AND** the fixture returns to baseline without business data mutation

### Requirement: Safe-action capture isolates candidate action frames

The protocol lab SHALL separate candidate action frame ranges from bootstrap,
refresh and cleanup traffic.

#### Scenario: Candidate range is isolated

- **WHEN** a safe action capture is reviewed
- **THEN** the candidate frame range excludes background refresh and cleanup
  traffic
- **AND** the evidence records normalized hash, dynamic fields and action
  result markers

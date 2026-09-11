## ADDED Requirements

### Requirement: V2 safe-action reporter publishes separated action evidence

The protocol lab SHALL publish V2 safe-action evidence with action,
background and recovery ranges separated.

#### Scenario: Reporter emits action-specific frame ranges

- **WHEN** a V2 safe-action capture is reported
- **THEN** each action row records `action_frame_range`,
  `background_frame_ranges` and `recovery_frame_range` when those ranges are
  present
- **AND** the action range is not treated as accepted proof by itself

#### Scenario: Reporter emits action result state

- **WHEN** a safe-action row has pre-state, post-state and recovery data
- **THEN** the report records `pre_state`, `post_state`, `recovery_result` and
  `action_result_markers`
- **AND** missing values keep the row non-accepted with an explicit reason

### Requirement: V2 safe-action reporter preserves V1 read-only reporting

The protocol lab SHALL keep V1 read-only report behavior stable while adding
V2 safe-action report output.

#### Scenario: V1 report path remains stable

- **WHEN** existing V1 read-only evidence is reported
- **THEN** V1 output remains compatible with the current evidence contract
- **AND** V2 action fields are added only to safe-action rows

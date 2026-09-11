## ADDED Requirements

### Requirement: Safe action case events record state transitions
The protocol lab SHALL record safe UI action case events with enough
state-transition detail to review the intended action independently from raw
traffic.

#### Scenario: Safe action event row is emitted
- **WHEN** the runner or analyzer emits a safe UI action case event
- **THEN** the event records `case_id`, `api_call`, `ui_target`,
  `pre_state`, `action`, `post_state`, `recovery_expectation` and
  `action_result_markers`
- **AND** the event records whether the case is `supported`, `pending`,
  `unsupported`, `partial`, `timeout` or `rejected`

### Requirement: Action frame ranges are separated from background refresh
The protocol lab SHALL distinguish action-related frames from background
refresh frames in reviewed action evidence.

#### Scenario: Background traffic surrounds an action
- **WHEN** a captured safe UI action includes active-window, active-form,
  idle or refresh traffic outside the selected action boundary
- **THEN** the compact evidence records the action frame range separately from
  background or refresh frame ranges
- **AND** the row does not treat refresh-only frames as proof of the action

### Requirement: Safe action rows preserve corpus evidence fields
The protocol lab SHALL retain the core corpus evidence fields for safe UI
action rows.

#### Scenario: Safe action row is generated
- **WHEN** compact reviewed evidence is generated for a safe UI action case
- **THEN** the row includes `case_id`, `api_call`, `ui_target`,
  `frame_range`, `normalized_hash`, dynamic fields, `operation_token`,
  `response_markers`, `replay_status` and action result markers
- **AND** raw request and response payloads remain outside reviewed evidence

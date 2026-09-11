## ADDED Requirements

### Requirement: Agent instructions enforce the V2 safety boundary
The protocol lab SHALL keep local agent-facing instructions aligned with the
documented V2 safe-action manifest contract.

#### Scenario: Agent plans a V2 safe action
- **WHEN** an agent plans a V2 UI action capture, replay or manager-runner
  step
- **THEN** the agent verifies that the action is represented by a reviewed V2
  safe-action manifest row
- **AND** the row has `mutates_business_data=false`, an allowed action family,
  target marker, pre-state, post-state, recovery expectation and expected
  action result markers

#### Scenario: User requests a broad click or action
- **WHEN** a user requests a click, input, command execution, write or other
  broad UI action during V2 work
- **THEN** the agent classifies the request against the V2 manifest allowlist
- **AND** fails closed or routes the request to later mutation/recovery work
  when the request is not explicitly fixture-local and non-mutating

### Requirement: Mutating UI behavior is routed outside V2
The protocol lab SHALL keep text input, value toggles, business command clicks
and persisted data mutation out of V2 agent workflows.

#### Scenario: Action would mutate or require rollback
- **WHEN** an action could write object data, change persisted settings, save,
  post, delete, fill, import, export or require cleanup evidence
- **THEN** local agent instructions route the work to a later V3/V4 card
- **AND** V2 protocol research does not execute or accept the action

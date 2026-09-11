## ADDED Requirements

### Requirement: V2 safe-action manifests are fail-closed
The protocol lab SHALL define every V2 safe-action candidate through a
complete manifest row before the action can be executed, captured or accepted
as protocol evidence.

#### Scenario: Manifest row is reviewed
- **WHEN** a V2 safe-action manifest row is added
- **THEN** the row records `action_id`, `target_id`, `target_marker`,
  `pre_state`, `action`, `post_state`, `recovery_expectation`,
  `mutates_business_data`, `allowed_action_family` and
  `expected_action_result_markers`
- **AND** `mutates_business_data` is `false`
- **AND** the row has enough expected markers to distinguish the action result
  from background refresh or unrelated UI traffic

#### Scenario: Manifest row is incomplete
- **WHEN** a V2 safe-action row lacks a target marker, pre-state, post-state,
  recovery expectation, safety flag or expected action result markers
- **THEN** the row is rejected before capture or manager-runner execution
- **AND** no protocol mapping is accepted from that row

### Requirement: V2 action families are explicitly allowlisted
The protocol lab SHALL limit the first V2 safe-action layer to non-mutating
fixture-local UI actions.

#### Scenario: Candidate action is allowlisted
- **WHEN** a V2 candidate action belongs to focus or activate existing element,
  activate existing window/form, switch fixture page, select local table row,
  or expand/collapse menu or group without command execution
- **THEN** the action may be represented in the V2 manifest as a candidate
- **AND** it still remains unaccepted until later capture and replay or direct
  probe evidence proves the action request shape

#### Scenario: Candidate action is outside V2
- **WHEN** a candidate requires text input, checkbox or value toggle, business
  command click, object write, save, post, delete, fill, import, export or an
  external side effect
- **THEN** the candidate is excluded from V2 and routed to later mutation or
  recovery work
- **AND** the V2 runner fails closed instead of attempting the action

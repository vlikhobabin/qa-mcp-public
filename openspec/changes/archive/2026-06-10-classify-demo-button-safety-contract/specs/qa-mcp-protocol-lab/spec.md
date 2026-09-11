## ADDED Requirements

### Requirement: Demo button classification fails closed before execution
The protocol lab SHALL classify a selected demo real-button target before any
runtime click or capture is attempted.

#### Scenario: Demo button is classified as capture-eligible
- **WHEN** the selected demo button has a complete manifest row with target
  marker, pre-state, concrete action, post-state, recovery expectation,
  expected action result markers, allowlisted action family and
  `mutates_business_data=false`
- **THEN** the classification evidence may mark the row as `safe_ui_action` or
  `inert_local_action` for the guarded capture step
- **AND** the evidence records the source facts that justify non-mutating
  behavior

#### Scenario: Demo button cannot be classified safely
- **WHEN** the selected target lacks required manifest fields, has unknown side
  effects or cannot justify `mutates_business_data=false`
- **THEN** the row is marked `blocked`, `unsupported` or routed to V3 mutation
  work before execution
- **AND** no runtime click is attempted by the classification step

### Requirement: Demo business buttons are routed to mutation work
The protocol lab SHALL route demo buttons that execute business commands or
require rollback to V3 or later mutation/recovery work rather than V2 capture.

#### Scenario: Button is a business mutation
- **WHEN** classification finds object writes, save, post, delete, fill,
  import, export, exchange, persisted settings or external side effects
- **THEN** the classification decision records a V3 routing reason, owner route
  and residual risk
- **AND** the guarded capture change receives no executable V2 row for that
  button

## ADDED Requirements

### Requirement: Demo button pilot capture executes only reviewed safe rows
The protocol lab SHALL execute a demo real-button pilot capture only when the
selected row has passed safety classification and still matches runtime
pre-state.

#### Scenario: Reviewed row is executed
- **WHEN** a selected demo button row is complete, non-mutating, allowlisted and
  runtime pre-state matches the manifest
- **THEN** the capture may execute the single reviewed action
- **AND** the run records pre-read, action-start, action-end, post-read and
  recovery or recovery-read phase evidence

#### Scenario: Capture gate fails
- **WHEN** the classification is missing, incomplete, unsafe, mutating or the
  live pre-state does not match the manifest
- **THEN** the capture records a blocked or rejected summary without clicking
  the button
- **AND** the row is routed to publication as non-accepted evidence

### Requirement: Demo button capture keeps raw runtime artifacts ignored
The protocol lab SHALL keep raw demo-button pilot runtime output outside
reviewed git while retaining compact evidence summaries.

#### Scenario: Runtime output is produced
- **WHEN** the guarded capture writes traffic logs, process logs, screenshots or
  generated replay payloads
- **THEN** raw output remains under ignored runtime or artifact paths
- **AND** reviewed evidence links only compact summaries, phase labels, frame
  ranges, markers and recovery status

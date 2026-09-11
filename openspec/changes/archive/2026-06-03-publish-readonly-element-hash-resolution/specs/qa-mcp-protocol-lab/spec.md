## ADDED Requirements

### Requirement: Read-only element hash resolution is published as accepted or unresolved
The protocol lab SHALL publish the final resolution for useful read-only
element hash gaps as either accepted mapping evidence or a precise unresolved
report.

#### Scenario: Element row is accepted
- **WHEN** `form-element-details` or `typed-input-field-readonly` has stable
  reviewed request hashes and accepted replay or direct Python-manager proof
  for the same operation
- **THEN** the published evidence records capture ids, frame ranges, request
  and response sizes, normalized hashes, dynamic fields, operation tokens,
  response markers, replay or probe status and evidence paths
- **AND** package descriptors may expose the row as accepted

#### Scenario: Element row remains unresolved
- **WHEN** accepted evidence is unavailable or incomplete for an element row
- **THEN** the published evidence records the non-accepted status, precise
  unresolved reason, source evidence paths and next actionable blocker
- **AND** package descriptors continue to expose `incomplete_hash` or another
  explicit non-accepted status for that row

### Requirement: Read-only element publication does not broaden action coverage
The protocol lab SHALL keep read-only element hash publication separate from
safe UI action, input and write behavior.

#### Scenario: Publication completes
- **WHEN** accepted or unresolved read-only element hash evidence is published
- **THEN** no click, input, command execution, business-data mutation or
  safe-action protocol descriptor is introduced by the publication change

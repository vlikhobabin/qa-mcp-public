## ADDED Requirements

### Requirement: Read-only corpus matrix covers common form element families
The protocol lab SHALL define an expanded read-only corpus matrix for common
1C form element families before action or write protocol cases are accepted.

#### Scenario: Expanded element case is captured
- **WHEN** a corpus case targets a supported read-only element family such as
  button, table, command bar, page, label, checkbox or typed input field
- **THEN** the case row identifies the element family, 1C testing API call,
  UI target, expected state and safety class
- **AND** the case row records frame ranges, normalized hash, dynamic fields,
  operation token, response markers and replay status

### Requirement: Missing element families are explicit corpus gaps
The protocol lab SHALL make unsupported or unavailable read-only element
families visible instead of silently omitting them from the matrix.

#### Scenario: Element family is unavailable in the current lab form
- **WHEN** the expanded matrix includes an element family not present in the
  current TestClient fixture
- **THEN** the corpus evidence records the family as `unsupported` or
  `pending`
- **AND** the reviewed notes identify whether a new fixture, metadata mapping
  or Python-manager probe is needed before acceptance

### Requirement: Expanded corpus evidence remains read-only
The protocol lab SHALL keep the expanded corpus matrix limited to read-only
queries until action and write semantics have separate recovery evidence.

#### Scenario: Proposed case would mutate business data
- **WHEN** a candidate case requires input, click, command execution or other
  business-data mutation
- **THEN** it is excluded from the read-only matrix
- **AND** it is routed to a later safe-action or mutation-specific card

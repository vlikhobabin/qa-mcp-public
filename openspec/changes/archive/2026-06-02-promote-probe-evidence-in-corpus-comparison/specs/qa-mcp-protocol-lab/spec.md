## ADDED Requirements

### Requirement: Probe-confirmed rows are promoted by repeatability comparison
The protocol lab SHALL allow repeatability comparison to classify stable
read-only rows as accepted when compact replay or direct-probe evidence
confirms the same operation.

#### Scenario: Stable row has accepted probe evidence
- **WHEN** two or more reviewed corpus inputs contain the same read-only
  `case_id` with the same non-null `normalized_hash`
- **AND** the row has accepted replay or direct Python-manager probe evidence
  linked to the same operation and expected response markers
- **THEN** the comparison report classifies the mapping as stable accepted
- **AND** the report lists the accepted case id, source captures, probe
  evidence path and normalized hash

### Requirement: Probe promotion preserves unresolved rows
The protocol lab SHALL keep rows without complete request-hash evidence or
unambiguous probe joins out of accepted comparison results.

#### Scenario: Probe evidence is useful but request evidence is incomplete
- **WHEN** a direct Python-manager probe returns useful data for a read-only
  family
- **BUT** the reviewed corpus row lacks request-frame or non-null
  `normalized_hash` evidence
- **THEN** comparison evidence records the row as `incomplete_hash`,
  `partial`, `pending` or another explicit non-accepted class
- **AND** the report records the unresolved reason for the next protocol pass

### Requirement: Accepted mapping evidence is compact and reproducible
The protocol lab SHALL generate compact accepted-mapping evidence without
committing raw captures or full probe output.

#### Scenario: Accepted mapping report is generated
- **WHEN** accepted read-only mappings are produced from repeated corpus rows
  and probe evidence
- **THEN** the reviewed evidence records capture ids, frame ranges, request
  and response sizes, normalized hashes, dynamic fields, operation tokens,
  response markers, probe status and evidence paths
- **AND** raw capture streams, process logs and full probe outputs remain
  under ignored runtime directories

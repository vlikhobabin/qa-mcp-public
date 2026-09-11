## ADDED Requirements

### Requirement: Read-only element hash gaps are audited before promotion
The protocol lab SHALL audit useful read-only element direct-probe rows against
the corpus evidence contract before promoting them or publishing a final
unresolved status.

#### Scenario: Element row evidence is inventoried
- **WHEN** `form-element-details` or `typed-input-field-readonly` is reviewed
  for possible promotion
- **THEN** the audit records the source evidence paths, capture ids, frame
  ranges, request and response sizes, normalized hashes, dynamic fields,
  operation token, response markers and replay or direct Python-manager status
  currently available for that row

#### Scenario: Element row gap is classified
- **WHEN** a useful element direct-probe row lacks complete accepted evidence
- **THEN** the audit records whether the gap is caused by missing request
  frames, an ambiguous operation join, unsupported fixture state, incomplete
  normalizer coverage or another explicit reviewed reason
- **AND** the row remains non-accepted until a later change supplies accepted
  evidence and publication updates

### Requirement: Element hash audits preserve raw evidence boundaries
The protocol lab SHALL keep raw captures, full probe output and local process
logs out of reviewed audit artifacts.

#### Scenario: Audit report references runtime evidence
- **WHEN** the audit needs to reference raw capture or probe output
- **THEN** it links or names the ignored runtime source location without
  copying raw TCP payloads, full runtime logs, credentials or local infobase
  data into committed evidence

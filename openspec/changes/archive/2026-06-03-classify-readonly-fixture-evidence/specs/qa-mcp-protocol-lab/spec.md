## ADDED Requirements

### Requirement: Fixture evidence is classified before publication

The protocol lab SHALL classify every planned controlled read-only fixture
family before publishing accepted fixture mappings.

#### Scenario: Fixture family has complete evidence

- **WHEN** repeated fixture corpus rows have stable non-null normalized hashes
  and accepted replay or direct-probe evidence for the expected operation
- **THEN** classification evidence may mark the family as `accepted`
- **AND** the evidence records capture ids, frame ranges, request/response
  sizes, dynamic fields, operation tokens, response markers, probe status and
  reviewed evidence paths

#### Scenario: Fixture family has incomplete evidence

- **WHEN** fixture evidence lacks a frame range, stable normalized hash,
  response marker, replay/probe confirmation or source readiness
- **THEN** classification evidence marks the family as `partial`, `pending`,
  `unsupported`, `timeout`, `rejected` or `blocked` with unresolved reason
- **AND** the family is not published as an accepted mapping

### Requirement: Fixture classification does not rewrite historical evidence

The protocol lab SHALL write fixture classification results under a new
reviewed evidence id instead of modifying historical corpus rows in place.

#### Scenario: Fixture comparison is generated

- **WHEN** fixture corpus runs are compared or classified
- **THEN** compact comparison, normalizer or accepted-mapping outputs use a new
  evidence directory
- **AND** raw capture streams, raw probe output and historical corpus rows
  remain unchanged

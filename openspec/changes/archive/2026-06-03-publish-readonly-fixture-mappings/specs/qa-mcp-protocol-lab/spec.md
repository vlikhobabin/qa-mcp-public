## ADDED Requirements

### Requirement: Fixture mapping publication is evidence-gated

The protocol lab SHALL publish controlled read-only fixture mapping results
only from reviewed classification evidence.

#### Scenario: Accepted fixture mapping is published

- **WHEN** a fixture family is classified as accepted
- **THEN** the published accepted-mapping docs link capture ids, frame ranges,
  normalized hashes, dynamic fields, operation tokens, response markers,
  replay or probe status and reviewed evidence paths
- **AND** raw captures and full probe output remain outside reviewed git
  changes

#### Scenario: Fixture family remains unresolved

- **WHEN** a fixture family is classified as `partial`, `pending`,
  `unsupported`, `timeout`, `rejected` or `blocked`
- **THEN** publication keeps the unresolved status, reason and next owner
  visible in corpus, comparison or evidence-index notes
- **AND** the family is not listed as an accepted mapping

### Requirement: Fixture publication preserves evidence lineage

The protocol lab SHALL preserve source, corpus, probe, comparison and accepted
mapping evidence lineage for fixture-derived rows.

#### Scenario: Fixture evidence is indexed

- **WHEN** fixture evidence is published
- **THEN** the evidence index links the source summary, corpus output, probe
  output, comparison/classification output and accepted-mapping output that
  were produced
- **AND** each link points to compact reviewed evidence rather than ignored
  runtime payloads

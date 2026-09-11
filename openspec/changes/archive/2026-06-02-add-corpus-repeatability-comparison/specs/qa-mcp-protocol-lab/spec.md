## ADDED Requirements

### Requirement: Corpus cases are compared across repeated captures
The protocol lab SHALL compare repeated corpus captures for the same case set
before treating expanded read-only mappings as stable dictionary entries.

#### Scenario: Repeated corpus rows are compared
- **WHEN** two or more corpus runs contain the same `case_id`
- **THEN** the comparison records capture ids, evidence paths,
  normalized hashes, request/response sizes, operation tokens and replay
  statuses for that case
- **AND** stable and divergent values are reported separately

### Requirement: Repeatability gaps are visible
The protocol lab SHALL report missing cases or unsupported replay outcomes in
repeatability evidence instead of hiding them.

#### Scenario: Repeated capture is missing a case
- **WHEN** a comparison input does not contain a case that exists in another
  run for the same matrix
- **THEN** the comparison report marks that case as a gap
- **AND** the report keeps the mapping out of accepted stable entries until
  the gap is explained

### Requirement: Divergence feeds dynamic-field investigation
The protocol lab SHALL route unexplained normalized-hash divergence to a
dynamic-field investigation path.

#### Scenario: Normalized hash diverges for the same case
- **WHEN** repeated captures have the same `case_id` but different
  `normalized_hash` values
- **THEN** the comparison report lists candidate differing fields or marks the
  case for normalizer investigation
- **AND** the mapping remains non-stable until the divergence is explained

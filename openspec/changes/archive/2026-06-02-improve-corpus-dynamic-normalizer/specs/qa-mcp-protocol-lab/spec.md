## ADDED Requirements

### Requirement: Dynamic-field normalizer changes are evidence-backed
The protocol lab SHALL add dynamic-field normalizer rules only when reviewed
evidence shows why the bytes are safe to replace.

#### Scenario: New dynamic range is normalized
- **WHEN** a new dynamic range is added to corpus normalization
- **THEN** reviewed evidence records the range name, source class, direction,
  offset or locator, length, replacement label and observed values
- **AND** the evidence links to repeated captures or replay/probe results that
  justify the replacement

### Requirement: Normalizer reports before and after hash behavior
The protocol lab SHALL report how a normalizer change affects request-shape
hashes for repeated corpus cases.

#### Scenario: Normalizer rule stabilizes a repeated case
- **WHEN** a new normalizer rule changes divergent hashes into a stable
  normalized hash
- **THEN** the compact evidence records the before-hash set, after-hash set
  and cases affected
- **AND** response markers or replay/probe status still support the mapping

### Requirement: Ambiguous dynamic ranges remain visible
The protocol lab SHALL keep ambiguous byte or text ranges visible instead of
normalizing them as accepted dynamic fields.

#### Scenario: Candidate range may be semantic
- **WHEN** a differing range cannot be proven session-specific
- **THEN** the analyzer marks it as ambiguous or pending investigation
- **AND** any affected mapping is not promoted as a stable accepted dictionary
  entry

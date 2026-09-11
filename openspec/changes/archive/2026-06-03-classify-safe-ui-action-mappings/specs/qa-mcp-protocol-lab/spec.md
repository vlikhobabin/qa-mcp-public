## ADDED Requirements

### Requirement: Safe UI action mappings require classification
The protocol lab SHALL classify safe UI action evidence before using an action
row as working protocol knowledge.

#### Scenario: Safe action evidence is classified
- **WHEN** compact safe UI action evidence is compared or reviewed
- **THEN** every row is classified as `accepted`, `pending`, `unsupported`,
  `partial`, `timeout`, `rejected` or `blocked`
- **AND** the classification records capture ids, action frame ranges,
  background refresh ranges, normalized hashes, dynamic fields, operation
  tokens, response markers, action result markers and evidence paths when
  available

### Requirement: Accepted safe UI action mappings require replay or probe proof
The protocol lab SHALL require replay or direct Python-manager confirmation
before a safe UI action mapping is accepted.

#### Scenario: Safe action row is accepted
- **WHEN** a safe UI action row is promoted to accepted mapping evidence
- **THEN** the row has reviewed action frame evidence and accepted replay or
  direct Python-manager proof for the same non-mutating action
- **AND** the row retains pre-state, post-state, recovery expectation,
  normalized hash, dynamic fields, operation token, response markers and
  action result markers

#### Scenario: Replay or probe is unavailable
- **WHEN** current tooling cannot safely replay or directly probe a safe UI
  action row
- **THEN** the row remains `pending`, `unsupported`, `partial`, `timeout`,
  `rejected` or `blocked` with an owner route and residual risk
- **AND** the row is not published as an accepted mapping

### Requirement: Safe action publication preserves unresolved rows
The protocol lab SHALL publish unresolved safe UI action outcomes without
rewriting historical evidence.

#### Scenario: Safe action publication completes
- **WHEN** safe UI action classification or accepted-mapping evidence is
  published
- **THEN** the evidence index links compact capture, classification,
  replay/probe and accepted or unresolved mapping artifacts
- **AND** unsupported or unresolved rows remain visible with reason values
  instead of being omitted from reviewed coverage

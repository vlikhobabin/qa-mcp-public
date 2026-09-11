## ADDED Requirements

### Requirement: Manager fixture V1 marker contract corrections are evidence-gated

The protocol lab SHALL change manager fixture V1 expected markers only when
current-run replay or direct-probe evidence proves the corrected semantic
contract.

#### Scenario: Marker correction is accepted

- **WHEN** a pending row's expected marker is corrected
- **THEN** the retained evidence records the previous marker, corrected marker,
  case id, manager frame range and normalized hash
- **AND** the regenerated report validates the corrected marker against the
  current cleanup row before accepting it

#### Scenario: Marker correction is candidate-only

- **WHEN** a candidate marker appears plausible but lacks current-run proof
- **THEN** the marker is retained as candidate evidence
- **AND** the row remains non-accepted

#### Scenario: Catalogs remain aligned

- **WHEN** marker expectations change in a manifest, JSON catalog or BSL source
- **THEN** the protocol lab verifies that the reviewed command catalogs remain
  aligned
- **AND** records any catalog drift as a blocker before publication

## ADDED Requirements

### Requirement: Broad manager fixture V1 pending windows are isolated before acceptance

The protocol lab SHALL isolate broad manager fixture V1 pending frame windows
or keep them non-accepted with an explicit isolation gap before publishing an
accepted protocol mapping for those rows.

#### Scenario: Broad window is isolated

- **WHEN** a pending row currently spans a broad manager frame range
- **THEN** the protocol lab produces a narrower reviewed range or focused
  rerun for that case id
- **AND** the isolated row records request size, response size, dynamic fields,
  normalized hash and response markers

#### Scenario: Isolation fails

- **WHEN** a broad pending row cannot be isolated from background or endpoint
  traffic
- **THEN** the row remains non-accepted
- **AND** the reviewed evidence records the blocker and owner route

#### Scenario: Target marker alone is insufficient

- **WHEN** a target marker appears inside a broad frame window
- **THEN** the marker alone SHALL NOT promote the row
- **AND** accepted promotion still requires matching replay or direct-probe
  proof for the reviewed range

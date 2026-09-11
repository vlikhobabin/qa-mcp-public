## ADDED Requirements

### Requirement: Manager V2 safe-action evidence is published compactly
The protocol lab SHALL publish manager fixture V2 safe-action candidate
evidence as compact reviewed rows without committing raw runtime captures.

#### Scenario: Candidate evidence is retained
- **WHEN** a manager V2 safe-action run publishes reviewed evidence
- **THEN** the row records action id, target marker, action frame range,
  background ranges, recovery result, normalized hash fields and action result
  markers where available
- **AND** raw captures, platform logs and generated replay payloads remain
  under ignored runtime paths

#### Scenario: Accepted status requires proof
- **WHEN** a manager V2 safe-action row has joined action frames but lacks
  accepted replay/probe or typed contract proof
- **THEN** the row remains candidate or another explicit non-accepted status
- **AND** accepted mapping output excludes the row

#### Scenario: Focused proof can consume evidence
- **WHEN** candidate evidence is published for the supported runner subset
- **THEN** the first focused V2 safe-action proof card can cite the evidence
  path and decide whether rows are accepted or remain candidate

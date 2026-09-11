## ADDED Requirements

### Requirement: First focused V2 safe-action proof is published with explicit status
The protocol lab SHALL publish the first focused V2 safe-action proof with
compact evidence links and explicit accepted or non-accepted status.

#### Scenario: Accepted proof is published
- **WHEN** at least one focused safe-action row has reviewed action frames,
  recovery evidence and accepted replay, direct probe or typed contract proof
- **THEN** protocol docs and evidence indexes link the compact proof report and
  accepted mapping output
- **AND** the report records action id, target marker, normalized hash, dynamic
  fields, operation token, action result markers and proof evidence links where
  available

#### Scenario: Candidate proof is published
- **WHEN** the focused row has reviewed compact evidence but lacks accepted
  replay, direct probe or typed contract proof
- **THEN** protocol docs and evidence indexes publish the row as candidate or
  another explicit non-accepted status
- **AND** accepted mapping output excludes the row and records why it is not
  accepted

#### Scenario: V2 safety boundary remains visible
- **WHEN** the first focused proof is published
- **THEN** docs state that text input, checkbox/value toggles, business command
  clicks, object writes, save/post/delete/fill/import/export and external side
  effects remain outside V2
- **AND** downstream demo pilot or mutation cards are linked only as later work

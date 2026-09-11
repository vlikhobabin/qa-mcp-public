## ADDED Requirements

### Requirement: Native write committed status is based on normalized target-field read-back

The qa-mcp protocol-layer native write path SHALL report `committed: true` only when the target field's decoded
read-back value equals the normalized requested value, except for explicitly documented type formatting such as a date
read-back suffix. Generic prefix matches SHALL NOT prove a commit.

#### Scenario: Prefix of existing value is not committed

- **WHEN** a native write requests `123` and the target field reads back `123456`
- **THEN** qa-mcp reports `committed: false`
- **AND** it records the observed `readback_value`

#### Scenario: Cyrillic value reads back as committed

- **WHEN** a native write requests a Cyrillic value and the target field's protocol read-back contains the same value
- **THEN** qa-mcp decodes that value from the read-back frame
- **AND** reports `committed: true`

#### Scenario: Edge-length values read back as committed

- **WHEN** a native write requests a one-character value or a value longer than 40 bytes and the target field reads back
  that value
- **THEN** qa-mcp decodes the read-back instead of rejecting it by length
- **AND** reports `committed: true`

#### Scenario: Missing read-back is not a commit

- **WHEN** the target field value cannot be decoded from protocol read-back frames
- **THEN** qa-mcp reports `committed: false`
- **AND** it does not infer success from a prefix, sibling field, or old value

## ADDED Requirements

### Requirement: Native write retargeting addresses UTF-16 field leaves

The qa-mcp native write path SHALL retarget write and read-back frames to the requested field leaf when an element path
is encoded as either latin1 or UTF-16LE. A write request for a Cyrillic-named field SHALL NOT send an expected write SET
frame that remains addressed to the captured template field.

#### Scenario: Cyrillic SET frame is retargeted

- **WHEN** a native write frame contains a UTF-16LE `EditField[<base>]` element leaf and the caller requests a Cyrillic
  target field
- **THEN** the emitted frame addresses `EditField[<target>]`
- **AND** the frame no longer addresses the captured base field for that SET operation

#### Scenario: Unexpected retarget miss fails closed

- **WHEN** a write or read-back frame is expected to contain the base field leaf but no latin1 or UTF-16LE leaf is found
- **THEN** qa-mcp reports a structured `retarget_failed` error before sending that frame
- **AND** it does not silently write to the template field

#### Scenario: Focus-change frames may omit the base leaf

- **WHEN** a commit or focus-change frame legitimately addresses a partner field instead of the written base field
- **THEN** qa-mcp may leave that frame unchanged
- **AND** the omission does not mask missing retargeting for the actual write SET frame

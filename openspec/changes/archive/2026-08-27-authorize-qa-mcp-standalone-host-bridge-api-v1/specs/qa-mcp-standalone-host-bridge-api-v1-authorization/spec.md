## ADDED Requirements

### Requirement: Bridge API v1 authorization source is exact and closed
The project SHALL publish one authorization object containing exactly the
OSS-05-I1 investigation card/id, OSS-05 successor card/id, production ceiling
`301` and `allow_new_authority_or_wire_protocol: true`.

#### Scenario: Exact source is inspected
- **WHEN** OSS-05-A1 is read from tracked `4.done` state
- **THEN** it contains exactly the six canonical ChangeRail fields
- **AND** every value matches the named OSS-05-I1-to-OSS-05 chain

### Requirement: Authorization relations are reciprocal
Published OSS-05-I1, OSS-05-A1 and the OSS-05 successor SHALL reference one
another through the headings consumed by deterministic preflight.

#### Scenario: Exact successor consumes the source
- **WHEN** preflight evaluates OSS-05 after authorization publication
- **THEN** the investigation blocks OSS-05 and the source depends on it
- **AND** OSS-05 depends on the investigation and references exact tracked OSS-05-A1

#### Scenario: Relation is incomplete or mismatched
- **WHEN** any required id, path, source state or relation differs
- **THEN** deterministic preflight rejects the source
- **AND** the wire-contract exception is not granted

### Requirement: Machine ceiling preserves the successor delivery cap
The source SHALL use machine ceiling `301`, while OSS-05 MUST retain its
independent at-most-`300` added production LOC gate.

#### Scenario: Candidate reaches preflight
- **WHEN** the exact successor is evaluated
- **THEN** ChangeRail recognizes ceiling `301`
- **AND** OSS-05 acceptance still forbids more than `300` added production LOC

### Requirement: Wire permission cannot expand scope
The source MUST permit only the investigated public bridge API major `1` for
the exact OSS-05 successor and MUST NOT authorize another card, API surface,
private route family or OSS-06.

#### Scenario: Another successor attempts reuse
- **WHEN** a different id or path references OSS-05-A1
- **THEN** deterministic preflight reports the source invalid
- **AND** no wire-contract exception is granted

### Requirement: Finalized candidate is proven
The publish workflow SHALL verify exact acceptance and bounded mismatch
rejection against the finalized source/card paths before push.

#### Scenario: Source is ready to publish
- **WHEN** OSS-05-A1 is finalized to `4.done` in the candidate
- **THEN** exact OSS-05 preflight recognizes the source
- **AND** a changed successor id or path fails closed

### Requirement: Authorization delivery is metadata-only
The OSS-05-A1 payload SHALL contain no production, test, protocol, runtime or
Windows implementation and SHALL perform no external action.

#### Scenario: Manifest scope is reconciled
- **WHEN** its delivery manifest is checked
- **THEN** every committable path is OpenSpec or board metadata
- **AND** runtime, Windows-native, live 1C and test-first checks are not applicable

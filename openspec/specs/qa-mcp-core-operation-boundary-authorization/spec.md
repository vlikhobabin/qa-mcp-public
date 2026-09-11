# qa-mcp core operation boundary authorization

## Purpose

Define the exact published ChangeRail authorization source and reciprocal
fail-closed board relations that allow only OSS-04D-R5 to consume the bounded
core operation-boundary investigation exception while retaining its stricter
300-line delivery cap.

## Requirements

### Requirement: Core boundary authorization source is exact and closed
The project SHALL publish one core operation-boundary authorization source
whose object contains exactly the R4-R1 investigation card/id, R5 successor
card/id, production LOC ceiling `301` and
`allow_new_authority_or_wire_protocol: false`.

#### Scenario: Exact source is inspected
- **WHEN** the completed A2 source is read from `4.done`
- **THEN** it contains exactly the six ChangeRail authorization fields
- **AND** every id, canonical board path, integer ceiling and boolean flag matches the named R4-R1-to-R5 chain

### Requirement: Core authorization relations are reciprocal
Published R4-R1, A2 and the R5 successor SHALL reference one another through
the relation headings consumed by deterministic preflight.

#### Scenario: Exact R5 successor consumes the source
- **WHEN** deterministic preflight evaluates R5 at its declared `3.inprogress` path after A2 publication
- **THEN** R4-R1 blocks R5, A2 depends on R4-R1, and R5 depends on R4-R1 and A2
- **AND** R5 references the tracked unchanged A2 `4.done` card as its published investigation authorization

#### Scenario: Relation is incomplete or mismatched
- **WHEN** any required id, path, relation or source state differs from the published chain
- **THEN** deterministic preflight rejects the authorization
- **AND** the ordinary production ceiling is not raised

### Requirement: Machine ceiling does not expand the R5 delivery cap
The A2 machine authorization ceiling SHALL be `301`, while R5 MUST retain its
independent at-most-`300` added production-line delivery cap.

#### Scenario: Candidate reaches the boundary
- **WHEN** deterministic preflight evaluates the exact authorized R5 candidate
- **THEN** the authorization source is valid with machine ceiling `301`
- **AND** R5 acceptance still forbids more than `300` added production lines

### Requirement: Authorization cannot expand successor or authority scope
The A2 source MUST authorize only the core operation-boundary work in R5 and
MUST NOT grant A3, R6, lifecycle work, another capability, new authority or a
wire protocol.

#### Scenario: Another card tries to reuse the source
- **WHEN** a card other than the exact R5 successor references A2
- **THEN** deterministic preflight reports the authorization as invalid
- **AND** no bounded complexity exception is granted

### Requirement: Candidate publication is proven deterministically
The publish workflow SHALL verify an exact finalized A2/R5 candidate and SHALL
retain a bounded secret-free outcome for both exact acceptance and mismatched
rejection.

#### Scenario: Final candidate is ready to push
- **WHEN** A2 is finalized to `4.done`, R5 is at its declared `3.inprogress` path and the candidate is evaluated
- **THEN** deterministic preflight recognizes the published authorization and ceiling `301`
- **AND** a bounded successor mismatch fails closed

### Requirement: Core authorization delivery is metadata-only
The A2 payload SHALL contain no production, test, protocol, runtime or Windows
implementation and SHALL make no runtime-behavior claim.

#### Scenario: Authorization payload reaches review
- **WHEN** its delivery manifest is reconciled
- **THEN** every committable path is under OpenSpec or board metadata
- **AND** Windows-native, live 1C and test-first runtime verification are recorded as not applicable

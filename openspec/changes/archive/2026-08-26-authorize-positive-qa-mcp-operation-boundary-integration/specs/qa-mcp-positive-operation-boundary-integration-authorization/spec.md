## ADDED Requirements

### Requirement: Positive integration authorization source is exact and closed
The project SHALL publish one authorization object containing exactly the
R5-R2 investigation card/id, R8 successor card/id, integer production LOC
ceiling `301` and boolean `allow_new_authority_or_wire_protocol: false`.

#### Scenario: Exact A5 source is inspected
- **WHEN** the completed A5 source is read from `4.done`
- **THEN** it contains exactly the six ChangeRail authorization fields
- **AND** every id, canonical board path, integer ceiling and boolean flag matches the named R5-R2-to-R8 chain

### Requirement: Positive integration relations are reciprocal
Published R5-R2, R7, A5 and R8 SHALL reference one another through the relation
headings consumed by deterministic preflight.

#### Scenario: Exact R8 successor consumes the source
- **WHEN** deterministic preflight evaluates R8 at its declared `3.inprogress` path after A5 publication
- **THEN** R5-R2 blocks A5 and R8, R7 blocks A5, A5 depends on R5-R2 and R7 and blocks R8, and R8 depends on R5-R2, R7 and A5
- **AND** R8 references the tracked unchanged A5 `4.done` card as its published investigation authorization

#### Scenario: Relation is incomplete or mismatched
- **WHEN** any required id, path, relation, field type or source state differs from the published chain
- **THEN** deterministic preflight rejects the authorization
- **AND** the ordinary production ceiling is not raised

### Requirement: Machine ceiling does not expand the R8 delivery cap
The A5 machine authorization ceiling SHALL be exact integer `301`, while R8
MUST retain its independent at-most-`300` added production-line delivery cap.

#### Scenario: Candidate reaches the boundary
- **WHEN** deterministic preflight evaluates the exact authorized R8 candidate
- **THEN** the authorization source is valid with machine ceiling `301`
- **AND** R8 acceptance still forbids more than `300` added production lines

### Requirement: Authorization cannot expand successor or authority scope
The A5 source MUST authorize only positive public operation-boundary
integration in R8 and MUST NOT grant A2/A3/A4, R5/R6, lifecycle work, another
capability, new authority or a wire protocol.

#### Scenario: Another card tries to reuse the source
- **WHEN** a card other than exact R8 references A5
- **THEN** deterministic preflight reports the authorization as invalid
- **AND** no bounded complexity exception is granted

### Requirement: Candidate publication is proven deterministically
The publish workflow SHALL verify an exact finalized A5/R8 candidate and SHALL
retain a bounded secret-free result for exact acceptance and mismatched
rejection.

#### Scenario: Final candidate is ready to push
- **WHEN** A5 is finalized to `4.done`, R8 is at its declared `3.inprogress` path and the candidate is evaluated
- **THEN** deterministic preflight recognizes the published authorization and ceiling `301`
- **AND** bounded source or successor id/path/reference mismatches fail closed

### Requirement: Positive integration authorization delivery is metadata-only
The A5 payload SHALL contain no production, test, protocol, runtime or Windows
implementation and SHALL make no runtime-behavior claim.

#### Scenario: Authorization payload reaches review
- **WHEN** its delivery manifest is reconciled
- **THEN** every committable path is under OpenSpec or board metadata
- **AND** test-first, Windows/live/runtime/protocol and external-action proof are recorded as not applicable

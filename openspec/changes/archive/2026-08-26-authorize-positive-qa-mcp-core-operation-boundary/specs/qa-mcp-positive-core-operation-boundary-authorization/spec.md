## ADDED Requirements

### Requirement: Positive core authorization source is exact and closed
The project SHALL publish one authorization object containing exactly the
R5-R2 investigation card/id, R7 successor card/id, integer production LOC
ceiling `301` and boolean `allow_new_authority_or_wire_protocol: false`.

#### Scenario: Exact A4 source is inspected
- **WHEN** the completed A4 source is read from `4.done`
- **THEN** it contains exactly the six ChangeRail authorization fields
- **AND** every id, canonical board path, integer ceiling and boolean flag matches the named R5-R2-to-R7 chain

### Requirement: Positive core authorization relations are reciprocal
Published R5-R2, A4 and R7 SHALL reference one another through the relation
headings consumed by deterministic preflight.

#### Scenario: Exact R7 successor consumes the source
- **WHEN** deterministic preflight evaluates R7 at its declared `3.inprogress` path after A4 publication
- **THEN** R5-R2 blocks A4 and R7, A4 depends on R5-R2 and blocks R7, and R7 depends on R5-R2 and A4
- **AND** R7 references the tracked unchanged A4 `4.done` card as its published investigation authorization

#### Scenario: Relation is incomplete or mismatched
- **WHEN** any required id, path, relation, field type or source state differs from the published chain
- **THEN** deterministic preflight rejects the authorization
- **AND** the ordinary production ceiling is not raised

### Requirement: Machine ceiling does not expand the R7 delivery cap
The A4 machine authorization ceiling SHALL be exact integer `301`, while R7
MUST retain its independent at-most-`300` added production-line delivery cap.

#### Scenario: Candidate reaches the boundary
- **WHEN** deterministic preflight evaluates the exact authorized R7 candidate
- **THEN** the authorization source is valid with machine ceiling `301`
- **AND** R7 acceptance still forbids more than `300` added production lines

### Requirement: Authorization cannot expand successor or authority scope
The A4 source MUST authorize only positive core operation-boundary work in R7
and MUST NOT grant historical A2/R5/R5-R1, A5/R8, lifecycle work, another
capability, new authority or a wire protocol.

#### Scenario: Another card tries to reuse the source
- **WHEN** a card other than exact R7 references A4
- **THEN** deterministic preflight reports the authorization as invalid
- **AND** no bounded complexity exception is granted

### Requirement: Candidate publication is proven deterministically
The publish workflow SHALL verify an exact finalized A4/R7 candidate and SHALL
retain a bounded secret-free outcome for exact acceptance and mismatched
rejection.

#### Scenario: Final candidate is ready to push
- **WHEN** A4 is finalized to `4.done`, R7 is at its declared `3.inprogress` path and the candidate is evaluated
- **THEN** deterministic preflight recognizes the published authorization and ceiling `301`
- **AND** a bounded successor id/path/reference mismatch fails closed

### Requirement: Positive core authorization delivery is metadata-only
The A4 payload SHALL contain no production, test, protocol, runtime or Windows
implementation and SHALL make no runtime-behavior claim.

#### Scenario: Authorization payload reaches review
- **WHEN** its delivery manifest is reconciled
- **THEN** every committable path is under OpenSpec or board metadata
- **AND** test-first, Windows/live/runtime/protocol and external-action proof are recorded as not applicable

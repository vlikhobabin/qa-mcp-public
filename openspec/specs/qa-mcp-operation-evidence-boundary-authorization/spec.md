# qa-mcp operation evidence boundary authorization

## Purpose

Define the exact published ChangeRail authorization source and reciprocal
fail-closed board relations that allow only OSS-04D-R3 to use the bounded
500-line operation-evidence implementation exception.

## Requirements

### Requirement: Published authorization source is exact and closed
The project SHALL publish one bounded operation-evidence authorization source
whose object contains exactly the R2 investigation card/id, R3 successor
card/id, production LOC ceiling `500` and
`allow_new_authority_or_wire_protocol: false`.

#### Scenario: Exact source is inspected
- **WHEN** the completed A1 source is read from `4.done`
- **THEN** it contains exactly the six ChangeRail authorization fields
- **AND** every id, canonical board path, integer ceiling and boolean flag matches the named R2-to-R3 chain

### Requirement: Authorization relations are reciprocal
The published R2 investigation, A1 source and R3 successor SHALL reference one
another through the relation headings consumed by deterministic preflight.

#### Scenario: Exact successor consumes the source
- **WHEN** deterministic preflight evaluates R3 after A1 publication
- **THEN** R2 blocks R3, A1 depends on R2, and R3 depends on R2 and A1
- **AND** R3 references the tracked unchanged A1 `4.done` card as its published investigation authorization

#### Scenario: Relation is incomplete or mismatched
- **WHEN** any required id, path, relation or source state differs from the published chain
- **THEN** deterministic preflight rejects the authorization
- **AND** the ordinary production ceiling is not raised

### Requirement: Authorization cannot expand scope
The A1 source MUST authorize only the typed operation-evidence boundary in R3
and MUST NOT grant another capability, successor, authority or wire protocol.

#### Scenario: Another card tries to reuse the source
- **WHEN** a card other than the exact R3 successor references A1
- **THEN** deterministic preflight reports the authorization as invalid
- **AND** no bounded complexity exception is granted

### Requirement: Candidate publication is proven deterministically
The publish workflow SHALL verify the exact finalized candidate tree before
push and SHALL retain a bounded secret-free outcome for both exact acceptance
and mismatched rejection.

#### Scenario: Final candidate is ready to push
- **WHEN** A1 has been finalized to `4.done`, R3 has the exact source reference and the candidate commit is evaluated
- **THEN** deterministic preflight recognizes the published authorization and ceiling `500`
- **AND** a bounded mismatched control fails closed

### Requirement: Authorization delivery is metadata-only
The A1 payload SHALL contain no production, test, protocol, runtime or Windows
implementation and SHALL make no runtime-behavior claim.

#### Scenario: Authorization payload reaches review
- **WHEN** its delivery manifest is reconciled
- **THEN** every committable path is under OpenSpec or board metadata
- **AND** Windows-native, live 1C and test-first runtime verification are recorded as not applicable

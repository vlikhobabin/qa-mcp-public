## ADDED Requirements

### Requirement: Authorization source binds exact I7 and I4 identities
The authorization source SHALL depend on exactly
`oss-06-s4-r1-i7-investigate-private-inventory-classifier-contract` and SHALL
contain exactly the following six-field `Investigation authorization` object,
with no additional or missing field or value change:

```json
{"investigation_card":"openspec/board/4.done/oss-06-s4-r1-i7-investigate-private-inventory-classifier-contract.md","investigation_id":"oss-06-s4-r1-i7-investigate-private-inventory-classifier-contract","successor_card":"openspec/board/3.inprogress/oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause.md","successor_id":"oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

#### Scenario: Exact source graph is published
- **WHEN** I8 is evaluated as a ChangeRail authorization source
- **THEN** its investigation card is an unchanged tracked `4.done` artifact
- **AND** its exact dependency names I7 and I7's `Blocks` relation names exact
  I4
- **AND** the object binds only the specified investigation and successor.

#### Scenario: Source graph or object differs
- **WHEN** a dependency, path, id, lane, field, ceiling, authority flag or
  reciprocal relation is missing, additional, stale, untracked or substituted
- **THEN** the authorization is invalid and MUST fail closed.

### Requirement: Authorization does not certify future I4 admission
The authorization SHALL treat the `301` ceiling as a conditional machine
envelope only. It MUST NOT claim that retained I4 already satisfies its
at-most-five-path scope, production LOC, blob identities or hostile/offline
verification floor.

#### Scenario: I8 is reviewed without retained I4
- **WHEN** the docs/OpenSpec authorization payload is verified
- **THEN** no retained I4 workspace, product/test byte, card or metadata is
  accessed, copied, modified, reviewed, staged or published
- **AND** I4's size, identity and verification claims remain future admission
  conditions.

#### Scenario: Later I4 admission is attempted
- **WHEN** a future fresh session prepares I4 to consume published I8
- **THEN** it MUST independently prove the at-most-five-path and `301`-LOC
  bounds, exact product/test blob identities and the complete I7 hostile
  offline verification floor
- **AND** I8 alone MUST NOT satisfy any of those conditions.

### Requirement: Authorization is documentation-only and independently published
I8 MUST change only its board card, OpenSpec authorization artifacts, synced
capability and deterministic archive/publication metadata. It MUST preserve
Apache-2.0 unchanged and MUST be independently reviewed and published unchanged
in `4.done` before I4 references its canonical path/id.

#### Scenario: I8 reaches publication
- **WHEN** verification and a fresh independent review return GO for the exact
  payload
- **THEN** scoped publication moves I8 unchanged to `4.done`
- **AND** the payload contains no product/test implementation, runtime
  behavior, new authority, wire protocol, retry, fallback, wait or live probe.

#### Scenario: External or implementation work enters scope
- **WHEN** any product/test/runtime byte or Windows, PowerShell, 1C, endpoint,
  target, SSH, live or historical-user operation is required
- **THEN** I8 delivery MUST stop without widening its authorization scope.

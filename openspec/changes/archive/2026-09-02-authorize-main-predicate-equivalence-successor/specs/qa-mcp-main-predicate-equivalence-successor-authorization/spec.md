## ADDED Requirements

### Requirement: Authorization source binds exact I10 and I11 identities
The authorization source SHALL depend on exactly
`oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract` and SHALL
contain exactly the following six-field `Investigation authorization` object
from I10's machine decision, with no additional or missing field or value
change:

```json
{"investigation_card":"openspec/board/4.done/oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract.md","investigation_id":"oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract","successor_card":"openspec/board/3.inprogress/oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract.md","successor_id":"oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

#### Scenario: Exact source graph is published
- **WHEN** I10a is evaluated as a ChangeRail authorization source
- **THEN** its investigation card is an unchanged tracked `4.done` artifact
- **AND** its exact dependency names I10 and I10's `Blocks` relation names exact
  I11
- **AND** the object binds only the specified investigation and successor.

#### Scenario: Source graph or object differs
- **WHEN** a dependency, path, id, lane, field, ceiling, authority flag or
  reciprocal relation is missing, additional, stale, untracked or substituted
- **THEN** the authorization is invalid and MUST fail closed.

### Requirement: Authorization does not implement or certify I11
The authorization SHALL treat the `301` ceiling and closed authority/wire flag
as a conditional machine envelope only. It MUST NOT claim that I11 already
satisfies its five-path scope, production LOC, blob lineage, connected
RED/GREEN matrices or offline verification floor.

#### Scenario: I10a is reviewed without advancing I11
- **WHEN** the docs/OpenSpec authorization payload is verified
- **THEN** no I11 product/test byte or card metadata byte is modified, reviewed,
  staged or published
- **AND** I11 remains blocked for a separate future delivery session.

#### Scenario: Later I11 admission is attempted
- **WHEN** a future fresh session moves exact I11 to its declared
  authorization-time `3.inprogress` path and prepares it to consume published
  I10a
- **THEN** it MUST independently prove every exact I10 path, LOC, identity,
  behavior and verification condition
- **AND** I10a alone MUST NOT satisfy any of those conditions.

### Requirement: Authorization is documentation-only and independently published
I10a MUST change only its board card, OpenSpec authorization artifacts, synced
capability and deterministic archive/publication metadata. It MUST preserve
Apache-2.0 unchanged and MUST be independently reviewed and published unchanged
in `4.done` before I11 enters its review gate.

#### Scenario: I10a reaches publication
- **WHEN** offline verification and a fresh independent ordinary/high review
  return GO for the exact payload
- **THEN** scoped publication moves I10a unchanged to `4.done`
- **AND** the S4-R1 parent and I11 remain blocked and unimplemented.

#### Scenario: External or implementation work enters scope
- **WHEN** any host-agent product/test/runtime byte or Windows, PowerShell, 1C,
  endpoint, lab/live/action, S5/S7, SSH or external operation is required
- **THEN** I10a delivery MUST stop without widening its authorization scope.

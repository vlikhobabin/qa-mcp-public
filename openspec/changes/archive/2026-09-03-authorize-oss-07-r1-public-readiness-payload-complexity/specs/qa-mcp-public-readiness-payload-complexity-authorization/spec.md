## ADDED Requirements

### Requirement: Authorization source binds exact I1 and OSS-07-R1 identities
The authorization source SHALL depend on exactly
`oss-07-r1-i1-investigate-public-readiness-payload-complexity` and SHALL
contain exactly the following six-field `Investigation authorization` object,
with no additional or missing field or value change:

```json
{"investigation_card":"openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md","investigation_id":"oss-07-r1-i1-investigate-public-readiness-payload-complexity","successor_card":"openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md","successor_id":"oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity","production_loc_ceiling":350,"allow_new_authority_or_wire_protocol":false}
```

#### Scenario: Exact source graph is published
- **WHEN** the authorization card is evaluated as a ChangeRail complexity source
- **THEN** its investigation card is the unchanged tracked published I1 in
  `4.done`
- **AND** its exact dependency names I1 and I1's `Blocks` relation names exact
  OSS-07-R1
- **AND** the object binds only the specified investigation and successor.

#### Scenario: Source graph or object differs
- **WHEN** a dependency, path, id, lane, field, ceiling, authority flag or
  reciprocal relation is missing, additional, stale, untracked or substituted
- **THEN** the authorization is invalid and MUST fail closed.

### Requirement: Authorization preserves the complete complexity boundary
The authorization SHALL treat `production_loc_ceiling: 350` as a hard maximum
for the exact complete successor-owned production scope. It MUST reject
whitespace deletion, production-source reclassification and owned-scope
exclusion as complexity-gate workarounds.

#### Scenario: Honest complete payload is within the ceiling
- **WHEN** a later fresh successor session measures every owned production path
  under stable classification and scope at no more than 350 lines
- **THEN** deterministic admission may continue only if every other exact
  source, graph, evidence and review condition also passes
- **AND** the ceiling MUST NOT be treated as permission to add implementation.

#### Scenario: Accounting workaround creates a nominal pass
- **WHEN** the reported count passes only because blank lines were deleted,
  production source was relabeled or owned scope was omitted
- **THEN** the authorization remains unsatisfied and the successor MUST stay
  blocked.

### Requirement: Authorization does not certify the successor payload
The authorization MUST NOT claim that OSS-07-R1 already satisfies its exact
production size, path, blob, test, evidence, deterministic-preflight or
semantic-review conditions.

#### Scenario: Authorization is reviewed without the successor
- **WHEN** the metadata-only authorization payload is verified
- **THEN** no OSS-07-R1 implementation or successor metadata byte is imported,
  read, modified, reviewed, staged or published
- **AND** all implementation identity, size and verification claims remain
  future admission work.

#### Scenario: Later successor admission is attempted
- **WHEN** a separate fresh session prepares exact OSS-07-R1 to consume the
  published authorization
- **THEN** the successor MUST separately depend on I1 and reference only this
  exact unchanged tracked `4.done` source
- **AND** it MUST pass deterministic preflight, retain its full verified
  evidence and obtain a fresh independent semantic review.

### Requirement: Authorization is metadata-only and grants no new authority
The authorization MUST change only its board card, OpenSpec authorization
artifacts, synced capability and deterministic archive/publication metadata.
It MUST set `allow_new_authority_or_wire_protocol` to `false`, preserve exact
SPDX `Apache-2.0` and published OSS-07-I2 unchanged, and keep OSS-07-I1 absent.

#### Scenario: Authorization reaches publication
- **WHEN** strict validation, exact-object, dependency, scope, whitespace,
  public-safety and fresh independent review gates pass
- **THEN** scoped publication moves the unchanged authorization card to
  `4.done`
- **AND** the payload contains no successor implementation, OSS-08/OSS-09
  implementation, license change, runtime behavior, public/wire contract,
  credential or mutation authority.

#### Scenario: External or implementation work enters scope
- **WHEN** live, SSH, Windows, 1C, TestClient, Apache-service, credential,
  mutation, network, release, OSS-08/OSS-09 or other external execution is
  required
- **THEN** delivery MUST stop without widening this authorization source.

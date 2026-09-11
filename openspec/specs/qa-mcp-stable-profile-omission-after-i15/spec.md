## Purpose

Define the evidence-bound card-405 stable-profile omission after published I15,
the preserved incomplete certification lineage and the separate OSS-07
handoff.

## Requirements

### Requirement: The omission binds the exact published-I15 outcome
The decision MUST bind published I15 commit
`1be1829ee71b96f8c1c690c9fa55c2e8e14c1425` and retain that its one authorized
canary produced no typed Session-1 receipt, candidate invocation count was
zero, no S4/I13 row ran, exact cleanup passed and no retry authority remains.
It MUST NOT represent I14 or I15 as certification.

#### Scenario: Published outcome is recorded without reinterpretation
- **WHEN** the omission decision is reviewed
- **THEN** its evidence and board summaries contain the exact fail-closed I15
  outcome and grant no retry, candidate action or certification authority.

### Requirement: Stable support omits only the unqualified tool
The declared stable release support profile and public support matrix SHALL
omit `open_external_processor` until a separately reviewed future
qualification publishes. The unchanged code-level `standalone` catalog SHALL
remain explicitly classified as pre-stable runtime inventory, and its dormant
tool membership MUST NOT be treated as stable admission. The omission MUST NOT
delete or modify dormant product/test source, Gherkin support, tracked EPFs,
runtime authority, source profile code or published foundations and MUST NOT
claim that those retained assets are stable certification. Stable release
cutover MUST enforce the declared 63-tool allowlist before promotion.

#### Scenario: Stable public documentation is reconciled
- **WHEN** a reader inspects the stable standalone capability documentation
- **THEN** `open_external_processor` is identified as omitted/dormant and the
  separately reviewed future-qualification condition is explicit, while the
  64-tool code catalog is identified as pre-stable inventory.

#### Scenario: Retained implementation remains unchanged
- **WHEN** the reviewed path scope is compared with published I15
- **THEN** no product, test, fixture, tracked EPF or runtime-authority path is
  changed or removed.

### Requirement: Incomplete I13 S4-R1 and S7 lineage is preserved
The decision MUST leave I13 active, unarchived and uncertified and MUST leave
S4-R1 and S7 incomplete. Parent and handoff cards SHALL record the stable
omission without moving those lineage cards to done, archiving I13 or
authorizing another attempt.

#### Scenario: Board lineage remains incomplete
- **WHEN** exact board and OpenSpec-state assertions run
- **THEN** I13 remains in `3.inprogress` with its change active, S4-R1 and S7
  remain in `2.todo`, and none is represented as certified or completed.

### Requirement: Post-I15 board truth and OSS-07 handoff are exact
The roadmap and affected cards MUST use the published I15 `4.done` path and
nine-entry evidence count and MUST represent OSS-07 as a `1.backlog` story
with no OpenSpec artifacts. After this decision publishes, OSS-07 SHALL be the
next separate card, carrying the operator-approved `Apache-2.0` choice into its
first future change without implementing or planning OSS-07 here.

#### Scenario: Actual board state replaces stale roadmap claims
- **WHEN** roadmap and dependency assertions compare tracked prose with the
  filesystem and `openspec list --json`
- **THEN** I15 resolves under `4.done`, OSS-07 resolves under `1.backlog`, no
  OSS-07 change artifacts exist and the next-card handoff is separate.

### Requirement: Publication is offline scoped and independently reviewed
The decision MUST pass strict OpenSpec, JSON, exact board/dependency,
public-surface/privacy, Apache-2.0 path, tracked-plus-untracked whitespace and
manifest scope checks plus a fresh ordinary-risk independent review before
publication. It MUST execute no live contour, SSH, historical-user, Windows, 1C,
`/Execute`, canary, S4/S5/S7 or candidate action.

#### Scenario: Offline gate passes without runtime action
- **WHEN** the final payload is prepared for review and publication
- **THEN** all declared offline gates pass, runtime execution evidence is
  explicitly not applicable and the manifest contains only permitted
  evidence/docs/spec/board paths.

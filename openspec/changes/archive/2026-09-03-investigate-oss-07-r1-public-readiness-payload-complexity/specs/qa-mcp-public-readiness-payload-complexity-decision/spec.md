## ADDED Requirements

### Requirement: Complexity decision binds one exact successor
The investigation decision MUST bind only successor
`oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity` at
authorization-time path
`openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`.
It MUST NOT authorize another card, path, payload, or reusable exception.

#### Scenario: Exact successor is prepared for later authorization
- **WHEN** a later authorization source consumes the published investigation
- **THEN** its successor id and path match the decision exactly
- **AND** the investigation blocks that successor and the successor depends on
  this investigation.

#### Scenario: Successor identity changes
- **WHEN** the successor id or authorization-time path differs from the
  published decision
- **THEN** this decision does not apply
- **AND** the payload requires a new investigation rather than reusing the
  ceiling.

### Requirement: Maximum production envelope is 350 complete lines
The decision MUST prepare `production_loc_ceiling` with integer value `350`
for the exact successor. The ceiling MUST be treated as a hard maximum, not a
target or permission to expand the implementation, and later admission MUST
measure the complete successor-owned production scope at no more than 350
lines.

#### Scenario: Complete payload is within the ceiling
- **WHEN** a fresh later session measures every successor-owned production path
  under stable classification and scope
- **THEN** admission may continue only when the total is at most 350
- **AND** it still requires the separate published authorization source,
  reciprocal metadata, deterministic preflight, and fresh independent review.

#### Scenario: Complete payload exceeds the ceiling
- **WHEN** the exact successor contains more than 350 added production lines
- **THEN** this decision does not authorize review or publication
- **AND** delivery requires a new split or investigation.

### Requirement: Complexity accounting cannot be gamed
The decision MUST reject whitespace deletion, production-source
reclassification, and owned-scope exclusion when their purpose or effect is to
evade the complexity guard. Later authorization and preflight MUST use the
complete honest payload boundary.

#### Scenario: Accounting workaround lowers the counter
- **WHEN** the reported count passes only because blank lines were deleted,
  source was relabeled, or owned paths were omitted
- **THEN** the complexity decision remains unsatisfied
- **AND** the successor stays blocked.

#### Scenario: Substantive simplification changes the payload
- **WHEN** an independently reviewable simplification changes the exact
  successor payload or scope
- **THEN** the prior approximately 313-line trigger is not reused as current
  size evidence
- **AND** a fresh complete count and applicable ChangeRail routing are required.

### Requirement: New authority and wire protocol remain forbidden
The prepared authorization data MUST set
`allow_new_authority_or_wire_protocol` to `false`. The investigation MUST grant
no live, SSH, Windows, 1C, TestClient, Apache, release, credential, mutation,
network, or external action authority.

#### Scenario: Existing disclosure and provenance scope is unchanged
- **WHEN** a later source binds only the current OSS-07-R1 disclosure and
  provenance payload with no new authority or wire protocol
- **THEN** the false authority flag is preserved
- **AND** all runtime and external operations remain unauthorized by this
  decision.

#### Scenario: New authority or wire behavior is proposed
- **WHEN** the successor adds a public/wire contract, credential or mutation
  authority, runtime action, or external operation
- **THEN** this decision does not apply
- **AND** the work requires new scope and a new investigation.

### Requirement: Future authorization source is exact and separate
The investigation MUST prepare an exact six-field object containing its future
published path/id, the exact successor path/id, ceiling `350`, and authority
flag `false`. The investigation MUST NOT create the separate authorization
source or modify the successor implementation or metadata.

#### Scenario: Separate source is later published
- **WHEN** a future metadata-only authorization card is delivered
- **THEN** it copies exactly the six prepared fields and depends on this
  unchanged tracked `4.done` investigation
- **AND** the successor later references only that exact unchanged tracked
  `4.done` source.

#### Scenario: Authorization graph is incomplete or altered
- **WHEN** any field, reciprocal relation, tracked state, or path/id is missing,
  additional, stale, or mismatched
- **THEN** deterministic preflight remains fail-closed
- **AND** the successor cannot use the 350-line ceiling.

### Requirement: Published license and safety lineage remains unchanged
The investigation MUST preserve exact SPDX `Apache-2.0`, keep OSS-07-I2
byte-identical, keep OSS-07-I1 absent, and add no OSS-08 or OSS-09
implementation. Its tracked payload MUST contain only its board/OpenSpec
decision, synced capability, and archive metadata.

#### Scenario: Investigation is delivered
- **WHEN** the investigation reaches independent review and publication
- **THEN** it contains no successor source, test, fixture, evidence payload,
  license-file, runtime, OSS-08, or OSS-09 change
- **AND** no Windows, SSH, 1C, TestClient, live, Apache-service, network,
  credential, mutation, or release operation has run.

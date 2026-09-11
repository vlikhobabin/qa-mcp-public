## ADDED Requirements

### Requirement: Exact exhausted design lineage is retained
The project SHALL retain secret-free exact recovery mappings for the exhausted
R3 implementation and R4 investigation before operation-boundary delivery
resumes.

#### Scenario: Both payloads are auditable without restoration
- **WHEN** the replacement reaches review
- **THEN** safe baselines, final trees, fingerprints, review cycles, rescue budgets, final findings and evidence hashes are recorded
- **AND** each named stash reconstructs its claimed tree/fingerprint without being restored or published

### Requirement: Evidence authority is explicit and context-local
The design SHALL use an application-owned ledger and per-admitted-operation
scope without ambient process-wide or executor-returned path authority.

#### Scenario: Concurrent contexts remain isolated
- **WHEN** two application contexts overlap and one hostile value raises during reconstruction
- **THEN** both scopes close deterministically and return typed results
- **AND** neither scope observes or changes the other's receipts or failure state

#### Scenario: Full-local path requires a current receipt
- **WHEN** executor artifact data supplies path, policy, provenance or callback state
- **THEN** sanitized output has no path
- **AND** full-local output can use only a same-operation receipt strictly contained below the frozen evidence root

### Requirement: Every provenance field has a closed grammar
Physical/path forms SHALL be rejected before field-specific exact grammar
validation for operation, target, session, binding, fingerprint and generation.

#### Scenario: Path candidates cover all six fields
- **WHEN** drive-relative, UNC/device or POSIX path-form candidates are supplied separately for each provenance field
- **THEN** admission fails typed before Local or Windows adapter invocation and emits no candidate
- **AND** the paired exact valid value for each field is preserved without broadening another field

### Requirement: Complete public JSON has structural and byte bounds
The design SHALL bound depth, per-container items, total nodes and string length
and SHALL enforce 65,536 UTF-8 bytes on the canonical complete public DTO.

#### Scenario: Aggregate pressure uses one fixed fallback
- **WHEN** valid individual values collectively exceed the encoded envelope
- **THEN** executor content is replaced by one fixed typed `result-too-large` failure below the ceiling
- **AND** admitted core provenance remains without one sentinel per input item

### Requirement: URL credential and userinfo depths are exact
Documentation URL admission SHALL inspect credential assignment and authority
userinfo hidden at each exact percent-encoding depth 1, 2, 3, 4 and 5 and SHALL
pair every depth with a benign control.

#### Scenario: Depths one through four are classified and canonicalized
- **WHEN** credential assignment, `user@` or `user:pass@` is hidden at exact depth 1, 2, 3 or 4
- **THEN** every hostile URL is absent with no original or decoded fragment emitted
- **AND** the paired benign encoded path with canonical no-userinfo authority emits the same canonical URL

#### Scenario: Fifth-depth fixed-point boundary is explicit
- **WHEN** a credential or userinfo hostile or benign path control is encoded at exact depth 5
- **THEN** all are rejected because a valid escape remains after four rounds
- **AND** no fragment is emitted and rejection does not misclassify the benign control as credential-bearing

#### Scenario: Both public paths execute the complete table
- **WHEN** the URL matrix is verified through real MCP and ScenarioRunner
- **THEN** each path covers the credential-path hostile, both userinfo hostile forms and the paired control at every depth 1–5
- **AND** both paths produce identical absence, canonical preservation or bounded-rejection outcomes

### Requirement: Route and reconstruction fail closed
Pure route admission SHALL precede evidence scope creation and executor calls,
and one outer boundary SHALL contain every reconstruction and encoding edge.

#### Scenario: Invalid bound state has no side effect
- **WHEN** target, session, attachment, generation or endpoint state is malformed, foreign or asymmetric
- **THEN** a typed blocked result returns with zero Local and Windows calls
- **AND** no evidence scope or serialization fallback changes route authority

### Requirement: Replacement handoff is reciprocal and bounded
The investigation SHALL create A2 → R5 → A3 → R6 with one exact authorization
per runtime card, future `3.inprogress` successor paths and no new authority or
wire protocol.

#### Scenario: Successor chain is publishable
- **WHEN** the replacement design publishes
- **THEN** A2 and A3 each use machine ceiling 301 while R5 and R6 each impose a stricter 300-line delivery cap
- **AND** only published R6 unblocks OSS-04E after fresh independent review

### Requirement: Replacement remains design-only
The replacement SHALL NOT modify production/test/runtime code, restore failed
payloads or claim Windows/live behavior from documentation-only verification.

#### Scenario: Design-only scope is verified
- **WHEN** the card reaches review
- **THEN** manifest scope contains only docs, OpenSpec and board paths
- **AND** test-first, Windows, live 1C and external-action proof are explicitly not applicable

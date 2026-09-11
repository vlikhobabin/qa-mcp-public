# qa-mcp operation boundary concurrency and bounds design

## Purpose

Define exact exhausted lineage, context-local evidence authority, field and
encoded-output bounds, complete credential/userinfo depth controls and the
bounded successor chain required before operation-boundary runtime resumes.
## Requirements
### Requirement: Exact exhausted design lineage is retained
The project SHALL retain secret-free exact recovery mappings for the exhausted
R3, R4, R5 and R5-R1 payloads before operation-boundary delivery resumes.

#### Scenario: All payloads are auditable without restoration
- **WHEN** the replacement reaches review
- **THEN** safe baselines, final trees, fingerprints, review cycles, rescue budgets, final findings and evidence hashes are recorded
- **AND** each named stash reconstructs its claimed tree/fingerprint without being restored or published

### Requirement: Evidence authority is explicit and context-local
The design SHALL use an application-owned ledger and per-admitted-operation
scope without ambient process-wide or executor-returned path authority and
SHALL separately bound every application-owned canonical evidence path.

#### Scenario: Concurrent contexts remain isolated
- **WHEN** two application contexts overlap and one hostile value raises during reconstruction
- **THEN** both scopes close deterministically and return typed results
- **AND** neither scope observes or changes the other's receipts or failure state

#### Scenario: Full-local path requires a current bounded receipt
- **WHEN** executor artifact data supplies path, policy, provenance or callback state
- **THEN** sanitized output has no path
- **AND** full-local output can use only a same-operation receipt strictly contained below the frozen evidence root whose canonical concrete-platform path is at most 2,048 Unicode scalars

### Requirement: Every provenance field has a closed grammar
Physical/path forms SHALL be rejected before field-specific exact grammar
validation for operation, target, session, binding, fingerprint and generation.

#### Scenario: Path candidates cover all six fields
- **WHEN** drive-relative, UNC/device or POSIX path-form candidates are supplied separately for each provenance field
- **THEN** admission fails typed before Local or Windows adapter invocation and emits no candidate
- **AND** the paired exact valid value for each field is preserved without broadening another field

### Requirement: Complete public JSON has structural and byte bounds
The design SHALL bound depth 8, 64 items per container, 512 total shared
executor-content nodes, 2,048 scalars per schema-admitted value/error string and
65,536 UTF-8 bytes on the canonical complete public DTO. Artifact fields and
application receipt paths SHALL use their stricter local contracts.

#### Scenario: Aggregate pressure uses one fixed fallback
- **WHEN** valid individual values collectively exceed the encoded envelope
- **THEN** executor content is replaced by one fixed typed `result-too-large` failure below the ceiling
- **AND** admitted core provenance remains without one sentinel per input item

#### Scenario: Every aggregate surface has exact controls
- **WHEN** shared nodes 511/512/513, receipt path scalars 2,047/2,048/2,049 or final canonical bytes 65,535/65,536/65,537 are exercised
- **THEN** below/at controls preserve eligibility and above controls return their specified fixed typed failure
- **AND** an admitted artifact plus value/error content proves the node counter is shared and the final byte gate runs last

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
and one outer boundary SHALL contain every schema admission, reconstruction and
encoding edge using only pre-snapshotted trusted fallback constants.

#### Scenario: Invalid bound state has no side effect
- **WHEN** target, session, attachment, generation, endpoint or public-result schema state is malformed, foreign, asymmetric or executor-controlled
- **THEN** a typed blocked/failure result returns with zero Local and Windows calls
- **AND** no evidence scope or serialization fallback changes route or disclosure authority

### Requirement: Replacement handoff is reciprocal and bounded
The replacement SHALL create A4 → R7 → A5 → R8 with one exact authorization per
runtime card, future `3.inprogress` successor paths and no new authority or wire
protocol. Exhausted R5/R5-R1 and former A3/R6 SHALL remain blocked/superseded.

#### Scenario: Successor chain is publishable
- **WHEN** the replacement design publishes
- **THEN** A4 and A5 each use machine ceiling 301 while R7 and R8 each impose a stricter 300-line cap
- **AND** only published R8 unblocks OSS-04E after fresh independent review

### Requirement: Replacement remains design-only
The replacement SHALL NOT modify production/test/runtime code, restore failed
payloads or claim Windows/live behavior from documentation-only verification.

#### Scenario: Design-only scope is verified
- **WHEN** the card reaches review
- **THEN** manifest scope contains only docs, OpenSpec and board paths
- **AND** test-first, Windows, live 1C and external-action proof are explicitly not applicable

### Requirement: Public executor text is positively admitted
The design SHALL rebuild executor-controlled public text only through an
immutable application-owned schema selected by exact operation identity and
binding exact JSON paths to finite classes. The schema and any literal tuple
SHALL be hard-coded source-reviewed application constants, not settings,
descriptor, provider, executor or returned data.

`literal_text` SHALL admit only an exact built-in string equal to one member of
the frozen operation-and-path-local tuple. Executor text SHALL be compared only
by exact type and equality, without character, token, alias or endpoint
classification.

The finite class catalog SHALL be exact: `boolean` admits only exact built-in
`False`/`True`; `int64` admits only exact built-in non-boolean integers from
`-9,223,372,036,854,775,808` through `9,223,372,036,854,775,807`;
`finite_number` admits only such integers or exact built-in finite floats;
`reference_count` admits only exact built-in non-boolean integers from `0`
through `2,147,483,647`; `literal_text` admits only an exact member of its
operation/path tuple; and `documentation_url` admits only an exact built-in
string accepted by the canonical public HTTP(S) fixed-point rules.

#### Scenario: Outcome partition is unique
- **WHEN** a public result contains an undeclared key
- **THEN** that key is omitted without inspecting its value
- **AND** omission is not an outcome available to a declared-path mismatch

#### Scenario: Every declared mismatch has one complete outcome
- **WHEN** a declared path receives a wrong class, non-exact built-in type, subclass, non-member literal or otherwise invalid value
- **THEN** the complete reconstruction returns fixed `invalid-executor-result`
- **AND** no partial field, alternate typed failure or original/decoded input fragment is emitted

#### Scenario: Every finite class has exact semantic controls
- **WHEN** `boolean` exercises both booleans and wrong types; `int64` exercises minimum/zero/maximum, wrong types, an int subclass and minimum−1/maximum+1; `finite_number` exercises int64 boundaries and finite floats, wrong types, int/float subclasses, out-of-range integers, `NaN` and infinities; and `reference_count` exercises 0/2,147,483,647, wrong types, an int subclass and −1/2,147,483,648
- **THEN** only the exact valid cells preserve their numeric/boolean DTO values
- **AND** every other applicable cell returns the complete fixed `invalid-executor-result` without an input fragment
- **AND** boolean subclass/invalid-domain cells are explicitly not applicable because built-in `bool` is not subclassable and both exact boolean values are valid

#### Scenario: Text classes have exact semantic controls
- **WHEN** `literal_text` exercises an exact member, wrong types, a string subclass and a non-member string, and `documentation_url` exercises canonical public controls, wrong types, a string subclass, private/local/userinfo/query/fragment/invalid-authority and depth-5 non-fixed forms
- **THEN** exact literal members preserve and admitted URLs canonicalize
- **AND** every wrong-type, subclass or invalid-domain cell returns the complete fixed `invalid-executor-result`, with the URL field absent and no original or decoded fragment

#### Scenario: Hostile and benign text use the same declared literals
- **WHEN** `value.referenceLabel` and `error.details.referenceLabel` are each bound to operation-and-path-local `literal_text(("Reference label 7",))`
- **AND** each path receives path forms, credential/connection assignments, `User Id`, `Data Source`, `accessKey`, `hostname`, local endpoints, another string, a string subclass or the exact safe literal
- **THEN** every non-member or non-exact-type cell returns complete fixed `invalid-executor-result` without an input fragment
- **AND** exact built-in `Reference label 7` preserves at both paths

#### Scenario: Executor cannot choose or mutate the schema
- **WHEN** executor data supplies a schema, mapping, callback or replacement attempt
- **THEN** the attempt is treated as a declared invalid result and returns fixed `invalid-executor-result`
- **AND** only the frozen application schema can classify public fields

### Requirement: Artifact fields have exact local contracts
The design SHALL validate artifact schema/tuple shape, declared id/media type,
hash and sensitivity, then full-local receipt/path in that exact order.
`artifact_id` SHALL be a declared exact built-in ASCII
`[a-z][a-z0-9._-]{0,127}`; `media_type` SHALL be a declared exact lower-ASCII
type/subtype with segments `[a-z0-9][a-z0-9.+-]{0,62}`; `sha256` SHALL be empty
or `sha256:` plus 64 lowercase hex; and sensitivity SHALL be exact built-in
`public` or `internal`. Executor path data SHALL never grant authority.

#### Scenario: Artifact field outcomes are exact
- **WHEN** id lengths 127/128/129, media total lengths 126/127/128, SHA empty/71 and malformed 70/72/uppercase/non-hex, and sensitivity valid/truncated/extended/private/case/subclass cells are tested
- **THEN** only exact valid declared cells preserve
- **AND** every invalid, undeclared or subclass cell returns fixed `invalid-executor-result`

#### Scenario: Artifact accounting and receipt boundaries are exact
- **WHEN** an artifact is reconstructed
- **THEN** a rejected artifact charges zero shared nodes and an admitted artifact charges exactly five
- **AND** same-operation canonical receipt paths of 2,047/2,048/2,049 scalars yield eligible/eligible/`invalid-evidence-receipt`
- **AND** sanitized output never emits a path and executor path data cannot change full-local authority

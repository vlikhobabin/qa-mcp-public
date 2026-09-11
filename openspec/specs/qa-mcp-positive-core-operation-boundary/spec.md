# qa-mcp-positive-core-operation-boundary Specification

## Purpose
TBD - created by archiving change implement-qa-mcp-positive-core-operation-boundary. Update Purpose after archive.
## Requirements
### Requirement: Operation schemas are immutable application state
Each `ApplicationContext` SHALL own a callback-free read-only operation schema
catalog composed only from sealed source constants. Settings, providers,
targets, executors, returned values and callers MUST NOT supply, replace or
mutate a schema, structural node, field class or literal tuple.

#### Scenario: Dynamic schema authority is absent
- **WHEN** a caller attempts constructor injection, mapping mutation, field replacement/deletion or executor-returned schema/callback data
- **THEN** the application catalog remains unchanged or reconstruction returns complete fixed `invalid-executor-result`
- **AND** no dynamic object classifies or emits a public field

### Requirement: Declared paths use one positive outcome partition
The boundary SHALL omit undeclared exact-string keys without inspecting their
values. At a declared path, every wrong class, non-exact built-in type/subclass,
non-member literal or invalid domain SHALL abort the complete reconstruction as
fixed `invalid-executor-result`, without a partial result or input fragment.
Finite-class test fixtures SHALL remain separate from the production active-window
value schema; changing that production schema MUST NOT weaken class-test or
public error.details reconstruction coverage.

#### Scenario: Same-path literal matrix is exact
- **WHEN** a declared finite-class fixture literal and public `error.details.referenceLabel` receive exact built-in `Reference label 7`, another string, path/credential/connection/local-endpoint forms, wrong types or a string subclass
- **THEN** only exact built-in `Reference label 7` preserves at each path
- **AND** every other declared cell returns the same complete fixed failure without an original fragment

#### Scenario: Unknown value is not inspected
- **WHEN** an undeclared key contains a value whose access or iteration would raise
- **THEN** reconstruction omits the key and completes without invoking that value

### Requirement: Active-window production fields have a finite positive schema
The production `read_active_window` success schema MUST admit only its documented
observation fields: `window_state` with exact local literals `observed`,
`missing` or `ambiguous`, `marker_count` as `reference_count` and optional
`assertion_passed` as an exact boolean. It MUST retain immutable source-owned
schema authority, trusted provenance and the existing total structural, scalar,
node, byte and artifact receipt protections. This change MUST NOT authorize
arbitrary UI strings.

#### Scenario: Declared active-window fields reject invalid data
- **WHEN** an executor supplies an invalid state literal, wrong field class/subclass, invalid count, malformed result or oversized admitted content
- **THEN** public reconstruction returns the existing complete fixed typed failure
- **AND** no partial value, input fragment or untrusted provenance is emitted.

#### Scenario: Generic reconstruction protection remains covered
- **WHEN** existing finite-class, URL, structural, byte and receipt controls run with explicit test fixtures or declared public `error.details` paths
- **THEN** their previous exact valid/invalid outcomes and bounds remain enforced
- **AND** no production synthetic operation or caller-supplied schema is introduced.

### Requirement: The finite scalar catalog is exact
The boundary SHALL support only exact built-in `boolean`, signed-64 `int64`,
signed-64 integer or finite built-in float `finite_number`, built-in
`reference_count` from 0 through 2,147,483,647, operation/path-local
`literal_text`, and exact built-in canonical `documentation_url` leaves.

#### Scenario: Every applicable class cell has one complete result
- **WHEN** each class exercises its published valid values, wrong types, subclass and invalid-domain boundaries
- **THEN** only exact valid values preserve or canonicalize
- **AND** every applicable invalid cell returns complete fixed `invalid-executor-result` without input data
- **AND** boolean subclass/domain cells are explicitly recorded as not applicable

### Requirement: Documentation URL admission is fixed-point and public
`documentation_url` SHALL decode authority and path separately for at most four
changing rounds, inspect every intermediate, require a fixed point and emit one
canonical public HTTP(S) URL with no userinfo, query or fragment.

#### Scenario: Encoded URL depth matrix is exact
- **WHEN** exact built-in strings at depths 1–4 contain a benign encoded path
- **THEN** each emits the same canonical public URL
- **AND** credential assignment or authority userinfo at those depths returns complete fixed `invalid-executor-result` with the URL absent and no original/decoded fragment

#### Scenario: Non-public and non-fixed URLs reject
- **WHEN** a URL is private/local/link-local/loopback, has userinfo/query/fragment/invalid authority or port, uses a string subclass, or changes on a fifth decode round
- **THEN** reconstruction returns complete fixed `invalid-executor-result`
- **AND** neither the URL nor any decoded fragment is emitted

### Requirement: Full-local evidence requires a current exact-scope receipt
Each application SHALL own a ledger with frozen evidence root/policy. A
full-local artifact path SHALL require a current same-ledger, same-operation,
same-artifact receipt for an existing canonical non-symlink path strictly below
the exact built-in platform `Path` root. Sanitized output SHALL never emit a
path and executor-returned path/provenance/schema data SHALL grant no authority.

#### Scenario: Concurrent and stale authority fails closed
- **WHEN** overlapping contexts/scopes exchange receipts, a scope closes or raises, a receipt/root/policy/path is forged or mutated, or a `Path` subclass/symlink/outside path is supplied
- **THEN** only a current exact-scope authoritative record can emit a full-local path
- **AND** every other case returns a fixed typed failure without changing another scope

#### Scenario: Receipt scalar boundary is exact
- **WHEN** otherwise valid canonical receipt paths contain 2,047, 2,048 and 2,049 Unicode scalars
- **THEN** the first two remain eligible and 2,049 returns fixed `invalid-evidence-receipt`

The shared operation SHALL accept artifact authority only from current trusted
production, bound to application, scope, canonical path and actual content digest.
Raw executor references SHALL NOT create records. Explicit low-level trusted
recording SHALL bind the actual file hash. Full-local normalization SHALL reject
changed bytes, mismatched artifact hash, stale path or symlink before success.
Sanitized current production SHALL remain verifiable after owned raw-file deletion.
Local artifact type/size validation SHALL retain priority over receipt failures.

#### Scenario: Old-file and false-hash result claims
- **WHEN** an untrusted executor returns a pre-existing in-root file, a false well-formed hash or metadata without current trusted production
- **THEN** the shared result is non-success with the exact applicable fixed artifact/receipt failure and discloses no path
- **AND** the pre-existing file is unchanged

#### Scenario: Current bytes determine receipt validity
- **WHEN** trusted current evidence is changed, redirected through a symlink or returned with mismatching hash before normalization
- **THEN** the operation fails closed with no current artifact disclosure
- **AND** valid current full-local evidence retains its exact readable path and actual digest

### Requirement: Artifact contracts and accounting are exact
The boundary SHALL validate declared artifact shape, exact built-in artifact
id, media type, SHA and sensitivity, then full-local receipt/path in that order.
Rejected artifacts SHALL charge zero shared nodes and admitted artifacts
exactly five.

#### Scenario: Every artifact field has local controls
- **WHEN** id lengths 127/128/129, media lengths 126/127/128, SHA empty/71 and malformed 70/72/uppercase/non-hex, sensitivity valid/truncated/extended/private/case/subclass and missing/forged fields are exercised
- **THEN** only exact valid cells preserve
- **AND** each invalid cell returns complete fixed `invalid-executor-result`

#### Scenario: Executor path has no authority
- **WHEN** sanitized or full-local executor artifact data supplies a path
- **THEN** sanitized output omits it and full-local output uses only the matching ledger receipt

### Requirement: Public reconstruction is total and bounded
The boundary SHALL enforce depth 8, 64 raw items per admitted container, 512
shared executor-content nodes, 2,048 Unicode scalars per admitted schema string
and 65,536 bytes for the complete compact sorted UTF-8 DTO. The node counter
SHALL be shared across value, error details and artifacts; the final byte gate
SHALL run last.

#### Scenario: Structural boundaries are paired
- **WHEN** depth and item cases exercise below/exact/above values and shared content exercises 511/512/513 nodes including one admitted artifact
- **THEN** below/exact controls preserve and structural/node above controls return fixed `result-too-large`

#### Scenario: Schema string boundary is exact
- **WHEN** an otherwise admissible documentation URL contains 2,047, 2,048 and 2,049 Unicode scalars
- **THEN** the first two canonicalize and 2,049 returns complete fixed `invalid-executor-result` as an invalid declared value

#### Scenario: Final byte boundary is exact
- **WHEN** individually valid content yields complete DTO sizes 65,535, 65,536 and 65,537 UTF-8 bytes
- **THEN** the first two preserve and 65,537 becomes one bounded fixed `result-too-large` failure

#### Scenario: Every malformed edge is total
- **WHEN** trusted DTO fields are deleted/mutated, mappings or properties raise, integers are oversized, floats are non-finite, encoding fails or schema/receipt state is forged
- **THEN** the API returns a serializable fixed typed result below the byte ceiling
- **AND** exception attributes, traceback context and input fragments do not enter the result

### Requirement: R7 remains core-only and authorized
The implementation SHALL add at most 300 production lines relative to
published A4, consume only A4's exact R7 authorization and add no route,
lifecycle, external authority or wire behavior.

#### Scenario: Delivery reaches review
- **WHEN** R7 finishes implementation
- **THEN** direct intended-oracle RED/green, focused and full non-live coverage, compilation, strict OpenSpec, LOC/scope/diff and exact-source Windows offline evidence pass
- **AND** MCP/ScenarioRunner routing, live 1C, protocol capture and external-action proof remain out of scope

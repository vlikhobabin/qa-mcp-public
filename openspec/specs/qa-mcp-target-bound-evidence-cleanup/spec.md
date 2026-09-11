# qa-mcp Target-Bound Evidence And Cleanup Specification

## Purpose

Define the project-bound schema, operation-evidence and exact-owned cleanup
requirements that preserve one admitted runtime target through lifecycle, read,
display and teardown on Linux and Windows.

## Requirements

### Requirement: Project tool schemas cannot retarget or change retention
Project-bound MCP schemas MUST omit physical target, connection, env file,
endpoint, credential, rebind and evidence policy/root inputs and MUST inject
provider-owned values from the admitted physical-config snapshot instead.
Bound diagnostic results MUST serialize only logical target identity and
provenance, never physical configuration or principal values.

#### Scenario: Bound registry is listed
- **WHEN** a project application lists lifecycle/read/display tools
- **THEN** model-controlled retargeting and retention fields are absent.

### Requirement: Read and display preserve admitted identity
Representative safe read and display operations SHALL execute through the
common executor with the admitted target/session and bounded evidence policy.

#### Scenario: Safe read executes
- **WHEN** a bound session requests a non-mutating window inventory
- **THEN** its result carries the same target/session and verdict class.

#### Scenario: Display evidence is retained
- **WHEN** a bound session captures a screenshot or display primitive
- **THEN** its artifact carries target/session/operation/binding/hash metadata
- **AND** sanitized reviewed evidence contains no raw image, UI text or path.

### Requirement: Cleanup is exact-owned and target preserving
Project cleanup MUST validate target, session, generation, ownership and
lifecycle/process handle before stopping only run-owned resources.

#### Scenario: Owned lifecycle is cleaned
- **WHEN** current exact-owned cleanup runs
- **THEN** its TestClient, display, helper, listener, stage and ownership record
  are removed and pre-existing resources remain unchanged.

#### Scenario: Non-owned or foreign cleanup is requested
- **WHEN** attachment is non-owned or its identity/handle differs
- **THEN** qa-mcp detaches without signalling, or refuses as not-owned.

### Requirement: Binding enforcement never provisions a fallback
No failure or recovery path SHALL create, copy, restore, register, convert,
switch or silently select another infobase or direct-Xvfb target.

#### Scenario: Declared operation fails
- **WHEN** launch, attach, read or display fails
- **THEN** the typed result is returned and exact-owned state is cleaned
- **AND** no alternate target/session is created.

### Requirement: Every bound native operation requires current route admission
Every project-bound native-session operation MUST validate the exact current
target, session, attachment, endpoint and binding generation independently of
positive-result schema membership. Rejection MUST produce a fixed blocked
outcome before native handlers, endpoint probes, display callbacks or protocol
sends, without changing target, session, attachment or ownership state.

#### Scenario: Native command has no current route
- **WHEN** a bound registered `click_command` or another native route has missing, stale or mismatched target, session, attachment or generation
- **THEN** it returns `runtime-target-route-blocked` before any native or display effect
- **AND** all application identities and ownership state remain unchanged.

#### Scenario: Shared entrypoint receives a schema-missing native operation
- **WHEN** a bound request reaches the common operation entrypoint without a positive-result schema
- **THEN** it cannot bypass route admission or execute an unknown route permissively.

### Requirement: Public operation classification is complete and explicit
Every registered public tool MUST have an explicit native-session-bound,
lifecycle, provider-data or pure/readiness classification. Schema presence MUST
NOT determine permission. Unknown routes in a bound application MUST fail
closed; lifecycle-specific admission and provider policies MUST remain in force.

#### Scenario: Registry completeness is checked
- **WHEN** both composed public profiles and direct/decorated registered routes are inventoried
- **THEN** every tool has one explicit classification and no unknown native route receives a permissive default.

### Requirement: Current admitted and unbound controls remain usable
An exact admitted bound route MUST retain representative read, write and display
operations using that route once. Pure tools, provider-data tools and valid
lifecycle operations MUST remain available under their own existing policies.
Explicit unbound compatibility MUST remain supported.

#### Scenario: Exact bound route executes
- **WHEN** representative read, write and display calls have the exact current admitted route
- **THEN** each native consumer receives its admitted endpoint and identity once
- **AND** there is no retargeting or cross-application state change.

#### Scenario: Independent and legacy operations execute
- **WHEN** pure/provider tools, valid lifecycle calls or explicit unbound tools are called
- **THEN** their supported behavior remains available with existing safety policies.

### Requirement: Final native proof is source bound and sanitized
Delivery MUST retain source-bound Linux and authorized Windows-native evidence
for lifecycle, read, display, negative paths and exact-owned cleanup.

#### Scenario: Final evidence is audited
- **WHEN** the complete OSS-04 source is ready for critical review
- **THEN** source hashes match the reviewed payload and evidence reports target/
  session hashes, verdicts, ownership and before/after inventory only
- **AND** unrelated 1C, Docker and infobase state is preserved.

#### Scenario: Older source evidence differs
- **WHEN** a preserved oversized or exhausted payload hash differs from the
  bounded published sequence
- **THEN** the mismatch is recorded as lineage and exact-final-source native
  proof is rerun
- **AND** the older payload is not restored or accepted as final evidence.

### Requirement: Screenshot cleanup follows trusted current production
The bound screenshot producer SHALL allocate a fresh owned destination within the
admitted root and validate backend-returned identity before reading, registering
or deleting it. A borrowed old path or symlink SHALL NOT authorize cleanup.
Sanitized policy SHALL remove only its own current raw capture and retain safe
verifiable artifact metadata; full_local SHALL retain useful current evidence.

#### Scenario: Borrowed backend file is preserved
- **WHEN** a backend returns an unrelated pre-existing path, wrong destination or symlink
- **THEN** bound capture is non-success and neither reads it as accepted evidence nor deletes/modifies the borrowed file
- **AND** unrelated sentinels and concurrent sibling bytes remain unchanged

#### Scenario: Cleanup and failure isolation
- **WHEN** an owned capture succeeds or its producer/validation/cleanup fails while a sibling is paused after production
- **THEN** only the current scope records and owned temporary resources are closed or cleaned
- **AND** no success claims missing evidence or failed required sanitization, and the sibling remains usable

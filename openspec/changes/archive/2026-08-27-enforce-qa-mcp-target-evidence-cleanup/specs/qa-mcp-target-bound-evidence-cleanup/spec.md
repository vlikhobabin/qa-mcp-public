## ADDED Requirements

### Requirement: Project tool schemas cannot retarget or change retention
Project-bound MCP schemas MUST omit physical target, connection, env file,
endpoint, credential, rebind and evidence policy/root inputs and MUST inject
provider-owned values instead.

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

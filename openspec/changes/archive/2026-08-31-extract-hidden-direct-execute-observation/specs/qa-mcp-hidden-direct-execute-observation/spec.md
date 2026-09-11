## ADDED Requirements

### Requirement: Main-window observation is exact and unchanged
S4 MUST begin from one S3-admitted hidden main window and MUST re-admit the
same non-zero HWND, PID, lifecycle job, hidden desktop, fixed class and owner
identity before each UIA snapshot. Missing, duplicate, foreign or changed
identity MUST fail closed with no observation receipt admitted and no action.

#### Scenario: Exact main window remains current
- **WHEN** fresh hidden inventory contains exactly the original job-owned main
  identity on the requested hidden desktop
- **THEN** S4 may inspect its passive UIA properties and records only a
  sanitized exact-identity hash

#### Scenario: Main identity is missing, foreign or changed
- **WHEN** PID/job/desktop/class/owner/HWND differs or more than one candidate
  matches
- **THEN** S4 returns a typed refusal before marker/topology acceptance and
  action count remains zero

### Requirement: Marker comparison is hash-only and unambiguous
S4 MUST accept the expected marker only as a canonical lowercase SHA-256, MUST
hash UIA names in memory and MUST admit only exactly one matching element in
each stable snapshot. Raw marker/UI names MUST NOT be returned, serialized or
retained.

#### Scenario: One exact marker hash is observed
- **WHEN** two exact-main snapshots each contain exactly one UIA name whose
  SHA-256 equals the caller-supplied marker hash
- **THEN** the receipt reports marker count one and the expected hash without
  exposing the original name

#### Scenario: Marker is missing, duplicated or invalid
- **WHEN** the hash is malformed or either snapshot contains zero or multiple
  matches
- **THEN** observation fails closed with the typed marker outcome and zero
  action

### Requirement: UIA inventory is bounded, structural and stable
S4 MUST inspect at most `512` exact-PID elements, retain only hashes of
control-type/class/automation-id/name/path identity plus fixed supported-pattern
flags, and MUST reject foreign PID, malformed hashes, overflow, duplicate row
identity or changed topology between snapshots.

#### Scenario: Stable bounded topology is observed
- **WHEN** both exact-main snapshots have unique fully hashed rows, the same
  bounded control count and the same deterministic topology hash
- **THEN** the receipt exposes only the count, topology hash and typed status

#### Scenario: Topology is foreign, ambiguous or changed
- **WHEN** a row belongs to another PID, lacks canonical hashes, duplicates an
  identity, exceeds the bound or the second snapshot changes topology
- **THEN** S4 refuses the observation and cannot pass data to an action stage

### Requirement: Receipts are sanitized and action-free
S4 MUST serialize only typed outcomes, bounded counts, booleans and canonical
hashes and MUST record `action_count` as zero. It MUST add no caller, public or
wire surface and MUST NOT invoke UIA actions, addressed messages, global keys,
mouse/cursor, foreground or desktop-switch APIs.

#### Scenario: Sanitized receipt is retained
- **WHEN** portable or exact Windows observation completes
- **THEN** evidence contains exact source/candidate/platform/target hashes,
  topology/marker counts and cleanup booleans but no raw UI text, title,
  credential, connection string, geometry or screenshot

#### Scenario: Action or leakage enters S4
- **WHEN** source scan, receipt validation or hostile fixture finds an action
  primitive, non-zero action count or non-hash raw string
- **THEN** verification fails and the S4 payload cannot be reviewed or
  published

### Requirement: Native proof uses exact lineage and cleanup
S4 MUST compose from published `46287c...` plus only exact S4 paths and MUST
passively prove direct-`/Execute` main/marker/topology observation on trusted
`HISTORICAL-LAB-HOST\\historical-user`, platform `8.3.27.2214` and declared
`C:\\1C_BASES\\vanessa_client` before exact current-run cleanup.

#### Scenario: Exact-source Windows observation passes
- **WHEN** the exact candidate observes two stable snapshots without sending
  an action
- **THEN** evidence binds the candidate/source, main/marker/topology receipt
  and removal of exact task/stage/PIDs/job/desktop/TPort while preserving
  unrelated listener `18081`, Docker and reboot state

#### Scenario: Native target or passive post-state is unavailable
- **WHEN** host/platform/target/fixture/license/marker/topology or exact cleanup
  cannot be verified
- **THEN** delivery records a typed blocker and does not substitute injected,
  visible-desktop, stale, synthetic or action-assisted proof

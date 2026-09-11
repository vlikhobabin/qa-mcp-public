# qa-mcp-hidden-window-isolation Specification

## Purpose

Define the dormant, read-only Windows primitive that inventories exact hidden
and operator desktop window identity, admits one lifecycle-owned surface
fail-closed and emits only sanitized zero-input receipts.

## Requirements

### Requirement: Hidden and operator desktop inventories are exact and read-only
The dormant S3 primitive MUST enumerate only top-level HWND, PID, class and
owner-HWND identity from one validated current-run hidden desktop and
`Winsta0\\Default`, MUST bind ownership to the exact S2 lifecycle job and MUST
NOT read window titles, text, controls, geometry, screenshots or operator input.

#### Scenario: Exact hidden lifecycle is inventoried
- **WHEN** an admitted S2 lifecycle owns windows on its unique never-activated
  hidden desktop
- **THEN** S3 returns their in-memory HWND/PID/class/owner identity, class hashes
  and exact job-owned counts while the operator desktop has zero job-owned
  windows

#### Scenario: Owned window reaches Default
- **WHEN** any window on `Winsta0\\Default` belongs to the exact lifecycle job
- **THEN** isolation fails closed and no exact hidden window is admitted

### Requirement: Window identity admission is unique and fail-closed
S3 MUST admit one window only when exactly one hidden-desktop candidate has the
expected non-zero PID, belongs to the exact lifecycle job, matches the fixed
case-insensitive class predicate and has the exact owner HWND. It MUST return no
candidate for missing, duplicate, foreign-PID, outside-job, wrong-class,
wrong-owner, wrong-desktop or foreign-hidden surfaces.

#### Scenario: Exact root and owned popup are selected
- **WHEN** one job-owned root matches PID/class/owner zero and one job-owned
  popup matches PID/class/owner root on the exact hidden desktop
- **THEN** each exact predicate admits its unique HWND without activating or
  sending input to either window

#### Scenario: Candidate topology is hostile or ambiguous
- **WHEN** a candidate is duplicated, foreign, outside the job, has a changed
  class or owner, or appears on the operator desktop
- **THEN** admission fails before any downstream observation or action

### Requirement: Isolation receipts are sanitized and input-free
S3 MUST serialize only bounded counts, SHA-256 class hashes and booleans, MUST
record zero global-input/desktop-switch calls and MUST add no non-test caller,
public API, wire/profile field, UIA/marker/prompt behavior or action primitive.

#### Scenario: Receipt is retained
- **WHEN** synthetic and real-TestClient native isolation cases complete
- **THEN** retained evidence contains source/candidate/platform/target hashes,
  counts and verdicts but no raw class, title, text, geometry, screenshot,
  operator application identity, input content or credentials

#### Scenario: Forbidden primitive enters S3 source
- **WHEN** either S3 production file resolves a global-input, foreground,
  desktop-switch, addressed-message or UIA action primitive
- **THEN** the source guard fails and the candidate cannot be reviewed or
  published

### Requirement: S3 native proof and cleanup use exact published lineage
S3 MUST reconstruct from published `HEAD:host-agent` plus only its exact four
source/test paths, MUST prove synthetic owner topology and a real platform
`8.3.27.2214` TestClient on the declared `vanessa_client`, and MUST remove only
current-run tasks, stages, processes, listeners and desktop handles.

#### Scenario: Exact-source Windows matrix passes
- **WHEN** the deterministic candidate runs on trusted
  `HISTORICAL-LAB-HOST\\historical-user`
- **THEN** synthetic and real-TestClient cases observe job-owned hidden windows,
  zero job-owned `Default` windows, zero input/action calls and complete exact
  cleanup while preserving unrelated processes, Docker and listener `18081`

#### Scenario: Native target is unavailable
- **WHEN** trusted host, platform, target, credentials, license or exact cleanup
  cannot be verified
- **THEN** delivery records a typed blocker and does not replace the missing
  real-platform proof with synthetic or fault-injected evidence

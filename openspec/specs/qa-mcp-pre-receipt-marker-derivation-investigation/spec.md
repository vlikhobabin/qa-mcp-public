## Purpose

Define the smallest test-only, privacy-safe investigation boundary for a
candidate that exits before the S4 marker receipt, including exact cleanup and
the evidence required for any later separately authorized resume.

## Requirements

### Requirement: The investigation diagnostic is test-only and base-independent
The investigation MUST add only new Go test paths that compile from published
base `77a4b389b0ff78649c9b0846d48433cb424e659f` and observe the exact S4-R1
candidate as a hash-bound external child. It MUST add no production caller,
public route, wire field, UI action or change to the seven protected S4-R1
paths.

#### Scenario: Clean-base diagnostic is built
- **WHEN** the diagnostic files are overlaid on a clean published-base export
- **THEN** focused/full Go tests, vet and Windows test cross-builds pass without
  copying or compiling any S4-R1 source edit into the diagnostic payload

#### Scenario: Protected or production scope drifts
- **WHEN** a caller scan, per-path digest or manifest detects a production
  caller, protected-byte change or non-test diagnostic path
- **THEN** investigation verification fails and neither S4-R1 nor this card is
  admitted for publication

### Requirement: Pre-receipt failures are closed and privacy-safe
The live observer MUST admit a strict typed status only after reaching an
implemented emission branch: argv identity mismatch, child launch failure,
nonzero child exit without a checkpoint, or nonzero child exit with a valid
failed checkpoint. Supported rows distinguish argv validation, child launch,
listener readiness, process exit, desktop/window inventory, main admission and
passive UIA sampling. `diagnostic_setup` is a reserved validation enum with no
live producer and MUST NOT be claimed as emitted evidence. Harness
precondition/setup, receipt freshness/allocation, timeout, checkpoint-read or
validation, unexpected-zero-exit and unsafe-write failures MUST abort
fail-closed without producing or admitting a positive row. Any emitted status
MUST contain only closed enums, bounded counts/exit codes, booleans and
canonical hashes, with action count zero and raw UI retention false.

#### Scenario: Implemented nonzero-exit branch produces a typed row
- **WHEN** the external candidate exits nonzero with no checkpoint or with a
  valid failed checkpoint
- **THEN** the diagnostic records the narrowest implemented failure stage and
  exit classification without raw argv, child output, UI text, credentials or
  paths
- **WHEN** the harness instead encounters setup/precondition, receipt
  freshness/allocation, timeout, checkpoint-read/validation, unexpected zero
  exit or unsafe write
- **THEN** it aborts fail-closed without producing or admitting an evidence row

#### Scenario: Diagnostic input or checkpoint is hostile
- **WHEN** input hashes, stage/status pairing, checkpoint schema, bounds,
  action count or privacy flags are invalid
- **THEN** validation or the live harness fails closed, the invalid row cannot
  serialize or be admitted, and the abort cannot be reinterpreted as success

#### Scenario: Receipt is missing or a retry differs
- **WHEN** no valid receipt exists, a row is rerun or two one-shot rows disagree
- **THEN** no sentinel, retry or partial checkpoint satisfies acceptance and
  the outcome remains failed or `NOT-VERIFIABLE`; only a nonzero child exit
  with no checkpoint is typed as
  `process_exit/candidate_exited_without_checkpoint`

### Requirement: Exact-contour evidence produces one bounded decision
The investigation MUST run one exact S3 control and two passive S4 diagnostic
rows with the same authorized host, principal, Session 1, platform, infobase,
candidate, run-1 fixture and argv identities. It MUST publish exactly one
privacy-safe runbook/environment correction, bounded S4-R1 resume hypothesis
with a concrete verification target, or `NOT-VERIFIABLE` with an exact resume
condition.

#### Scenario: Two passive rows agree
- **WHEN** exact preflight and S3 pass and both one-shot S4 rows report the same
  typed failure stage/outcome
- **THEN** the curated decision may state only the causal boundary supported by
  those receipts and keeps S4-R1/S7 certification stopped pending a separate
  authorized resume

#### Scenario: Exact contour or classification is unavailable
- **WHEN** target identity, fixture/config hashes, S3 control, either diagnostic
  row or exact cleanup cannot be proven
- **THEN** the card records `NOT-VERIFIABLE` with the exact external-state
  resume condition and does not substitute a target, platform, fixture,
  visible desktop or action-assisted proof

### Requirement: Cleanup and protected scope remain exact
Every live row MUST restore exact configuration bytes, ACL and metadata and
remove only current-run task, stage, PID/job/desktop/TPort state. Evidence MUST
prove zero owned residue, unchanged unrelated task/boot fingerprints and
unchanged protected tracked and untracked/excluded bytes.

#### Scenario: Exact-owned cleanup completes
- **WHEN** a diagnostic row succeeds, fails, times out or exits before receipt
- **THEN** all current-run cleanup steps are attempted and retained evidence
  proves exact configuration restoration, zero owned residue and protected
  resource preservation

#### Scenario: Cleanup or protected identity is incomplete
- **WHEN** configuration, ACL/metadata, owned residue, unrelated fingerprints or
  protected digests cannot be proven exact
- **THEN** the investigation is blocked and cannot publish a resumable S4-R1
  hypothesis

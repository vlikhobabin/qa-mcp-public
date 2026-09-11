## ADDED Requirements

### Requirement: Receipt validates the published hidden chain
S6 MUST create an internal receipt only when the exact current S2 lifecycle
response, successful S4 observation and optional successful S5 prompt receipt
validate. Prompt-free and prompt-confirmed outcomes MUST use distinct admitted
statuses, and a present S5 receipt MUST bind the same main identity as S4.

#### Scenario: Exact prompt-free result is bound
- **WHEN** the current lifecycle and one successful S4 receipt validate with no
  prompt receipt
- **THEN** S6 emits the typed prompt-free internal status

#### Scenario: Nested outcome is malformed or inconsistent
- **WHEN** lifecycle, S4 or S5 schema, status, hash, count, type or shared main
  identity is invalid
- **THEN** S6 rejects the envelope before any cleanup, action or public callback

### Requirement: Cleanup identity is immutable and current-run exact
S6 MUST bind the receipt to exact run, worker-token and desktop hashes, port and
worker/child/listener PIDs using one independently recomputable lowercase
SHA-256. Every PID MUST be an exact Go `uint32` value in `1..4294967295`.
Python MUST compare every field against independently supplied current-
run identity and MUST reject missing, stale, foreign, reused or ambiguous
identity without selecting cleanup from receipt data.

#### Scenario: Current-run identity matches exactly
- **WHEN** every independently supplied cleanup field and the canonical binding
  hash equal the validated receipt
- **THEN** an immutable dormant stop lease may be created

#### Scenario: Receipt is stale, foreign or changed
- **WHEN** any run hash, token hash, desktop hash, port, PID or binding hash is
  absent, malformed, mismatched, replayed or mutated after binding
- **THEN** admission or stop fails with zero cleanup, action and public calls

### Requirement: Stop and cleanup are single-use
S6 MUST revalidate the exact admitted receipt immediately before stop, MUST
consume its binding in a caller-owned ledger before invoking the injected exact-
owned cleanup callback, and MUST make the shared-ledger check-and-consume atomic
across concurrent leases so it invokes that callback at most once. Callback
failure MUST remain consumed and MUST NOT authorize an automatic retry.

#### Scenario: Exact lease stops once
- **WHEN** one unchanged admitted receipt is stopped with an unused binding
- **THEN** the ledger is consumed before the exact cleanup callback runs once

#### Scenario: Stop or cleanup repeats
- **WHEN** the same receipt, another lease with the same binding or a prior
  failed-cleanup binding is stopped again, including concurrently
- **THEN** S6 rejects it before a second callback

### Requirement: Boundary remains private and privacy-safe
S6 receipts MUST contain only typed statuses, bounded counts, booleans and
lowercase SHA-256 values plus bounded port/PID identity. They MUST NOT contain
raw UI, paths, credentials, connection strings, handles, screenshots or
exception content. S6 MUST add no non-test caller, capability advertisement,
public tool/profile route, chooser, global input, foreground/desktop switch or
S7 stable admission, and production additions MUST remain at most `300` lines.

#### Scenario: Dormant boundary is audited
- **WHEN** clean composition, LOC, predecessor, caller, public, forbidden-action
  and privacy gates inspect the candidate
- **THEN** only the isolated internal receipt/lease boundary is present and
  Linux/public behavior remains unchanged

#### Scenario: Authority or private content escapes
- **WHEN** a public caller/route, forbidden action primitive, OS handle, raw UI
  or sensitive value enters the S6 payload
- **THEN** verification fails before independent review

### Requirement: Offline evidence binds exact S6 scope
S6 MUST retain privacy-safe hostile RED/GREEN, focused/full Go and Python, vet,
Windows cross-build, clean-composition, production LOC, predecessor-byte,
scope and OpenSpec evidence against published
`3a0e0f6899e75c05c33ba762d3c89873bf610b81`. A Windows live prompt rerun MUST
NOT be required unless the published S5 Windows behavior or artifact boundary
changes.

#### Scenario: Exact offline matrix passes
- **WHEN** the isolated S6 source/tests pass every declared offline and clean-
  composition gate while S1-S5 hashes remain unchanged
- **THEN** the payload is ready for one fresh ordinary independent review

#### Scenario: Runtime boundary changes unexpectedly
- **WHEN** implementation requires editing certified Windows S5 behavior or its
  artifact boundary
- **THEN** delivery stops and records the exact live-proof requirement before
  any Windows action

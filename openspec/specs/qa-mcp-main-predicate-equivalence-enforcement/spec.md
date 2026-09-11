# qa-mcp-main-predicate-equivalence-enforcement Specification

## Purpose

Define the private offline enforcement of the published main-predicate equivalence decision within exact I11 authorization.

## Requirements

### Requirement: Enforcement starts from the exact authorized payload
I11 SHALL reconstruct only the five reviewed product/test blobs recorded by
published I10 from Git tree `cda26645dc8f0e3cc1bab8761125b0de1af0fb9c`.
The implementation MUST remain within those five paths and at most 301 added
production lines against `2517ed6b55a6efed8f2cd84b46f8dea18090fd36`.

#### Scenario: Reviewed reconstruction is admitted
- **WHEN** each initial blob ID and SHA-256 equals I10's machine decision and
  I10/I10a are unchanged tracked `4.done` sources with the exact I11 object
- **THEN** the bounded implementation may proceed and records final blob
  lineage for the same five paths.

#### Scenario: Source or envelope differs
- **WHEN** a blob, source object, path, production LOC, authorization field or
  authority/wire flag differs
- **THEN** delivery fails closed before review or publication.

### Requirement: First and second predicates remain complete and ordered
The first evaluator MUST validate nonzero PID, non-empty class, class length at
most 256, canonical lowercase SHA-256 desktop hash and non-nil membership in
that order. The second evaluator MUST validate its explicit predicate plus
first-admission valid-identity provenance, expected HWND matching and exact
post-admission returned-identity equality before UIA. Both evaluators MUST
validate every row in the unchanged structural, hash, membership and match
order.

#### Scenario: Empty inventory follows a valid predicate
- **WHEN** a valid boundary predicate/provenance is paired with empty inventory
- **THEN** the decision is `absent` and consumes zero admission membership
  answers.

#### Scenario: Empty inventory follows an invalid predicate
- **WHEN** a predicate/provenance rule is invalid while inventory is empty
- **THEN** the decision is `invalid`, produces no cause and remains before
  passive UIA.

#### Scenario: Second class spelling drifts
- **WHEN** case-insensitive second admission succeeds but returned class
  spelling or casing differs from expected
- **THEN** exact returned-identity equality makes the connected decision
  `invalid` before the second UIA and without a cause.

### Requirement: Replay is ordered call-neutral and exactly consumed
The unchanged admission SHALL run once through a recording membership adapter.
The pure evaluator MUST replay only those ordered booleans, MUST consume every
answer exactly once in admission traversal order and MUST make zero membership
or Windows calls.

#### Scenario: Admission and replay agree on absence
- **WHEN** admission returns its broad error and replay proves valid predicate,
  valid job-owned inventory and zero matches with exact answer consumption
- **THEN** the combined outcome is `absent`.

#### Scenario: Replay or admission disagrees
- **WHEN** replay underflows, has surplus answers, consumes in a different
  order, finds invalidity, or disagrees with admission success/identity
- **THEN** the combined outcome is `invalid` and no cause is synthesized.

### Requirement: Only proven absence projects a closed cause
Enforcement SHALL expose only private `exact`, `absent` and `invalid`
decisions. Only `absent` MAY select the existing `successful_empty` or
`successful_nonempty_main_absent` cause; invalid or ambiguous state MUST select
no cause and MUST not reach passive UIA.

#### Scenario: Valid non-empty inventory has no match
- **WHEN** all reached rows are valid and job-owned but none matches
- **THEN** the outcome is `absent` with the existing non-empty absence cause.

#### Scenario: Matching inventory is ambiguous
- **WHEN** more than one valid job-owned row matches
- **THEN** the outcome is `invalid` with no cause, UIA or action.

### Requirement: Predecessor calls and control behavior are identical
The successful one-window path MUST retain exactly two inventories, four fence
snapshots, eight process Open/Wait/Close calls each, four port probes, twelve
membership calls, one `250 ms` sleep, two passive UIA calls and zero actions.
First and second absence or invalidity MUST retain the predecessor polling,
`200 ms` sleeps and terminal outcomes with exact reached-row membership counts.

#### Scenario: First boundary is hostile
- **WHEN** invalid or ambiguous state reaches the actual first decision
- **THEN** it retains retry/sleep and final `main_not_ready`, with zero UIA and
  no immediate inventory-failure return.

#### Scenario: Second boundary is hostile
- **WHEN** invalid or ambiguous state reaches the actual second decision
- **THEN** it retains the first UIA and `250 ms` prefix, then `200 ms` retry
  sleep and `second_uia_not_ready`, with no second UIA or added external call.

### Requirement: Connected mutation evidence binds every invariant
Verification MUST exercise identical matrices at both actual connected
decisions and bind decision, cause, exact dynamic calls, sleeps, outcome, UIA
order, privacy and zero action. It MUST retain RED for every declared predicate,
projection, live replay, second exact-identity, after-UIA, replay mismatch,
invalid cause and first-sleep/outcome mutation, followed by GREEN for the final
payload.

#### Scenario: A connected guard or projection is removed
- **WHEN** any declared mutation is applied while pure helper tests remain
  unchanged
- **THEN** a behavioral connected oracle fails RED; a source-string assertion
  alone cannot satisfy the evidence requirement.

#### Scenario: Final implementation is verified
- **WHEN** the unmodified final payload runs the same connected matrix
- **THEN** every row passes GREEN with exact behavior and call counts.

### Requirement: Enforcement remains private offline and non-mutating
I11 MUST add no exported API, route, wire field, retry, fallback, wait, Windows
operation, desktop mutation, handle transfer, authority, marker derivation or
public caller and MUST preserve Apache-2.0. Windows binaries MUST only be
cross-built deterministically and MUST NOT be executed.

#### Scenario: Offline proof floor passes
- **WHEN** focused/full Go tests and vet, Linux not-live coverage,
  deterministic amd64/386 cross-build pairs, strict OpenSpec and exact scope,
  authorization, blob, LOC, call, privacy, public-surface, license, whitespace,
  evidence and manifest gates pass
- **THEN** the exact payload may enter fresh ordinary/high review without any
  Windows, PowerShell, 1C, endpoint, lab/live/action, S5/S7 or SSH contact.

## ADDED Requirements

### Requirement: Boundary predicates are complete and ordered
The decision SHALL enumerate the distinct first-admission predicate and
second-readmission predicate/provenance rules, their short-circuit order, every
inventory-row validity rule, membership-call order, matching cardinality and
handle constraint. It MUST identify first-boundary class length at most `256`
and second-boundary valid-identity provenance plus post-admission exact returned-
identity equality, and MUST evaluate empty inventory only after a valid
predicate/provenance guard.

#### Scenario: Empty inventory follows a valid predicate
- **WHEN** a boundary has valid expected predicate/provenance and an empty
  fenced inventory
- **THEN** admission membership is called zero times and the pure decision is
  true absence
- **AND** the boundary retains its predecessor retry/sleep outcome before UIA.

#### Scenario: Empty inventory follows an invalid predicate
- **WHEN** the first expected class is longer than `256` or another expected
  predicate/provenance rule is invalid while inventory is empty
- **THEN** the decision is invalid rather than absent
- **AND** no successful absence cause or passive UIA is produced.

#### Scenario: Second admission returns class spelling drift
- **WHEN** second admission succeeds through case-insensitive class matching
  but the returned identity differs from expected in class spelling or casing
- **THEN** the wrapper's exact post-admission identity comparison makes the
  outcome invalid before UIA
- **AND** no successful cause is produced.

### Requirement: Admission and classification are call-neutral equivalents
The successor decision SHALL reuse the unchanged admission result plus a pure
replay of only the membership booleans recorded during that admission. Replay
MUST make no external membership or Windows call, MUST consume exactly the
recorded answers in admission order and MUST fail invalid on underflow,
surplus, returned-identity disagreement or decision/admission disagreement.

#### Scenario: Broad error is proven true absence
- **WHEN** admission returns its broad error and pure replay proves a valid
  predicate, valid job-owned inventory and zero matching identities
- **THEN** the combined outcome is true absence
- **AND** only the closed empty or non-empty absence cause is eligible.

#### Scenario: Broad error represents hostile state
- **WHEN** admission returns its broad error and replay finds an invalid
  predicate, malformed/foreign row, false membership, multiple matches or a
  second-boundary handle mismatch
- **THEN** the combined outcome is invalid
- **AND** no successful cause is synthesized.

#### Scenario: Replay would call membership again
- **WHEN** a mutation replaces a recorded boolean with another live membership
  evaluation
- **THEN** the connected dynamic call-count oracle fails RED
- **AND** the successor cannot pass review.

### Requirement: Closed outcomes distinguish exact absence and invalidity
The contract SHALL expose only `exact`, `absent` and `invalid` private
decisions. `absent` MUST require a valid predicate/provenance, all rows valid
and job-owned and zero matches; `exact` MUST require exactly one match and the
second-boundary expected HWND plus exact returned-identity equality after
admission; every other state MUST be invalid. Duplicate
non-matching rows remain absence because unchanged admission does not reject
them, while duplicate matching rows are invalid ambiguity.

#### Scenario: Valid non-empty inventory has no match
- **WHEN** all rows are valid and job-owned but none matches PID,
  case-insensitive class and owner
- **THEN** the outcome is true non-empty absence
- **AND** the closed cause is `successful_nonempty_main_absent`.

#### Scenario: Matching inventory is ambiguous
- **WHEN** two valid job-owned rows match the boundary predicate
- **THEN** the outcome is invalid
- **AND** no cause, UIA or action follows that decision.

### Requirement: Connected predecessor behavior is unchanged
The successor SHALL preserve exactly two inventory calls on success, all
pre/post fences, poll/deadline behavior, `200 ms` retry sleeps, the `250 ms`
inter-sample sleep, terminal statuses, passive UIA order, privacy and zero
action. For the successful one-window path it MUST preserve eight calls each
to process Open/Wait/Close, four port probes, twelve job-membership predicate
calls and two UIA calls, with zero replay calls.

#### Scenario: First-boundary hostile state
- **WHEN** invalid or ambiguous main state reaches the real first decision
- **THEN** it retains the `200 ms` sleep/retry path, final `main_not_ready`,
  zero UIA and the exact reached-row membership count
- **AND** it does not return a new immediate inventory failure.

#### Scenario: Second-boundary hostile state
- **WHEN** invalid or ambiguous main state reaches the real second decision
  after one successful first UIA
- **THEN** it retains the `250 ms` prefix, a `200 ms` retry, one UIA already
  completed and `second_uia_not_ready`
- **AND** it adds no membership, fence, Windows or action call.

### Requirement: Connected RED and GREEN matrices bind every mismatch
The successor verification SHALL run identical hostile rows through the actual
first and second connected decisions. It MUST retain RED failures for each
disconnected projection, each removed expected/row guard including class
length, removed second post-admission exact-identity comparison, repeated live
membership, after-UIA projection, invalid-cause synthesis and changed first-
boundary sleep/outcome, then retain GREEN for the unmodified final payload
with exact dynamic counts.

#### Scenario: Pure helper is correct but a boundary is disconnected
- **WHEN** either connected projection is deliberately disconnected while pure
  helper tests remain unchanged
- **THEN** the identical connected matrix fails RED
- **AND** source-string or call-site counts cannot substitute for the failure.

#### Scenario: Missing class-length row is reintroduced
- **WHEN** the `len(className) <= 256` rule is removed from first-boundary pure
  evaluation and an overlength predicate is paired with empty inventory
- **THEN** the identical connected row fails because invalid collapsed to
  absence and a success cause
- **AND** GREEN requires invalid, no cause, predecessor counts/sleep/outcome
  and zero UIA.

#### Scenario: Second exact-identity comparison is disconnected
- **WHEN** the wrapper's `current == expected` comparison is removed and a
  case-insensitive admission match returns changed class spelling or casing
- **THEN** the identical connected second-boundary row fails RED
- **AND** GREEN requires invalid, no cause, unchanged predecessor calls/sleeps
  and zero second UIA.

### Requirement: I11 uses a new exact bounded authorization
The decision SHALL record that the I8 five-product/test-path and
`301`-production-LOC envelope is quantitatively sufficient because canonical
I9 cycle 3 used those five paths and `247` production LOC. It MUST also record
that I8's exact-I4 authorization is not reusable and SHALL prepare a separate
authorization source bound to published I10 and exact I11 before I11 review.

#### Scenario: Exact successor stays within the decision
- **WHEN** I11 changes only the five named product/test paths, remains at or
  below `301` added production LOC against `2517ed6`, adds no authority/wire or
  external operation and passes the complete proof floor
- **THEN** a separately published exact authorization source may clear the
  repeated-defect complexity guard
- **AND** I11 still requires deterministic preflight and fresh independent
  ordinary/high GO review.

#### Scenario: I8 is offered as I11 authorization
- **WHEN** I11 references published I8 or any source whose successor path/id is
  not exact I11
- **THEN** authorization is invalid and MUST fail closed
- **AND** I8 remains unchanged and exact-I4-only.

### Requirement: Investigation is documentation-only and offline
I10 MUST change only its card, OpenSpec decision artifacts, synced capability,
curated public-safe decision evidence, parent roadmap and prepared successor
cards. It MUST preserve Apache-2.0, change no host-agent product/test file and
perform no Windows, PowerShell, 1C, endpoint, lab/live/action, S5/S7 or SSH
operation.

#### Scenario: I10 reaches publication
- **WHEN** strict validation, scope, decision-schema, lineage, public-surface,
  license and whitespace gates plus fresh independent review pass
- **THEN** only documentation/OpenSpec/board files are published
- **AND** the S4-R1 parent remains blocked and no classifier exists in product.

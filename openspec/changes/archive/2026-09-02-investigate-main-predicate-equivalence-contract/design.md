## Context

The safe published baseline is
`2517ed6b55a6efed8f2cd84b46f8dea18090fd36`. Published I7 and I8 authorize
only exact I4, while I4 and its I9 linked replacement remain rejected and
unpublished. I4 collapsed every broad admission error to `main_absent`. I9
cycle 1 changed the first-boundary retry/sleep/call outcome, cycle 2 repeated
the external membership predicate, and cycle 3 omitted the first admission's
`len(className) <= 256` predicate so empty inventory became false absence.

The canonical I9 cycle-3 verdict is bound to reviewed tree
`cda26645dc8f0e3cc1bab8761125b0de1af0fb9c`. The later working tree contains
an unauthorized interrupted cycle-4 test addition and is not the reviewed
payload. I10 uses only the canonical verdicts/history/evidence index, concise
retained outputs and Git objects at the reviewed tree. Old workspaces remain
immutable.

There are no protocol captures, frame ranges, dynamic protocol fields or
replay traffic. The only replay discussed here is a pure in-memory replay of
already-recorded boolean job-membership answers. No runtime resource is
created, so runtime cleanup is not applicable.

## Goals / Non-Goals

**Goals:**

- Freeze the complete first- and second-boundary predicate semantics and order.
- Make true absence provable and every invalid/ambiguous state cause-free.
- Preserve all predecessor calls, fences, polling, sleeps, outcomes, passive
  UIA order, privacy and zero action.
- Define connected mutation-sensitive RED/GREEN matrices.
- Decide the exact bounded path/LOC/authority handoff for I11.

**Non-Goals:**

- Implementing or continuing I4/I9, or implementing I11 in I10.
- Changing the unchanged admission functions or any host-agent product/test
  file in I10.
- Adding a public surface, wire field, runtime authority, Windows operation,
  retry, fallback, wait or external action.
- Windows, PowerShell, 1C, endpoint, lab/live/action, S5/S7 or SSH work.

## Decisions

### 1. Treat I4 and I9 only as rejected design evidence

I4 is evidence that broad admission errors cannot be mapped to absence. I9's
three canonical review cycles are evidence that correctness also requires
first-decision binding, exact predecessor behavior, external-call neutrality
and complete predicate equivalence. Neither card is completed or published;
neither working tree is a source baseline.

Alternative: continue I9 with another test/fix cycle. Rejected because the
operator forbids a third same-card rescue and ChangeRail requires an
investigation after the repeated invariant class.

### 2. Freeze two distinct admission contracts instead of one lossy helper

The first boundary calls `admitExactHiddenWindow` with predicate
`(desktopHash, listenerPID, "V8TopLevelFrameSDI", owner=0, member)`. Its
short-circuit order is:

1. reject `pid == 0`;
2. reject empty class;
3. reject class length greater than `256`;
4. reject a malformed/non-canonical desktop SHA-256;
5. reject a nil membership predicate;
6. for each item in slice order, validate `HWND != 0`, `PID != 0`,
   `OwnerHWND != HWND`, non-empty class, class length at most `256`, exact
   desktop-hash equality and canonical hash;
7. only after that row is valid, call membership exactly once for its PID and
   reject false;
8. match PID, case-insensitive class and owner; accept exactly one match.

The second boundary first rejects a nil passive observer, then calls unchanged
`admitHiddenDirectMainWindow` with the first admitted identity. Its explicit
expected guard checks nonzero PID, non-empty class, canonical desktop hash and
non-nil membership, in that order; it does not independently check expected
class length or expected HWND. The connected boundary therefore MUST retain
the stronger provenance proof from the first admission: the expected identity
has nonzero HWND/PID, non-self owner, non-empty class of at most `256` bytes and
the exact canonical desktop hash. It then validates/items/calls membership and
matches PID/class/owner in the same row order, and accepts only one match whose
HWND equals the expected HWND. After that admission succeeds, the wrapper
compares `current != expected` by exact struct equality before UIA. This is a
distinct final rule because inner class matching uses `EqualFold`: class
spelling/casing drift can pass admission but MUST fail the connected wrapper.

This distinction closes I9 cycle 3: class length is an explicit first-boundary
predicate and a second-boundary provenance invariant. A shared evaluator may
not silently use the weaker intersection of the two guards.

Empty inventory is evaluated only after a valid predicate/provenance guard.
It performs zero admission membership calls and is `absent`, never `invalid`.
Empty inventory with an invalid first predicate or invalid second provenance is
`invalid`, never `absent`.

Alternative: infer semantics from admission error strings. Rejected because
the errors are broad, privacy-sensitive implementation text and do not carry a
closed outcome.

### 3. Reuse the admission traversal through a bounded boolean replay

I11 may wrap the existing membership predicate while the unchanged admission
runs and retain only the ordered boolean answers. A boundary-specific pure
evaluator then replays those booleans over the same immutable expected value
and inventory slice. It MUST perform no external call and MUST report both its
closed decision and the exact number of answers consumed.

The pair is accepted only under this equivalence table:

| Admission result | Pure decision | Combined outcome |
| --- | --- | --- |
| success with admitted identity exactly equal to expected | `exact` with the same identity | `exact` |
| broad error | `absent` | true absence |
| broad error | `invalid` | invalid, no cause |
| success with returned identity drift | any | disagreement, invalid |
| success with exact identity | `absent` or `invalid` | disagreement, invalid |
| broad error | `exact` | disagreement, invalid |
| any | replay underflow, surplus or wrong consumption | invalid |

The replay MUST consume exactly the membership results produced by the
admission. An invalid predicate consumes zero; an invalid row consumes none for
that row or later rows; a valid reached row consumes one even when it does not
match. No PID, HWND, handle, class, hash, raw error or dynamic identity is
retained in the replay record.

Alternative: call membership again from the classifier. Rejected by I9 cycle
2 because on Windows each extra job-membership probe adds OpenProcess,
IsProcessInJob and CloseHandle calls. Alternative: replace both admission
functions with a new combined implementation. Rejected for I11 because it
changes the published admission boundary and exceeds the bounded rescue
decision; that requires a separate refactor investigation.

### 4. Use a closed three-outcome taxonomy

- `exact`: the boundary-specific predicate/provenance is valid, every reached
  inventory row is valid and job-owned, exactly one matching row satisfies the
  boundary's handle rule and, at the second wrapper, the returned identity is
  exactly equal to expected after admission.
- `absent`: the predicate/provenance is valid, every inventory row is valid and
  job-owned, and zero rows match. Empty inventory is the empty subset of this
  outcome. Duplicate non-matching rows remain absence because unchanged
  admission does not reject them.
- `invalid`: invalid predicate/provenance; malformed, foreign or non-job row;
  more than one matching row; second-boundary handle mismatch; replay
  mismatch; or disagreement with the admission result.

Only `absent` may project the existing closed true-absence cause:
`successful_empty` for a fenced empty inventory or
`successful_nonempty_main_absent` for a fenced non-empty inventory. `invalid`
MUST project no success cause and MUST remain before passive UIA. The words
"successful" describe the existing closed observation-cause vocabulary; they
do not turn the worker operation into success.

### 5. Preserve the connected predecessor state machine exactly

For a successful one-window path, the predecessor contract remains two
inventory calls, four fence snapshots, eight process Open/Wait/Close calls of
each kind, four exact-port probes, twelve total job-membership predicate calls,
two UIA calls, one `250 ms` inter-sample sleep, zero diagnostics, zero input or
action, and a passed passive receipt. The pure replay adds zero calls.

At the first boundary, true absence or invalid state retains the predecessor
`200 ms` sleep and retry/poll path, no UIA, no immediate inventory-failure
return and final `main_not_ready` when the deadline closes. At the second
boundary, true absence or invalid state occurs after the already-completed
first UIA and `250 ms` sleep, retains one further `200 ms` sleep/retry and the
`second_uia_not_ready` state. Fenced inventory/liveness failure remains the
existing immediate diagnostic path and is not reclassified as main absence.

Every row MUST bind exact dynamic counts. For one attempted first poll, fence
membership contributes four calls; admission adds zero for empty/invalid
predicate or malformed first row, one for one valid reached row and two for
two valid duplicate matches. For a second-boundary attempt after a one-row
exact first boundary, the fixed prefix is nine calls (four first-fence, one
first admission, four second-fence); second admission adds zero, one or two by
the same reached-row rule. These formulas prevent static call-site checks from
substituting for the actual first decision.

### 6. Require connected, identical mutation-sensitive matrices

The successor matrix includes:

- predicate/provenance rows: zero PID, empty class, class lengths `256` and
  `257`, malformed/uppercase/wrong-length desktop hash, nil membership,
  second expected zero/mismatched HWND, valid empty inventory;
- row-validity rows: zero HWND, zero PID, self owner, empty class, class lengths
  `256` and `257`, desktop mismatch, malformed desktop hash and membership
  false at each reached position;
- cardinality/identity rows: empty, valid non-empty no match, one exact match,
  first-boundary case-folded match, two matching rows, one wrong-handle match
  at the second boundary, second-boundary case-fold admission with changed
  class spelling/casing, and duplicate non-matching rows;
- connected-order rows: first and second projection, before-UIA ordering,
  replay consumption, exact membership/fence/inventory/UIA counts, sleeps,
  terminal outcomes, privacy and zero action.

The identical matrix MUST first fail under isolated mutations that disconnect
the first projection, disconnect the second projection, remove each guard
(especially `len <= 256`), remove the second wrapper's exact returned-identity
comparison, call live membership during replay, move projection after UIA,
allow an invalid cause, or change the first-boundary sleep/outcome. The second
class-spelling/casing drift row MUST be invalid, cause-free and before UIA.
GREEN is accepted only after the unmodified final payload passes every row.
Pure-helper tests alone and source-string/call-site counts are insufficient.

### 7. Retain the five-path/301 envelope but issue new exact authority

The canonical I9 cycle-3 reviewed tree changed exactly these five product/test
paths and measured `247` added production LOC:

1. `host-agent/windows-display-agent/hidden_desktop_window_isolation_windows.go`
2. `host-agent/windows-display-agent/hidden_direct_execute_observation.go`
3. `host-agent/windows-display-agent/hidden_direct_execute_observation_test.go`
4. `host-agent/windows-display-agent/hidden_direct_execute_observation_windows_test.go`
5. `host-agent/windows-display-agent/s4_r2_pre_receipt_diagnostic_test.go`

The missing predicate row and equivalence assertions fit within the remaining
`54`-LOC production headroom because tests are excluded from production LOC
and no sixth product/test path is needed. Therefore the quantitative envelope
remains sufficient. I11's complete replacement payload remains capped at five
paths and `301` added production LOC against `2517ed6`.

Published I8 cannot authorize I11: its exact six-field object binds the
successor id/path of I4. Rewriting or treating it as reusable would invalidate
the machine contract. I10 therefore prepares a separate authorization-source
card whose future published object binds I10 and exact I11; I11 remains
fail-closed until that source is independently delivered in `4.done`.

## Risks / Trade-offs

- [A future helper again uses the intersection of two guards] -> Keep distinct
  boundary modes and mutation REDs for every guard, provenance and the second
  post-admission exact-identity rule.
- [Replay changes side effects] -> Retain booleans only and bind exact dynamic
  membership and Windows-call counts, including underflow/surplus rows.
- [Invalid becomes a new terminal behavior] -> Assert predecessor sleeps,
  retries, deadlines and worker statuses on the real connected decisions.
- [The five-path envelope is mistaken for reusable I8 authority] -> Publish a
  new exact source card; leave I8 unchanged and exact-I4-only.
- [Tests pass at a disconnected helper] -> Require identical connected
  first/second mutation REDs and dynamic call/oracle assertions.

## Migration Plan

1. Publish I10's docs/OpenSpec-only decision and machine JSON after fresh GO.
2. Separately deliver the prepared authorization-source card so it becomes an
   unchanged tracked `4.done` artifact bound to I10 and I11.
3. In a fresh I11 session, reconstruct the reviewed I9 cycle-3 tree from Git
   object `cda26645...`, not the contaminated working tree; prove initial blobs.
4. Add the missing equivalence rows first and retain connected RED evidence,
   then implement within the exact five paths/301 LOC and retain GREEN.
5. Run the complete offline proof floor, deterministic preflight and a fresh
   independent ordinary/high review. Publish only on a validated fresh GO.

Rollback of I10 removes no runtime behavior. If I11 cannot remain inside the
exact path/LOC/authority envelope or cannot prove call-neutral equivalence, it
stops for a new investigation instead of widening.

## Open Questions

None. Quantitative scope is sufficient; exact successor authorization must be
new and separately published.

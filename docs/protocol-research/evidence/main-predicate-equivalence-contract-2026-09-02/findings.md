# Main-Predicate Equivalence Contract Decision

## Decision

The five-product/test-path, 301-added-production-LOC envelope remains
quantitatively sufficient for one new implementation attempt. The canonical
I9 cycle-3 reviewed tree used the same five paths and 247 added production LOC,
leaving 54 production LOC for the missing equivalence guard and integration.

Published I8 is not reusable machine authority. Its exact six-field source
binds I4's id and path. I10 therefore prepares a separate authorization-source
card bound to published I10 and exact I11. I11 remains blocked until that card
is independently reviewed and published unchanged in `4.done`.

I4 and I9 are rejected and unpublished evidence. They are not completed or
published cards. I9 evidence is bound to canonical review cycle 1, review
history, the retained evidence index/concise outputs and cycle-3 reviewed tree
`cda26645dc8f0e3cc1bab8761125b0de1af0fb9c`, never to its later contaminated
working tree.

## Failure Lineage

| Source | Status | Retained finding |
| --- | --- | --- |
| I4 | rejected, unpublished | Invalid predicate, malformed/foreign rows and duplicate/ambiguous matching inventories shared a broad admission error and were collapsed to `successful_nonempty_main_absent`. |
| I9 cycle 1 | NO-GO | First-boundary invalid handling bypassed the predecessor `200 ms` retry/sleep path, changed dynamic calls and terminal outcome, and the oracle did not execute the real first decision. |
| I9 cycle 2 | NO-GO | Classification re-traversed membership, adding two Windows membership probes/six API calls on the successful two-boundary path; the oracle did not bind dynamic calls. |
| I9 cycle 3 | NO-GO | Pure taxonomy omitted the first admission's class-length limit; an overlength expected class plus empty inventory became absence and then `successful_empty`, while the connected matrix missed the row. |

## Exact Admission Predicates

### First connected boundary

`admitExactHiddenWindow` checks the expected predicate before inventory:

1. `pid != 0`;
2. class is non-empty;
3. `len(className) <= 256`;
4. desktop hash is canonical lowercase SHA-256;
5. membership predicate is non-nil.

It then checks each row in slice order:

1. `HWND != 0`;
2. `PID != 0`;
3. `OwnerHWND != HWND`;
4. class is non-empty;
5. row class length is at most `256`;
6. row desktop hash equals the expected hash;
7. row desktop hash is canonical;
8. membership is called exactly once only after row validity passes;
9. PID, case-insensitive class and owner determine a match.

Exactly one match is admitted; zero is absence only after all earlier checks;
more than one matching row is invalid ambiguity. Duplicate non-matching rows
remain absence because the unchanged admission does not reject them.

### Second connected boundary

The wrapper rejects a nil UIA observer before admission.
`admitHiddenDirectMainWindow` explicitly checks nonzero expected PID,
non-empty expected class, canonical expected desktop hash and non-nil
membership. It does not independently check expected class length or HWND.
The connected second boundary must therefore retain first-admission provenance:
the expected identity already has nonzero HWND/PID, a non-self owner,
non-empty class of at most 256 bytes and the exact canonical desktop hash.

Rows are validated and membership/matching is evaluated in the same order as
the first boundary. The second boundary additionally requires exactly one
match whose HWND equals the expected HWND. After admission succeeds, the
wrapper compares the returned `current` identity to `expected` by exact Go
struct equality before UIA. Because inner admission matches class with
case-folding, this final comparison is a distinct rule: any class spelling or
casing drift is invalid even when PID, owner, HWND and desktop hash match.

### Empty inventory

- Valid first predicate or valid second provenance plus empty inventory is
  true absence with zero admission membership calls.
- Invalid predicate/provenance plus empty inventory is invalid with zero
  admission membership calls; it can never become absence.

## Closed Result/Replay Contract

The unchanged admission runs once with a recording membership adapter. The
record contains ordered booleans only. A boundary-specific pure evaluator
replays those booleans over the same expected value and immutable inventory.
It makes no external call and must consume exactly the answers admission
produced.

| Admission | Replay | Result |
| --- | --- | --- |
| success, admitted identity exactly equals expected | exact | exact |
| broad error | absent | true absence |
| broad error | invalid | invalid, no cause |
| success with returned identity drift | any | disagreement, invalid |
| success with exact identity | absent/invalid | disagreement, invalid |
| broad error | exact | disagreement, invalid |
| any | underflow/surplus/wrong consumption | invalid |

Closed outcomes are `exact`, `absent` and `invalid`. Only absence may project
`successful_empty` or `successful_nonempty_main_absent`. Invalid state has no
success cause and remains before passive UIA.

## Predecessor Invariants

Successful one-window path:

| Surface | Exact count/order |
| --- | --- |
| inventory | 2 |
| pre/post fence snapshots | 4 |
| process Open/Wait/Close | 8 each |
| exact-port probes | 4 |
| job-membership predicate | 12 total; replay adds 0 |
| passive UIA | 2, after each successful admission |
| sleeps | one `250 ms` inter-sample sleep |
| diagnostic/action/input | 0 |

First-boundary absence or invalidity retains `200 ms` sleep/retry, zero UIA,
no immediate inventory-failure return and final `main_not_ready` at deadline.
For one attempted poll, fences contribute four membership calls; admission
adds zero for empty/invalid-predicate/malformed-first-row, one for one valid
reached row, or two for two valid duplicate matches.

Second-boundary absence or invalidity occurs after one first UIA and the
`250 ms` sleep, then retains a `200 ms` sleep/retry and
`second_uia_not_ready`. Its fixed membership prefix is nine calls; second
admission adds zero, one or two by the reached-row rule. Fenced
inventory/liveness errors stay on their existing immediate diagnostic path.

## Connected RED/GREEN Matrix

Every row runs at both real connected decisions where reachable and binds
decision, cause, call counts, sleeps, outcome, UIA and zero action.

| Group | Required rows |
| --- | --- |
| expected/provenance | zero PID; empty class; class lengths 256/257; malformed, uppercase and wrong-length desktop hash; nil membership; second zero/mismatched HWND provenance; valid empty inventory |
| inventory row | zero HWND; zero PID; self owner; empty class; class lengths 256/257; desktop mismatch; malformed hash; membership false at first and later reached positions |
| cardinality/identity | empty; valid non-empty no match; one exact; first-boundary case-fold match; two matching rows; second wrong-handle match; second case-fold admission with class spelling/casing drift; duplicate non-matching rows |
| connected order | first/second projection before UIA; exact replay consumption; dynamic fence/inventory/membership/UIA counts; `200`/`250 ms` sleeps; terminal outcomes; privacy; zero action |

The identical matrix must retain RED failures for mutations that disconnect
either projection, remove each guard (especially class length), remove the
second wrapper's exact returned-identity comparison, call live membership
during replay, project after UIA, synthesize a cause for invalid state, alter
replay consumption, or change first-boundary sleep/outcome. The second class-
casing drift row must fail without that comparison and pass only as invalid,
cause-free and before second UIA. Pure helper GREEN or static source counts
are not connected proof.

## Bounded Successor

I11 is limited to these exact product/test paths:

1. `host-agent/windows-display-agent/hidden_desktop_window_isolation_windows.go`
2. `host-agent/windows-display-agent/hidden_direct_execute_observation.go`
3. `host-agent/windows-display-agent/hidden_direct_execute_observation_test.go`
4. `host-agent/windows-display-agent/hidden_direct_execute_observation_windows_test.go`
5. `host-agent/windows-display-agent/s4_r2_pre_receipt_diagnostic_test.go`

The complete replacement is capped at 301 added production LOC against
`2517ed6b55a6efed8f2cd84b46f8dea18090fd36`. It may add no sixth
product/test path, modify `hidden_desktop_window_isolation.go`, add authority
or wire protocol, or add any Windows operation, retry, fallback, wait, action,
public route or live surface.

The machine decision is retained in `decision.json`. Any path, LOC, authority,
predicate, invariant, matrix or evidence-floor mismatch requires a new
investigation; it is not a same-card rescue allowance.

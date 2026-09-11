## Context

Published I10 closed the semantic gap exposed by three rejected I9 review
cycles: the first connected decision changed predecessor behavior, a later
classifier repeated live membership calls, and the final reviewed evaluator
omitted the first admission's class-length predicate. Published I10a supplies
an exact six-field authorization bound to this I11 card in `3.inprogress`, a
301-added-production-LOC ceiling and no new authority or wire protocol.

The implementation baseline is published commit
`2517ed6b55a6efed8f2cd84b46f8dea18090fd36`. Only five canonical I9 cycle-3
blobs from reviewed Git tree `cda26645dc8f0e3cc1bab8761125b0de1af0fb9c`
are reconstruction sources. The old workspace working tree is explicitly
excluded. There are no protocol captures, frame ranges, dynamic protocol
fields or runtime replay traffic: "replay" means pure in-memory consumption of
ordered booleans already observed by the unchanged admission call. No runtime
resource is created and runtime cleanup is not applicable.

## Goals / Non-Goals

**Goals:**

- Make each real boundary distinguish `exact`, `absent` and `invalid` using
  the complete boundary-specific predicates and exact row traversal order.
- Preserve the unchanged admission as the sole source of membership/Windows
  operations, retaining only ordered boolean answers for pure replay.
- Permit an existing closed success cause only when replay proves absence.
- Preserve exact predecessor calls, fences, polling, sleeps, outcomes, passive
  UIA order, privacy and zero action.
- Retain connected mutation-sensitive evidence for every semantic and control
  invariant within the exact five paths/301-LOC envelope.

**Non-Goals:**

- Changing `hidden_desktop_window_isolation.go`, admission APIs, public
  surfaces, wire data, callers, authority or marker derivation.
- Adding any retry, fallback, wait, Windows operation, mutation, handle
  transfer, external side effect, S5/S7 or live/action behavior.
- Executing Windows binaries, PowerShell, 1C, an endpoint, lab or SSH command.

## Decisions

### 1. Reconstruct exact reviewed blobs before adding I10 corrections

The five initial product/test files are reconstructed by Git object identity
from the reviewed tree. Their blob IDs and SHA-256 values MUST exactly match
I10 before any correction is applied, and final lineage MUST record each final
blob. This preserves the reviewed cycle-3 starting point without trusting the
contaminated workspace.

Alternative: copy the old workspace files. Rejected because that tree contains
post-review changes and is not an admissible evidence source.

### 2. Keep distinct boundary modes and ordered boolean replay

One private evaluator has an explicit first/second boundary mode. The first
mode validates nonzero PID, non-empty class, class length at most 256,
canonical desktop hash and non-nil membership. The second mode validates its
weaker explicit admission predicate plus the stronger valid-identity
provenance established by the first boundary. Both validate rows in unchanged
order and consume one recorded boolean only after a row is structurally valid.

The recording adapter wraps the real admission's membership predicate. Replay
receives only its ordered booleans and must consume exactly all of them. It
never receives or retains PID, HWND, handle, class, hash, raw error or dynamic
identity and performs no external call.

Alternative: a shared weakest predicate or a second live membership traversal.
Rejected because each caused a published I9 invariant failure.

### 3. Combine admission and replay fail-closed

Admission success is `exact` only when replay is exact, both identities agree,
and the second wrapper's returned identity exactly equals expected before UIA.
A broad admission error becomes `absent` only when replay proves a valid
predicate/provenance, valid job-owned rows and zero matches. Invalid replay,
underflow/surplus, identity drift or any admission/replay disagreement is
`invalid` with no cause.

This preserves empty-inventory semantics: empty plus a valid predicate is
absence; empty plus an invalid predicate/provenance is invalid. Case-insensitive
second admission with class spelling/casing drift is invalid before UIA.

### 4. Project before passive UIA without changing predecessor control flow

The projection runs immediately after each unchanged admission attempt and
before its UIA call. Absence may select the existing empty/non-empty cause;
invalid selects no cause. Both continue through the predecessor retry/poll
path, including `200 ms` sleep and terminal `main_not_ready` or
`second_uia_not_ready`. The successful path retains two inventories, four
fences, 8 Open/Wait/Close calls each, four port probes, 12 membership calls,
one `250 ms` sleep and two UIA calls.

Alternative: return a new immediate failure on invalidity. Rejected because it
would repeat I9 cycle 1's control-flow regression.

### 5. Treat mutation-sensitive connected tests as implementation evidence

The same matrix exercises the actual first and second decisions, binding
decision, cause, dynamic calls, sleeps, outcome, UIA and zero action. Each
declared mutation must first fail RED and the final unmodified payload must
pass GREEN. A pure-helper-only test or a source-string assertion is not
sufficient evidence.

## Risks / Trade-offs

- [A predicate is silently weakened] -> Cover every expected/provenance and row
  guard, including class length and second exact identity, with connected RED.
- [Replay changes external call behavior] -> Retain booleans only and assert
  exact consumption plus dynamic membership/Windows call counts.
- [Invalid state gains a closed cause or reaches UIA] -> Bind cause and UIA
  ordering in each connected hostile row.
- [Scope drifts during rescue] -> Fail closed on any sixth path, more than 301
  production lines, new authority/wire/public surface or different object.

## Migration Plan

1. Prove baseline, immutable tree and all five exact initial blob identities.
2. Reconstruct the canonical reviewed files and retain identical RED evidence
   for each required mutation.
3. Add the complete I10 correction, format and retain final GREEN evidence.
4. Run the full offline proof floor, exact deterministic authorization/scope
   gates and fresh independent ordinary/high review.
5. Publish only a validated GO payload. Rollback is the scoped commit revert;
   no runtime data or external state requires recovery.

## Open Questions

None. Any path, LOC, authority, object, predicate or evidence mismatch requires
a new investigation rather than widening I11.

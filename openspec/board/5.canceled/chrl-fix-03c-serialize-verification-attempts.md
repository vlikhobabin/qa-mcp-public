# Prevent concurrent duplicate checks within one authorized run

## Status

5.canceled

## Owner

qa-mcp

## Series

chrl-fix-03c

## Order Index

406.223

## OpenSpec Stage

ordinary offline implementation independently accepted; not admitted or published

## Priority

P1

## Source

- `openspec/board/5.canceled/chrl-fix-03-persist-and-enforce-card-evidence-contract.md`
- Existing focused-repeat and pre-review/final cache checks happen before execution without a shared check-execution lock. A serial fake-callback test is not two-process proof.

## Summary

Serialize decision, launch and completion for verification within one current
authorized run. Consume 03B's terminal result contract; do not build another
receipt format or execute an ambiguous interrupted attempt again automatically.

## Acceptance

### Requirement: Make check admission single-flight

#### Scenario: Two processes request verification in the same run
- [C1] WHEN two real local processes request the same focused check or configured floor for the same run/payload, THEN only one enters execution; the contender returns busy or observes valid completed reuse after rechecking state under the same lock. It must not spawn a second child, overwrite an attempt or allocate a duplicate floor cycle.
- [C2] AND the run-local lock covers the reuse decision, attempt allocation, subprocess completion and terminal receipt publication. Identity/payload/configured commands are rechecked after lock acquisition; stale pre-lock observations cannot authorize reuse or execution. A single lock per run intentionally serializes different checks too.

### Requirement: Refuse ambiguous restart

#### Scenario: A verifier disappears while its child may still be running
- [C3] WHEN execution ownership is interrupted before a terminal receipt, THEN durable started state remains unconfirmed; losing a kernel lock or seeing a missing/reused PID is not completion or retry authority. Another caller refuses an unresolved attempt without killing unrelated processes or silently rerunning its command. A validated completed receipt remains reusable after a caller restart.

### Requirement: Keep receipt, lineage and role authority separate

#### Scenario: Ordinary delivery and legacy recovery use the check lane
- [C4] AND serialization leaves the configured commands, roles, review budgets, proof meaning, exact recovery eligibility and legacy records unchanged. It neither provides cross-run lineage adoption nor enables FIX-02. Resolving an unknown orphan is an explicit owned-process/retained-outcome decision, never an age-based lease steal or new automatic retry loop.

## Scope

- Future production: `scripts/changerail/local_delivery.py`, check-entry locking around `run_evidence`, `preverify`, `verify`/their shared floor execution, and small ownership-state helpers using 03B records.
- `tests/test_local_changerail_delivery.py`, canonical wiring spec and local-delivery runbook during implementation.
- No publisher transaction lock, review-session lock redesign, process scheduler, dependency or CLI authority expansion.

## Non-Goals

- Defining receipt integrity again, condition-proof maps, executing records, cross-run adoption, automatic orphan cleanup or guaranteeing exactly-once effects in arbitrary external programs.
- Testing concurrent processes by mocking the lock, child, receipt publisher or protected state transition.

## Affected Capabilities

- `changerail-consumer-wiring`

## Depends On

- `openspec/board/5.canceled/chrl-fix-03b1-retain-focused-check-proof.md`
- `openspec/board/5.canceled/chrl-fix-03b2f-retain-final-verification-proof.md`

03B2-F transitively requires 03B2-P and 03B1. The superseded 03B2 aggregate
is not a done dependency; plans/offline reports do not satisfy runner gates.

## Change Set

- `chrl-fix-03c-serialize-check-admission-and-completion`

## Design

Use the existing Linux `fcntl.flock` capability with one stable run-local lock.
Choose nonblocking busy refusal, not an unbounded queue. Check cache/receipt and
payload under the lock, then allocate the attempt and retain ownership until
completion is durably recorded. Do not acquire the same lock recursively from
preverify and its floor helper; the outer check entry owns it once. Preserve
existing review-lock ordering and release on every normal/error path.

Persist invocation identity/start state before launching a child. A killed
parent can release flock while leaving a child alive: therefore an unresolved
started record blocks re-entry even when flock is free. No automatic retry,
PID-only liveness shortcut, timeout-based success or lock-file deletion may
resolve this uncertainty. Keep it a concrete refusal with the owned invocation
reference. Normal terminal failure may be retried only through an explicit
already-authorized call; ambiguous state requires separate reconciliation.
This boundary is one run, not FIX-02's missing root-lineage adoption mechanism.

Tests use two real verifier processes, a local barrier/pipe-controlled child and
a durable invocation counter. Prove first-only invocation, unchanged records,
terminal reuse and the parent-dies/child-lives window. Stop only fixture-owned
PIDs; preserve unrelated fixture sentinels. No sleeps as race-proof substitutes.

## Delivery Budget

- primary_invariant: One current authorized run cannot launch a concurrent duplicate check or reuse an unresolved attempt as completion.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 1
- estimated_production_loc: 190

## Budget Notes

Look-ahead estimate: roughly 60 lock/helper, 70 entrypoint and 60 ownership/refusal
lines, reusing 03B records. Includes real-process regression work and docs.
Re-estimate after 03B; automatic reconciliation or cross-run authority is not
hidden inside these numbers. Do not weaken interruption proof to fit a budget.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

Future locators only; no test execution is claimed.
```json
{
  "schema":"qa-mcp.card-evidence.v1",
  "conditions":[
    {"condition":"C1","seam":"two-process check entry","precondition":"same run and payload with a barrier-held child","action":"start a contender while the first child is held","expected":"one actual invocation and no duplicated cycle; contender busy or verified reuse","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_check_singleflight_real_processes"},"stage":"implementation"},
    {"condition":"C2","seam":"lock-protected cache and allocation","precondition":"state changes between pre-lock observation and acquisition","action":"release a controlled competing owner and enter the real locked path","expected":"current identity is revalidated and stale observations cannot cause a spawn or false reuse","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_check_singleflight_revalidates_under_lock"},"stage":"implementation"},
    {"condition":"C3","seam":"parent interruption","precondition":"fixture verifier parent and independently observable live child","action":"terminate only the parent then request the same check; also restart after a completed control","expected":"unknown running attempt refuses without duplicate/foreign cleanup; terminal control is reused","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_check_singleflight_orphan_refusal"},"stage":"implementation"},
    {"condition":"C4","seam":"ordinary role and recovery boundaries","precondition":"current ordinary and exact-legacy fixtures","action":"inspect scoped diff and exercise existing guards","expected":"same roles/budgets/commands and unchanged history; no cross-run adoption or finalizer enablement","method":{"kind":"inspection","target":"scripts/changerail/local_delivery.py"},"stage":"review"}
  ],
  "risks":[
    {"kinds":["concurrency","restart","mutation"],"applies":true,"decision":"One kernel lock plus durable unresolved-attempt refusal; real competing-process and orphan tests, no age-based retry.","conditions":["C1","C2","C3"]},
    {"kinds":["input_safety"],"applies":true,"decision":"Reuse run-bound record/path validation from 03B; no caller-selected lock paths or PID-only proof.","conditions":["C2","C3"]},
    {"kinds":["publication","external_effects"],"applies":true,"decision":"Check lane only, current role authority retained, real test children fixture-owned and external/model/publication actions forbidden.","conditions":["C1","C3","C4"]}
  ]
}
```

Plan focused `uv run pytest -q tests/test_local_changerail_delivery.py -k check_singleflight`,
then ordinary relevant harness/static checks and the runner-owned final floor
only for authorized delivery. This planning step runs none of those subprocess tests.

## Related

- `openspec/board/5.canceled/chrl-fix-03d-bind-acceptance-to-observed-proof.md`
- `docs/development/local-changerail-delivery.md`

## Result

Implemented the offline run-local verification-attempt boundary. Focused,
pre-review, final and direct shared-floor checks serialize decision through
terminal receipt/index publication. This repair adds FIFO-controlled real
acquisition races for preverify, verify and the direct floor; contender-busy
snapshots across same-command and cross-lane contention; typed, fail-closed
intent ownership checks; and fixture-owned process-group cleanup. The focused
producer retains its unsafe-owner and validation-retention refusal boundary.
The closed canonical cycle-name reader now accepts exactly the allocator's
positive minimum-width names (`cycle-01`…`cycle-09`, then `cycle-10` and
higher), including `cycle-100`, while retaining refusal of started, malformed
and foreign intent records.
The implementation chronology below remains offline evidence, not runner GO,
handoff or publication. Later independent acceptance is recorded below;
earlier incomplete assessments and repair attempts remain immutable history.

The bounded check-03 repair additionally makes direct `_run_full_floor` callers
perform the existing validated completed-result decision under the same live lock
before cycle allocation. Real delayed direct contenders and restarted callers
therefore preserve the prior cycle and reuse it. Focused, preverify and final
fixture verifiers now hold the real lock across post-child terminal-receipt and
configured index-publication gates; fixture-only early unlock is rejected by the
new barriers. Payload-only acquisition drift is observed without configuration
drift, and the two final/direct-holder fixtures use owned process-group cleanup
with an after-child-ready failure/sentinel control.

Final offline outcome: fresh independent `check-04/review/assessment.json`
accepted C1-C4 and closed F5/F6/F7 without new findings; earlier F1-F4 were
already closed. Completion is indexed in
`.runtime/changerail/offline-fix03c-UhUyjW/completion-report.md` and `completion.json`.
Related checks: 14 focused plus 617 supporting tests, 70 specs, compilation and
wiring. The non-live result is composed: 2247 full-run passes with 74.69%
coverage plus the sole failed Xvfb test passing separately on unchanged bytes.
No original failed result is relabeled successful.

This roadmap-only edit follows that acceptance and changes the whole-payload
fingerprint; it does not issue a fresh semantic verdict or runner authority.
The exact reviewed bytes and all original reports are preserved in that evidence
root. Status/location remain backlog and unpublished, not an eligible done gate.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-03c-serialize-check-admission-and-completion`

### Why

Sequential cache checks cannot prevent two workers from executing concurrently.

### Goal

Serialize the real check boundary and refuse uncertain restart state.

### Scope

The current run's check entrypoints and ownership records only.

### Ordered Tasks

1. Reproduce two-process duplicate launch and parent-loss ambiguity using controlled fixture processes.
2. Add one lock/ownership boundary around reuse through terminal publication, using 03B identity and no nested acquisition.
3. Verify all C1-C4 assertions, lock release/error paths and completed reuse; update contract/docs and retain focused evidence before authorized completion.

### Acceptance

- C1-C4 have real-process evidence rather than call-order mocks.

### Depends On

- none

## Log

- 2026-09-07T07:16:05Z Reconciled final independent offline acceptance and
  composed verification in roadmap metadata/Result/Next. Preserved Acceptance,
  Design, Verify, Change checkpoints, card location and prior logs. This
  documentation-only delta is not another implementation or runner GO.
- 2026-09-07T05:47:10Z Repaired check-03 F5/F6/F7 in ordinary offline scope. Direct shared-floor acquisition now validates and reuses a completed current configured proof before cycle allocation; a real held-child/direct-prelock contender and a restarted direct caller preserve one invocation, one cycle and prior bytes. New real focused/preverify/final post-child observation gates retain flock through terminal receipt and aggregate index publication, with contender-busy snapshots and successful configured reuse; a task-local fixture-only early-unlock probe fails all three barriers without changing tracked payload. Final/direct payload-only acquisition tests start from completed proof and observe final stale-prerequisite refusal or a fresh current direct cycle without stale reuse. The two flagged fixture regressions now use `_FixtureProcessGroups`, and injected post-child-ready failure proves owned descendant cleanup while an independent sentinel survives. No runner context, admission/events/handoff/finalizer, card move, commit/push, pilot/live/1C work or independent acceptance was performed.
- 2026-09-07T05:15:35Z Tightened the repair-04 canonical-cycle matcher to exclude the unpadded one-digit names that the minimum-width allocator never emits. The existing real `cycle-100` reuse regression now includes a closed positive/negative name table (`01`, `09`, `10`, `99`, `100`, `101` versus zero, unpadded, overpadded, signed, Unicode-digit and suffixed forms) while retaining its started/malformed/foreign refusal assertions. No runner/handoff/finalizer/publication/pilot/live work, card transition, commit or independent acceptance was performed.
- 2026-09-07T05:09:18Z Repaired the uncapped-cycle reader mismatch found by the outer inspection. A real preverification fixture seeded through `cycle-99`, then used the allocator/producer/ownership reader to create observed terminal receipts in `cycle-100`; its next call now reaches normal reuse rather than a false unresolved refusal. The reader accepts only allocator-canonical positive cycle names and continues to refuse started, missing-observed-exit, foreign-card and noncanonical-cycle intent records before a new cycle. No runner/handoff/finalizer/publication/pilot/live work, card transition, commit or independent acceptance was performed.
- 2026-09-07T04:59:12Z Completed the remaining check-02 F1/F4/F5 implementation assertions in ordinary offline scope: real process gates now change current configuration/payload before the real lock acquisition for preverify, verify and direct floor; same-command and distinct cross-lane contenders return explicit busy before the held child is released with receipt/cycle byte snapshots; stale/forged ownership and malformed/foreign/terminal-without-observed-exit intent fail closed; unsafe FIFO/leaf/ancestor lock paths refuse before proof spawn; normal validation release and publication-retention refusal are differentiated. Fixture-owned process-group cleanup protects failure paths and keeps an unrelated sentinel alive. Focused evidence is recorded separately; no runner/handoff/finalizer/publication/pilot/live work, card transition, commit or independent acceptance was performed.
- 2026-09-07T04:30:04Z Extended repair-02 evidence with a controlled owner change between preliminary observation and actual lock acquisition, plus a no-follow unsafe-lock-path refusal; both prove no focused child allocation. The ordinary offline authority boundary is unchanged.
- 2026-09-07T04:24:31Z Repaired all check-02 independent-review findings in ordinary offline scope: direct helpers now require real active lock ownership, direct floors revalidate configured commands under lock, and receipt-bound start intent fails closed across damaged/missing receipts and interrupted/unknown outcomes. Added barrier-controlled cross-lane/final/direct-helper regressions and retained repair-02 evidence. No runner context, handoff, finalizer, publication, pilot, live work, commit or independent acceptance was performed.
- 2026-09-07T04:00:05Z Repaired the focused producer compatibility boundary found by the outer supporting harness: missing/unsafe owner reads again refuse as DeliveryError before lock/child side effects, and the extracted locked helper owns its ValidationError retention boundary. Ran focused producer/safe-read/storage-fault/retention groups and the complete local delivery test file; no runner context, finalizer, publication or other lifecycle action occurred.
- 2026-09-07T03:47:03Z Implemented the ordinary offline 03C boundary and focused real-process regression evidence. No runner context, card transition, finalizer, live work, independent acceptance, commit or publication was performed.
- 2026-09-06T12:56:20Z Recorded the independently useful single-flight look-ahead boundary with a 30-minute/190-line provisional budget. No lock, process behavior, card transition or publication was changed.
- 2026-09-06T14:18:25Z Replaced the non-executable 03B aggregate dependency with both actual 03B1 focused and 03B2 configured-proof successor cards. Other plan sections are unchanged; neither dependency is claimed delivered and no implementation/admission occurred.
- 2026-09-06T16:45:59Z Followed the operator-approved 03B2 split: replaced its aggregate done dependency with actual 03B2-F, transitively requiring 03B2-P; retained explicit 03B1 prerequisite and all acceptance/implementation scope. No dependency completion, admission or implementation is claimed.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

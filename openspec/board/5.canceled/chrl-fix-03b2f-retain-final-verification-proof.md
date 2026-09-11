# Retain complete final proof through reuse and safe delivery summaries

## Status

5.canceled

## Owner

qa-mcp

## Series

chrl-fix-03b2f

## Order Index

406.22222

## OpenSpec Stage

operator-planned lane successor; Tasks/Verify drafted; not admitted or implemented

## Priority

P1

## Source

- `openspec/board/5.canceled/chrl-fix-03b2-retain-configured-verification-proof.md`: preserved aggregate C1-C6 and approved lane split.
- `openspec/board/5.canceled/chrl-fix-03b2p-retain-pre-review-verification-proof.md`: owns usable configured adapters/ordered-set predicate and complete pre_review lane; consume its actually delivered interface.
- `.runtime/changerail/offline-checkpoint-fix03b2-knAAuZ/checkpoint-report.md`: final missing-log/drift RED and overlooked publisher evidence-reader inventory, not passing final proof.

## Summary

Activate the final lane using the delivered pre_review adapters and sole shared
receipt validator. Switch final reuse, the publisher's existing evidence-read
gate, exact-byte pytest summary/receipt and metrics together. This completes
the final portion of 03B2; it grants no new publication/finalization authority.

## Acceptance

### Requirement: Bind real final execution to current owning proof

#### Scenario: An existing authorized final verification runs

- [C1] WHEN the existing final-verification caller runs a configured command, THEN actual run/card/unique invocation, explicit final lane, exact configured shell text AND actual argv, UTC start and before-payload are retained before launch. Through the delivered sole schema/validator, terminal proof preserves actual exit/signal or explicit spawn/interruption/unknown outcome, UTC finish, finite nonnegative duration and after-payload separately from wrapper verdict. Stable/silent succeeds; per-command drift/incomplete execution or retention fails to the caller and stops later commands, including restoring ones; missing/unsafe owner launches nothing. Preserve aggregate start/end comparison, fresh GO, manifest and preverification prerequisites and runner ownership of the final floor.
- [C2] AND final attempts use exclusive run/cycle-owned paths isolated from focused/pre_review projections, complete regular size/SHA-256-bound logs and terminal-after-log atomic publication. Malformed/unknown/duplicate/deep/bad-terminal/running/missing/tampered/truncated proof and storage failures cannot establish success; silent zero-byte regular output can. Retain the actual process outcome in writable evidence or diagnostics when storage fails, without overwriting history or fabricating success.

### Requirement: Switch final reuse, publication evidence and log consumption together

#### Scenario: A final proof consumer inspects a complete or damaged set

- [C3] WHEN verify's final reuse guard, the shared matcher, publish's existing final-evidence admission, final pytest summary/receipt or final metrics consumes evidence, THEN one delivered aggregate predicate uses the sole receipt validator with explicit expected run/card/final lane/configured order/current payload and unique invocation references. Require the complete exact ordered set; missing/extra/reordered/duplicate/foreign/stale/failed/running proof refuses reuse/admission even when pre_review and final command lists match. Owner/index/record/log content, including preliminary/repeated reads, must use component-wise bounded regular no-follow access first. The summary parses precisely the same validated log bytes, never a reopened path or unchecked fallback; silent/no-summary output does not fabricate a pytest summary. Invalid observations are safely unconfirmed without incidental decoder/type/sort failures; loaded text never executes.
- [C4] AND an intact unchanged final set reuses with no second child; invalid proof is not a cache hit and only existing authorized callers create a new set. Historical cycle indexes/records/logs stay byte-identical except the existing current-index alias may advance. Real producer -> schema/hash -> wrapper -> aggregate -> actual verify/reuse -> safe summary/receipt/metrics compose for stable, drift and missing-log states. Final publication evidence rejection precedes card movement/staging/commit/push and preserves those fixture states; its valid control reaches the existing allowed boundary without bypassing prerequisites. Metrics keep command/exit/duration/time display without independent proof authority or focused/pre_review double-counting.

### Requirement: Preserve established lanes, history and authority

#### Scenario: Final legacy proof, pre-review or intentional repair coexists

- [C5] WHEN legacy/carried final evidence is read, THEN it stays historical/unconfirmed without upgrade, cross-run adoption, rewriting runs/contexts or changing exact manifests/counters/recovery eligibility/verdicts. Previously delivered pre_review and focused proof retain their behavior; real deliberate import repair remains changed-payload success only, not unchanged verification proof. No existing general shell repair gate is strengthened into a verification drift gate.
- [C6] AND this slice reuses the existing schema/validator/executor and delivered set predicate; it adds no condition-proof binding, single-flight, global decoder/framework/dependency, configured command/model/budget/role/floor ownership change, FIX-02/finalizer enablement, pilot or publication. Changes inside publish are limited to consuming validated final proof before its existing actions. Offline completion is relevant checks/report, never fabricated GO/handoff; endpoint evidence does not promise semantic adequacy, detection of edit/revert inside one child, hostile-writer safety or environmental reproducibility.

## Scope

- `scripts/changerail/local_delivery.py`: final opt-in to the delivered `_run_full_floor`/configured adapters; `_successful_verification_matches` final caller wiring; `verify` and necessary preliminary owner/index reads; publish's final-evidence read/validation adapter before existing mutation; `pytest_summary_from_verification`, `delivery_receipt_lines`, final `deterministic_commands`/metrics projection. Remove only the temporary legacy-final opt-in seam introduced by 03B2-P.
- `tests/test_local_changerail_delivery.py`: real final lane/set/summary/metrics fixtures and publication-gate state assertions with external actions isolated, plus delivered pre_review/focused/repair compatibility.
- `openspec/specs/changerail-consumer-wiring/spec.md`, `docs/development/local-changerail-delivery.md` and this card's implementation Result/Log.
- Consume actual 03B2-P adapters/aggregate predicate and unchanged `tools/changerail/schemas/check-result.schema.json`; no new schema or duplicate structural/set validator. Missing/incompatible dependency interface requires replan.

## Non-Goals

- Reimplementing pre_review or focused proof, another shell executor, global JSON/recovery hardening, automatic historical migration/adoption or command execution from proof/plan text.
- Publisher Git transaction/retry/crash recovery, new authority, board-finalizer repair or invoking publication; FIX-02 remains independent and disabled.
- 03C single-flight/orphan policy, 03D condition binding, live/provider/admin/Windows work or environment hashing.

## Affected Capabilities

- `changerail-consumer-wiring`

## Depends On

- `openspec/board/5.canceled/chrl-fix-03b2p-retain-pre-review-verification-proof.md`

This transitively requires 03B1. Use the real live dependency path and its
actual delivered interface, never a fictitious done path or the superseded
03B2 aggregate. Offline reports do not satisfy runner dependency/clean gates.

## Change Set

- `chrl-fix-03b2f-deliver-final-proof-and-safe-consumption`

## Design

Pass final explicitly from the authorized verify caller. Reuse the complete
configured observation/allocation/set mechanism delivered by 03B2-P; do not
copy its executor or implement a second validator. Remove the interim legacy
final path only when producer AND all final consumers use the same contract.
Separate attempts and metrics provenance; equal configured command text does
not transfer success across lanes. Require unique references at each ordered
position, including distinct attempts if the configured text itself repeats.

Preserve per-command and aggregate before/after equality independently. A
failed/drifting first command prevents a restoring second command. Retain
actual outcome separately from wrapper failure and use the sole safe reader
for owner, aggregate index, record and log. Audit each preliminary/repeated
read in verify and publish; inserting a later predicate after unsafe load_json
is insufficient. Preserve all existing role/GO/manifest/preverification gates.

Have the existing final summary/receipt consume validated bytes from the same
complete-set decision, not validate then reopen. A display-only loaded mapping
or root index ok flag cannot authenticate a final result. No summary is invented
for an empty log or absent terminal pytest line; existing required-summary
refusal remains. Reject malformed/deep/nonregular inputs safely while preserving
compatible historical command/exit/duration/time observations.

The publisher is included only because it is an authority consumer of final
evidence; finalizer/commit/push algorithms stay unchanged. Exercise its actual
pre-action evidence gate on a disposable card/index/worktree: corrupt proof
must leave card path/bytes and Git index unchanged and never reach external
actions. Provide a valid-prerequisite control; isolate only the later external
publication boundary, not the validator or publish gate under test. Such a
fixture is not permission to publish the occupied repository or to claim a
full publication transaction was independently verified.

## Delivery Budget

- primary_invariant: Every final current-success/reuse/admission and pytest-summary claim consumes one intact complete final proof set and its validated bytes.
- expected_wall_minutes: 24
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 1
- estimated_production_loc: 80

## Budget Notes

Incremental candidate 50-80 added production lines on a usable 03B2-P interface:
final caller/gate wiring 20-30, validated-byte summary/receipt 20-30 and final
metrics/compatibility 10-20. Tests/docs remain real reviewed effort. Estimated
21-24 minutes includes 2 actual-interface/RED inventory, 4 integration,
7-8 real final/path/reuse/publication-gate matrix, 2 docs/static, 4-5 fresh
review and 1-3 floor. No credit for a merely planned pre_review interface.

Before first product edit, confirm the adapter returns the needed identity,
validated observations/log bytes and current-set decision without a second
validator. After first final stable/drift composition, retain actual additions,
elapsed time and remaining coverage: more than 35 added integration lines or
6 elapsed minutes, or projected complete >80 additions/>24 minutes, means
stop/replan. Never borrow the pre_review allowance, silently shrink matrix,
raise 300/30 profile limits or reset review/repair accounting. The two-lane split
adds separate review/floor overhead; it is not an assertion of smaller total work.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

Planned locators, not completed evidence. Keep real Git state, owning metadata,
configured children, indexes/records/logs, shared decoder/schema/hash and set
predicate. Narrow storage/read faults and later model/network/publication
boundaries may be isolated; do not mock the acceptance seam itself.

```json
{
  "schema": "qa-mcp.card-evidence.v1",
  "conditions": [
    {"condition":"C1","seam":"final producer and retained role/per-command/aggregate gates","precondition":"genuine preverification/final owner fixtures and stable/silent, drift-restoration, nonzero/signal, missing/unsafe owner, spawn and interruption cases","action":"execute actual authorized final wrapper/verify fixture and inspect children, hashes, observed outcomes and caller status","expected":"only intact stable succeeds, drift/failure stops later commands, owner failure starts none; actual outcomes and aggregate/GO/manifest/prerequisite controls remain enforced","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_final_check_terminal_outcomes"},"stage":"implementation"},
    {"condition":"C2","seam":"final shared retention contract","precondition":"genuine terminal/running/silent final records with malformed/deep/duplicate/type/date/log and post-exit storage variants","action":"validate actual final records and inject narrow log/terminal publication failures","expected":"complete regular logs precede terminal success, every invalid/incomplete variant refuses, history survives and real observed outcomes remain disclosed","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_final_check_contract_and_retention"},"stage":"implementation"},
    {"condition":"C3","seam":"final ordered-set reuse and exact-byte pytest summary","precondition":"real complete final sets, missing/extra/reordered/duplicate/foreign/stale/failed/running proof, equal pre_review lists, unsafe owner/index/record/log paths and mixed malformed display","action":"exercise actual final matcher/verify/publish evidence gate and summary/receipt/metrics with outside-read and reopen sentinels","expected":"only exact owning final proof is authority; no preliminary unsafe read, lane merge, incidental parser crash or loaded execution; summary uses the same validated bytes and never fabricates output","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_final_check_set_and_safe_summary"},"stage":"implementation"},
    {"condition":"C4","seam":"real final composition and publication evidence rejection","precondition":"counted real final children, stable/drift/missing-log sets, saved history/card/index and valid/invalid publication prerequisites","action":"run producer through validation, aggregate, actual verify/reuse, summary/receipt/metrics and actual publish pre-action gate with only external actions isolated","expected":"intact reuse starts no child, damaged proof is no cache hit; old history preserved except allowed current alias; invalid publication evidence leaves card/index untouched and cannot reach mutation","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_final_check_composed_reuse_and_publish_gate"},"stage":"implementation"},
    {"condition":"C5","seam":"final history and delivered pre_review/focused/repair compatibility","precondition":"saved legacy/copied final indexes, delivered lane controls and actual changed-Python import repair fixture","action":"read history and exercise affected pre_review/focused/real-repair regression paths under final integration","expected":"no historical adoption or state/accounting rewrite; delivered lanes survive and intended changed-payload repair remains repair success only","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_final_check_legacy_and_lane_compatibility"},"stage":"implementation"},
    {"condition":"C6","seam":"sole contract and unchanged workflow/publication authority","precondition":"final scoped diff, Result/Log and existing role/finalizer guards","action":"inspect reuse of delivered adapters/schema/predicate and the publisher read-only evidence adapter; run relevant existing guards","expected":"no duplicate validator/executor, binding, single-flight, command/model/budget/role/floor or publisher transaction change, FIX-02/pilot enablement or publication","method":{"kind":"inspection","target":"scripts/changerail/local_delivery.py"},"stage":"review"}
  ],
  "risks": [
    {"kinds":["input_safety"],"applies":true,"decision":"Same safe owner/index/record/log decoder/validator before consumption, including publish preliminaries; final parsing consumes validated bytes without reopen.","conditions":["C2","C3"]},
    {"kinds":["mutation","restart"],"applies":true,"decision":"Per-command and aggregate endpoint proof, explicit incomplete outcomes, exclusive history and no adoption; publisher rejection is proven before state mutation.","conditions":["C1","C2","C4","C5"]},
    {"kinds":["concurrency"],"applies":true,"decision":"Exclusive attempt identity and complete unique references only; no single-flight, orphan cleanup or hostile-writer race guarantee until applicable separate work.","conditions":["C2","C3","C6"]},
    {"kinds":["publication"],"applies":true,"decision":"Validate final proof at the existing publisher gate before any board/Git mutation; preserve authority/transaction and keep FIX-02 disabled.","conditions":["C3","C4","C6"]},
    {"kinds":["external_effects"],"applies":true,"decision":"Only existing caller-configured argv executes in owned fixtures; all loaded prose is inert and later external publication effects are isolated.","conditions":["C1","C3","C4","C6"]}
  ]
}
```

Carry the complete applicable final-lane matrix, not just shared-schema unit
tests: valid controls, unknown fields/version, recursive escaped duplicates,
deep JSON, nonfinite numbers, boolean exits, invalid/non-UTC dates, negative
duration, running/silent/missing/tampered/truncated logs, nonzero/signal/spawn/
interruption and log/terminal-write/interruption faults after known exit.
Include wrong owner/card/attempt/lane/shell text/argv/payload and absolute/
traversal/symlink leaf/ancestor/nonregular owner/index/record/log paths. Require
read-order observations distinguishing open/fstat and content, FIFO zero-byte
log guard sensitivity, and a no-reopen sentinel for summary. Test legitimate
no-pytest/silent output separately from missing required pytest summary.

- Pin behavioral missing-log reuse and drift-before-later-restoration through the actual final caller, with stable and preserved aggregate-drift controls; retained checkpoint RED is diagnosis, not final-payload proof.
- Focused final: `uv run pytest -q tests/test_local_changerail_delivery.py -k 'configured_final_check or configured_pre_review_check or focused_check'`.
- Supporting boundaries: existing final verify fresh-preverification/changed-payload/changed-command-set/missing-prerequisite cases, `test_finalize_card_moves_once_without_rewriting_result_or_log`, handoff/role guards and the delivered real import-repair regression. Fake success at proof-requiring boundaries must be replaced with genuine sets, not new schema tags.
- After final Result/Log, retain focused evidence. Measured runner owns fast pre-review, fresh independent review and one frozen-payload post-GO floor: `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`, compilation and strict canonical specs. Ordinary offline completion is relevant checks/report without invented runner context or duplicate unchanged floor.
- `git diff --check`; `./bin/openspec validate --specs --strict --no-interactive` under the applicable completion boundary.

## Related

- `openspec/board/5.canceled/chrl-fix-03b1-retain-focused-check-proof.md`
- `openspec/board/5.canceled/chrl-fix-03c-serialize-verification-attempts.md`
- `openspec/board/5.canceled/chrl-fix-03d-bind-acceptance-to-observed-proof.md`
- `docs/development/local-changerail-delivery.md`

## Result

Implemented the authorized ordinary offline final-lane slice after the fresh
independent P assessment accepted C1-C6 and closed F1-F4. Final producer/reuse,
publisher's existing pre-action evidence gate, summary/receipt and metrics now
share the delivered receipt validator and complete ordered-set decision. A
private result carries the exact validated bytes into summary and receipt;
decoded mappings cannot certify success. Both configured producers explicitly
select their lane; the temporary legacy-final executor/matcher branch is gone.

C1/C2: actual configured children retain owning pre-launch identities and
terminal outcomes, including silent/nonzero/signal/interruption/storage cases.
Per-command drift stops a later restoring child; independent aggregate-drift
controls preserve the separate aggregate guard. C3/C4: ordered-set, schema,
identity, malformed/numeric/path/FIFO and historical-index controls exercise
real readers and policy. Summary tests run actual pytest in an owned fixture,
then forbid reopening; the actual publisher receives that same decision's
bytes. Publication refusal preserves disposable card/index/HEAD state, while a
valid control reaches only the isolated later finalizer boundary. Intact reuse
launches no child, damaged-log authorized rerun preserves earlier history, and
typed observations retain damaged and sibling rows without double-counting.

C5/C6: legacy final rows remain unconfirmed; focused/pre_review and real scoped
import-repair controls remain covered. No condition binding, single-flight,
additional schema/executor, publication transaction change or FIX-02 enablement
was added. The shared reader now also explicitly refuses absolute/traversal log
references. Necessary existing fixture-only adaptations in
`tests/test_changerail_qa_adaptation.py` replace unchecked summary mappings and
legacy preverification with real owning proof; their original bytes and reason
are retained in the separate scope-extension record.

Evidence root: `.runtime/changerail/offline-continue-fix03b2-WkKmHK/F/`.
`behavioral-red.log` retains both old final failures; intermediate integration
logs include diagnosed fixture iterations and the absolute-log regression, not
final green claims. `final-check.json` indexes focused/supporting/static evidence
after this Result/Log, exact scoped diffs, fingerprint and preservation checks.
Fault injection is confined to storage/read boundaries and downstream model/
publication boundaries; actual Git state, children, schema/hash/owner/ordered
set policy are not replaced with fabricated success.

The 2026-09-06 operator waiver makes the old numerical checkpoints informational;
estimates and prior attempts remain recorded, without claiming old limits were
met. Budget policy is a separate baseline, not part of F. This is offline
implementation evidence, not runner GO/READY, admission, a done dependency,
handoff, board transition, pilot, commit or push. Occupied project changes and
stopped-pilot evidence remain protected. Endpoint proof retains the stated
semantic/concurrency/environment limitations.

The first independent F review rejected one metric defect (F1, C3/C4): a
historical final index could reference a real pre_review receipt and count it
again as final, although current proof was correctly refused. The repair is
limited to identity-scoped observation salvage: foreign lane/run/card/attempt
and out-of-run references no longer contribute final observations. Real focused
and pre_review references, four foreign-identity/path variants, repeated-text
distinct final invocations and missing/tampered-own-log sibling controls now
assert exact count/duration preservation and unchanged retained history.
The derived `metrics.json` report remains explicitly regenerated, not execution
history. Finding-specific confirmation: 10 passed. Original F review/evidence
remain intact; repair snapshot, RED/green iterations and frozen final checks
are retained separately at
`.runtime/changerail/offline-continue-fix03b2-WkKmHK/F2/`.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-03b2f-deliver-final-proof-and-safe-consumption`

### Why

Pre_review proof cannot authenticate equal-list final success or make the old
final-log reader safe; final reuse and publisher evidence must switch together.

### Goal

Require complete intact final proof and exact validated log bytes at every
final success/reuse/report/admission consumer, retaining existing authority.

### Scope

Only this card's final-lane caller/consumer adapters, fixtures and contracts.

### Ordered Tasks

1. Preserve occupied/retained state, inspect the delivered 03B2-P interface and reuse its exact invariant/fixtures. Pin final missing-log and drift RED, full caller inventory including publish and planned selectors; confirm <=80 added lines/24 minutes before edits, or stop/replan without a second validator.
2. Activate final producer with explicit lane and real outcome/aggregate guards, adapting final reuse together. Verify real stable/silent/drift composition. CHECKPOINT: <=35 integration additions/6 elapsed minutes and credible remaining full scope; do not hand off this partial switch.
3. Integrate publisher's pre-action proof gate, exact-byte summary/receipt and final metrics using the same validated set. Prove C2-C4 malformed/identity/path/FIFO/no-reopen/composed controls and actual before/after rejection state; isolate only later external effects.
4. Prove C5 legacy/history and delivered pre_review/focused/actual-repair compatibility plus C6 unchanged authority. Confirm full delta/time and remaining review/floor allowance, without moving missing work to another card.
5. Update final canonical contract/runbook and Result/Log, retain final focused evidence and use only the separately authorized completion boundary. Do not finalize/publish the occupied project or resume the stopped pilot.

### Acceptance

- C1-C6 have complete final-lane observations, including exact-byte parsing and publisher's existing evidence gate; no aggregate completion is inferred from planning or counts.

### Depends On

- none

## Log

- 2026-09-06T16:39:17Z Created the operator-approved final end-to-end successor dependent on actual 03B2-P, with preserved C1-C6/Verify, explicit safe-summary/publisher-read scope and provisional 80-line/24-minute budget plus early integration checkpoint. Planning only; no product edits, admission, implementation, model review, pilot or publication.
- 2026-09-06T19:28:43Z Completed authorized offline final producer/consumer integration on independently accepted P, retaining real missing-log/drift RED, exact-byte pytest/publisher controls, malformed and nonregular path coverage, history/metrics and adjacent-lane compatibility. Final Result/Log precede the retained focused/supporting/static evidence. Numerical budgets are informational by explicit operator policy; scope, independent review, safety and publication authority remain unchanged. No project publication, board move, FIX-02 enablement or pilot execution.
- 2026-09-06T19:42:34Z Repaired independent F review F1 without additional permission: foreign receipt references cannot relabel/double-count final work. Retained six behavioral RED cases; 10 finding-specific and own-log preservation controls pass after the repair. Prior assessment and evidence were not overwritten; F2 holds the separate repair baseline and final checks. Scope, historical accounting, publication and pilot restrictions are unchanged.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

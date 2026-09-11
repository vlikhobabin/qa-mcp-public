# Retain complete pre-review proof without changing deliberate repair

## Status

5.canceled

## Owner

qa-mcp

## Series

chrl-fix-03b2p

## Order Index

406.22221

## OpenSpec Stage

operator-planned lane successor; Tasks/Verify drafted; not admitted or implemented

## Priority

P1

## Source

- `openspec/board/5.canceled/chrl-fix-03b2-retain-configured-verification-proof.md`: preserved aggregate C1-C6; operator approved the pre_review/final split.
- `.runtime/changerail/offline-checkpoint-fix03b2-knAAuZ/checkpoint-report.md`: actual interface/caller inventory and behavioral RED, not passing implementation evidence.
- `.runtime/changerail/offline-rereview-fix03b1-4x0gJ2/assessment.json`: independently accepted offline focused interface; not a done dependency or runner GO.

## Summary

Deliver one complete pre_review current-proof boundary: actual configured
commands, retained attempts, all preverification guards/reuse and compatible
metrics, while deliberate import repair can still change payload successfully.
Shared adaptations ship only with this working lane. Final proof and final-log
parsing remain the separate 03B2-F boundary, not implicitly completed here.

## Acceptance

### Requirement: Retain real pre-review execution in the sole shared contract

#### Scenario: A pre-review command completes or fails

- [C1] WHEN an authorized pre_review command starts, THEN actual owning run/card, unique invocation, explicit lane, exact configured shell text AND actual shell argv, UTC start and before-payload are retained before launch. Terminal proof uses the existing qa-mcp.check-result.v1 schema/validator and records actual exit/signal or explicit spawn/interruption/unknown outcome, UTC finish, finite nonnegative duration and after-payload separately from verification verdict. Stable/silent zero exits succeed; per-command drift, incomplete execution or retention fails to the caller and stops later commands, including one that could restore the original payload. Missing/unsafe owner refuses before launch. Preserve the aggregate start/end comparison independently.
- [C2] AND attempts use exclusive run/cycle-owned paths outside focused-evidence, complete regular size/SHA-256-bound logs and terminal-after-log atomic publication without overwriting history. Running-only, malformed/unknown/duplicate-key/deep records, bad terminal types/dates/durations and missing/tampered/truncated logs cannot establish success; a genuine silent zero-byte log can. Storage failures retain the real observed outcome in writable failure evidence or diagnostics, never forge exit zero/current success.

### Requirement: Switch the whole pre-review producer-to-consumer boundary

#### Scenario: A preverification guard, reuse caller or metrics reads a set

- [C3] WHEN preverify, its shared successful-preverification guard (including handoff/review/final-verification callers), the pre_review reuse matcher or pre_review metrics consumes evidence, THEN actual owner/index/record/log bytes are read component-wise no-follow as regular bounded files before consumption, including preliminary and repeated reads. One aggregate completeness predicate uses the sole receipt validator to require the exact complete ordered configured sequence, unique attempt references, owning run/card, explicit pre_review lane, exact shell identities and one current frozen payload. Missing/extra/reordered/duplicated/foreign/stale/failed/running proof refuses reuse; equal command lists never merge lanes. Aggregate booleans/exit lists and previously decoded untrusted mappings are not authority. Invalid observations remain safe/unconfirmed, with no accidental decoder/type/sort exception or loaded-command execution.
- [C4] AND an unchanged intact set reuses with no second child; invalid proof is no cache hit and only an existing authorized entrypoint may allocate a new set. Historical cycle indexes, records and logs remain byte-identical; only the existing current-index alias may advance to a newly retained set. Real producer -> schema/hash -> wrapper -> aggregate -> actual guard/reuse -> metrics compose for stable/silent, drift and missing-log cases. Metrics retain command/exit/duration/time observations, do not independently certify proof, and do not count configured attempts as focused evidence.

### Requirement: Preserve repair, history and untouched lanes

#### Scenario: Legacy evidence or deliberate import repair is used

- [C5] WHEN legacy/carried preverification evidence or a deliberately authorized import repair is used, THEN history remains historical/unconfirmed without rewrite, cross-run adoption or changes to manifests, counters, recovery eligibility, contexts, verdicts or old runs. A real existing safe import repair on changed in-scope Python files may exit zero with changed payload and remains repair success, but is never unchanged verification proof. Keep the general shell helper's intentional-change contract; prove real before/action/after source bytes and unchanged excluded files, not a stub that merely edits the fixture.
- [C6] AND focused proof remains compatible; no duplicate receipt schema/validator, new executor/framework/dependency, loaded-plan execution, condition mapping, single-flight, changed configured command source/model/budget/role/floor ownership, FIX-02 enablement, pilot or publication is introduced. Final-lane producer/reuse/summary/metrics behavior is not migrated or claimed current by this card; only its use of the strengthened preverification prerequisite may change. Offline completion is relevant checks/report, not fabricated handoff/GO. Endpoint proof does not claim semantic adequacy, transient edit/revert detection inside one child, hostile-writer resistance or environment reproducibility.

## Scope

- `scripts/changerail/local_delivery.py`: a narrow backward-compatible shared allocation destination and configured observation adapter; explicit opt-in by preverify to the existing `_run_full_floor`; pre_review set completeness and `_successful_verification_matches` adapter; `require_current_successful_preverification`, preliminary owner/index reads, pre_review `deterministic_commands`/metrics projections, necessary safe index compatibility in `run_safe_handoff_repair` only.
- `tests/test_local_changerail_delivery.py`: genuine pre_review owner/producer/index/guard/metrics and import-repair fixtures; adapt fabricated success only at proof-requiring boundaries; retain focused and untouched-final controls.
- `openspec/specs/changerail-consumer-wiring/spec.md`, `docs/development/local-changerail-delivery.md` and this card's Result/Log during separately authorized implementation.
- Reuse `tools/changerail/schemas/check-result.schema.json` unchanged and the existing safe reader/validator. An incompatible schema/interface requiring more than the narrow adapter triggers replan, not a parallel contract.

## Non-Goals

- Final configured producer/reuse, publisher final-evidence adapter, pytest summary and final metrics: 03B2-F. Do not alter publisher Git steps or authority here.
- A separately delivered shared core, global JSON/recovery-source hardening, generic executor/config framework, automatic migration/adoption/cleanup or arbitrary record-text execution.
- 03C single-flight/parent-loss policy, 03D condition binding, FIX-02 finalization, live/provider/admin/Windows work or Git publication.

## Affected Capabilities

- `changerail-consumer-wiring`

## Depends On

- `openspec/board/5.canceled/chrl-fix-03b1-retain-focused-check-proof.md`

Use its actual accepted local interface. Offline acceptance is not a literal
done path, eligible clean main or permission to run delivery. Follow actual
board transitions; never depend on the superseded 03B2 aggregate as done.

## Change Set

- `chrl-fix-03b2p-deliver-pre-review-proof-boundary`

## Design

Reuse the delivered owner reader, receipt schema, record/log writer and safe
validator, including depth normalization and regular-file-before-read checks.
Give shared allocation a narrow caller-supplied run-local destination while
preserving the default focused path. New pre_review attempts must not leak into
focused summaries or be double-counted. Keep the existing subprocess executor;
add only the observation/retention adapter needed by configured verification.
Bind exactly the actual shell argv plus text before launch, never read a command
from a receipt for execution. Do not infer lane from path or command-list equality.

Activate new proof explicitly from preverify; final callers keep the existing
legacy behavior until 03B2-F. If a shared signature changes, give that untouched
caller a minimal explicit compatibility path, not a second executor or a
lane-guessing heuristic. The final successor removes this migration seam when
it activates final proof. This card is a usable end-to-end pre_review lane,
not a claim that all configured evidence is fixed during the interim.

Use one aggregate completeness predicate, with safe input bytes and explicit
run/card/lane/configured sequence, calling the sole receipt validator for each
unique ordered reference. Return validated observations/bytes for consumers;
do not build a second receipt structural validator. Repeated configured text
may occupy distinct authorized positions, but one attempt cannot fill two
positions. Retain aggregate before/after equality AND per-command equality;
stop on the first unconfirmed command so a later command cannot hide drift.

Audit every preverification read before the final predicate, including owner
reads, handoff/review/final prerequisite paths and repeated import-repair index
reads. No safe-preflight followed by unsafe reopen. Safely typed legacy display
is not proof; malformed fields cannot crash metrics. The unchanged final lane
must not accidentally enter this predicate merely because lists match.

Keep intentional import repair outside verification-specific drift success.
Use the real existing repair command in an owned fixture, with retained changed
Python bytes, excluded files and observed exit. Missing repair executable is
a concrete verification gap to resolve, not permission to substitute a fake
success producer. Narrow fault/read sentinels and model/network/publication
boundary stubs are allowed; real subprocess/schema/hash/ordered-set policy is not mocked.

## Delivery Budget

- primary_invariant: Every pre_review current-success/reuse claim requires intact ordered owning proof without breaking deliberate repair or focused evidence.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 1
- estimated_production_loc: 150

## Budget Notes

Candidate 110-150 added production lines, not net of deletions: narrow
allocation/outcome adapter 35-50, set/guard integration 45-60, metrics/repair
compatibility 30-40. Reuse the 03B1 schema; tests/docs are additional reviewed
effort. Approximate total 27-30 minutes: 2 inventory/RED reuse, 5 adapter,
6 full consumer integration, 8 real matrices/repair, 2 docs/static,
4-5 fresh review and 1-2 floor. This tight estimate is provisional, not READY.

Before product edits, confirm actual interface, genuine repair executable and
remaining complete test/review/floor allowance. Before activating the producer,
retain adapter/focused-control evidence, added lines and elapsed time: adapter
above 65 additions or 8 elapsed minutes, or projected total above 150 additions
or 30 minutes, means stop/replan. Never ship just the adapter, shrink tests,
raise profile ceilings or reset clocks after repair/review. All related earlier
03B1/03B2 work remains recorded; the approved split is not a retrospective
claim that the original 25-minute aggregate succeeded.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

These are planned locators, not existing/passing tests. Use actual temporary
Git repositories, run/card metadata, controlled children and retained
record/index/log bytes, shared schema/hash checks and real callers.

```json
{
  "schema": "qa-mcp.card-evidence.v1",
  "conditions": [
    {"condition":"C1","seam":"pre_review producer and per-command/aggregate drift gates","precondition":"real owner plus stable/silent, drift then restoration, nonzero/signal, missing/unsafe owner, spawn and interruption variants","action":"run actual configured pre_review entrypoint and inspect child count, before/after bytes, outcomes and caller status","expected":"stable succeeds; failure/drift stops later commands with actual outcome retained, missing owner launches nothing and independent aggregate drift control remains active","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_pre_review_check_terminal_outcomes"},"stage":"implementation"},
    {"condition":"C2","seam":"exclusive allocation and shared retention contract","precondition":"genuine running/terminal/silent attempts plus malformed/deep/duplicate/type/date/log/storage variants","action":"validate produced attempts and inject narrow log/terminal-write faults after known exits","expected":"only complete intact proof succeeds; silent regular zero-byte log is valid; attempts/history are not overwritten and failed retention exposes real outcome without success","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_pre_review_check_contract_and_retention"},"stage":"implementation"},
    {"condition":"C3","seam":"all preverification guards and safe ordered-set validation","precondition":"real complete index and missing/extra/reordered/duplicate/foreign/stale/running/failed references, equal lane lists, unsafe owner/index/record/log and deep mixed observations","action":"exercise actual preverify, shared handoff/review/final prerequisites, matcher and metrics with read-order sentinels","expected":"only exact owning pre_review proof reuses; unsafe content is not read before refusal, loaded text never executes and malformed observations do not crash consumers","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_pre_review_check_set_and_safe_reads"},"stage":"implementation"},
    {"condition":"C4","seam":"real pre_review producer-to-reuse/metrics composition","precondition":"counted real children, stable/drift/missing-log states, old cycle/record/log bytes and focused controls","action":"run producer, validator, wrapper, aggregate, actual guard/reuse and metrics; reexecute invalid proof only via authorized fixture caller","expected":"intact reuse launches no child; damaged proof is not a cache hit; old history stays identical except advancing current alias, metrics stay compatible and no focused double-count occurs","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_pre_review_check_composed_reuse"},"stage":"implementation"},
    {"condition":"C5","seam":"legacy/carried observations and actual intentional import repair","precondition":"saved historical/copy fixtures plus changed in-scope Python imports and excluded files","action":"read history and execute real existing safe import repair with actual subprocess, source bytes and payload hashes","expected":"no upgrade/history/accounting mutation; intended changed-payload exit zero remains repair success only, changed-file scope is enforced and excluded files survive","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_pre_review_check_legacy_and_deliberate_repair"},"stage":"implementation"},
    {"condition":"C6","seam":"focused and untouched-final compatibility, scope/authority","precondition":"final Result/Log and scoped diff with delivered focused and existing final/role guard controls","action":"inspect sole validator/executor use and run relevant unchanged-lane/role guards","expected":"only pre_review proof is activated; focused and legacy final behavior survive, no new authority or configured command source and no full-parent completion claim","method":{"kind":"inspection","target":"scripts/changerail/local_delivery.py"},"stage":"review"}
  ],
  "risks": [
    {"kinds":["input_safety"],"applies":true,"decision":"Shared bounded no-follow regular reader before preliminary/repeated owner/index/record/log use; sole schema plus ordered-set semantics, inert command observations.","conditions":["C2","C3"]},
    {"kinds":["mutation","restart"],"applies":true,"decision":"Pre-launch identity, actual outcomes, per-command and aggregate hashes, immutable history; intentional repair remains separate and incomplete/carried proof never upgrades.","conditions":["C1","C2","C4","C5"]},
    {"kinds":["concurrency"],"applies":true,"decision":"Exclusive attempt paths only; no single-flight, parent-loss recovery or automatic orphan cleanup until 03C.","conditions":["C2","C6"]},
    {"kinds":["publication"],"applies":true,"decision":"Existing preverification prerequisites become proof-backed without changing role/floor/publisher authority; no final proof or FIX-02 enablement.","conditions":["C3","C6"]},
    {"kinds":["external_effects"],"applies":true,"decision":"Execute only caller-configured commands or existing scoped import repair in owned offline fixtures; receipt/plan text remains inert.","conditions":["C1","C3","C5","C6"]}
  ]
}
```

Mandatory matrix: valid controls accompany unknown schema/fields, recursive
escaped duplicate keys, nonfinite numbers, boolean exits, invalid/non-UTC dates,
negative duration and deep JSON. Include running-only, silent-empty, missing/
tampered/truncated log, actual nonzero/signal/spawn/interruption, log-write and
terminal-write/interruption faults after known exits. Check wrong run/card/
attempt/lane/argv/shell/payload and absolute/traversal/symlink leaf/ancestor/
nonregular owner/index/record/log paths. Read sentinels must distinguish open/
fstat from content reads; include FIFO empty-log and guard-sensitive negative
controls. Keep the decoder/schema/hash/I/O real, not patched success.

Reuse the retained checkpoint RED as diagnosis where source hashes match;
pin permanent behavioral missing-log and per-command drift regressions before
new-field assertions. Port real state observations, not baseline-only expected
bugs. All C1-C6 require acceptance evidence; no test-count substitute.

- Focused final: `uv run pytest -q tests/test_local_changerail_delivery.py -k 'configured_pre_review_check or focused_check'`.
- Supporting selectors from the retained inventory: `test_implementation_handoff_freezes_current_preverified_manifest`, `test_implementation_handoff_retries_after_safe_deterministic_repair`, `test_safe_handoff_repair_is_scoped_to_changed_python_imports`, `test_final_verify_runs_final_floor_once_after_matching_preverification`, `test_final_verify_fails_closed_after_payload_change`, `test_final_verify_fails_closed_for_changed_verification_command_set`, `test_final_verify_fails_closed_without_preverification`. Keep their assertions; fabricated success is not the acceptance fixture.
- Record focused evidence after final Result/Log edits. In measured delivery, runner owns fast pre-review, fresh review and one frozen-payload final floor: `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`, compilation, strict canonical specs. Ordinary authorized offline work ends with relevant checks/report; no invented runner context or duplicate unchanged floor.
- `git diff --check`; `./bin/openspec validate --specs --strict --no-interactive` under the applicable completion boundary.

## Related

- `openspec/board/5.canceled/chrl-fix-03b2f-retain-final-verification-proof.md`
- `openspec/board/5.canceled/chrl-fix-03c-serialize-verification-attempts.md`
- `openspec/board/5.canceled/chrl-fix-03d-bind-acceptance-to-observed-proof.md`
- `docs/development/local-changerail-delivery.md`

## Result

Authorized ordinary offline implementation candidate now connects pre_review
execution, exclusive cycle receipts, ordered current-proof reuse/prerequisites
and safe unconfirmed metrics through the existing shared validator. Per-command
drift stops later children; aggregate drift remains independently checked.
Deliberate import repair retains changed-payload success. Focused behavior and
the legacy final producer/reuse/summary remain separate and unchanged in scope.

The retained adapter checkpoint contains 53 added production lines at 370.44
elapsed seconds and 92 passing primitive/focused controls. Permanent behavioral
regressions first failed on missing-log reuse and drift-restoration, then passed.
Real configured shell/silent/nonzero/signal, malformed records, ordered sets,
symlink/FIFO read sentinels, immutable cycle history and actual import repair
have focused evidence; only narrow fault injection and existing model/publication
boundaries are substituted. Shared schema, protected history and unrelated
payload are preserved. Candidate/final checks, scoped diffs, timing and any
independent offline assessment are retained under
`.runtime/changerail/offline-impl-fix03b2p-HRkCVW/`.

This Result is not a runner GO, done dependency, clean admission, full-parent
completion or publication receipt. Final lane work remains 03B2-F and requires
a usable accepted P interface; no pilot, finalizer, board move or commit/push
was executed by this implementation.

The completed independent offline assessment in
`.runtime/changerail/offline-continue-fix03b2-WkKmHK/prior-review-completion/`
identified F1-F4. The repair candidate closes their exact boundaries: safe
preliminary/repeated owner reads at actual final/review prerequisites; per-row
display-only metrics retaining damaged-proof observations and intact siblings;
finite nonnegative overflow-safe legacy duration conversion; and an independent
aggregate-drift control with genuine stable per-command receipts. All 20 new
finding-specific cases pass after 8 intended RED failures and 12 controls.
Final scoped diffs/checks and the subsequent assessment are retained under
`.runtime/changerail/offline-continue-fix03b2-WkKmHK/P/`.

The user's 2026-09-06 removal of numerical budget stops is recorded separately
in AGENTS/profile and the `budget-policy/` sibling evidence. Earlier P estimates,
attempts and actual overruns remain historical; this repair does not assert
that the original 150-line/30-minute estimate was met. Scope, the existing sole
receipt schema, authority and final-lane exclusions remain intact.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-03b2p-deliver-pre-review-proof-boundary`

### Why

Preverification currently reuses missing-log success and misses drift restored
by a later command; focused proof alone does not close those callers.

### Goal

Make pre_review success/reuse depend on intact actual owning proof while
preserving deliberate import repair and focused/untouched-final behavior.

### Scope

Only the narrow shared adaptations and this card's entire pre_review boundary.

### Ordered Tasks

1. Preserve baseline/history, use retained source/caller inventory, pin genuine missing-log and per-command drift assertions and actual repair availability. Confirm the complete 150-line/30-minute candidate before product edits; stop/replan if not credible.
2. Extend allocation and configured outcome retention narrowly, retaining focused defaults and explicit lane/invocation. Verify real shell/silent/drift/fault and focused controls before activation. CHECKPOINT: adapter <=65 added lines/8 elapsed minutes, with full remaining integration/tests/docs/review/floor still fitting. No core-only handoff.
3. Activate pre_review producer and ALL preverification guards/reuse/metrics together, using one safe ordered-set predicate and preserving aggregate drift. Keep final legacy path explicit. Pass real C1-C4 composition and malformed/path/FIFO/read-order cases before continuing.
4. Prove C5 real import repair and history/scope preservation plus C6 focused/untouched-final/authority controls. Confirm actual total size/time and remaining verification allowance; do not move missing pre_review work into 03B2-F.
5. Update pre_review canonical contract/runbook and Result/Log, retain final focused evidence, then use only the separately authorized completion boundary. No final-lane implementation, pilot or publication as a side effect.

### Acceptance

- C1-C6 have observable pre_review assertions and complete mapped verification; final-lane obligations are explicitly retained in the dependent successor.

### Depends On

- none

## Log

- 2026-09-06T16:39:17Z Created the operator-approved pre_review end-to-end successor of 03B2 with C1-C6/Verify, real repair compatibility, explicit interim final-lane boundary and a provisional 150-line/30-minute budget plus early adapter checkpoint. Planning only; no product edits, admission, implementation, model review, pilot or publication.
- 2026-09-06T17:26:08Z Retained adapter checkpoint before producer activation: 53 added production lines, 370.44 elapsed seconds; 92 primitive/focused checks passed. Original tree matched the planning fingerprint and 3976 protected paths remained unchanged; actual Ruff 0.15.20 was available.
- 2026-09-06T19:04:33Z Repaired completed offline review F1-F4 with 20 finding-specific passing cases, including actual prerequisite read sentinels, damaged-log sibling preservation, real malformed historical numeric rows and independent aggregate drift. Prior attempts/accounting are preserved; numerical stops were separately disabled by the operator, not silently reset. No publication, pilot or final-lane implementation.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

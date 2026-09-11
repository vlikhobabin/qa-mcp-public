# Bind required acceptance conditions to observed proof

## Status

5.canceled

## Owner

qa-mcp

## Series

chrl-fix-03d

## Order Index

406.224

## OpenSpec Stage

operator-refined board-only plan; two coherent Change checkpoints; not admitted or authorized for implementation

## Priority

P1

## Source

- `openspec/board/5.canceled/chrl-fix-03-persist-and-enforce-card-evidence-contract.md`
- `implementation_handoff` currently checks preverification, not one observation per implementation-stage condition. `validate_verdict` enforces scenario coverage but accepts arbitrary nonempty evidence strings.
- A result receipt proves execution identity/completion, not semantic adequacy or that the declared test actually covers a condition.

## Summary

Use one namespaced condition/proof inventory at the appropriate implementation,
review and final boundary. Keep semantic adequacy with the independent reviewer.
One card now owns the complete invariant through two ordered Change checkpoints.
The earlier successor proposal is preserved in Design and Log; the decision to
keep these checkpoints together follows the actual common inventory, version
selection and consumers, not the removal of numerical limits. Implementation
requires separate authorization; the parent 03 aggregate stays non-executable.

## Acceptance

### Requirement: Connect implementation-stage observations to the current plan

#### Scenario: An implementation requests handoff
- [C1] WHEN handoff evaluates a current versioned card, THEN each implementation-stage condition has an observation bound to source-card path/hash, condition ID, declared method/locator, current payload and a valid terminal execution receipt or typed inspection/runtime artifact. Missing, duplicate, foreign, stale, planned-only or failed proof refuses. Future review/final evidence is not demanded at handoff.

### Requirement: Use the same inventory at later gates

#### Scenario: The independent reviewer and outer runner consume proof
- [C2] WHEN context, verdict template and validator enumerate required proof, THEN they derive identical namespaced conditions and scenario grouping, reject missing/duplicate/foreign references and preserve per-clause coverage. An explicitly authorized additional plan may join only after its owning caller proves adoption; this work does not implement that authority.
- [C3] AND GO requires meaningful reviewed observations, not merely a nonempty string, while final-stage proof remains pending until the outer runner supplies its actual configured floor and enforces those references before publication. Neither a claim of passing tests nor a receipt's zero exit automatically proves a test's relevance, risk N/A credibility or complete clause coverage.

### Requirement: Activate new evidence rules without rewriting old authority

#### Scenario: New runs coexist with exact retained legacy work
- [C4] WHEN the new proof contract is activated, THEN its version/required stages are bound at new-run creation and cannot be downgraded by a caller flag or missing field. Exact legacy records retain their recorded contract/accounting; migration requires explicit scope and invalidates affected proof, never rewriting original records. Ordinary offline reports remain possible without fabricated handoff/GO, and FIX-01/FIX-02 gain no admission, adoption or publication authority.

## Scope

Future implementation scope (no implementation in this planning pass):

- `scripts/changerail/local_delivery.py`: one derived inventory, typed proof
  reader/recorder, activation selection, handoff, context/template/verdict,
  final verification and the existing pre-mutation publisher evidence gate.
- Proposed `tools/changerail/schemas/card-proof.schema.json` and
  `tools/changerail/schemas/review-verdict-v2.schema.json`. Preserve existing
  `review-verdict.schema.json` as the exact v1 compatibility contract; neither
  the plan-only nor check-result schema changes its meaning.
- Proposed `tests/test_local_changerail_observed_proof.py` for C1-C4 fixtures;
  extend `tests/test_local_changerail_delivery.py` only where existing composed
  handoff/final/recovery fixtures are needed. No broad fixture-link repair.
- During implementation synchronize `openspec/specs/changerail-consumer-wiring/spec.md`,
  `docs/development/local-changerail-delivery.md`, `openspec/board/README.md`,
  and the source deliver/review skills under `tools/changerail/skills/` with
  these role-specific proof obligations. No new policy checklist in AGENTS,
  profile change, generic helper module or new FF lifecycle.

## Non-Goals

- Reimplementing 03B receipts or 03C process coordination; executing arbitrary plan locators; semantic classifiers; a new workflow engine or percentage threshold.
- Implicit bootstrap/additional-plan adoption, finalizer repair or publisher crash recovery; these remain FIX-02's independent authority/workflow problem.
- Treating a declared test locator as proof that a command selected it. Reviewer comparison of actual invocation/output with the method is still required.
- Authenticating a hostile same-user writer or proving transient edit/revert,
  every test framework, live runtime behavior or environment reproducibility.
  v1 test observations use retained pytest node results; unsupported output is
  unconfirmed with a concrete diagnostic, never silently treated as inspection.
- Repairing the 27 test-fixture board-reference findings or enabling either
  offline-finalization mode. No real model, native 1C, commit/push or pilot is
  needed to exercise this card's offline fixtures.

## Affected Capabilities

- `changerail-consumer-wiring`

## Depends On

- `openspec/board/5.canceled/chrl-fix-03a-validate-evidence-plans-before-admission.md`
- `openspec/board/5.canceled/chrl-fix-03b1-retain-focused-check-proof.md`
- `openspec/board/5.canceled/chrl-fix-03b2f-retain-final-verification-proof.md`
- `openspec/board/5.canceled/chrl-fix-03c-serialize-verification-attempts.md`

03B2-F transitively requires 03B2-P and 03B1. Neither the superseded 03B2
aggregate nor a planning/offline report is a literal done dependency. This
03D plan uses the accepted offline interfaces for separately authorized offline
work. A runner delivery still needs actual done dependencies and an eligible
checkout; this refinement changes neither dependency identities nor eligibility.

## Change Set

- `chrl-fix-03d-enforce-implementation-proof-inventory`
- `chrl-fix-03d-enforce-reviewed-and-final-proof-coverage`

## Design

### Boundary decision and retained sizing history

The 2026-09-06 SPLIT_REQUIRED proposal estimated 45 minutes/350 production-schema
lines and proposed (a) implementation inventory/activation and (b) reviewer/final
coverage/verdict compatibility. These are retained historical candidates, not
current sibling cards or a measured verdict. They could yield a deliberately
partial handoff-only feature, but that would require a second rollout contract:
the current run creation, scenario extractor and later consumers have no
separately versioned stage-inventory interface. This plan keeps one rollout and
all C1-C4 in one card; Change 1 establishes the shared interface and Change 2
completes its consumers before activation is usable. No checkpoint alone claims
card acceptance. The parent 03 aggregate and old 03B/03B2 remain non-executable.

### Actual interfaces inspected on 2026-09-07

| Existing seam | Actual guarantee or gap | Planned use |
| --- | --- | --- |
| `validate_evidence_plan_text`, `acceptance_condition_ids_text` | Closed plan, exact ID/risk coverage, inert locators; no observations | Read each source once and derive inventory from validated bytes |
| `acceptance_criteria` | Complete Requirement/Scenario review units, flat-bullet fallback; no ID-to-scenario map | Share grouping for context, v2 template and validator, including every C clause |
| `read_check_result`, `_check_bytes`, `_check_json` | Sole current receipt/log validator; bounded regular no-follow reads | Consume validated receipt and exact log bytes; extend typed observation validation only |
| `implementation_handoff`, `require_current_implementation_handoff` | Current preverify/manifest and fingerprint; no condition coverage | Require current implementation proof before handoff publication/reuse and revalidate on consumption |
| `build_review_context`, `verdict_template`, `validate_verdict` | Context alone reads `bootstrap_acceptance`; v1 template/validator enumerate only main card; evidence is nonempty strings | One authorized-source inventory and v2 typed references for all three consumers |
| `verification_attempt_lock`, `_run_full_floor`, `_verified_command_set` | 03C lock and 03B receipt/set validation through publication and reuse | Reuse them; do not add another executor, success reader or lock capability |
| `verify`, `publish`, `delivery_receipt_lines` | GO/preverify before final, complete final set before mutation/summary | Enforce final condition coverage on both execution and reuse, then revalidate before `finalize_card` |
| `run_delivery` and its recovery branch | Creates `qa-mcp.delivery-run.v1` before card movement; records no observation-contract selection | Pin new version at creation, bind current inventory after normal move/edits, select exact compatibility before writes |

### Single source, derived inventory and stage obligations

Keep `qa-mcp.card-evidence.v1` unchanged as the editable plan. Derive an inventory
from safe once-read source-card bytes; each key is `(repository-relative source
path, SHA-256 of complete source bytes, condition ID)`. Its derived fields are
scenario identity, declared method/locator and required stage. Run identity,
whole payload fingerprint and inventory digest bind each retained projection.
Acceptance prose may be displayed from those bytes but is never a second
editable requirement list. Recompute and compare at each gate; a cached inventory
is not permission to accept changed cards. Result/Log edits also change source
hashes: finish them before focused evidence, and refresh affected observations
after any later edit. The initial todo-to-inprogress move is likewise not a
permanent source-path pin; the contract version is fixed at creation, while the
inventory binds the current source path/hash at proof collection and handoff.

Every top-level condition belongs to exactly one complete scenario; flat cards
use their condition as the review unit. Reject ambiguous mixed grouping or
orphan clauses instead of dropping them. Separate sources may reuse C1, and
separate requirements may reuse scenario titles: their namespaced identities
remain distinct. Repeated ambiguous headings within the same source refuse.
Multiple proof items may support one condition, and one actual invocation may
support several conditions through distinct explicit mappings. Duplicate
condition rows or duplicate reference identities are errors; neither an array
length nor one scenario label proves all clauses.

| Gate and owner | Due proof | Future-stage behavior |
| --- | --- | --- |
| Implementation handoff | Every implementation condition, current preverify and existing manifest/checkpoints | Review/final are declared pending, never prerequisites for handoff |
| Independent review | Revalidated implementation observations plus reviewer-owned review-stage observations and per-condition semantic decisions | Final conditions are explicitly pending; reviewer assesses their planned mechanism and required future artifact without asserting an executed floor |
| Outer `verify` after GO | All earlier due references still current, configured final set and every final condition observation | A successful floor alone cannot fill unrelated condition rows |
| Publisher evidence gate | Revalidate complete inventory, reviewed decisions, all due observations and configured final proof for frozen bytes | Any missing/stale reference refuses before card move, staging or Git publication |

Final-stage test rows can map to actual node results from final receipts;
inspection/runtime rows must already have their separately authorized typed
artifacts for the outer validator to consume. `verify` never executes a static
locator or launches runtime work to fill an empty row. An inspection of the
floor can be derived from its validated command-set bytes; an unrelated artifact
cannot be synthesized from `exit_code=0`. Direct `_run_full_floor` remains a
check producer, not a substitute for `verify` or publisher acceptance.

### Closed observations and retention

Proposed `qa-mcp.card-proof.v1` is a separate closed observation document under
the owning ignored run directory. Common fields: schema, owning run/card,
inventory digest, current payload, namespaced condition, exact method and stage,
observation identity, recorder role, observation time, typed outcome and artifact
references (relative path, size, SHA-256, exact fragment locator where needed).
Unknown fields/kinds, duplicate JSON keys, missing identities, wrong types,
unsupported outcomes and absent observations refuse. Artifact roots and all path
components use the existing bounded regular no-follow access; require containment
in the owning run, reject traversal, symlinks, FIFOs, oversized/truncated content
and changed hashes. Read referenced bytes once per decision and carry validated
bytes onward, rather than reopen a pathname after validation.

| Kind | Required actual observation | Insufficient evidence |
| --- | --- | --- |
| `test` | Exact receipt path/hash, lane, attempt and command identity validated by `read_check_result`; selected pytest node IDs with terminal per-node outcomes and byte spans in that receipt's complete log; before/action/after references to inspected assertions for a stateful seam | `true`, silent exit zero, collection-only, skipped/deselected required node, unrelated passing node, summary count, invented node not present in the validated log |
| `inspection` | Hashed run-owned inspection record; observer/role, inspected source/artifact hashes and locators, observed before/action/after fragments and conclusion tied to the specific condition; explicit mocked seams and residual risks | A plan, an instruction to inspect, arbitrary prose or copied success string without resolvable observations |
| `runtime` | Hashed run-owned runtime record with existing authorization/preflight reference, target/session identity, observed before/action/after, expected-result markers and recovery/rerun or concrete non-applicability reference | Fixture output represented as native proof, a screenshot alone, unbound target, a runtime recipe or authorization inferred from the card method |

For v1 pytest proof, choose verbose node-result output in the existing focused
command or use already sufficient retained output. Parse only the documented
pytest result form from the validated receipt log; node identity must match the
declared selector or be within the declared test file. Parameterized instances
remain individual results. If configured output lacks those observations, report
unconfirmed and retain that outcome; this card does not silently alter configured
floor commands or accept aggregate counts. Any needed later command-policy
change requires its own explicit scope. Matching nodes proves selection, while
the reviewer still decides whether their assertions observe the claimed behavior.

Use a bounded `chrl proof record <artifact>` adapter for already-created typed
input, not another command launcher. It validates current inventory/role and
referenced bytes, retains an exclusive immutable observation record, and advances
only its owning current index after successful validation. Implementation may
record implementation rows, review its review rows, and the outer runner final
rows. Missing role is not implicit outer authority. Both handoff and every later
reader revalidate records, so an input document cannot self-certify by setting a
role/status field. A failed write leaves no accepted partial index; reattempts
retain prior records and never repair historical receipts in place. Proof-index
publication reuses 03C's run-local ownership boundary without nested acquisition;
this serializes this run's proof recording, not Git publication or other runs.

Offline reports may use the same inventory and observation shapes with an
explicit offline scope identity and owned artifact root. They are validated as
offline reports only, do not call measured `chrl proof record`, and cannot be
imported as run-owned proof. No fake `CHRL_RUN_DIR`, handoff or GO is required.

### Review version and additional-plan boundary

New runs select `qa-mcp.review-verdict.v2`. Preserve v1 schema and recorded
verdicts for exact legacy compatibility. V2 retains reviewer independence,
findings with operational repair scope, workspace and complete scenario decisions;
each decision includes all namespaced condition references and typed observation
identities. Final-only conditions use an explicit `pending_final` disposition,
not a fabricated pass. GO means all due observations and semantic review passed,
with only genuine final-stage obligations pending. NO-GO can record missing or
failed observations and concrete findings; structural validation must not make
an honest negative verdict impossible. Missing scenario/condition decisions,
duplicates, foreign references or arbitrary success evidence still refuse.

One shared inventory feeds context, template and validator, including compact
delta reviews: unchanged clauses may cite revalidated current proof but cannot
disappear because a diff omits their file. Reviewer explicitly assesses chosen
test relevance, actual before/after assertions, applicable risk N/A reasons,
mocked seams and every WHEN/THEN/AND clause. Do not encode semantic adequacy as a
keyword classifier or a magic `adequate=true` field. Typed integrity is necessary
but independent review is the semantic acceptance boundary.

Additional sources are absent by default. The inventory builder accepts only
an internal caller-validated source set bound to current run/payload and source
path/hash, not a request flag or `run.json.bootstrap_plan` mapping. There is no
production caller with new adoption authority in 03D: ordinary delivery refuses
unproved extras; the disabled finalizer stays disabled. A fixture-only caller
can supply the checked interface to test main/additional namespaces and complete
coverage. That positive fixture proves inventory composition only, not actual
finalizer adoption. CHRL-FIX-02 must separately implement and prove its authority
before connecting that caller. Do not broaden `_check_owner` or receipt ownership
to treat a receipt from another run as local proof.

### Activation, exact legacy and migration

`run_delivery` selects the new observation/verdict version and required-stage
policy before its first run metadata write/model call. Retain the selection in
the creation record and bind its digest in subsequent manifest/handoff/context
records; every consumer uses one selector. Do not pin the mutable initial card
bytes as the final inventory. A missing/unknown field, a false flag or a v1
verdict cannot downgrade a newly created run. A failed/partial creation record
cannot be reconstructed as a legacy run merely from its date or directory name.

Legacy selection requires existing exact retained recovery admission plus an
independently retained pre-activation identity of the original run metadata and
contract, manifest, card and baseline; version absence alone is insufficient.
Treat any allowed legacy source identities as explicit hash-bound migration
inputs, never wildcard/time-based exceptions or a user-supplied waiver. No real
legacy identity is admitted by this plan. Without that independently retained
anchor, refuse measured continuation with an explicit migration diagnostic while
allowing read-only/offline reporting. Exact legacy compatibility preserves its
old contract, not stronger proof claims or exemption from other current gates.

Explicitly authorized migration creates new versioned metadata and requires new
affected proof, while preserving original records, counters, attempts and verdicts
byte-for-byte. Use existing accounting inheritance; cross-run copied summaries
stay historical/unconfirmed even if product hashes match. This card defines and
tests selection/invalidation, not a new migration command or amended-payload
adoption route. Actual migration of OSS-FIX-01 remains CHRL-FIX-02's separate
scope and authority. Changing version metadata never enables finalizer modes.

### Risk mechanisms and observable controls

| Risk | Mechanism and C coverage | Positive and material negative observation |
| --- | --- | --- |
| `input_safety` | Closed shapes, safe contained reads, exact namespace/method/artifact identity; C1/C2/C4 | Valid references resolve; malformed/foreign/unsafe inputs refuse without reading an outside sentinel or creating accepted proof |
| `mutation` | Immutable observation attempts, current source/payload checks, atomic current-index advance; C1/C3/C4 | Authorized replacement advances only current index and preserves old bytes; corrupt proof or write failure leaves prior accepted index and card/index Git state unchanged |
| `restart` | Pinned activation, exact legacy selection, no implicit adoption; C1/C4 | Restart revalidates intact current proof and inherits accounting; missing creation field, interrupted proof write or stale legacy anchor refuses without rewriting originals |
| `concurrency` | Reuse 03C ownership for proof recording and existing verification lanes; C1/C3 | Real holder/contender demonstrates busy through proof-index publication; held verifier or unresolved invocation cannot be converted to accepted proof or a second child |
| `publication` | Final coverage on fresh and reuse branches, repeated pre-mutation evidence gate; C2/C3/C4 | Complete final references reach the fixture publisher boundary; missing/stale final proof preserves active-card bytes/location, staging and Git refs |
| `external_effects` | No locator execution, method/role checks and caller-owned adoption; C1/C2/C3/C4 | Offline composed controls use real local fixtures with fake model/native/network calls; hostile locator, fake runtime proof or unadmitted extra source causes zero external calls |

## Delivery Budget

- primary_invariant: Every required condition has stage-appropriate current proof rather than an unvalidated success string.
- expected_wall_minutes: 180
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 3
- estimated_production_loc: 800

## Budget Notes

Current planning estimate: about 450 owner/adapter lines plus 350 lines in two
executable schemas, three product files, one owner, no native runtime contour.
Two test files and five documentation/role-guidance paths add reviewed scope.
The 180 minutes estimates implementation, focused regression, independent review
and the applicable final floor; it is provisional, not a ceiling or claim of
measured usage. Original 45 minutes/350 lines (180 owner + 170 schema) remain
historical estimates, not a budget claimed met. Retain all actual attempts and
accounting during future authorized work. Scope/evidence/role gates still apply.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

Future proof obligations, not implemented tests or a GO declaration:
```json
{
  "schema":"qa-mcp.card-evidence.v1",
  "conditions":[
    {"condition":"C1","seam":"implementation handoff proof gate","precondition":"valid declared plan with valid, missing, stale and failed observations","action":"invoke real handoff inventory checks using retained fixture artifacts","expected":"only complete current implementation-stage proof passes without demanding future stages","method":{"kind":"test","target":"tests/test_local_changerail_observed_proof.py::test_observed_proof_handoff_coverage"},"stage":"implementation"},
    {"condition":"C2","seam":"shared context/template/verdict inventory","precondition":"main plan and explicitly caller-admitted additional-plan fixture plus reference corruptions","action":"derive inventory and validate fake-model verdict through real consumers","expected":"same namespaced conditions everywhere; omission, duplication, foreign and unadmitted plan references refuse","method":{"kind":"test","target":"tests/test_local_changerail_observed_proof.py::test_observed_proof_inventory_consistency"},"stage":"implementation"},
    {"condition":"C3","seam":"review and final evidence boundaries","precondition":"structured observations, an irrelevant zero-exit check and absent final proof","action":"inspect semantic review requirements and exercise actual stage/reference validators","expected":"receipt identity does not masquerade as test adequacy; final proof is enforced only at its outer-runner boundary","method":{"kind":"inspection","target":"scripts/changerail/local_delivery.py"},"stage":"review"},
    {"condition":"C4","seam":"run-version activation and legacy compatibility","precondition":"new run, exact retained legacy run and attempted downgrade/migration","action":"exercise real contract selection and negative identity fixtures","expected":"new-run requirements cannot be bypassed; old history/accounting remain exact and no new authority is inferred","method":{"kind":"test","target":"tests/test_local_changerail_observed_proof.py::test_observed_proof_rollout_preserves_authority"},"stage":"implementation"}
  ],
  "risks":[
    {"kinds":["input_safety","mutation","restart"],"applies":true,"decision":"Closed source/condition/receipt identity, pinned run contract and explicit migration preserve old bytes and reject stale/foreign proof.","conditions":["C1","C2","C4"]},
    {"kinds":["concurrency"],"applies":true,"decision":"Consume 03C serialized execution and terminal 03B results; no duplicate executor or inferred completion.","conditions":["C1","C3"]},
    {"kinds":["publication","external_effects"],"applies":true,"decision":"Stage-specific proof consumption never grants execution, additional-plan adoption or Git authority; fixture external/model calls remain fake.","conditions":["C2","C3","C4"]}
  ]
}
```

### Planned scenario matrix (no results claimed)

All new test locators below are proposed, not files/tests reported as existing.
The C3 Verify row is reviewer-owned inspection of actual implementation and
test assertions; its supporting mechanical tests below run at implementation.
This distinguishes when 03D itself is reviewed from the stages it enforces for
future cards. Runtime-kind fixtures validate artifact integrity offline and
cannot establish native execution or runtime permission.

| Case / conditions | Positive control | Material negative control and before/after oracle | Real and mocked seams |
| --- | --- | --- | --- |
| `test_observed_proof_handoff_coverage` / C1 | Real pytest child and receipt, complete implementation observations; handoff created with review/final pending | Remove/duplicate a row, change source hash/ID/method/stage/payload or use failed/planned-only proof: no new accepted handoff/history; retain prior handoff bytes | Real plan parser, safe reader, receipt producer/reader, inventory and handoff; isolated repository/profile, no model |
| `test_observed_proof_typed_artifacts` / C1/C3 | Each closed test/inspection/runtime fixture resolves exact observed fragments; selected parameterized node outcomes pass | Silent `true`, wrong node, collection/skips/count-only log, instruction-only inspection, wrong target/preflight, absent before/action/after refuse; existing artifacts unchanged | Real log parsing, schemas, hashes and fragment checks; runtime provider itself fake and marked fixture-only |
| `test_observed_proof_safe_retention` / C1/C4 | Exclusive observation retention followed by current-index replacement; prior records retain hashes | Leaf/ancestor link, traversal, FIFO, oversize/truncation, duplicate keys, corrupt log or failed index publication: no outside sentinel read, no accepted partial index; retry appends, never overwrites | Real bounded no-follow readers, filesystem and atomic writes; injected write failure delegates all other operations |
| `test_observed_proof_inventory_consistency` / C2 | Main + fixture-authorized additional source both contain C1 and shared scenario names; identical complete inventory in all three consumers, including flat/delta cases | Unadmitted extra, stale source, ambiguous grouping, missing clause/scenario, duplicate/foreign proof references refuse; context cannot add a source absent from template/validator | Real extraction/context/template/verdict; fake model output and explicitly fake adoption caller, no finalizer authority |
| `test_observed_proof_review_and_final_gates` / C2/C3 | Current implementation/review observations produce GO with explicit pending final; real configured receipt then completes final coverage; valid reuse launches no child | Nonempty-string GO, premature final pass, failed review row, wrong-lane/stale/missing final proof on fresh and reuse branches refuse; prior receipts/cycles unchanged; honest NO-GO remains writable | Real validators, `verify`, `_run_full_floor`, command-set reader; local harmless configured commands, synthetic reviewer identity only |
| `test_observed_proof_publish_preserves_state` / C3/C4 | Complete frozen proof reaches instrumented pre-mutation publisher continuation | Damage a condition artifact after `verify`; actual publisher gate refuses before `finalize_card`: card bytes/path, Git index and refs unchanged and no commit/push attempt | Real `publish` evidence checks and isolated Git state; observation wrapper at continuation, Git mutation/network actions intercepted |
| `test_observed_proof_rollout_preserves_authority` / C4 | Real creation selector chooses v2 before writes; exact fixture legacy anchor retains v1 and counters; explicit migration invalidates affected proof in new metadata | Omitted/false/unknown version, v1 on new run, changed/renamed/copied legacy anchor or unlisted payload refuse; all original hashes/counters retained, no fake pilot adoption | Real selector and existing exact recovery/metadata/accounting paths; isolated creation/orchestration stop before model; no production legacy pin |
| `test_observed_proof_serialized_recording` / C1/C3 | Actual process holder publishes proof index under 03C lock; restarted reader validates completed bytes | Contender in pre-index window is busy with unchanged index/attempts and zero extra children; unresolved verifier cannot authorize proof recording | Real flock/processes/recorder; observation gate delegates original publisher; fixture owns cleanup and preserves unrelated sentinel process |
| `test_observed_proof_offline_and_role_boundary` / C1/C3/C4 | Offline report keeps quality inventory without measured context; permitted roles record only due rows | Missing/forged role, offline record imported into measured run, runtime locator as command or unproved additional plan refuse with zero external calls and unchanged measured state | Real role/ownership/shape readers; fake runtime/model/network callbacks record zero calls |

Reviewer inspection must trace the real mechanism and assertions for each C1-C4
row and each risk, especially selection versus relevance, replacement versus
final count, and refusal before any publisher mutation. Existing integration
anchors include `test_implementation_handoff_freezes_current_preverified_manifest`,
`test_configured_final_check_composed_reuse_and_publish_gate`,
`test_check_singleflight_direct_floor_reuses_completion_after_delayed_acquisition`,
the exact-recovery tests and `test_verdict_acceptance_coverage_*` in
`tests/test_local_changerail_delivery.py`. Inspect their mocked boundaries before
reuse; old passing counts are not 03D acceptance.

Planned commands after implementation (not run by this planning session):

- `.venv/bin/python -m pytest -vv -ra tests/test_local_changerail_observed_proof.py`
- `.venv/bin/python -m pytest -vv -ra tests/test_local_changerail_delivery.py -k 'handoff or verdict or recovery or configured_final_check or check_singleflight'`
- `./bin/verify-project`, compilation, whitespace and
  `./bin/openspec validate --specs --strict --no-interactive`.
- The runner owns the configured full non-live coverage floor after independent
  GO for a measured delivery. An ordinary offline implementation instead reports
  its exact authorized checks/acceptance without a runner GO. Do not repeat the
  old 03C floor merely for these document edits or erase negative outcomes.

## Related

- `openspec/board/5.canceled/chrl-fix-02-finalize-authorized-offline-repair.md`
- `docs/development/local-changerail-delivery.md`

## Result

Repair-10 additionally closes the independent R1-R4 blockers: closed pytest
receipt grammar, inert reviewer/implementation final drafts bound only by outer
verify/reuse, duplicate aggregate verdict-ID refusal, and A→B→C v1 provenance
with separate predecessor admission.

Ordinary-offline implementation completed the two authorized Changes and the
retained C1-C4/nine-group regression matrix. `local_delivery.py` now carries a
once-validated, namespaced inventory through handoff, context/template/verdict,
outer final verification and the pre-mutation publisher gate; v2 refuses raw
bootstrap injection. Typed test observations bind selected receipt-node byte
spans plus current inspected before/action/after assertion-source fragments.
Runtime references bind outcome, target/session, scope and authorization/recovery
data; offline reports use the same closed informational shapes under an owned
offline root without measured-run import or authority.

New v2 selection is fail-closed. Exact v1 recovery preserves original contract,
accounting and history only when its independent pinned identity and current
whole-payload recovery admission still match; missing/renamed/copied metadata
does not downgrade. Final proof uses the explicit outer dispatch and existing
lock/receipt boundaries, while verify reuse and publish revalidate current
implementation/review/final proof. No production additional-plan adoption,
legacy pin/migration authority, runner/handoff/GO, model/runtime/pilot,
finalizer, board move, staging, commit or push was added.

Focused observed-proof and the complete delivery harness passed after scoped
legacy fixture repairs. The only disclosed test isolation is for old mutable
legacy receipt/review-accounting unit seams whose purpose is malformed or
changed historical metadata; C4 and all new v2 integration controls retain real
production selectors and gates. Independent Astra review remains root-owned;
this ordinary-offline Result is not GO, finalization or publication.

Repair-09d closes the final C4 lifecycle boundary: a v1 continuation selected
only after exact source recovery now retains its closed admission snapshot and
immutable original run/manifest provenance. Later authorized code/Result/Log
changes are evaluated through that continuation's own current
manifest/receipt/role/fingerprint gates, without renewing the source pin or
rewriting source accounting/history. Real recovery creation plus focused,
manifest and handoff evidence cover this positive control and stale own payload
or corrupt original source refusals.

Repair-11 closes R5–R7 and the remaining R4 lifecycle coverage. Due final test
rows now require exact membership in the current validated configured final
receipt set at fresh verification, reuse, and the publisher gate; inspection
and runtime remain independently typed. Measured schemas/readers reject
kind-foreign assertion support and non-string mocked-seam/residual-risk items
before retention. Every continuation consumer now independently requires the
immutable external origin anchor while preserving B/C current code and
Result/Log gates; the A→B→C regression gives C its own focused receipt,
manifest, handoff, and nonzero inherited accounting evidence. The retained
ordinary-offline checks are not acceptance, GO, or publication; fresh Astra
review remains root-owned.

Repair-12 closes R8/R9. The shared reference reader now rejects untyped nested
source fields before locator resolution/read, and runtime observations explicitly
support only empty `inspected_sources`; inspection and offline sources continue
to use fully typed safe references. The R6 closed-types regression was corrected:
its earlier description did not itself prove accepted-history preservation because
it reused a damaged timestamp and started without an accepted index. The revised
control creates valid accepted inspection/runtime records first, restores valid
artifact bytes per one-property mutation, recomputes references, compares retained
history/index bytes after each refusal, and has an in-memory gate-removal
sensitivity control. This ordinary-offline result remains neither acceptance,
GO, nor publication.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-03d-enforce-implementation-proof-inventory`

### Why

Static plan completeness is not current implementation evidence.

### Goal

Bind implementation observations and enforce them at handoff.

### Scope

Shared observation identity, current-run activation and implementation gate.

### Ordered Tasks

1. Implement once-read inventory/grouping and closed proof schema using the
   existing plan and receipt readers; add positive/negative namespace, typed
   artifact, selected-node and path-safety tests from the matrix.
2. Implement immutable observation recording/current-index advance with existing
   03C ownership. Exercise real publication-window contention and failed-write
   preservation; keep historical receipt and accounting bytes intact.
3. Define creation-time contract selection and exact compatibility interface,
   with omission/downgrade and post-move source-hash tests. Keep activation
   incomplete until Change 2 connects every required consumer.
4. Enforce due implementation proof at handoff publication, reuse and consumption;
   prove future stages remain pending and refusal preserves prior handoff state.

### Acceptance

- C1 is covered by the first three matrix groups and real handoff integration;
  C2's shared representation and C4's activation/legacy interface are established.
  Full C2-C4 acceptance still requires Change 2; this is not a partial release.

### Depends On

- none

## Change 2: `chrl-fix-03d-enforce-reviewed-and-final-proof-coverage`

### Why

Free-text review evidence can omit required condition proof.

### Goal

Use the same complete inventory through review and the outer final gate.

### Scope

Versioned verdict references, semantic guidance, final-stage checking and compatibility.

### Ordered Tasks

1. Connect the shared inventory to context, versioned verdict template and
   validator, preserving v1 only for exact eligible legacy. Test complete
   scenario/clause coverage, honest NO-GO, final pending and caller-validated
   additional-source fixtures without adding a production adoption caller.
2. Enforce final proof on `verify` execution/reuse and repeated publisher
   evidence checks before mutation; preserve the existing floor/receipt/summary
   path. Exercise stale-after-verify, wrong-lane and missing-final preservation.
3. Complete new-run activation through all consumers and exact legacy/recovery
   accounting/offline tests. Prove omission or caller flags cannot choose v1;
   do not create production migration pins or enable CHRL-FIX-02.
4. Synchronize canonical observable guarantees, runbook and deliver/review
   guidance. Finalize card Result/Log before current focused evidence, retain
   the matrix and disclosed mocks for independent review; use the completion
   boundary appropriate to separately authorized offline or measured work.

### Acceptance

- C2/C3/C4 and cross-stage revalidation of C1 are complete only with all matrix
  controls and independent semantic review. Tests and code are still unimplemented
  at this planning checkpoint; no future floor is reported as already executed.

### Depends On

- Change 1

## Log

- 2026-09-07T14:05:59Z: Repair-12 corrected R8 nested inspected-source typed
  validation and R9's poisoned-baseline regression. Runtime source support is
  explicitly empty-only; inspection/offline references require closed typed
  safe locators before reads. The Result corrects the earlier overstatement of
  the old R6 preservation test. No runner, GO, admission, live/native/pilot,
  finalizer, board move, staging, commit or push occurred.

- 2026-09-07T13:36:43Z: Repair-11 repaired R5 final configured-receipt
  membership at verify/reuse/publish, R6 closed measured metadata/kind shapes,
  and R7/R4 independent continuation-origin anchoring plus C-owned lifecycle
  evidence. Focused regressions and the two frozen test files remain retained
  under `offline-fix03d-5Ek6EN/repair-11`; no runner, GO, admission, pilot,
  native/live work, finalizer, board move, staging, commit or push occurred.

- 2026-09-07T12:57:29Z: repaired independent R1-R4 C4 lifecycle and
  observed-proof blockers; fresh Astra re-review remains root-owned.

- 2026-09-07T12:10:58Z Repair-09d corrected the created-v1-continuation
  lifecycle: later consumers no longer require the mutable live card to retain
  the original source-card hash after the source was exactly admitted at
  creation. The closed selection now carries a successful-admission snapshot
  while still hash-checking immutable source run/manifest provenance. A real
  isolated recovery creation then changed code and Result/Log, produced current
  focused/manifest/handoff evidence and consumed the v1 contract without
  renewing any source pin; own-payload drift and corrupt original metadata or
  manifest refused. No migration authority, runner/GO/model/native action,
  finalizer, staging, commit or push was added. Root retains independent review.
- 2026-09-07T11:56:28Z Repair-09c completed the scoped final integration:
  raw v2 bootstrap metadata now refuses before review context publication;
  affected synthetic legacy fixtures now carry genuine exact-v1
  run/manifest/card identities, and fresh verifier subprocesses receive only
  their fixture-owned identity. The complete delivery harness passed 508 tests;
  canonical consumer/runbook/board/role guidance was synchronized. Narrow
  legacy accounting/receipt units explicitly isolate only the unrelated C4
  selector when they intentionally mutate old metadata; real C1-C4 integration
  remains selector/gate-backed. Retained evidence is under repair-09c. No
  runner GO/handoff, model/native action, finalizer, staging, commit or push;
  root owns fresh independent review.
- 2026-09-07T08:38:48Z Repair-01 retained the first attempt and corrected the
  confirmed completeness failures: absence/unsafe observed-proof selection now
  fails closed unless a fixture-only exact legacy anchor validates; v2 GO now
  requires nonempty per-condition current observation references; declared proof
  kind must match the plan; and inspection artifacts require a structured
  hash-bound observed transition rather than arbitrary strings. Updated two
  legacy synthetic handoff fixtures to use an exact fixture-owned anchor and
  added exploit regressions. This repair does not claim the full nine-group
  matrix, independent acceptance, runner GO or publication.
- 2026-09-07T08:25:58Z Implemented the separately authorized ordinary-offline
  CHRL-FIX-03D Change 1 and Change 2 scope. Added closed card-proof and v2
  verdict schemas; hash-bound inventory and stage/role/artifact validation;
  immutable locked proof-index recording; new-run contract selection; handoff,
  review-context/verdict, verification and pre-mutation publisher consumers;
  focused fixture tests and canonical guidance. No runner context, events,
  admission, finalizer enablement, fixture-link repair, pilot/live/model action,
  board move, staging, commit or push. Exact focused command/output/fingerprints
  are retained in `.runtime/changerail/offline-fix03d-5Ek6EN/` for outer review.
- 2026-09-07T07:41:01Z Operator-authorized board-only refinement selected one
  complete C1-C4 invariant with two ordered Changes after inspecting actual
  03A/B1/P/F/C interfaces. Specified shared namespace/grouping, typed observations,
  stage ownership, v2 activation/exact legacy selection and real before/after
  positive/negative controls. Preserved Acceptance and historical split/budget
  records; re-estimated 180 minutes/800 production-schema lines as information.
  Handoff baseline matches `sha256:664e34ddf933801aad73d5fbe6ce5dda309e5310c63830365e3cb49aaa3b653b`;
  new scoped preservation evidence is under
  `.runtime/changerail/plan03d-20260907-BXt2O3/`. No code/schema/test/spec/skill
  implementation, admission, independent model review, pilot, finalizer or Git
  publication was performed. Next is separate implementation authorization.
- 2026-09-07T07:16:05Z Marked refinement as the next planning step after
  accepted offline 03C. Clarified precedence of the operator budget waiver over
  historical sizing text; preserved the full Acceptance/Design/Verify and
  proposed boundaries for substantive refinement. No new successor, code,
  schema, gate, verdict, admission or publication was created.
- 2026-09-06T12:56:20Z Recorded remaining condition-proof enforcement as SPLIT_REQUIRED (45 minutes/350 production-schema lines) with two concrete future successor boundaries. No scope was silently dropped or implemented.
- 2026-09-06T14:18:25Z Replaced the non-executable 03B aggregate dependency with both actual 03B1/03B2 successors, preserving existing 03A/03C prerequisites and all other plan sections. This aggregate still requires its own split; no predecessor completion, admission or implementation is claimed.
- 2026-09-06T16:45:59Z Followed the operator-approved 03B2 split: replaced only its aggregate dependency with actual 03B2-F (transitively 03B2-P), preserving 03A/03B1/03C and this card's separate split decision. No predecessor completion, scope expansion, admission or implementation.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

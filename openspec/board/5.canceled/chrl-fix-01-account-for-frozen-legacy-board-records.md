# Separate four frozen legacy records from the active delivery lane

## Status

5.canceled

## Owner

qa-mcp

## Series

chrl-fix-01

## Order Index

406.19

## OpenSpec Stage

verified offline repair; operator-authorized publication; not runner-admitted

## Priority

P1; migration workflow prerequisite

## Source

- Operator requested this bounded plan after FIX-01 readiness checks on 2026-09-05 at commit `e777c9a7f673b120f852d5797f9f2ac19220d434`.
- `docs/development/board-inventory-2026-09-05.md` establishes the retained NO-GO and NOT-VERIFIABLE dispositions; publication or directory membership is not new delivery authority.
- FIX-01's dry-run admission returned READY, but doctor rejected `card-state` (still backlog) and `single-active-card` (the four records below). No card moved or runtime executed.

## Summary

Both delivery doctor and the shell start guard currently count every Markdown file in `3.inprogress` as active work. Three exhausted/replaced records and one suspended, unqualified record therefore block unrelated new delivery. FF and publish also treat these records as mutable live-link sources. Introduce one exact, hash-checked historical classification shared by these consumers, preserving the original files and all prohibitions on execution.

## Frozen Records

All paths below remain regular files at their original locations, with unchanged bytes and Status. SHA-256 values were computed and compared with the source commit above during planning. They are the complete authorized classification set, not examples or a pattern.

| Record | Exact path | SHA-256 | Non-deliverable disposition / evidence |
| --- | --- | --- | --- |
| OSS-06-S1 | `openspec/board/3.inprogress/oss-06-s1-extract-hidden-desktop-process-foundation.md` | `3fc2954bda90325c1732e02521756818dad8556c53e89b2f40fbdad5b672be0b` | `superseded-no-go`; S1-R1 published at `8b329a2` |
| OSS-06-S5 | `openspec/board/3.inprogress/oss-06-s5-extract-prompt-admission-action.md` | `8251e87eb409a9878bfbda22dbcb203e294618316bfdf999cfad183663133726` | `superseded-no-go`; S5-R1 published at `3a0e0f6` |
| OSS-07 | `openspec/board/3.inprogress/oss-07-prepare-qa-mcp-public-repository-readiness.md` | `a8813738de11088e7df1146833ec24f3ea2c092273e83292bb81cdad7d93d9f1` | `superseded-no-go`; OSS-07-R1 published at `8e94a21`; the source's old Next is not retry authority |
| OSS-06-I13 | `openspec/board/3.inprogress/oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence.md` | `30db65b617b858b94dca1b67ab588e704c9954ef016b150f2be89711466a6a9b` | `suspended-not-verifiable`; I15 admitted no receipt/candidate; I16 at `10598ef` is omission, not replacement or certification |

## Acceptance

### Requirement: Classify only exact unchanged records

#### Scenario: Four records and a foreign active card

- WHEN the four declared files match their exact paths and hashes, THEN the common classifier reports three superseded NO-GO records and one suspended NOT-VERIFIABLE record separately from active work.
- AND an additional unlisted card, including a similarly named copy, remains active; neither directory-wide rules nor title/Result wording grant an exemption.

#### Scenario: Frozen identity drifts

- WHEN a declared file is missing, moved, edited, or replaced through a file/ancestor symlink, THEN classification fails closed before lifecycle side effects; no hash is regenerated or exemption silently dropped to make a gate pass.
- AND decisions revalidate current bytes rather than relying on a cached classification from an earlier transition.

### Requirement: Preserve single-active and dependency safety across entrypoints

#### Scenario: Start and recovery agree on the actual lane

- WHEN a clean isolated fixture has all four frozen records and no real active card, THEN doctor and the shell start guard agree that the active lane is empty while reporting the retained history separately.
- AND adding one real active card blocks a second start; recovery allows only that one real card with its existing exact retained manifest and objective, never a different or second active card.
- AND depending on a frozen record remains unsatisfied: its disposition is not `4.done` and must not be resolved automatically to a published successor.

### Requirement: Never deliver a frozen source

#### Scenario: Direct invocation cannot revive old work

- WHEN any frozen path is selected for admission, FF/resume, start/recovery, fresh review, handoff or publish, THEN the entrypoint rejects it as non-deliverable before editing Result/Next/Log, emitting delivery evidence or invoking an agent/publisher.
- AND `board-do` rejects its already-inprogress branch for these targets, including dry-run; forged ready-looking metadata or old recovery/verdict state cannot authorize the source.
- AND read-only inspection can explain the disposition, while I13 remains unqualified and requires a separately authorized successor for any future runtime work.

### Requirement: Preserve source bytes and live-link hygiene

#### Scenario: Unrelated FF and publication rewrite their own links

- WHEN a normal card changes columns through the existing FF/publish helpers, THEN all four frozen files and their paths remain byte-identical, and the normal live-card references are still updated.
- AND only outbound references inside verified frozen source files are treated as historical, not maintained as live links; broken links in ordinary live cards or product payload still fail, and a missing frozen file fails its integrity check first.
- AND frozen paths are never added to ignored payload/fingerprint prefixes; any attempted edit/deletion remains visible and rejected, and `.changerail/legacy-lifecycle.json`, `openspec/changes/`, done/canceled history and original verdicts remain unchanged.

## Scope

- `scripts/changerail/local_delivery.py`: one small fixed classification table and shared checks; doctor/admission/target guards, live-reference source selection and publication rewriting.
- `scripts/changerail/local_ff.py`: frozen-target rejection, including resume, and shared immutable-source filtering before reference writes.
- `scripts/board-lib.sh`: use the shared active-lane check for starts while retaining existing dependency validation.
- `bin/board-do`: reject frozen targets before its already-inprogress branch can append Log or replace Next.
- Tests: `tests/test_local_changerail_delivery.py`, `tests/test_local_changerail_ff.py`, `tests/test_board_helpers.py`, `tests/test_changerail_qa_adaptation.py`.
- During authorized implementation, update `docs/development/local-changerail-delivery.md`, `docs/development/legacy-board-transition.md`, `openspec/board/README.md` and the canonical wiring spec directly. Keep the dated inventory as historical evidence.

## Affected Capabilities

Verified frozen legacy records neither occupy the actual active lane nor become executable or mutable as a consequence of that classification.

## Non-Goals

- No move to backlog/done/canceled, status rewrite, alias/symlink replacement, deletion, or alteration of the four source records.
- No general paused-card workflow, new board column, configurable ignore list, environment override, database, registry service or extra scheduler.
- No exemption for other legacy todo records; no reset of exhausted reviews or adoption of unrelated dirty work as recovery.
- No change to clean-start, one-real-active-card, dependency, GO/fingerprint, bounded repair or publication authority rules.
- No product/runtime fix, live 1C/Windows operation, OSS-06 qualification, source snapshot regeneration or migration pilot.

## Depends On

- none

## Change Set

- `chrl-fix-01-classify-and-guard-frozen-records`
- `chrl-fix-01-preserve-history-through-transitions`

## Design

Keep the four literal path/hash/disposition rows in the existing local delivery module and expose one checked classification helper. This finite migration correction does not need a new JSON configuration file, generic schema or policy plug-in. The reviewed source table owns classification; runtime callers cannot add exemptions or substitute their own hashes. Tests use explicit synthetic fixtures and inject test rows only inside the test harness.

Reuse this helper for active-lane calculation, historical target rejection and immutable reference-source selection. A narrow read-only CLI adapter lets the Bash guard consume the same policy and failure status without duplicating the Python classification or re-parsing JSON in shell. Guard `board-do` before either todo or already-inprogress handling. Keep normal dependency checks and genuine recovery checks intact.

Inspect all named public lifecycle entrypoints before selecting common guard call sites: guarding doctor alone is insufficient for direct FF/resume/review/handoff/publish calls. Apply integrity validation before skipping historical link sources; ordinary broken live links still fail. Keep hash checks independent from the existing frozen lifecycle manifest; do not edit that manifest or introduce ignored-prefix exemptions.

Rejected alternatives: moving/rewriting originals breaks immutable lineage; ignoring all legacy/inprogress files weakens exclusivity; updating only doctor leaves a shell blocker; a general historical-card subsystem is unnecessary for this exact four-record migration boundary.

## Delivery Mode And Bootstrap Boundary

This is an ordinary, operator-authorized offline migration repair, not the migration pilot and not an initial `chrl-run` input. The uncorrected runner is blocked by the very state this card addresses. Do not start it with a recovery flag, relax a gate temporarily, fabricate handoff/GO, or introduce a dependency on this card reaching runner-owned done to escape that cycle.

Planning does not authorize implementation. After a separate implementation request, apply only the named correction and run the relevant checks under AGENTS.md's ordinary offline-fix boundary. Report actual verification in Result/Log without minting a measured verdict or moving this card to done. Commit/push requires explicit publication authority. An offline verification record is not native certification or pilot approval.

After the correction is verified and, if authorized, published on clean main, recheck FIX-01 readiness. Its backlog `card-state` failure remains expected until actual acceptance; FF then changes the card and live links, which need a scoped planning commit before a clean-start delivery. The pilot card and exact `chrl-run` command still require separate prior agreement. This card is a global workflow prerequisite, not a `Depends On` alias that pretends the repair has already reached `4.done`.

## Implementation Plan

1. Pin the four source identities above and add negative/positive fixture controls; implement the shared classifier, single-active checks and frozen-target refusals across the declared Python/Bash entrypoints.
2. Make both reference writers and live-link validation preserve verified frozen sources; test FF, start, genuine recovery and publication with fake agents/Git publishers, retaining all current safety gates.
3. Update the canonical wiring contract and narrow workflow documentation, run the focused matrix and repository floor, then record actual offline verification without changing historical payload or claiming runner/native acceptance.

## Delivery Budget

- primary_invariant: Verified frozen legacy records neither occupy the actual active lane nor become executable or mutable as a consequence of that classification.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 4
- estimated_production_loc: 240

## Budget Notes

Provisional estimate for one coherent migration invariant, including the fixed table, shared helper, small CLI/guard integration and transition protection. Test/docs edits are excluded from product-file/LOC estimates; verification is included in the time estimate. The two Change checkpoints are not independently publishable policy states. If the complete guard/transition coverage exceeds the configured caps, return SPLIT_REQUIRED with a coherent revised boundary; do not omit direct-entrypoint or history protection to force READY. No measured wall-time or review telemetry is claimed for the separately authorized offline mode.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

- `uv run pytest -q tests/test_local_changerail_delivery.py tests/test_local_changerail_ff.py tests/test_board_helpers.py tests/test_changerail_qa_adaptation.py`
- `bash -n scripts/board-lib.sh bin/board-do`
- `git diff --check`
- `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`
- `uv run python -m compileall -q src tests scripts/changerail`
- `./bin/openspec validate --specs --strict --no-interactive`
- `./bin/chrl wiring`
- `python3 tools/public_readiness.py audit --history --json`
- Verify the four SHA-256 values and unchanged paths against Frozen Records; keep `.changerail/legacy-lifecycle.json` and `openspec/changes/` byte-identical. In isolated fixtures cover all four frozen targets, a fifth real active card, genuine and forged recovery, missing/changed/symlinked originals, and normal versus historical link sources. Real agent/native/push call counts must remain zero in these tests.

## Runtime And Authority

No lab target is required. Use isolated temporary Git repositories, synthetic card contents and mocked agents or fixture-only local publishers. Tests may perform fixture-only transitions but cannot accept, resume, review, publish or rewrite the actual historical sources or FIX-01. The operator subsequently authorized scoped commit/push of this verified repair. Live runtime and pilot execution remain outside that authority.

## Related

- `openspec/board/4.done/oss-fix-01-freeze-physical-target-configuration.md`
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`
- `openspec/board/4.done/oss-06-s1-r1-certify-hidden-desktop-process-foundation.md`
- `openspec/board/4.done/oss-06-s5-r1-replace-prompt-fingerprint-with-addressed-admission.md`
- `openspec/board/4.done/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`
- `openspec/board/4.done/oss-06-s4-r1-i16-record-stable-profile-omission-after-i15.md`

## Result

Implemented offline after the operator separately authorized publication of the existing planning work and this repair. Planning commit `d430813a816b0eceb47c94a460accc9583e0600e` was pushed to `origin/main` and the clean tree verified before implementation. The operator then authorized scoped publication of the verified repair. This card remains backlog, with no measured handoff, GO, done transition or native certification; Git history and the remote HEAD identify the publication, not a runner-owned completion verdict.

- One fixed table and shared integrity/target/activity policy now cover the named Python and Bash entrypoints. Historical sources cannot be revived through direct calls or forged FF/recovery state. Both reference writers preserve their bytes, while normal references and dependency/recovery guards retain their checks.
- Focused matrix: 203 passed. Regression controls include all four targets, fifth/copy activity, missing/edited/moved/file- and ancestor-symlinked originals, pre-write refusals, ordinary FF, genuine versus forged recovery and fixture-only publication with unchanged originals.
- Full non-live coverage floor: 1814 passed in 402.89 seconds; coverage 74.67% against the required 60%. No product code changed after this successful floor.
- Bash syntax, compilation, whitespace, strict canonical validation (70 specs), local wiring and public-source/history audit passed. No dangling ordinary live-board references were found.
- Pre-publication FIX-01 read-only doctor reported `single-active-card: pass (empty)`, three `superseded-no-go` and one `suspended-not-verifiable` source; admission size and dependencies passed. At that checkpoint doctor failed only `clean-start` (then-uncommitted repair) and `card-state` (FIX-01 remains backlog); remote preflight was not requested. Recheck after publication without moving FIX-01.
- All four approved SHA-256 identities match. `.changerail/legacy-lifecycle.json`, `openspec/changes/`, the four source cards and done/canceled history have no diff against `d430813`. Production scope is four workflow files, 150 added plus 46 removed lines (196 total), below the 300-line cap. Tests/docs are outside that production count.
- No real agent/review, live 1C/Windows operation, runner delivery or pilot was invoked. Publication testing used an isolated local bare Git fixture, not the project remote.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-01-classify-and-guard-frozen-records`

### Why

Filename enumeration currently confuses retained history with active delivery, and public entrypoints can otherwise target those source records directly.

### Goal

One exact classifier admits no historical execution and preserves one-real-active-card semantics in both Python and Bash.

### Scope

- The four named workflow paths and their focused tests; no history edits or caller-specific exemption lists.

### Acceptance

- The complete classification, exclusivity/dependency and non-deliverability scenarios above pass, including `board-do`'s already-inprogress branch and direct/recovery entrypoints.

### Depends On

- none

### Ordered Tasks

1. Add test-first fixed-identity, drift, fifth-card, dependency and direct-target controls in isolated fixtures.
2. Implement the shared checked table and target/active guards; make the shell guard consume that same policy and reject before writes.
3. Run the four focused harness test modules and Bash syntax checks; retain concise public-safe results.

## Change 2: `chrl-fix-01-preserve-history-through-transitions`

### Why

Ignoring a record in the active count alone does not stop FF or publication from rewriting its bytes or misclassifying old outbound links as live work.

### Goal

Normal transitions preserve all frozen source bytes and ordinary live-link/fingerprint checks.

### Scope

- Existing FF/publication link writers, live-reference source selection, tests and the named workflow contract/docs.

### Acceptance

- The complete immutable-source/live-link scenario passes; all Change 1 controls remain green and no actual board transition or agent call occurs during offline verification.

### Depends On

- `chrl-fix-01-classify-and-guard-frozen-records`

### Ordered Tasks

1. Reuse the classifier in both link writers and historical source selection; cover normal and stale historical links, source tampering and exact-byte preservation in fixture transitions.
2. Update the canonical wiring spec and workflow instructions to distinguish these exact non-deliverable records from real activity, without changing the dated inventory or pilot rules.
3. Run the focused matrix and final checks in Verify, record the offline result and recheck the four actual hashes. Do not mint a runner verdict or publish without separate authority.

## Log

- 2026-09-05T16:14:23Z Subsequent operator-authorized FIX-01 planning step: deterministic FF returned READY and moved that card to todo from clean published `17c569d`. Its Related link is updated here; this repair remains backlog with no runner verdict. Only the accepted plan/live-link publication is in scope, not the pilot.
- 2026-09-05T15:50:57Z Operator authorized the next step: scoped commit/push of the verified CHRL-FIX-01 offline repair. Confirmed the same 14-file scope and unchanged workflow/test payload, with main and origin/main at `d430813` before publication. Retain the successful 1814-test floor; final publication checks and the local pre-commit hook apply. No runner context, GO, done transition, FIX-01 acceptance or pilot is authorized by this step.
- 2026-09-05T09:48:06Z Full non-live floor completed: 1814 passed, coverage 74.67% (required 60%), 402.89 seconds. Offline correction is verified; only scoped implementation/test/docs changes remain uncommitted. Publication and the FIX-01 pilot remain separately authorized actions.
- 2026-09-05T09:44:15Z Operator-authorized offline repair applied from clean published `d430813`. Focused 203 tests, strict 70-spec validation, Bash/compile/whitespace, wiring and public audit passed; the full non-live floor is still running. Actual active lane is empty; original hashes/history unchanged. No card transition, measured verdict, implementation publication or pilot.
- 2026-09-05T09:13:11Z Created at operator request after FIX-01 readiness diagnosis. Four source hashes match published `e777c9a`; planning only, no code, status move, runtime, admission, commit/push or pilot.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

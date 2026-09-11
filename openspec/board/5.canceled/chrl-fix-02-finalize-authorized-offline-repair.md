# Finalize one explicitly authorized offline correction after a stopped delivery

## Status

5.canceled

## Owner
qa-mcp

## Series
chrl-fix-02

## Order Index
406.21

## OpenSpec Stage
operator-redesigned backlog draft; implementation approval pending; not admitted

## Priority
P1

## Source

- Operator requested this recovery plan after the FIX-01 pilot stopped and its separately authorized offline correction passed verification.
- Inspected baseline: `e7f7d4f59044689a5b017cb5a3da539f8a978abe`, plus the retained FIX-01 working changes.
- Pilot `20260905T170917Z-oss-fix-01-freeze-physical-target-configuration` ended with `final verification repair budget exhausted`: two ordinary reviews and one post-floor review completed; the final full suite still had 118 failures.
- The subsequent offline correction aligned integration session generations and reconciled exact publication-scanner allowances. Verification: 1820 non-live tests passed, 74.69% coverage, 70 canonical specs passed, compilation and wiring passed. These checks are not a fresh runner GO for the amended payload.
- Read-only recovery doctor at 2026-09-05T18:19:04Z rejected the added `config/publication-policy.json` and `tests/test_positive_operation_boundary_integration.py` paths as outside the retained manifest. The active card was also amended. Existing recovery does not provide a separately authorized finalization lane for this state.
- The facts and reproduction obligations are restated here; ignored local pilot and offline reports are operator evidence, not clean-clone test prerequisites.

## Summary

Provide one explicit, fingerprint-bound finalization of an already corrected
offline payload after a terminal delivery run. Preserve the source run and its
spent budgets; do not pretend the amended files are its original payload. The
new attempt performs fresh independent review and the final floor before the
existing deterministic publisher can act. It starts no implementation session
and grants no automatic repair or repeated finalization allowance.

## Acceptance

### Requirement: Admit only an explicit exact offline amendment

#### Scenario: Check and adopt the same named correction

- [C1] WHEN a closed request names the terminal source and its immutable root lineage, source run/manifest digests, sole actual active card, unchanged baseline HEAD, exact current payload and exhaustive reasoned old/new per-path amendment, THEN check-only validates those same bytes without any run, reservation, model, Git/card or history write. Execution rereads and rejects request/source/payload drift before a side effect; a self-declared authority string is not execution permission.
- [C2] AND retained paths require complete fingerprints; added/modified/deleted paths match explicit amendments, including file kind/mode and deletion markers. Missing/extra/duplicate paths, unknown or duplicate JSON keys, unsafe IDs, traversal, symlinked ancestry, wrong baseline, dirty index, another actual active card and frozen-history drift refuse. The unchanged four verified frozen records are not additional active cards; copying their names never grants that classification.

### Requirement: Keep lineage and attempt accounting intact

#### Scenario: One serialized transaction survives interruption

- [C3] WHEN an eligible terminal source is adopted, THEN an atomic reservation keyed by its validated root lineage retains request/source/plan digests, old/new payload, full inherited and new actual usage, and the approved scope. Source run manifests/verdicts/logs/terminal reasons stay byte-identical. Descendants and renamed requests cannot reserve a second transaction; missing/cyclic/foreign lineage or ambiguous accounting refuse, not zero-fill or reset.
- [C4] AND a nonblocking no-follow attempt lock spans revalidation, review/check children, durable receipts and publication state. Contenders have zero child/publish calls. Restart continues only the same exact transaction: valid completed stages are reused without another review/check/commit; incomplete review is retryable only after proving no owned session remains and retaining its usage. Unknown children, payload drift, completed NO-GO, red floor or corrupt stage proof refuse without automatic repair or a successor transaction. Numeric budgets are informational, not new execution authority.

### Requirement: Require fresh whole-scope observed proof

#### Scenario: Finalize the corrected payload and every adopted bootstrap plan

- [C5] WHEN full finalization is explicitly authorized, THEN the finalizer selects one creation-pinned observed-proof source set for the active card and every explicitly adopted supporting plan, reusing 03D's namespaced inventory and safe readers. A caller-owned adoption capability binds request, root, attempt, payload and plan bytes. Missing/malformed evidence declarations refuse as migration-required before reservation. Raw metadata, a fixture capability, an old GO, version removal or an ordinary offline report cannot admit a source or supply current proof.
- [C6] AND a distinct finalizer-owned evidence-preparation phase obtains fresh receipts and typed before/action/after observations for that source set; it neither fabricates an implementation handoff nor launches an implementation/repair model. Ordinary role rules stay unchanged. Independent Astra/high review validates every complete active/bootstrap scenario and observation; review/final rows stay with their owners. Missing, stale, duplicate, swapped or summary-only proof blocks advancement. Only a matching whole-scope GO and the configured final floor with complete 03D coverage admit the publisher; every earlier failure has zero done/stage/commit/push calls.

### Requirement: Preserve exact publication and bootstrap boundaries

#### Scenario: Interrupted publication cannot publish another payload or ref

- [C7] WHEN the existing deterministic publisher is admitted, THEN its transaction records the intended baseline, exact resulting tree, card/reference transforms, branch, remote destination identity and full destination ref before mutations, and durably records the exact commit before push. Crash probes across card movement, staging, commit and push prove restart creates at most one commit and pushes only that commit to the pinned destination. Wrong tree/parent/HEAD/index/ref/upstream/remote, ambiguous effects or source drift refuse; an already accepted exact remote commit needs no second push. Every owned transition is counted; frozen records and unrelated changes remain untouched.
- [C8] AND offline bootstrap implementation keeps this card in backlog and the actual FIX-01 pilot stopped; no source-manifest refresh, temporary gate relaxation, fake run, automatic fallback or cleanup/publish of unrelated work is used. The eventual request explicitly enumerates all support paths and plan hashes; publication moves only its active card, not supporting backlog cards. Existing ordinary clean delivery and exact recovery preserve their gates. Passing check-only, offline acceptance or this draft authorizes neither a pilot nor commit/push.

## Scope

- `scripts/changerail/local_delivery.py`: exact request/lineage/adoption, attempt serialization, explicit finalizer evidence producer and existing publisher continuity seams. No alternate publisher.
- `.changerail/profile.toml`: named finalization lane and recorded estimates/usage; retain `budgets.enforce_limits=false`, do not turn the historical numeric cap into a budget stop.
- `tools/changerail/schemas/offline-finalization-request.schema.json` (planned new closed v2 request) and `card-proof.schema.json` only for a narrowly typed finalizer producer identity. No blanket role bypass.
- `tests/test_local_changerail_offline_finalization.py` (planned new focused file): synthetic immutable lineage, real local files/locks/Git and an isolated bare remote; fake model and expensive product-floor invocations only.
- `tests/test_local_changerail_delivery.py` and `tests/test_local_changerail_observed_proof.py`: compatibility, real 03D gate and existing publisher integration regressions.
- `openspec/specs/changerail-consumer-wiring/spec.md`: canonical finalization and authorization contract.
- `docs/development/local-changerail-delivery.md`: request contents, check/execute/restart semantics and bootstrap procedure.
- This card's Result/Log during implementation. No FIX-01 product or acceptance migration is implemented by this card; any required card-declaration migration is separately enumerated and approved before actual adoption.

## Non-Goals

- No automatic adoption, wildcard dirty-tree acceptance, budget reset, review bypass or reuse of an old GO for changed bytes.
- No new generic workflow framework, background service, third-party dependency or alternate publisher.
- No replay of completed Change checkpoints or automatic implementation/repair agent in finalization.
- No redesign of ordinary final-floor repair prompting. Its failure to resolve the recorded floor is a separate process finding, not extra implementation scope here.
- No live 1C, Windows, provider calls, real finalizer-launched model sessions, working-repository publication or retained pilot mutation during offline tests. Independent offline review of this implementation is separate; test Git effects are confined to disposable local repositories.
- No new `openspec/changes/` artifacts, automatic rescue cards or edits to frozen/done/canceled history.

## Depends On

- none
- This is an offline bootstrap repair, not a new runner input while FIX-01 is active. It must not depend on its own runner-owned done state to make finalization possible.

## Change Set

- `chrl-fix-02-check-exact-offline-amendment`
- `chrl-fix-02-serialize-root-lineage-attempt`
- `chrl-fix-02-bind-adopted-observed-evidence`
- `chrl-fix-02-prove-exact-publication-continuity`

## Design

One invariant: a separately approved exact offline amendment becomes at most
one accounted publication transaction, with fresh whole-scope proof and immutable
source history. Adoption, evidence and publication cannot independently enable a
safe finalizer, so use four ordered Change checkpoints in this card, not competing
active successors. The former two-part SPLIT_REQUIRED record remains historical;
numeric ceilings are not the reason to decompose under current operator policy.

Keep both public modes disabled until all checkpoints and independent offline
review pass. Proposed CLI shape, not a currently runnable workflow:

`./bin/chrl finalize-offline <inprogress-card> --request <ignored-request.json> --check`

Removing `--check` requests the full finalization including commit/push. The
future operator-facing execution request must spell out that authority; this
card authorizes neither invocation.

### Exact request and root lineage (C1-C3; input safety, mutation)

Replace the incomplete draft request with a closed versioned v2 document. Fields:
schema, source run/card, source run and manifest SHA-256, baseline, expected whole
payload, exhaustive path amendments with old/new fingerprints and reasons,
an explicit list of supporting plan path/hash pairs, inert observation-draft
path/hash references per condition, a pinned branch/remote/ref destination and
concise authority/objective text. Validate types, canonical
relative paths, uniqueness and duplicate JSON keys; read request/source/plan
bytes once per decision through existing bounded no-follow readers. No raw
connection strings, credential-bearing URLs or source bodies in receipts.
Remote identity must be checked without logging credentials (retain a digest
plus a safe remote name/ref); never use a default unpinned `git push`.

Resolve predecessor links to their real root from retained hash-bound metadata,
checking run/card/baseline continuity, terminal state and complete accounting.
Never key lineage solely by the caller's source_run string. Missing anchors,
cycles, forked/conflicting reservations or unknown usage are explicit diagnostics;
unknown usage is not zero. Use `board_activity`/`checked_frozen_records`, not a
raw inprogress glob. Every retained path needs a digest, including unchanged
ones, before amendment comparison. Do not conflate an absent file with a missing
fingerprint or normalize escaping input before validation.

### One retained attempt (C3-C4; concurrency, restart)

Reserve a root-keyed immutable request/lineage record atomically under the ignored
offline-finalizations root. Use a regular no-follow nonblocking flock covering
the whole execution, not the draft's short mkdir lock around reservation only.
After acquisition reread request, identities and current state. Keep an explicit
attempt lock order above 03C's run-local verification lock, with no nested second
acquisition of the same verification lock. Record intent before every child;
unknown/interrupted ownership uses 03C's fail-closed semantics, not PID-based
assumptions. Fresh incomplete reviewer retries remain accounted in the same
transaction and require proof that the earlier owned session ended.

Stages: reserved -> evidence/preverify -> reviewed -> final-verified ->
publish-prepared -> transformed/staged -> committed -> pushed. Each stage binds
validated artifacts and exact payload; stage labels alone are never proof.
Complete NO-GO/red floor/payload drift close this transaction without automatic
repair. That is an outcome/authority boundary, not an elapsed/review-count stop.
The historical one-review profile field remains accounting context; current
numeric policy must not mint a second transaction or reset inherited usage.

### Integration with accepted 03D (C5-C6; input safety, role ownership)

Current concrete gaps: `_current_proof_inventory` admits additional sources only
through a fixture registry; raw `bootstrap_plan` metadata is rejected. The draft
finalizer cannot legitimately call preverify/review/verify as an ordinary run.
Introduce an internal caller-owned finalization admission object, created only
after exact request/root validation and bound to the new attempt's immutable
creation receipt. Every later consumer reconstructs it from checked original
request/source/attempt anchors; `mode`, JSON flags or fixture dictionaries cannot
manufacture it. Reuse `_derive_proof_inventory_from_checked_sources` for the
already read current card and all explicitly adopted supporting plan bytes.

Precondition: every source has complete C IDs and a closed evidence declaration.
The old FIX-01 card does not currently meet that prerequisite. Check-only must
report migration-required, not synthesize IDs, reinterpret missing version as
legacy or copy Acceptance into an editable alternate plan. Its separately
authorized current-card migration must be part of the exact future amendment;
the historical source card/manifest and accepted evidence stay unchanged.

Proposed new authority to approve before implementation: a distinct typed
`finalizer` producer may supply implementation-stage observations only for this
admitted finalization source set, using freshly executed attempt-owned checks
and explicit inspected before/action/after assertion references. This is not an
implementation model session or a fabricated implementation handoff. Ordinary
run producers and all review/final ownership remain unchanged. The finalizer's
new producer requires the checked admission object, not a role/env flag. Input
observation drafts are inert request-bound run-local artifacts, never shell
commands derived from Verify locators; existing configured evidence commands are
the only executions. Bind actual receipt/log/node/source hashes after execution;
missing drafts, opaque output, unknown methods or unobserved transitions refuse.
Offline reports may guide an author but cannot be imported as measured proof.

Fresh review consumes that one source-qualified inventory and judges relevance,
mock boundaries and full scenario clauses across every included plan. It owns
review rows; the outer final verification owns final rows with the existing
receipt/node binding. Do not make a second verdict validator or bypass
`require_current_stage_proofs`. Missing current implementation-stage observations
remain a refusal, not permission for GO merely because the final floor is green.

### Existing publisher transaction (C7-C8; publication, external effects)

Extend the existing `_publish_continuation` boundary with a small explicit
transaction journal, not a second publisher. Prepare and record deterministic
card/receipt/link transformations and resulting expected tree before staging.
Persist commit intent (baseline parent, exact tree, message and identity needed
to recognize the one intended commit); record resulting commit before network
push. A crash between commit and its receipt may recognize HEAD only when the
entire recorded intent and parent/tree/ref match; otherwise refuse. No reset,
cleanup or second commit to make state appear continuous.

Restart validates each checkpoint against actual card paths, worktree, index,
HEAD and the pinned remote/ref before using it. A moved card must be resolved
from the journal, not rejected by an initial inprogress-only lookup. Before
push, compare the remote ref read-only; retry only the exact retained commit and
destination, without force. If already present, retain success without a second
push. Unknown transform/staging/commit effects remain diagnosis-required. Tests
must cover exceptions and process exits before and after every durable boundary,
including push success before the local success receipt.

Real seams in offline tests: no-follow files, hashes, root traversal, OS locks
with competing processes, board classifier, 03D inventory/verdict validators,
receipt readers and Git against disposable repositories/bare remotes. Mock only
model transport and costly full product-floor commands; use small real pytest
children for receipt/observation integration. Fake call-order tests alone do not
prove C5-C7. No runtime contour is applicable; external effects are limited to
explicit future Git publication and isolated test Git operations.

Rejected shortcuts: refreshing source manifests, whole-dirty-tree adoption,
raw metadata extra plans, importing old offline proof, ordinary role bypass,
reset counters, repeated review after completed GO, naked push retry, or enabling
only the easy part while evidence/publication continuity remains unproven.

## Implementation Plan

1. After explicit approval of this redesign, implement Changes 1-4 sequentially with their narrow positive/negative checks. Keep public execution disabled until the integrated gates are proven together.
2. Update canonical contracts/runbook and Result/Log; retain independent offline review, focused integration tests and the non-live floor for final implementation bytes. This planning pass creates no such results.
3. Separately enumerate any required evidence-declaration migration, supporting plan/path scope and excluded changes. Obtain agreement on exact adoption and finalization/publication authority; no actual request hash is fabricated in this draft.

## Delivery Budget

- primary_invariant: One explicitly authorized offline-amended delivery payload can be finalized only through its own bounded fresh review and verification without rewriting source-run history or accepting unrelated changes.
- expected_wall_minutes: 360
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 4
- estimated_production_loc: 1200

## Budget Notes

Revised estimate includes the real 03D integration and publisher crash windows,
not just the disabled draft helpers. Informational, not a measured READY or stop.
Original 30-minute/280-line assumptions and failed implementation remain in Log
and Git history; no old budget is declared met. One production owner, zero live
runtime contours. Reassess an actual unrelated intent or new owner, not numeric
excess. All attempts, model usage and failures must remain accounted.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

The methods below are planned tests, not execution evidence. All C1-C8 rows
describe offline implementation verification; the future adopted cards retain
their own stage assignments. Each named test family includes positive and
negative cases and asserts real before/after state, not only mocked call counts.

```json
{
  "schema": "qa-mcp.card-evidence.v1",
  "conditions": [
    {"condition":"C1","seam":"request check","precondition":"terminal synthetic source and exact amendment","action":"check and mutate request/source/payload independently","expected":"exact read-only success; every drift refuses before writes","method":{"kind":"test","target":"tests/test_local_changerail_offline_finalization.py::test_request_exact_read_only"},"stage":"implementation"},
    {"condition":"C2","seam":"path and activity admission","precondition":"complete manifest and four pinned frozen sources","action":"vary path/type/JSON/index/active/frozen inputs","expected":"only exhaustive exact safe scope passes; frozen bytes preserved","method":{"kind":"test","target":"tests/test_local_changerail_offline_finalization.py::test_admission_paths_and_frozen_history"},"stage":"implementation"},
    {"condition":"C3","seam":"root lineage reservation","precondition":"root and recovery descendants with retained usage","action":"reserve from root and descendant/renamed requests","expected":"one immutable root transaction and cumulative accounting; corrupt lineage refuses","method":{"kind":"test","target":"tests/test_local_changerail_offline_finalization.py::test_root_reservation_and_accounting"},"stage":"implementation"},
    {"condition":"C4","seam":"attempt lifecycle lock","precondition":"owned child or completed stage with real receipts","action":"compete and interrupt around child/receipt boundaries","expected":"no duplicate child; exact resume only; unresolved/terminal states refuse","method":{"kind":"test","target":"tests/test_local_changerail_offline_finalization.py::test_serialized_attempt_restart"},"stage":"implementation"},
    {"condition":"C5","seam":"caller-owned 03D source admission","precondition":"active and supporting card declarations","action":"admit exact source set then forge metadata/version/plan bytes","expected":"single current inventory only through exact adoption; legacy migration explicit","method":{"kind":"test","target":"tests/test_local_changerail_offline_finalization.py::test_adopted_source_inventory"},"stage":"implementation"},
    {"condition":"C6","seam":"finalizer proof and role gates","precondition":"fresh attempt checks and explicit assertion drafts","action":"produce/validate observations and remove or swap one plan condition","expected":"full genuine proof permits review/final; omissions and wrong producer refuse before publish","method":{"kind":"test","target":"tests/test_local_changerail_offline_finalization.py::test_whole_scope_observed_gates"},"stage":"implementation"},
    {"condition":"C7","seam":"existing Git publisher continuity","precondition":"green exact scope and isolated bare remote","action":"crash around each transform/stage/commit/push boundary and alter destination","expected":"one intended commit, exact remote/ref only; ambiguity refuses without duplicate effects","method":{"kind":"test","target":"tests/test_local_changerail_offline_finalization.py::test_exact_publication_crash_boundaries"},"stage":"implementation"},
    {"condition":"C8","seam":"bootstrap and compatibility boundary","precondition":"occupied synthetic board plus ordinary clean/recovery fixtures","action":"check/execute only explicitly authorized synthetic scope","expected":"backlog support and history preserved; ordinary gates unchanged; no implicit fallback","method":{"kind":"test","target":"tests/test_local_changerail_offline_finalization.py::test_bootstrap_and_ordinary_boundaries"},"stage":"implementation"}
  ],
  "risks": [
    {"kinds":["input_safety"],"applies":true,"decision":"closed single-read no-follow request/source admission and 03D capability validation","conditions":["C1","C2","C5","C6"]},
    {"kinds":["mutation"],"applies":true,"decision":"exact exhaustive amendment and immutable source/history checks before every stage","conditions":["C1","C2","C3","C8"]},
    {"kinds":["restart","concurrency"],"applies":true,"decision":"root-keyed reservation, full-attempt flock and durable child/publication intents","conditions":["C3","C4","C7"]},
    {"kinds":["publication","external_effects"],"applies":true,"decision":"whole-scope current evidence then journaled existing publisher with pinned commit and destination; real Git only in disposable offline fixtures","conditions":["C6","C7","C8"]}
  ]
}
```

- Change 1: new focused file with `-k 'request_exact or admission_paths'`.
- Change 2: new focused file with `-k 'root_reservation or serialized_attempt'`.
- Change 3: new focused file with `-k 'adopted_source or whole_scope_observed'`, plus affected 03D tests.
- Change 4: new focused file with `-k 'exact_publication or bootstrap_and_ordinary'`, plus existing local bare-remote publisher test.
- `uv run pytest -q tests/test_local_changerail_offline_finalization.py tests/test_local_changerail_delivery.py tests/test_local_changerail_observed_proof.py tests/test_local_changerail_ff.py tests/test_changerail_qa_adaptation.py`
- `git diff --check`
- `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`
- `uv run python -m compileall -q src tests scripts/changerail`
- `./bin/openspec validate --specs --strict --no-interactive`
- `./bin/verify-project`
- Retain before/after hashes for source-run records and frozen history; assert zero real model/live/commit/push calls in offline tests. Fixture publication and failed-push restart must prove exact call counts and refs.

## Related

- `openspec/board/4.done/oss-fix-01-freeze-physical-target-configuration.md`
- `docs/development/local-changerail-delivery.md`
- `openspec/specs/changerail-consumer-wiring/spec.md`

## Result

OFFLINE IMPLEMENTATION RESULT — independent acceptance and publication are separate.

The preceding review-08 assessment returned NOT ACCEPTED: C1/C2/C5/C6/C7
passed, while C3/C4/C8 failed on terminal manifest producer continuity (F24),
the run writer's own output-ancestry lifetime (F25), and explanation F14.
It confirmed the earlier F19/F20/F21/F22/F23 repairs and the bounded K2
test-only evidence reuse. Those assessments, failed probes and all original
usage remain retained; no old verdict is relabeled as acceptance of new bytes.

The scoped L repair persists a distinct closed terminal_manifest_intent BEFORE
manifest installation: creation-pinned initial hash, exact produced after hash,
fixed publish metadata/timestamp and the known pushed-journal reference. This
is an incomplete producer expectation, not a completed receipt. The later
atomic manifest-pin/run-intent group remains separate. An installed manifest
cannot renew its own expected identity after a pre-run-intent interruption;
changed bytes, a different valid timestamp, lost intent and unsafe/conflicting
inputs refuse before later writes. Independently pinned legacy groups retain
their existing compatibility boundary.

The manifest producer parent holds its exact before input, same checked origin
and journal through its own final flush. The manifest writer holds the known
certified parent record, origin, journal and output through its own return.
The run writer likewise holds its known parent, manifest, origin and output.
Recovery reacquires and file-flushes the admitted producer bytes; a replaced
inode never inherits an earlier object's fsync. Both expected-before writers
revalidate dependencies after the before-file flush and retire only that obsolete
lease at legitimate replacement. Output object/content and no-follow ancestry
remain held through the writer's OWN last flush, not merely a later outer refusal.
Ordinary generic writers and the complete outer certified review closure remain
unchanged. There is no new transaction, operation identity or source refresh.

Actual paired pipeline tests assert at those writer returns. Actual interruptions
cover manifest producer temp-file flush, installed producer, installed manifest,
the original pre-run-intent window, installed run intent and installed run.
Intact recovery preserves proof/HEAD/ref and the same seven operation identities
without another model/check/commit/push. Changed-byte and changed-valid-timestamp
manifest restarts, missing/unsafe/conflicting evidence and both before-install
guards have distinct controls. Closed synthetic producer-schema/storage tests
are identified as such; they are not whole-pipeline semantic proof.

Verification provenance is explicit. The initial three actual L failures were
followed by 29 intermediate passes. A newly consumed producer-record input then
reproduced an unflushed same-byte replacement at manifest writer return; its
24-case correction passed. The next collection failed before executing any test
because of a pytest parameter/default conflict, now corrected without changing
the old direct-call interface. A separate oversized-record diagnostic exposed a
wrong test assumption about low-level versus admitted size, not a new production
defect; no size limit changed. The corrected L transition set passed all 99 tests
on its retained execution fingerprint, with all eight workers terminal.
These original receipts are not rewritten as later-fingerprint executions.
The following 248-node regression run completed with 159 passes and 89 failures,
including all 60 publication crash cases. Old transparent test wrappers discarded
the writer's new certified-reference return, causing None errors or child exit 99
before the intended exit 97; one refusal test expected the former diagnostic.
The scoped test-only correction returns the actual writer result, preserving all
assertions and fault boundaries, and expects the precise producer refusal for
that target. Its 11 representative restart/process/contender checks passed.
Production, schemas, profile and ordinary tests are unchanged. Exact whole-file
test deltas and original argv/node/log/exit provenance are retained separately;
the 89 original failures are not erased or labeled green. Remaining failed nodes
require corrected execution, including successful coverage of all 60 crash cases.
Unaffected successes keep their original fingerprints, not a new execution label.

| Acceptance | Implemented boundary and evidence surface |
|---|---|
| C1–C2 | Review-08 confirmed unchanged exact read-only request/source/amendment, typed scope, lineage, frozen-history and no-follow admission. Current actual active/supporting paths traverse the same gates. |
| C3–C4 | One creation-pinned root attempt, full lock and cumulative accounting; distinct manifest/run producer intents, complete input/output lifetimes and exact public restart. No repinning, duplicate work or second transaction. |
| C5–C6 | Review-08 confirmed unchanged creation-bound namespaced inventory, finalizer authority and real receipt/node/assertion proof; model transport alone is synthetic in actual pipeline tests. Review/final ownership remains separate. |
| C7 | Existing exact publisher tree/parent/commit/destination gates are unchanged. The complete 60-case exception/process-exit matrix remains a final check; additional terminal recovery preserves exact Git state and seven identities. |
| C8 | Public enabled=false; this card stays in backlog. The ten-path scope, 4838 protected hashes, original HEAD and empty index are preserved. Ordinary compatibility is checked; no pilot, source migration or checkout publication occurs. |

Current L reports/map and authenticated receipts are retained under the ignored
offline task directory; K/K2/review-08 artifacts and every historical Log remain
unchanged. Failed or partial commands remain failed or partial. Injected fsync
and process interruptions do not claim an observed physical power-loss test.
Fresh independent assessment and the full current non-live coverage floor have
their own retained outcomes; this section records implementation and author
evidence, not a runner GO, enablement, done transition or publication authority.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-02-check-exact-offline-amendment`

### Why

Ordinary recovery cannot admit the named correction, and refreshing the old
manifest would erase the distinction between reviewed and offline-amended bytes.

### Goal

Check the exact operator request and return read-only eligibility without
reserving an attempt, modifying its source or accepting an unlisted path.
Reservation and execution remain exclusively in Change 2 after this admission.

### Scope

- Read-only request, source/path/activity admission seams and their isolated tests only; no reservation or runtime-store writes.

### Acceptance

- C1-C2 pass through real files and frozen-record classification; read-only before/after inventory proves zero writes. No reservation or publisher is enabled by this Change.

### Depends On

- none

## Change 2: `chrl-fix-02-serialize-root-lineage-attempt`

### Why

The same root can be reached through recovery descendants and parallel callers;
a request-name directory or a short reservation lock cannot serialize execution.

### Goal

Reserve one accounted root transaction and preserve exact restart state through
child and receipt completion without changing source history.

### Scope

- Root traversal, safe atomic reservation, attempt lock/state/accounting and real competing-process tests.

### Acceptance

- C3-C4 pass; descendant/renamed/concurrent requests cannot obtain another transaction or reset usage. Terminal and unresolved outcomes refuse with original evidence retained.

### Depends On

- Change 1

## Change 3: `chrl-fix-02-bind-adopted-observed-evidence`

### Why

03D rejects raw bootstrap metadata and unbound offline proof; the current draft
has neither admitted source composition nor valid implementation-stage proof.

### Goal

Bind every explicitly adopted plan and fresh observation to one checked attempt
without impersonating ordinary implementation or weakening review/final gates.

### Scope

- Caller-owned source admission, typed finalizer producer, fresh receipt/observation preparation, existing inventory/verdict/final validators and integration tests.

### Acceptance

- C5-C6 pass using real 03D validators and small real check children. Omitted bootstrap criteria, forged producer/metadata, stale bytes and old offline reports refuse; zero publication on any missing proof.

### Depends On

- Change 2

## Change 4: `chrl-fix-02-prove-exact-publication-continuity`

### Why

The existing publisher moves/stages/commits before retaining push outcome. A
retry based only on HEAD can select another destination or duplicate effects.

### Goal

Integrate a durable exact transaction into the existing publisher and prove
restart at every side-effect boundary before enabling the finalizer.

### Scope

- Existing publisher journal and explicit ref push, real isolated Git crash fixtures, ordinary compatibility tests, canonical contract/runbook and final Result/Log.

### Acceptance

- C7-C8 pass, including successful remote push followed by lost local receipt. One exact commit, no wrong ref/remote or automatic repair; only the active card moves. All prior C1-C6 remain green before public enablement and independent acceptance.

### Depends On

- Change 3

## Log

- 2026-09-09T01:31:50Z L2 fixture compatibility correction: the 248-node L
  regression run completed 159 passes/89 failures (all 60 crash cases red).
  Traces identify old test wrappers dropping the new certified writer return,
  missed child interruption points and one diagnostic-regex mismatch. Six
  wrappers now return the real result without changing assertions or fault
  boundaries; the refusal test uses its precise producer diagnostic. All 11
  representative corrected checks passed, including actual child interruption
  and process contenders. No production/schema/profile/ordinary-test change;
  remaining failed scenarios and independent review still have separate proof.
  Original failures, fingerprints and prior Log remain intact. No enablement,
  runner/finalizer/handoff, pilot or actual-checkout publication occurred.

- 2026-09-09T00:49:52Z Scoped L repair after review-08: retained exact manifest
  producer intent before output installation and held required run/manifest
  producer inputs, outputs and no-follow ancestry through each writer's own
  last flush/return. Actual interruption/restart and corruption controls preserve
  original proof, Git state and seven operation identities without repeated work.
  Retained the three original failures, later producer-input failure, 29/24
  intermediate passes, collection-only error and wrong size-test assumption;
  corrected transition verification passed all 99 tests. Current Result/runbook/
  spec distinguish these author mechanisms and exact evidence provenance from
  independent acceptance, full floor and publication. Historical sections/Logs,
  K/K2/review-08 evidence, protected sources and empty index remain unchanged.
  Public finalization stays disabled; no runner/finalizer/handoff, pilot,
  source migration, actual-checkout commit/push or card movement occurred.

- 2026-09-08T23:14:07Z K2 selected verification completed all962 nodes:961
  passed, one fixture setup failed before its intended missing-journal refusal
  because push_uncertain was written without the required root lock. All60
  crash cases passed; both timers ran isolated. Every group is terminal and
  retained. Fixed only that test's setup to use the real attempt lock, preserving
  its original refusal/zero-publish assertions. Production code and all other
  implementation paths remain K2-identical. Recheck the affected fixture family
  and static gates, authenticate exact unchanged production and retained prior
  receipts for review; do not relabel the failed command or old fingerprints.
  The full current-payload floor remains post-independent-acceptance. No new
  production repair, author model, publication, pilot, source migration or
  enablement was performed; all historical evidence/accounting remains.

- 2026-09-08T22:28:58Z Author origin-snapshot follow-up within F22/F23: actual
  pipeline reproduced a double-read creator input gap before independent review.
  Stopped only eight owned pytest workers; retained all terminal exit2 receipts,
  isolated timer success and 133 partial passes, not a successful 959-case run.
  With all checks stopped, made origin comparison and dependency holding consume
  one checked snapshot. Added intact/same-byte/changed-pin pipeline controls.
  Expanded 44-case run passed 43; one new test wrongly required same-byte success
  despite correct outer inode refusal. Preserved that failure, allowed safe
  refusal or file-fsynced success, and all three controls passed. No new author
  or review session, publication, pilot, source migration or enablement occurred.
  Parent-k2 evidence identifies the corrected candidate; all K/J/prior records
  and original immutable card sections remain retained.

- 2026-09-08T22:11:10Z Parent review-07 intent repair: retained NOT ACCEPTED
  assessment, its actual accounting and all prior evidence. Actual reproductions
  exposed before-input replacement at the intent parent's last flush and changed
  active-run repinning after lost intent. Current repair holds the phase-local
  before input, checks the creation producer pin across pre-intent restart, and
  atomically retains manifest pin plus intent. Creation snapshot joins both
  parent and outer closures. Initial 14-case correction passed 11 with three
  premature test interruptions; corrected/expanded 41-case run passed 40 with
  one diagnostic-text mismatch. The final narrow origin/compatibility correction
  passed all 11. Conflicting evidence and all original no-repeat/ref/accounting
  assertions remain. Current Result/runbook/spec distinguish author repair,
  final current checks, independent acceptance, full floor and separate public
  authority. Public flag stays false; no actual checkout publication, pilot,
  source migration, runner/finalizer/handoff or unrelated changes occurred.

- 2026-09-08T20:30:47Z Parent review-06 residual repair: retained NOT ACCEPTED
  assessment, all prior evidence and counted reviewer usage. Three real
  regressions reproduced changed installed-run repinning, an unheld outer
  restart diff and uncertified history copying. Initial correction passed 11
  checks. Expanded diagnostics passed 42; four new intent-failure tests stopped
  at a premature injection point before intent installation. That test-only
  boundary was corrected without weakening its assertions; all 10 installed-
  run/intent and before-install controls then passed. Current mechanisms retain
  a distinct before/after run intent, the shared complete outer dependency group
  and certified history source. Result/runbook/spec describe these boundaries;
  diagnostic counts are not final current-suite proof or independent acceptance.
  Public enablement stays false; no actual checkout publication, pilot, source
  migration, runner/finalizer/handoff or unrelated work was performed.

- 2026-09-08T18:49:35Z Parent review-05 input-closure repair: retained NOT
  ACCEPTED assessment and reviewer accounting. Three actual last-flush input
  replacements reproduced F19/F20. Initial correction passed 12 cases; the
  expanded storage/input/restart matrix passed 104. A further real installed-run
  failure probe reproduced renewal of a changed manifest on restart; its pin is
  now persisted before run installation. Explicit context input groups also
  survive completion/recovery checks, without filename-based dependency discovery.
  The correction passed 16 storage/pin/restart cases. Counts are checkpoint
  evidence, not final acceptance or the full product floor. Current Result and
  runbook distinguish producer/snapshot pins, held inputs/outputs, independent
  assessment and separately authorized publication. Historical sections/logs,
  protected work, clean index/HEAD and enabled=false remain; no actual checkout
  publication, pilot, source migration or runner/finalizer/handoff occurred.

- 2026-09-08T17:28:48Z Parent review-04 output-lifetime repair: retained NOT
  ACCEPTED assessment and actual reviewer accounting. Two actual-pipeline
  regressions reproduced unflushed replacement manifest/terminal-parent outputs.
  The output now joins its input descriptor/content/ancestry closure through
  the final flush for parent, review artifact and session receipt writes.
  Initial diagnostic retained seven real late-window passes and 70 failures
  from applying ownership to dependency-free fixture setup; that compatibility
  correction passed 79 storage/launcher/reservation cases. Seven adaptive storage
  controls locate and replace the output at the very last fsync and all pass.
  These are checkpoints, not independent acceptance or a full product floor.
  Previous logs, protected payload/evidence, index/HEAD and enabled=false remain;
  no actual publication, pilot, source migration or runner/handoff occurred.

- 2026-09-08T16:41:32Z Parent F05 binding correction: the 998-node diagnostic
  ended with 996 passes/two fixture-setup failures; all 60 crash cases passed.
  The two tests now create intentional corruption directly or hold the actual
  root lock for legitimate writes, preserving every original assertion.
  An additional self-check reproduced recomputation of a verdict dependency
  digest; parent retention now consumes its certifying result reference, and
  ended-incomplete retry pins its exact termination reference. Result creation
  compares and hashes the same validated JSON snapshot. The corrected probe
  and 47 focused regressions passed. Those are checkpoint fingerprints, not
  final independent acceptance; all failures and prior evidence remain retained.
  No enablement, actual publication, pilot, source migration or runner handoff.

- 2026-09-08T16:09:08Z Parent review-03 repair candidate: retained NOT ACCEPTED
  assessment (C1/C2/C5/C6/C7 pass; F05/F18 blockers, F14 explanation) and actual
  reviewer accounting. Nine new regressions reproduced dependency-inode and
  outside-temp overwrite failures. Scoped repair holds safely read/flushed
  dependency objects through receipt and parent writes, including recovery;
  offline review lock/manifest/context/diff/history outputs use owned storage.
  Checkpoints retained 39 storage passes, 19 real pipeline/recovery passes and
  83 expanded storage/launcher passes at their respective fingerprints.
  Final current evidence, independent assessment and full product floor remain
  separate. Historical sections/logs, source evidence, protected work and public
  enabled=false are preserved; no pilot, source migration or checkout publication.

- 2026-09-08T15:01:25Z Parent diagnostic/correction: exact 913-case focused run
  retained 826 passes and 87 failures, including the isolated timer control.
  Bounded causes were ambient review destination on journal restart, write-tree
  effects during invalid-index refusal and ordinary launcher/owner-read routing.
  Corrected those without weakening the snapshot or proof assertions. Added
  same-inode temporary-content race refusal and real installed-receipt directory-
  fsync interruption/restart tests; recovery flushes validated dependencies before
  advancement. Correction checks: 47 storage/compatibility cases and 5 actual
  publication continuity cases passed. Historical failed logs stay retained;
  final current evidence and independent acceptance are recorded separately.
  No public enablement, real checkout publication, pilot or source migration.

- 2026-09-08T14:39:12Z Parent review-02 repair candidate: addressed F04/F05/F06/
  F07/F11/F15/F16/F17 in the scoped implementation and expanded genuine restart,
  proof-consumer and Git regressions. Narrow runs retained 42 guard passes,
  15 real review-restart passes, 31 storage/ownership passes and 8 real launcher
  storage passes at their respective fingerprints; they are not one final
  current-payload result. Earlier diagnostic failures remain retained. F14
  current explanation now explicitly records review-02 NOT ACCEPTED and the
  difference between storage-unit and end-to-end proof. Current focused checks,
  independent assessment and the non-live floor are still separate acceptance
  work. Public enabled=false, backlog position, protected history and no actual
  checkout staging/commit/push/pilot authority are unchanged.

- 2026-09-08T13:36:39Z Parent semantic recheck: 10 cases passed; the repaired
  old unit fixture exposed a real zero-success fallthrough for push_uncertain
  without a publication journal. The pre-publication state machine now refuses
  push_uncertain/pushed labels that did not enter journal recovery, and rechecks
  complete final proof for publish_prepared. Added all three label-without-proof
  regressions; genuine journal continuations still use the existing publisher.
  Current full verification and independent acceptance remain separate; no
  public enablement, checkout publication or pilot authority was added.

- 2026-09-08T13:32:13Z Parent combined-current verification retained 774 passes
  and 11 failures across 785 cases. Eight older coupled-forgery tests stopped
  at the newer preparation pin rather than their intended semantic boundary;
  fixtures now coherently alter that copy too, without weakening validators.
  Two unit fixtures now declare the required evidence command configuration.
  The existing 150-ms interruption test failed under parallel load and passed
  alone (1 passed in 2.25s); its code is unchanged and final scheduling isolates
  it. All original failure logs remain retained. Candidate/disabled status,
  protected history and separate independent-review/floor authority are unchanged.

- 2026-09-08T13:19:50Z Parent offline E continuation: corrected the partial E1 claim;
  retained its original report, evidence and session accounting. Genuine public
  review/final receipt-loss and ended-incomplete restart tests reproduced and
  fixed unbound session-metadata reuse. Added exact termination/usage binding,
  live-child contention, post-child source drift and whole-source proof/draft
  refusals; summary-only proof now returns an offline typed-proof error.
  Updated current Result/spec/runbook and fixture path construction without
  scanner exemptions. Latest narrow addendum: 13 passed; prior 14-case restart
  green and 25-pass/one-schema-error diagnostic retained separately. Final
  current checks, independent assessment and floor remain acceptance steps;
  public enabled=false and all publication/pilot prohibitions are unchanged.

- 2026-09-08T12:52:55Z E1 offline reviewer-ownership checkpoint: replaced
  predicted review-session ownership with intent-to-actual-launch binding,
  retained exact context/verdict receipts beside the reaped child, and added
  fail-closed recovery. A real `launch_codex` process-exit fixture (fake model
  transport only) proves incomplete retry and completed-GO reuse without
  duplicating configured preverification. E2 source/post-child/proof coverage,
  E3 docs/final map, independent review, combined current60, repository floor,
  and all publication authority remain outstanding; `enabled=false` unchanged.

- 2026-09-08T12:32:00Z D3C3A correction: the retained five-node RED exposed
  that cached diff text is relative to the deliberately changed `HEAD`, not an
  independent index invariant. The HEAD fixture now compares its actual
  `write-tree` value before and after the expected-old ref update and refusal;
  no worktree/card/index restoration was introduced. The same exact five-node
  selection remains the final focused evidence. Public finalization remains
  disabled; E, independent review, parent combined current60/full floor, and
  publication authority remain outstanding.

- 2026-09-08T12:29:49Z D3C3A bounded repair: replaced the committed-journal
  HEAD-drift fixture's destructive reset with an expected-old `update-ref` to
  the retained parent. The fixture now records and reasserts unchanged index,
  moved-card absence/destination bytes, and all non-Git worktree bytes around
  the isolated ref mutation and after public restart refusal, while preserving
  the no-new-effect assertion. The exact five-node completion selection is the
  HEAD drift plus before-index-stage and after-pushed-run-receipt exception and
  process-exit paths. E, independent review, parent combined current60/full
  floor, and publication authority remain outstanding; public finalization
  remains disabled.

- 2026-09-08T12:13:50Z D3C3 addendum: retained a real RED showing that a
  committed interrupted fixture accepted an extra untracked file. The resumed
  committed/pushed-state validator now refuses any nonempty porcelain state.
  The focused eleven-case genuine restart matrix passes for worktree,
  extra-untracked, index, HEAD, branch, upstream, scope, tree, parent,
  commit-intent, and destination drift, with no next owned effect. The shared
  crash fixture now includes concrete preverification/verification directories
  in preserved bytes and proves the two exact retained receipt identities,
  paths, deterministic command count, and summed duration. E, independent
  review, and parent final floor remain outstanding; public finalization stays
  disabled.

- 2026-09-08T11:59:04Z D3C3 repair checkpoint: replaced the post-move
  drift fixture's swallowed/None ownership with the genuine forwarded root-lock
  owner. Added forked public-entry contenders after a real preverify child,
  during real index staging, and before terminal receipt; each is reaped and
  refuses without changing its observed local/remote state. Added public-route
  ambiguity refusals for multiple push URLs, `insteadOf`, and `pushInsteadOf`,
  genuine restarted prior-ref drift in both directions, and the initial-parent
  rejecting-hook failed-push/retry combination. Retained RED/green focused
  receipts; E, independent review, and parent final floor remain outstanding.
  Public finalization remains disabled.

- 2026-09-08T11:41:57Z D3C2 final accounting correction: configured check
  observations now consume the existing lock-owned authenticated original proof
  view after the active card moves; ordinary no-view ownership checks still
  refuse a missing card. This retains both configured check identities and
  deterministic check duration in terminal accounting. The focused real
  before-index exception recovery passes with the owned view. The retained
  current60 partition receipts prove the preceding payload only; parent owns
  the later combined current-payload matrix after D3C3/E. Public finalization
  remains disabled.

- 2026-09-08T11:22:14Z D3C2 correction/addendum: the first terminal current60
  partition run retained a real references-only RED at before-index-stage
  (exception and process exit), while the other partitions passed. Recovery now
  distinguishes a fully received worktree with a missing index receipt from an
  uncompleted worktree, so it only resumes the original index action. The shared
  crash fixture now also anchors inherited 7/1/2/1/6 usage, one real reviewer
  1/0/1/0 usage record, exact retained session/check receipt bytes, and exactly
  one identity for each successful publication operation. The focused two-node
  replacement passes; public finalization remains disabled.

- 2026-09-08T11:04:23Z D3C2 repair checkpoint: retained a real red
  after-prepared-journal exception regression, then reconciled its original
  prepare/journal identities without a duplicate action; the equivalent real
  process-exit case passes. Added closed typed operation-history validation,
  shared initial/resumed publish-completed accounting, and before/after terminal
  `run.json` receipt exception/process-exit cases. Retained the original56
  exception partition RED (15 pass/13 fail) while repairing its concrete
  duplicate-intent causes; all focused replacement cases recorded in the D3C2
  harness evidence. Public finalization remains disabled; this is not whole-card
  acceptance and no actual checkout publication occurred.

- 2026-09-08T10:19:01Z D3C correction/addendum: the retained combined
  `d3c-prior-ref-drift-and-ledger.json` receipt completed with exit 1 because
  of the literal-backslash regex defect; it was not a timeout. The corrected
  separately retained absent drift case passed. Added genuine interrupted
  public-restart drift refusal and a rejecting disposable-bare-hook same-
  attempt failed-push/retry case; both passed. Existing real-process root-lock
  contender coverage also passed. Public finalization remains disabled; this
  checkpoint is not whole-card acceptance.

- 2026-09-08T10:12:40Z Repair checkpoint D3C: retained a red prior-ref reader
  regression, then added exact absent/parent ref pinning, malformed/foreign
  `ls-remote` refusal, and real disposable-bare-remote deletion/recreation
  drift cases. The publisher now records typed durable preparation/journal/
  worktree/index/commit/push/terminal operation events and preserves them when
  the outer caller resumes; exact terminal manifest/run receipts remain stable.
  Focused harness evidence covers the red-to-green reader, parent transition,
  both drift directions, and closed-ledger rejection. This checkpoint is not
  whole-card acceptance; public finalization remains disabled and no real
  finalizer, runtime/provider/pilot, checkout Git effect, lifecycle action or
  publication occurred.

- 2026-09-08T09:45:41Z D3B repair continuation: retained the failed
  before-pin and staged-index matrix receipts, then repaired both concrete
  recovery gaps. A no-pin `publish_prepared` attempt now resumes via the real
  validated publish gate; a journal still marked prepared but whose exact
  expected worktree and durable index tree already exist is recognized as
  staged before its receipt is retained. Focused before-pin and before-commit
  exception probes pass after the repair. This remains a bounded checkpoint:
  public finalization is disabled and parent-owned D3C/E, independent review,
  and final floor are outstanding.

- 2026-09-08T09:30:05Z Repair checkpoint D3B: added the single exact
  parameterized crash-boundary family for controlled exceptions and real
  owned-child `os._exit` across each required publisher effect and durable
  receipt. Its disposable fixture observes/fsyncs the actual commit and push
  calls, asserts exact local HEAD/tree/parent/index/ref boundary state, and
  preserves all original source-history/request bytes. Repaired the
  live-card-only retry: after canonical finalized bytes are written but before
  the physical move, recovery now accepts only the retained journal's exact
  authenticated partial state, revalidates original proof/admission under the
  owned lock, and otherwise refuses. This checkpoint is not whole-card
  acceptance, review, final floor, or enablement; public finalization remains
  disabled.

- 2026-09-08T09:10:04Z Repair checkpoint D3A: sealed a typed full
  pre-journal publication intent with the independently pinned receipt, then
  recovered that exact intent after real owned child-process exits on both
  sides of journal retention. Canonical reference recovery now replays only
  retained transform after-bytes; admitted support and dirty assertion sources
  retain original proof references while ending at the exact done-card link.
  Focused disposable-Git checks include missing/conflicting preparation and
  altered-reference refusals, plus a reaped child exit after the first of two
  reference writes and exact one-commit/one-push completion. D3B retains the
  before-pin/before-journal and exception-between-reference matrix rows; this
  checkpoint is not whole-card acceptance, review, final floor or enablement.

- 2026-09-08T08:37:19Z Repair checkpoint D2C5 added permanent genuine
  active+supporting pipeline route regressions. After a real move, each
  negative mutates origin.pushurl and the retained staged journal only under
  the restart root lock, preserving original request/source bytes and both
  bare refs; coherent journal diversion and coupled mutable
  creation/attempt diversion both refuse before a new commit or push. The
  request-pinned distinct-pushurl positive retains one commit only on its
  authorized bare endpoint. Existing route code already enforced these
  boundaries, so this checkpoint adds proof rather than a product-code change.
  The card is NOT ACCEPTED: D3/E, parent floor, and independent review remain
  outstanding, and public finalization stays disabled.

- 2026-09-08T08:21:27Z Repair checkpoint D2C4 added the sealed original-proof
  read view for post-publication recovery. It is factory-issued and lock/PID/
  descriptor-bound, supplies only reference-hash-checked original transformed
  source bytes, and threads through the existing inventory, observed proof,
  receipt, v2 GO, and final stage validators. Focused disposable regressions
  retain the prior missing-proof RED, then prove missing proof index/record,
  receipt record/log, review verdict, and final verification each refuse before
  a new effect; supporting proof-record and receipt-log drift introduced under
  the actual restart lock also refuse. Exact clean and dirty move/commit/push
  restarts preserve one commit, the exact ref, and no duplicate push. The card
  is NOT ACCEPTED: parent-owned D3/E, full floor, and independent review remain
  outstanding, and public finalization remains disabled.

- 2026-09-08T07:43:19Z Repair checkpoint D2C3 added the real dirty-active-card
  post-move restart regression. The fixture retains source history first, then
  admits an explicit active-card Result amendment with authentic baseline/new
  states and full payload. The prior missing-card manifest comparison refused;
  it now obtains only that admitted active-card fingerprint from the validated
  journal approved-payload artifact, preserving live checks for every other
  path. Dirty and clean move-restart fixtures pass with one disposable commit
  and exact remote push, no duplicate push, preserved supporting history, and
  preserved amended Result. The card is NOT ACCEPTED: remaining findings stay
  parent-owned and public finalization remains disabled.

- 2026-09-08T07:34:02Z Repair checkpoint D2C2 strengthened the missing-card
  restart branch. It independently reconstructs original request/source-set
  authority from creation-pinned request bytes, retained pre-move card bytes,
  root lineage and source manifest/accounting, then requires immutable
  payload/destination and exact effective push-route agreement. Disposable
  post-move, under-lock request, source-manifest, and supporting-plan mutations
  refuse before an additional commit or push; retained fixture sources are not
  restored or repinned. This is NOT ACCEPTED: parent-owned proof-receipt,
  dirty-active-card, route-coupling, process-window, floor, and independent
  review work remains, and public finalization stays disabled.

- 2026-09-08T07:14:32Z Repair checkpoint D2C1 retained the concrete staged
  coupled payload/tree regression in tracked coverage and bound publication
  transforms to admitted or baseline original bytes/modes. The canonical tree
  now permits only the one receipt-pinned active-to-done card transformation
  and exact eligible board-reference replacements. Disposable Git mutations of
  payload, reference before/after bytes, finalized card bytes, receipt input,
  and extra/omitted/duplicate transforms each refuse before commit/push, while
  normal publication and all existing restart windows pass. This checkpoint is
  NOT ACCEPTED: parent-owned post-move anchors, process-exit matrix, proof
  negatives, final floor, and independent review remain; public finalization
  stays disabled pending independent review.

- 2026-09-08T05:52:36Z Repair checkpoint D2C retained the parent’s actual
  coupled journal/index mutation regression. The publisher now freezes every
  admitted dirty payload byte/mode/deletion state and recomputes the only
  allowed tree from that immutable view plus the recorded transforms. The probe
  reaches its staged unapproved tracked.txt mutation and refuses before a new
  commit/push; ordinary disposable success remains green. Coupled transform and
  destination negatives, original proof/source negatives, process-exit windows,
  and independent review remain outstanding. The card is NOT ACCEPTED and public
  finalization remains disabled pending independent review.

- 2026-09-08T05:38:53Z Repair checkpoint D2B retained a real active+supporting
  publisher route and added hash-bound original/after artifacts before its first
  board/index effect. Public-entry restart tests retain exceptions after a moved
  card, after commit before receipt, and after push before local receipt; each
  recovers the exact disposable commit/ref without publishing a new transaction.
  Hand-written v2 journals now refuse. Process-exit variants and coupled
  source/journal authority negatives remain outstanding; this whole card is NOT
  ACCEPTED and public finalization remains disabled pending independent review.

- 2026-09-08T05:16:44Z Repair checkpoint D2 retained the parent request-route
  concern as a focused check-only regression and changed destination admission
  from fetch URL to the actual single effective push endpoint. Disposable Git
  fixtures prove an unpinned changed `pushurl` refuses before reservation while
  an explicitly request-pinned distinct `pushurl` succeeds through public retry;
  the real active+supporting publisher positive path remains green. Durable
  moved-card reconstruction and representative crash restart coverage remain
  outstanding; the card is NOT ACCEPTED and public finalization is disabled.

- 2026-09-08T05:11:43Z Repair checkpoint D retained a red real bare-remote
  parent-ref retry regression, then repaired the existing publisher's active-card
  deletion scope and durable v2 journal. Focused disposable-Git tests prove the
  genuine C3 active+supporting proof/review/final path commits once and pushes to
  the pinned ref, a public restart accepts the journaled parent, and a distinct
  `pushurl` receives the commit while the fetch remote remains unchanged. URL
  rewrites refuse and public enablement remains false. This does NOT accept the
  whole card: crash/restart and other review findings remain outstanding.

- 2026-09-07T20:31:08Z Repair checkpoint C3 retained the red mode-only
  ordinary-run finalizer-producer/command-lane regression, then required every
  finalizer-shaped or physical attempt consumer to reconstruct creation-pinned
  authority. Reservation now requires a sealed checked-admission snapshot and
  a real held-lock ownership token; copied mappings and caller-made ownership
  fail. Focused fixtures prove partial/missing/copied/stale attempts refuse
  before proof, shared verdict/manifest or child effects; the genuine
  active+backlog-supporting route retains meaningful before/action/after pytest
  assertions, GO reaches the known pre-Git publisher refusal, and NO-GO stops
  before final/publisher. This checkpoint does not accept C1-C8 or Change 4;
  public finalization remains disabled pending independent review.

- 2026-09-07T20:04:30Z Repair checkpoint C2 retained a real disposable-Git
  active+supporting source pipeline: two source-qualified inert assertion
  drafts were bound after small configured pytest child receipts, actual review
  context/launcher used fixture-only transport to record review proof, and the
  real final lane retained final proof. The existing publisher then reproduced
  its exact scope failure after card movement (deleted active path omitted),
  before commit/push. The test itself passed by asserting that failure. The
  harness command ran the green test but could not retain its final record
  because parent-owned `parent-notice-deliveries.json` is malformed; old
  retained records remain untouched. The card remains NOT ACCEPTED and public
  finalization remains disabled.

- 2026-09-07T19:43:11Z Repair checkpoint C retained red regressions for the
  raw 03D proof-record/accounting mismatch and same-named active/supporting C1
  draft collision. It now converts authenticated typed proof-record references
  into the ledger dialect, retains proof-records in owned accounting, refuses
  cross-stage completed-receipt deletion, reconstructs creation-pinned
  request/source/payload/inherited-accounting authority for finalizer
  consumers, and source-qualifies implementation draft ownership. Focused
  offline-finalization and observed-proof tests passed. The complete enabled
  review/final/publisher positive path was not proven in this checkpoint; the
  card remains NOT ACCEPTED, public finalization remains disabled, and no
  lifecycle, pilot, model, production Git or publication action occurred.

- 2026-09-07T19:25:54Z Repair checkpoint B3A: retained the red distinct
  review-intent/actual-launch timestamp regression and corrected completed
  stage recovery. The real review runner/launcher with fixture-only transport
  now retains the later actual session timestamp, reuses a matching GO without
  a new review, validates current evidence before an incomplete retry, and
  reuses exact terminal final-check receipts when the parent stage receipt was
  lost. Unknown ownership and corrupt evidence still refuse. This does NOT
  accept the card: F01 beyond bounded parts and F07-F14 remain outstanding;
  no lifecycle, pilot, model, production Git or publication action occurred.

- 2026-09-07T19:06:49Z Repair checkpoint B3: retained the red false-success
  restart regression for preverify-failed, evidence-preparing,
  final-verification-started and unknown stages. The closed stage boundary now
  validates current mutable owners against creation authority, refuses
  incomplete/terminal/unknown states and missing/corrupt receipts before a
  child, and permits only an exact ended review session with retained transport
  usage to retry the same attempt. Real configured preverify receipt and
  process-lock contender tests cover non-duplication windows. This does NOT
  accept the card: F01 beyond bounded parts and F07-F14 remain outstanding;
  no lifecycle, pilot, model, production Git or publication action occurred.

- 2026-09-07T18:47:16Z Repair checkpoint B2A: retained a red real
  configured-check child plus fake-transport session regression showing that
  owned accounting stored only stage labels. Transitions now carry hash-bound
  checked session/receipt inputs and pure actual usage, lower bounds, command,
  timing and review data; exact reuse is idempotent, changed receipt bytes
  refuse, and a second ended review session remains separate work. Source
  review-budget history is retained from review/context records rather than the
  current profile and is deduplicated across recovery descendants. This does
  NOT accept the card: F01 beyond bounded parts and F06-F14 remain outstanding;
  no lifecycle, pilot, model, production Git or publication action occurred.

- 2026-09-07T18:36:14Z Repair checkpoint B2: retained a red real-session
  check-only regression that rewrote source `metrics.json`, then split pure
  metrics calculation from the ordinary writing builder. Adoption now rejects
  caller-authored/boolean direct usage and partial source sessions, retains
  complete per-run session/command/review/timing accounting plus source anchors
  once across root/descendant lineage, and gives its owned attempt a started
  record and idempotent durable transition ledger. This does NOT accept the
  card: F01 beyond its bounded parts and F06-F14 remain outstanding; no
  lifecycle, pilot, model, production Git or publication action occurred.

- 2026-09-07T18:18:27Z Repair checkpoint B1: retained the red unsafe
  symlink-root/FIFO-lock and lock-acquisition payload-drift reproductions, then
  added descriptor-owned no-follow root/attempt/lock acquisition, one
  root-lineage flock across revalidation/reservation/children, and fsynced
  exclusive-temp initial receipts with a creation-complete anchor. Real-process
  contention, interrupted pre-anchor creation, immutable selection drift, and
  fixture-source writer-format compatibility are focused-test covered. This
  does NOT accept the card: F01 beyond the bounded lock-held subpart, F04, and
  F06-F14 remain outstanding; no lifecycle, pilot, model, production Git or
  publication action occurred.

- 2026-09-07T18:00:42Z Repair checkpoint A2: retained a red legacy-source
  compatibility regression, then admitted pre-`path_states` manifests only
  when an inert no-follow old-byte snapshot (or current matching bytes) exactly
  reproduces the source path fingerprint; later unlisted baseline paths use a
  read-only tree/blob state. Added separate recovery-context predecessor
  fingerprint, payload-path, terminal-code and no-edge regressions. This does
  NOT accept the card: F01 beyond same-byte identity and F04-F14 remain open;
  no lifecycle, pilot, model, production Git or publication action occurred.

- 2026-09-07T17:44:46Z Repair checkpoint A: retained red-to-green regressions
  for the request parse/digest replacement race, missing/false typed source
  inventory, and foreign/context-less recovery lineage. Check-only now hashes
  its one no-follow request snapshot, requires writer-retained path states, and
  binds root/descendant writer-format recovery contexts plus source anchors.
  This does NOT accept the card: only F02, F03 and the same-byte subpart of F01
  are addressed; F01 otherwise and F04-F14 remain outstanding. No lifecycle,
  pilot, model, production Git or publication action occurred.

- 2026-09-07T17:11:51Z Completed the authorized offline repair pass: replaced
  the deferred test-router route with production orchestration behind the named
  default-disabled public flag; grounded lineage/accounting in retained run and
  metrics formats; converted allowed old offline fixtures to closed v2; added
  planned C2/C7/C8 nodes and retained bare-remote retry, frozen/input and
  normal-03D compatibility evidence. The first complete focused run had one
  timing-only SIGINT fixture failure (598 passed); its isolated rerun passed.
  No independent review/GO, pilot, live/native/provider action, production
  model, commit, push or board transition occurred.

- 2026-09-07T16:43:57Z Implemented the explicitly approved offline C1-C8/four-
  Change redesign in the ten scoped paths. Retained focused harness evidence for
  initial collection, C1 admission, C2 root/lock, C3 source/proof and C4 focused
  checks; public finalization remains default-disabled pending independent review.
  No runner/FF/admission event/handoff/GO/recovery/finalizer command, pilot,
  real model, live/native/provider operation, production commit or push occurred.

- 2026-09-07T16:02:49Z Repaired independent offline review F1: Change 1 Goal
  and Scope now explicitly stop at read-only C1-C2 eligibility; reservation
  remains exclusively in Change 2/C3-C4. No implementation or prior Log/evidence
  changes; the original not_accepted assessment remains retained.
- 2026-09-07T15:51:46Z Refined the disabled draft after accepted offline 03D:
  C1-C8 with closed evidence plan and four coherent Change checkpoints. Added
  safe root-lineage admission, full-attempt serialization, explicit finalizer
  producer/source-set authority, declaration-migration precondition and real Git
  crash/restart obligations. Historical failed draft and numeric estimates are
  preserved; implementation of this redesign needs separate approval. No code,
  schema, pilot/source record, board transition or publication changed here.
- 2026-09-05T18:24:39Z Created the operator-requested board-only recovery plan from the stopped FIX-01 pilot and its verified offline amendment. No FF stage/context exists in this operator session; the card is a draft, not measured READY/admission. No implementation, retained-manifest modification, budget reset, live execution or publication.
- 2026-09-05T18:29:05Z Completed planning checks: all 16 template sections are present and nonempty, four requirement/scenario groups, two ordered Changes, all Delivery Budget fields and nine referenced local paths verified. Only this new backlog card was added by the planning step; prior working changes remain preserved.
- 2026-09-05T18:48:12Z Implemented the separately authorized offline repair in the six scoped paths. Added exact request/admission/reservation and bounded finalization tests with fake review/floor/publisher calls; focused `offline_finalization` tests passed. No CHRL lifecycle command, real model session, live runtime call, pilot execution, commit or push occurred.
- 2026-09-05T19:09:35Z Acceptance feedback confirmed material safety/design gaps (frozen activity classification, root-lineage/accounting, immutable request/source parsing, execution serialization, bootstrap verdict enforcement and exact publication retry). Marked this card INCOMPLETE/SPLIT_REQUIRED and disabled both public `finalize-offline` modes before all side effects. No pilot or source artifact was inspected or modified by this correction.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

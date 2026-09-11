# Open-source standalone and shared-core roadmap

## Status
2.todo

## Owner
qa-mcp

## Series
oss-00

## OpenSpec Stage
roadmap / epic

## Source
- Product-model decision on 2026-08-24.
- Follow-up decision to retire source protection for every qa-mcp deployment,
  including server-side AI for 1C cloud use.
- Decision to plan this epic as independently deliverable child cards rather
  than run `$changerail-do` on the whole roadmap.

## Summary
Make qa-mcp a fully open GitHub upstream shared by two products:

- a simple standalone Docker/HTTP MCP with its own open Windows host bridge;
- the more capable AI for 1C cloud product, which consumes a pinned public
  core and adds private Runtime Proxy, Relay, live-mcp, Team, artifact and
  telemetry integrations without forking core behavior.

Retire source compilation, stripping, bundled-data encryption,
protected-image verification and private delivery from the entire active
qa-mcp code base. Open/free distribution does not remove runtime security:
HTTP and bridge authentication, loopback-safe defaults, immutable target
binding, mutation safety and owned cleanup remain mandatory.

## Product Boundaries

### Public upstream `qa-mcp`
- Owns the TestClient protocol/scenario engine, public operation and result
  contracts, standalone tool profile, authenticated HTTP runtime, local
  executors, open protocol assets and independent Windows host bridge.
- Publishes readable Python packages, a source-visible GHCR image and Windows
  bridge artifacts from public source.
- Has no dependency on AI for 1C binaries, proxy, portal, credentials,
  licensing, Runtime Relay/RPW, live-mcp or Team infrastructure.

### Private AI for 1C downstream
- Consumes a pinned semantic version of public qa-mcp, not a fork or copied
  source tree.
- Adds RuntimeProxyExecutor, Relay/RPW sessions, live-mcp access, Team,
  artifacts and telemetry in the owning private repositories.
- Sends generic core fixes upstream first and adopts them by dependency
  update after public release.

## Epic Acceptance
- The public repository contains all source, tests and redistributable assets
  required to build and run standalone qa-mcp and its Windows bridge.
- Active code, dependencies, images, workflows, tests and docs contain no
  Nuitka/source stripping, bundled-data encryption/key, protected-image gate,
  license restriction or private release-portal dependency.
- The public core exposes stable extension contracts and contains no reverse
  import or build-time dependency on private AI for 1C code.
- A clean public clone builds the authenticated standalone HTTP container and
  open Windows bridge using only public inputs.
- A tagged release publishes Python, GHCR and Windows artifacts with checksum,
  SBOM/provenance, compatibility and rollback metadata from one commit.
- AI for 1C passes the public consumer contract against a pinned release.
- Immutable target binding is delivered before public stable promotion.
- `open_external_processor` is present in the stable standalone profile only
  after deterministic target-bound qualification; otherwise it is omitted and
  remains explicit public backlog work.

## Child Cards

| Step | Order | Card | Current state | Depends on |
| --- | ---: | --- | --- | --- |
| 1 | 400 | [Shared-core boundary](../4.done/oss-01-establish-qa-mcp-shared-core-boundary.md) | `4.done`, published | none |
| 2 | 401 | [Retire protected delivery](../4.done/oss-02-retire-qa-mcp-protected-delivery-stack.md) | `4.done`, published | 400 |
| 3 | 402 | [Independent HTTP/Docker runtime](../4.done/oss-03-make-qa-mcp-standalone-http-runtime-independent.md) | `4.done`, published | 400, 401 |
| 4 | 403 | [Immutable runtime-target binding](../4.done/oss-04-bind-testclient-to-declared-project-runtime-target.md) | `4.done`, reviewed and published | 400, frozen shared descriptor contract |
| 5 | 404 | [Open Windows host bridge](../4.done/oss-05-extract-independent-open-windows-host-bridge.md) | `4.done`, reviewed and published | 400 |
| 6 | 405 | [External-processor open flow](oss-06-stabilize-external-processor-open-flow.md) | stable profile/public support omitted by I16 after published I15; dormant foundations retained, I13/S4-R1/S7 incomplete | 403 and 404 complete |
| 7 | 406 | [Public repository readiness](../3.inprogress/oss-07-prepare-qa-mcp-public-repository-readiness.md) | final NO-GO historical source; do not resume | 400-404, published 405 omission decision and published OSS-07-I2 |
| 7.1 | 406.1 | [Public-readiness disclosure and evidence replacement](../4.done/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md) | `4.done`, published at `8e94a21` | safe base `61b8d90`, immutable OSS-07 lineage |
| 8 | 407 | [GitHub/GHCR release train](../1.backlog/oss-08-publish-qa-mcp-github-ghcr-release-train.md) | `1.backlog`; historical base published, corrective publication gates open | 402, 404, 406.1, FIX-10, FIX-11, FIX-12 |
| 9 | 408 | [Stable cutover and downstream adoption](../1.backlog/oss-09-cut-over-qa-mcp-public-stable-and-downstream.md) | `1.backlog`, blocked; needs ff | 403, 407, and 405 delivered or omitted |

## Current Delivery Snapshot

- **2026-09-11:** FIX-07 published at `15ab9a7`: useful observed/missing/ambiguous window outcomes and private predicates through actual default factories/shared MCP/ScenarioRunner. Final 637 focused, 1435 affected offline, one integration, compile, 70 strict specs and diff passed. Actual independent sessions: one interrupted native and one manual cycle-2 GO, with same-thread postarchive confirmation; all 133 native files preserved. Operator-authorized manual completion, not native success. Publication: `.runtime/qa-roadmap/oss-00/fix-07-manual-completion/publication/publication.json`.
- **Next delivery:** FIX-08; current published-source probe proves old-file/false-hash promotion. Prepare one native producer-authority change with actual factory and paused-sibling cleanup proof.

### Previous selection after FIX-06 (retained)

- **2026-09-11 FIX-06 published natively at `79d0b92`: trusted window-list adapter preserves display failure verdicts, generic dictionaries stay data, and direct legacy results remain compatible. Independent cycle 1 and same-thread postarchive GO have no findings. Final checks: 950 offline, one integration, compile, 70 strict specs and diff passed. Publication: `.runtime/changerail/runs/20260911T003123Z-oss-fix-06-preserve-display-failure-verdicts/publication.json`.
- **Next delivery:** FIX-07 is native-admitted with one actual-DTO observation/predicate change. Baseline on `79d0b92` shows success/value={} and matching expected-window assertion false. Preserve privacy, positive reconstruction and unbound compatibility; default single-session BDD remains FIX-09A.

### Previous selection after FIX-05 (retained)

- **2026-09-11 FIX-05 published natively at `8b6a873`: standalone captures retain readable images, while admitted bound sanitized/full_local policy stays intact. Independent cycle 1 and same-thread postarchive GO; final 942 offline and one integration, compile, strict specs and diff passed. Initial model-capacity stop and exact supported resume are retained. Publication: `.runtime/changerail/runs/20260910T234511Z-oss-fix-05-preserve-standalone-screenshot-evidence/publication.json`.
- **Small test-only follow-up:** corrected the screenshot backend fixture to raise actual DisplayBackendError instead of accidental TypeError, with exact type/code/detail precheck; all eight focused tests pass. Separate evidence: `.runtime/qa-roadmap/oss-00/fix-05-fixture-followup/`. Original review/receipts remain unchanged.
- **Next delivery:** FIX-06 is native-admitted with one change/checkpoint on `2405247`; real bound baseline proves typed error becomes success/value={} while ordinary failure and counts remain correct. Execute trusted window-list translation with C1-C3 factory/generic/legacy/privacy proof; continue actual dependencies/order autonomously.

### Previous selection after FIX-04C (retained)

- **2026-09-10 FIX-04C published:** `2a4c159` isolates workspace/default outputs and ownership marker placement/discovery through active application Settings. Both bound/unbound launch branches, explicit/fallback roots, template/capture consumers and same-task root/context restoration are proven. Two native NO-GOs are retained; the final C2 per-owner inventory gap was closed by a bounded test-only manual exception with one separately accounted extra review (total 3) and same-thread postarchive GO. Final checks: 1192 offline, two integration, compile and 70 strict specs. All 199 native run files remain unchanged. Publication: `.runtime/qa-roadmap/oss-00/fix-04c-manual-completion/publication/publication.json`.
- **Next delivery:** FIX-05. Real default and explicit standalone factory screenshots on `2a4c159` still return already-deleted paths. Prepare/admit one native policy-partition change with real factory, admitted bound policy and per-failure inventory proof. Continue the remaining actual cards by dependency/order under the autonomous mandate.

### Previous selection after FIX-03 (retained)

- **2026-09-10 FIX-03 published:** native delivery `f5ad9c0` enforces shared admission independently of result schemas, validates current session generation and malformed context, and blocks unclassified bound extensions. First-cycle NO-GO R1-R3 was repaired; cycle-2 and same-thread postarchive GO accepted C1-C3. Final floor: 1311 offline, one integration, compile and 70 specs. Original finalization stop and supported exact-run resume are retained. Publication: `.runtime/changerail/runs/20260910T203233Z-oss-fix-03-enforce-native-operation-admission/publication.json`.
- **Minor R4 completed separately:** `1046b9f` strengthens one concurrency test after delivery. Exact route/application pairs, counts and context restoration are covered through both MCP dispatch and the actual registered callback. A test-only missing-reset plugin exposed task-isolation masking and is rejected by the callback control; swapped pairs also fail. Final module: 42 offline passes. Evidence: `.runtime/qa-roadmap/oss-00/fix-03-r4-test-followup/final-verification.json`. Original review findings/receipts remain unchanged.
- **Next delivery:** FIX-04C has one native change and one cohesive checkpoint. Three real factory probes reconfirm the process-env workspace/ownership leak on `1046b9f`; native admission is READY and the card is in todo. Preserve bound evidence authority, owned cleanup validation and separate FIX-05/FIX-08 scope. Continue remaining actual cards autonomously by dependencies/order.

### Previous selection after FIX-02 (retained)

- **2026-09-10 FIX-02 published:** `289f432` completes the retained attach-containment card. Same cycle-2 reviewer accepted current C1-C3 and final metadata; zero new independent cycles. Final checks: 215 product offline cases plus one public snapshot/history check, one stdio integration, compilation, 70 strict specs and wiring. All 156 original run files and original archive artifacts are unchanged; interrupted old floor remains unsuccessful. The exact suspended card is hash-pinned inside its archive. Publication: `.runtime/qa-roadmap/oss-00/fix-02-manual-final-completion/publication/publication.json`.
- **Next delivery:** FIX-03 now has completed dependencies and a reproduced no-session native-call defect. Prepare/accept one native admission change, publish planning, then use the installed runner. Continue FIX-04C and subsequent actual cards by dependency/order under the autonomous mandate.

### Previous selection after FIX-04B (retained)

- **2026-09-10 FIX-04B published:** `fd77f05` completes application-owned native relay configuration. Independent cycle 2 and same-thread postarchive confirmation are GO for C1–C4; 1597 affected offline and two integration tests pass. Malformed hosts fail before socket creation; real factories prove exact consumer destination/credential/timeout and context restoration. The accepted-plan deadlock was resolved by the operator-authorized manual exception, preserving the original native run/admission and cycle-1 NO-GO. Evidence/publication: `.runtime/qa-roadmap/oss-00/fix-04b-manual-completion/publication/publication.json`.
- **Current authority and next work:** the operator authorized autonomous completion of the remaining actual OSS-00 product roadmap, resolving implementation questions without repeated requests. Next, complete retained FIX-02 final evidence and same-cycle confirmation before unblocking FIX-03. Its prior cycle-2 GO left C3 pending final; its interrupted old full floor is not completion. Preserve all historical review accounting and source records. Canceled ChangeRail maintenance and superseded aggregates remain outside execution.

### Earlier delivery selections (retained)

- **2026-09-10 next delivery selected:** FIX-04A is published in `54d7bac`; verified runtime/consumer maintenance is `1b7d06c`, and the prepared FIX-04B plan is `bd64e5a`. Main matches remote and is clean. All five no-socket factory observations reconfirm FIX-04B; its own native admission/delivery follows with two ordinary reviews.

- **2026-09-10 FIX-04A accepted:** additional repair 1/5 resolves the full display/list diagnostic family and preserves safe failed-launch cleanup. Independent cycle 4 GO covers all C1–C4. Stock archive and final affected-module verification are complete: 855 offline tests, one integration test, compile and 70 strict specs. Prior three NO-GOs are retained unchanged. Final same-session confirmation/publication receipts belong to `.runtime/qa-roadmap/oss-00/fix-04a-five-repairs/iteration-01/delivery/`; no native completion receipt is invented.
- **Next available card:** FIX-04B has prepared native artifacts; start only after FIX-04A publication and a clean primary main. FIX-02 remains operator-stopped and FIX-03 retains that dependency. Live qualification/release authority is separate.

### Earlier checkpoints retained for history

- **2026-09-10 terminal local exception:** the operator authorized one manual extra review of FIX-04A, with total cap 3. Cycle 3 returned NO-GO: R1–R3 resolved, C1/C2/C4 pass, remaining R4/C3 is process-env mode/availability in composed list diagnostics. Reproduced through real `search_list` with fake HTTP/native replay and sockets/X11 prohibited. The exception is exhausted (3/3); old two-review native history is unchanged. No archive or publication; FIX-04B remains prepared but cannot start over the unfinished payload. A future runtime update alone cannot grant a fourth review.

- **2026-09-10 independent planning checkpoint:** FIX-04B now has one stock native change, four acceptance conditions and ten ordered tasks. Five real-factory no-socket observations reconfirm the process-relay leak. Strict change validation and native admission dry-run are READY; the card remains backlog, with no implementation or actual admission. The old two-change draft/full-suite requirement was replaced with the current focused evidence policy. FIX-04A still occupies the delivery lane with preserved 2/2 reviews; latest available ChangeRail remains rc.3.

- **2026-09-10 manual repair checkpoint:** FIX-04A implementation reached two independent NO-GO verdicts and remains in progress. The operator then authorized a verified ChangeRail update and manual product repairs. Installed runtime is now `2.0.0-rc.3`; retained runs are read-only with both reviews preserved. R1 public error-code normalization and R3 nested exception/request pairing are implemented locally; fresh R2/C1–C4 evidence is recorded under `.runtime/qa-roadmap/oss-00/manual-fix-04a-and-upgrade/`. No GO, archive or publication is claimed. The upstream one-time review-extension card is planning only.

- **2026-09-10 orchestrator handoff:** the operator selected one supervising Codex session and sequential native runner sessions, with roadmap/next-card refresh after each delivery. See `docs/development/oss-00-orchestration.md` and its launch prompt. This preparation reconciles accumulated changes into a clean Git baseline without completing stopped FIX-02. A fresh Codex worker moved four test-selector subprocess cases to integration; the five offline and four integration cases passed separately. No product runtime change or ChangeRail development was performed by this preparation.
- **2026-09-10 current continuation plan:** FIX-02 remains operator-stopped and FIX-03 depends on it. [FIX-04A](../4.done/oss-fix-04a-isolate-display-and-host-agent-settings.md) retains its unfinished delivery and exhausted review history. FIX-04B is the next independent candidate after supported disposition of FIX-04A and a clean delivery lane. FIX-04 remains a superseded aggregate.
- **Current verification/process policy:** T0–T5 test improvements are complete; see `docs/development/test-improvement-results.md` and `docs/development/test-policy.md`. Use affected-module checks, separate offline/integration/live lanes, and reserve full pytest for epic closure or explicit agreement. All CHRL-FIX cards are canceled: consume ChangeRail only as executable tooling. Earlier process-development and FIX-02 continuation instructions below are historical and do not override these operator decisions. This refresh implements no product change and resumes no stopped run.

- **2026-09-09 continuation:** reconciliation published at `05b2b44`; the operator then authorized sequential delivery of the remaining product roadmap, including implementation, review, checks, commit and push. FIX-02 has passed native admission and is the next delivery. Select subsequent cards by actual board state and dependencies; historical workflow recommendations below do not override this direction. Runtime qualification still requires its concrete target/effect admission and real evidence.

- **2026-09-09 direction:** adopt the ordinary native OpenSpec scheme from meta-mcp and return to product work. See `docs/development/native-transition.md`. The previous CHRL-FIX-02-first sequence below is retained historical planning, not the current default queue. FIX-02 now has a native plan; FIX-01 closes through the separately authorized 2026-09-09 reconciliation. The four original frozen records remain unchanged.

- **2026-09-09 finalization:** all current repository changes are included in the operator-authorized reconciliation. FIX-01 is in `4.done`; native FIX-02 is the next product plan. The general offline finalizer remains disabled. The product/ordinary-harness run passed 2280 non-live tests with 74.69% product coverage. Publication additionally requires all 638 historical-finalizer cases, native integration and finding-specific repairs, strict specs, compilation, wiring and the public-source audit; their terminal results are retained with this reconciliation. Fresh final-candidate GO and matching staged bytes gate publication.

### Historical checkpoint before this reconciliation

- Reconciled on **2026-09-07** against the local board, source and retained
  assessments. HEAD remains `e7f7d4f`; implementation and workflow corrections
  below are uncommitted. The only actual active card is the stopped
  [OSS-FIX-01 pilot](../4.done/oss-fix-01-freeze-physical-target-configuration.md).
  Three frozen NO-GO sources and one NOT-VERIFIABLE source remain history, not
  extra active cards. No new card is admitted by this roadmap update.
- CHRL-FIX-03A, 03B1, 03B2-P, 03B2-F, 03C and 03D have independently accepted offline
  implementations; their backlog location is not their implementation state.
  They are not published/done dependencies. 03C's C1-C4 pass and all review
  findings are closed. 03D's two Changes are implemented, C1-C4 pass and its
  independent offline assessment has no open findings. The subsequent separately
  authorized publisher-fixture adaptation is also accepted offline;
  CHRL-FIX-02 finalization remains incomplete and disabled.
  See the workflow checkpoint below before selecting new work.
- The latest 03D checkpoint retained 28 observed-proof and 508 delivery tests,
  70 strict canonical specs, compilation and wiring; independent review added
  five passing finding-specific probes. The later publisher-fixture adaptation
  retained 20 passing tests and its own independent acceptance. These are separate
  scoped results, not a new full product CI/coverage floor or one whole-tree GO.
  The preceding 03C full-floor evidence is **composed**:
  **2247 non-live tests passed** in the full run with **74.69%** `qa_mcp`
  coverage; its sole failed Xvfb test passed separately on unchanged product
  bytes. The full run's exit 1 and the earlier `/tmp` quota failure are retained,
  not rewritten as one green process. The related harness passed 617 tests plus
  14 retained focused tests; 70 strict canonical specs, compilation and wiring
  passed. Condition binding is now accepted offline through 03D; current native
  qualification and release readiness remain separate obligations.
  Editing this roadmap changes the payload fingerprint; retained reviews/floor
  remain evidence for their recorded bytes, not a new GO for the edited tree.
- The 2026-09-05 code review adds the corrective backlog and release gate
  below. Published status is historical delivery evidence, not a fresh
  correctness verdict for the reviewed integration paths.
- Published top-level cards: OSS-01 through OSS-05.
- Published OSS-04 outcome: every bounded reviewed successor through OSS-04F
  is complete; immutable target identity now spans resolution, lifecycle,
  operations, evidence and exact-owned cleanup with Linux/Windows proof.
- OSS-05 is published: the standalone public Windows bridge and exact
  Windows-native lifecycle/display/relay/cleanup proof are complete.
- OSS-06 delivery has published the bounded investigation/authorization and
  S1-R1 through S6 foundations. Final S7 remains apply-ready but incomplete at
  `405.10`; its dormant source/tests/EPFs and foundations are retained. I16
  omits `open_external_processor` from the stable standalone profile/public
  support matrix without claiming S4-R1/S7 certification.
- Published I11 at `964e29f` closes the private S4-R1 main-predicate
  equivalence defect with five paths, 259 production LOC and a complete offline
  proof floor. I12 maps the remaining parent gaps. I13 exact preflight and S3
  passed, but its first tracked S4 row exited before a receipt and protected
  task topology drifted. I14 at `405.10197` ruled out simple inclusion of its
  excluded task, but the historical started-route/harness behavior and external
  drift remain indistinguishable. I15 at `405.10198` then used one authorized
  original-route canary, received no typed Session-1 receipt and invoked no
  candidate; S4-R1 and S7 remain incomplete. I16 records the release-scope
  omission and grants no retry or certification authority.
- OSS-07 remains immutable in `3.inprogress` after final review cycle 3
  `NO-GO`; its same-card rescue budget is exhausted at `2/2`. Linked
  replacement OSS-07-R1 at `406.1` is published at `8e94a21` in `4.done`;
  it owns the public source snapshot and bounded disclosure/evidence-integrity
  repair. The original source card is not another review or repair queue item.
  Published OSS-07-I2 at `61b8d90` is a completed
  design/investigation prerequisite: its byte-frozen matrix and 23 hostile
  mutations close only I1's false-PASS class. The operator selected
  `Apache-2.0`; the first parent change binds that approval and preserves
  I2 without restoring the failed I1 payload. OSS-08 is ready for bounded
  planning; OSS-09 remains blocked on release artifacts and downstream work.
- The exhausted OSS-04 stashes remain local historical lineage evidence only;
  they are not inputs to later implementation.

## Delivery Sequence

```text
400 shared core ✓
├── 401 remove protection ✓ ──> 402 HTTP/Docker ✓
├── 403 target binding: 04A ✓ -> 04B ✓ -> 04C ✓ -> bounded D ✓ -> E/R1 ✓ -> 04F ✓
└── 404 Windows bridge ✓

403 + 404 ──> 405 external processor
400..404 ──> 406 public repository readiness NO-GO ──> 406.1 replacement
402 + 404 + 406.1 ──> 407 GitHub/GHCR release candidate
403 + 407 + (405 delivered OR tool omitted) ──> 408 public stable cutover
```

Cards 401 through 404 are complete. New local runner deliveries are sequential.
Card 405's qualification lineage remains incomplete after I15 admitted no
receipt and kept candidate invocation at zero. Published I16 satisfies the
stable-release fork through explicit tool-profile/public-support omission;
it does not complete I13/S4-R1/S7 or authorize a retry. Card 406 is historical
final-NO-GO lineage; its replacement 406.1 is published. The next release-sequence
story is planning for 407, followed by 408 after its prerequisites. The immediate
engineering queue is the workflow/product correction path below, not publication.

## Corrective Backlog After Published-Stage Review

### Historical workflow prerequisite

The initial readiness check found a blocker caused by four retained legacy
records in `3.inprogress`, not FIX-01's size or dependencies. The separate
[CHRL-FIX-01 plan](../5.canceled/chrl-fix-01-account-for-frozen-legacy-board-records.md)
now has an operator-authorized offline implementation of exact hash-checked
historical classification, shared active-lane guards and source-preserving link
maintenance, published at `17c569d`. The active lane was empty at that checkpoint.
The operator subsequently authorized FIX-01 acceptance and planning publication;
local deterministic FF accepted it on 2026-09-05, published at `e7f7d4f`.
The separately authorized pilot then started at 2026-09-05T17:09:17Z and remains
stopped in `3.inprogress`, with an implemented but unpublished product payload.
Its final-floor failure received an authorized offline correction; the old GO
and manifest do not authenticate the amended payload. Removing numerical budget
limits on 2026-09-06 did not adopt that payload or resume the pilot.
The original four paths/bytes, NO-GO history and I13 NOT-VERIFIABLE state remain
unchanged. This workflow prerequisite is not counted in the product backlog
below and is not a synthetic `4.done` dependency.

### Historical workflow checkpoint and proposed steps — 2026-09-07

`CHRL-FIX-*` names process corrections; `OSS-FIX-*` names product corrections.
In particular, CHRL-FIX-02 is the disabled offline finalizer, whereas OSS-FIX-02
is the still-planned target-bound attach correction. They are different work.

| Work | Observed state | Remaining obligation |
| --- | --- | --- |
| [CHRL-FIX-03A](../5.canceled/chrl-fix-03a-validate-evidence-plans-before-admission.md) | Implemented and independently accepted offline, C1-C8 pass | Preserve exact evidence; no synthetic done/publication |
| [CHRL-FIX-03B1](../5.canceled/chrl-fix-03b1-retain-focused-check-proof.md) | Focused proof implemented and accepted offline, C1-C6 pass | Reuse sole receipt/schema contract |
| [03B2-P](../5.canceled/chrl-fix-03b2p-retain-pre-review-verification-proof.md) then [03B2-F](../5.canceled/chrl-fix-03b2f-retain-final-verification-proof.md) | Both implemented and accepted offline, C1-C6 pass; review findings repaired | No repeated implementation; 03B/03B2 are superseded aggregate plans |
| [CHRL-FIX-03C](../5.canceled/chrl-fix-03c-serialize-verification-attempts.md) | Implemented and independently accepted offline, C1-C4 pass; no open findings | Preserve exact accepted evidence; no repeated implementation, synthetic done or publication |
| [CHRL-FIX-03D](../5.canceled/chrl-fix-03d-bind-acceptance-to-observed-proof.md) | Both Changes implemented and independently accepted offline, C1-C4 pass; no open findings | Preserve exact evidence; no repeated implementation or synthetic done/publication |
| Publisher-fixture adaptation | Separately implemented and independently accepted offline; 20 tests pass | Its own test delta does not promote the earlier 03D assessment to the new whole-tree fingerprint |
| Fixture-link correction | Synthetic paths constructed explicitly in four test modules; original 27 findings now zero, production scanner unchanged | Retain scoped tests/review; real test/product/board links remain checked |
| [CHRL-FIX-02](../5.canceled/chrl-fix-02-finalize-authorized-offline-repair.md) | Incomplete implementation; redesigned C1-C8/four Changes; both public modes disabled | Separately approve the expanded offline scope, including finalizer proof producer and publisher journal, then independently prove all gates before enablement |
| [OSS-FIX-01](../4.done/oss-fix-01-freeze-physical-target-configuration.md) | Stopped pilot; amended offline implementation, unpublished | Fresh explicitly authorized finalization/recovery path for the exact payload; old GO is not reusable |

Recommended engineering order: **accepted offline 03D and publisher fixture →
fixture-link correction/review → CHRL-FIX-02 redesign approval → separately agreed
offline implementation → exact candidate agreement/review → explicitly finalize the amended
OSS-FIX-01 payload → remaining OSS-FIX corrections → native qualification →
OSS-08 → OSS-09**. This is sequencing guidance, not a new literal dependency on
the stopped pilot or permission to execute/finalize it. Review finalizer design
in its own scope; do not make it depend on publishing itself.

The accepted 03C checkpoint covers `run_evidence`, `preverify`, `verify` and
the direct shared floor through one nonblocking run-local lock, including
terminal receipt/index publication and validated completed reuse. A retained
started intent refuses ambiguous restart even with a missing/corrupt receipt;
`interrupted`/`unknown` is not completion. Real competing processes, payload-only
acquisition races, publication-window mutation sensitivity and owned cleanup
were reviewed. This is distinct from the existing review-session lock and
does not add another receipt validator. 03D now adds the common condition inventory,
typed observations, stage-owned gates and exact legacy handling over those receipts.

By operator policy, numerical time/LOC/command/review budgets are informational
for current and future sessions. Historical SPLIT_REQUIRED/overrun records stay
intact, but numeric excess alone no longer requires a split or stops execution.
This does not reactivate superseded cards, remove structural/proof gates,
reset prior accounting, make dirty work exact recovery, or authorize publication.
Before any new implementation, explicitly choose its ordinary offline scope or
an eligible clean runner checkout; the occupied primary tree is not the latter.

Historical integration warning: the whole-dirty-payload reference check reported
27 nonexistent fixture paths, retained in
`.runtime/changerail/roadmap-refresh-20260907-COlzzT/after.json` and reconfirmed
after 03C/03D. The separately authorized continuation now constructs those paths
through `FIXTURE_BOARD` in four test modules; their runtime values are preserved
and the unchanged production scanner reports zero findings. Negative controls
still reject actual broken links in tests, product files and docs, including a
real link alongside synthetic construction. Frozen history remains protected.
This correction removes that integration obstacle, not the finalizer/admission
gates. It is not missing 03C/03D implementation or a full runner GO.

Retained local acceptance evidence (optional on a clean clone):

- 03A: `.runtime/changerail/offline-fix03a-delta-x54SHO/assessment.json`.
- 03B1: `.runtime/changerail/offline-rereview-fix03b1-4x0gJ2/assessment.json`.
- P/F, repaired findings and exact final floor:
  `.runtime/changerail/offline-continue-fix03b2-WkKmHK/completion-report.md`,
  `P/review/assessment.json`, `F2/review/assessment.json` and `final-floor.json`
  under that same evidence root. The reports are not a portable publication
  receipt and are not rewritten by this roadmap refresh.
- 03C: `.runtime/changerail/offline-fix03c-UhUyjW/completion-report.md` and
  `completion.json`; `check-04/review/assessment.json`,
  `check-04/final-check.json` and `check-04/final-floor-composed.json` under that
  same root. The accepted payload fingerprint was
  `sha256:ade8a94aa8e0564afb55b86ffaf5a5950d3eaf1035eb0811c0007d85212914c7`.
  Keep the full failed runs, successful focused rerun and earlier reviews;
  do not rerun their snapshot/completion scripts or overwrite their records.
- This documentation-only continuation delta and preserved-path checks:
  `.runtime/changerail/roadmap-handoff-20260907-tRpAJg/after.json`.
- Subsequent 03D operator refinement: scoped before/after hashes and document
  checks under `.runtime/changerail/plan03d-20260907-BXt2O3/`; this is continuity
  evidence only, not a recovery manifest or a current implementation GO.
- 03D implementation and independent acceptance:
  `.runtime/changerail/offline-fix03d-5Ek6EN/completion-report.md`,
  `completion.json` and `check-04/review/assessment.json` under that root;
  accepted fingerprint `sha256:7b680b603cff2eb6c8f415cc526a0dabf2aedab4fd2b53f9576738965229bcdb`.
- Subsequent publisher-fixture adaptation:
  `.runtime/changerail/offline-publisher-fixture-bXbJi9/report.md`,
  `completion.json` and `review/assessment.json` under that root;
  recorded fingerprint `sha256:130a1db71225fb3c31b3e578f76b5ecf28aca055d8a0cd0f8f8b48fc7a56d0b0`.
  This closes the earlier fixture-setup limitation, not the separate 27 links.
- Subsequent roadmap/fixture-link correction and finalizer redesign planning:
  `.runtime/changerail/roadmap-next-L1dgyZ9e/` retains the before snapshot,
  scoped diffs, checks, independent review and completion when available. Missing
  completion/review records are not acceptance. This is not a recovery manifest.

The [new-session prompt](../../../docs/development/roadmap-continuation-prompt.md)
records the post-03D checkpoint and remaining scoped work. Old 03D planning
instructions are superseded, not a reason to repeat implementation. It carries no
implementation, finalization, publication or pilot authority. Check temporary
storage and quota before costly verification; do not clean unrelated data.

### Product corrective backlog

The operator requested corrective planning on 2026-09-05. The review reproduced
ten defects at `8e46aa5` despite the existing floor passing 1730 tests with
74.67% coverage. The publication history above remains valid, but its old
`done` states alone do not prove current correctness or readiness.

As of the 2026-09-11 post-FIX-07 refresh, the corrective set has nine completed
corrections in `4.done` (FIX-01, FIX-02, FIX-03, FIX-04A, FIX-04B, FIX-04C, FIX-05, FIX-06, FIX-07), with native
stops and manual exceptions preserved separately, and seven remaining plans
(five Python corrections and two native qualification cards),
plus two retained superseded aggregates, FIX-04 and FIX-09. FIX-01 closes R9 through the operator-authorized one-off reconciliation; its stopped pilot remains separate history. Successors
restate their symptoms, desired-behavior scenarios, canonical contracts, ordered
checkpoints, dependencies and estimates; ignored local audit files are optional
context, not clean-clone prerequisites.

| Order | Card | Finding / invariant | Depends on |
| --- | --- | --- | --- |
| 406.20 | [FIX-01](../4.done/oss-fix-01-freeze-physical-target-configuration.md) | R9: immutable physical configuration, one-off reconciliation complete | none |
| 406.21 | [FIX-02](../4.done/oss-fix-02-reject-unproven-project-attach.md) | R8: containment complete; published `289f432`, retained old floor | FIX-01 |
| 406.22 | [FIX-03](../4.done/oss-fix-03-enforce-native-operation-admission.md) | R2: native admission delivered `f5ad9c0`; minor test follow-up `1046b9f` | FIX-01, FIX-02 |
| 406.23 | [FIX-04](../1.backlog/oss-fix-04-isolate-application-runtime-configuration.md) | Superseded R4 aggregate; not executable | See FIX-04A/B/C |
| 406.231 | [FIX-04A](../4.done/oss-fix-04a-isolate-display-and-host-agent-settings.md) | R4: completed; independent cycle-4 GO after operator-authorized repair 1/5 | none |
| 406.232 | [FIX-04B](../4.done/oss-fix-04b-isolate-testclient-transport-settings.md) | R4: published `fd77f05`; scoped transport and exact factory evidence, cycle-2 GO | none |
| 406.233 | [FIX-04C](../4.done/oss-fix-04c-isolate-workspace-and-ownership-roots.md) | R4: workspace/ownership roots | FIX-04B |
| 406.24 | [FIX-05](../4.done/oss-fix-05-preserve-standalone-screenshot-evidence.md) | published `8b6a873`; R1 standalone screenshot retention | FIX-04C |
| 406.25 | [FIX-06](../4.done/oss-fix-06-preserve-display-failure-verdicts.md) | published `79d0b92`; truthful display failure verdicts | none |
| 406.26 | [FIX-07](../4.done/oss-fix-07-make-bound-window-reads-useful.md) | published `15ab9a7`; R6: useful private-safe active-window outcomes | FIX-06 |
| 406.27 | [FIX-08](../1.backlog/oss-fix-08-bind-artifacts-at-trusted-production.md) | R7: trusted producer artifact receipts | FIX-05, FIX-06, FIX-07 |
| 406.28 | [FIX-09](../1.backlog/oss-fix-09-unify-default-bdd-operation-boundary.md) | Superseded R3 aggregate; not executable | See FIX-09A/B/C |
| 406.281 | [FIX-09A](../1.backlog/oss-fix-09a-admit-default-bdd-session-and-reads.md) | R3: default admission, reads/assertions and result policy | FIX-03, FIX-04B, FIX-04C, FIX-07, FIX-08 |
| 406.282 | [FIX-09B](../1.backlog/oss-fix-09b-admit-stateful-and-nested-bdd-steps.md) | R3: stateful and nested steps | FIX-09A, FIX-04A |
| 406.283 | [FIX-09C](../1.backlog/oss-fix-09c-control-session-independent-bdd-steps.md) | R3: local and optional provider steps | FIX-09A |
| 406.29 | [FIX-10](../1.backlog/oss-fix-10-scan-decoded-json-credential-assignments.md) | R10: decoded JSON credential scanning | none |
| 406.30 | [FIX-11](../1.backlog/oss-fix-11-verify-corrected-linux-runtime.md) | Final Linux qualification and cleanup | FIX-01–03, FIX-04A/B/C, FIX-05–08, FIX-09A/B/C |
| 406.31 | [FIX-12](../1.backlog/oss-fix-12-verify-corrected-windows-runtime.md) | Final Windows/Python qualification and cleanup | FIX-01–03, FIX-04A/B/C, FIX-05–08, FIX-09A/B/C |

FIX-04 and FIX-09 retain their original above-limit budgets and SPLIT_REQUIRED
history; they are not runner inputs or done prerequisites. The six successors
now own the complete boundaries: display, transport and filesystem ownership
for R4; default guarded reads, stateful/nested work and local/provider policy
for R3. Their budgets remain provisional informational estimates; structural,
dependency and clean-fingerprint admission still apply. Shared files are delivered sequentially,
not by competing writers. No generic execution framework or wire rewrite is planned.

FIX-09A provides useful guarded reads and blocks every unintegrated composed
step family. FIX-09B/C remove only their own blocks through that same dispatcher.
A partial safe slice, a skipped provider capability or an aggregate label cannot
close the complete finding or release gate. FIX-11/FIX-12 reference all six
successors directly. Existing native support and explicit unsupported cases must
remain distinguishable in reports and downstream claims.

FIX-02 is explicitly containment: unproven non-owned project attach is blocked;
owned launch and unbound compatibility remain supported. General non-owned
bound attach is not declared repaired or qualified until a separately reviewed
observer contract proves current identity. Do not copy a declaration and call
it observation.

### Corrective release gate

Release automation can be planned while corrections are in backlog, but
publication and stable promotion must not rely only on former OSS-01/04/05/07
completion. OSS-08 now depends on FIX-10 and both final qualification cards,
which transitively require the runtime corrections, including all six named
FIX-04A/B/C and FIX-09A/B/C successors. Resolve their final delivered identities
and source/artifact fingerprints before publication; older
native evidence is not current proof after affected behavior changes.
OSS-09 inherits this gate, actual stable tool-omission enforcement and the
separately owned pinned downstream acceptance requirement.

These are hermetic Python-side implementation plans plus two separately
authorized native qualification contours. No live 1C/Windows operation,
business mutation, commit or push is authorized by this planning request.
The existing clean-tracked/single-active gates and separate migration pilot
approval remain in force. Historical done/canceled records are unchanged.

Additional telemetry coupling and large-module/readability debt remain
architectural follow-up, not hidden acceptance inside these ten review findings.
No broad rewrite or dormant OSS-06 reactivation is included. I16's declared
63-tool stable support decision remains in force.

## Change Set
- none: this parent roadmap is not a `chrl-run` input.
- Each child owns its board-local Changes, verification and independent review;
  the authorized outer runner alone owns done, commit and push.

## Verify
- Every child completes risk-appropriate tests and strict canonical-spec
  validation before its authorized done/publication boundary. New lifecycle
  artifacts are not created, synced or archived; old `openspec/changes` is frozen.
- Cards 406-408 additionally prove disclosure safety, exact public artifacts
  and downstream pinned-version adoption.
- Epic closure checks every Epic Acceptance item against child delivery and
  published release evidence, not planning status or historical test counts.

## Archive
- not started; close only after all mandatory child cards are completed and
  card 405 is either completed or explicitly omitted from the stable profile.

## Related
- `openspec/board/1.backlog/product-v1-runtime-proxy-qa-execution.md`
- Suite-root card `runtime-proxy-v1-qa-adapter-epic`.

## Result

2026-09-11: FIX-07 published at `15ab9a7`: useful observed/missing/ambiguous window outcomes and private predicates through actual default factories/shared MCP/ScenarioRunner. Final 637 focused, 1435 affected offline, one integration, compile, 70 strict specs and diff passed. Actual independent sessions: one interrupted native and one manual cycle-2 GO, with same-thread postarchive confirmation; all 133 native files preserved. Operator-authorized manual completion, not native success. Publication: `.runtime/qa-roadmap/oss-00/fix-07-manual-completion/publication/publication.json`. FIX-08 is the next available card; source applicability and native plan preparation are retained separately.

### Previous result after FIX-06 (retained)

2026-09-11: FIX-06 published natively at `79d0b92`: trusted window-list adapter preserves display failure verdicts, generic dictionaries stay data, and direct legacy results remain compatible. Independent cycle 1 and same-thread postarchive GO have no findings. Final checks: 950 offline, one integration, compile, 70 strict specs and diff passed. Publication: `.runtime/changerail/runs/20260911T003123Z-oss-fix-06-preserve-display-failure-verdicts/publication.json`. FIX-07 is reproduced with actual DTOs and admitted as the next native change.

Previous result after FIX-05 (retained):

2026-09-11: FIX-05 published natively at `8b6a873`: standalone captures retain readable images, while admitted bound sanitized/full_local policy stays intact. Independent cycle 1 and same-thread postarchive GO; final 942 offline and one integration, compile, strict specs and diff passed. Initial model-capacity stop and exact supported resume are retained. Publication: `.runtime/changerail/runs/20260910T234511Z-oss-fix-05-preserve-standalone-screenshot-evidence/publication.json`. The separate fixture correction proves the intended typed backend exception with eight focused offline passes. FIX-06 is next.

Previous result after FIX-04C (retained):

2026-09-10: FIX-04C published at `2a4c159`. Native two-review NO-GO history is
preserved; one separately accounted manual C2 evidence repair/review and
same-thread final confirmation accepted C1-C3. Final affected checks: 1192
offline, two integration, compile and 70 specs. Next FIX-05 is reproduced on
that clean published source; one native policy-partition plan is prepared.

Previous result after FIX-03 (retained):

2026-09-10: FIX-03 published natively at `f5ad9c0`; two independent cycles and
same-cycle postarchive confirmation preserve the original NO-GO and supported
resume history. Final affected checks pass 1311 offline and one integration.
Minor test-only R4 follow-up is separately published at `1046b9f`, with 42 offline
passes and sensitive pairing/reset controls. FIX-04C is prepared next on the
reconfirmed workspace/ownership-root defect.

Previous result after FIX-02 (retained):

2026-09-10: FIX-02 published `289f432` after same-cycle current C1-C3 GO and final
metadata confirmation. All original history remains exact; no native resume or
old successful floor was invented. Final checks: 216 offline and 1 integration,
compile, 70 specs and wiring. FIX-03 is now available and its no-session defect
is reconfirmed through real registration with fake native effects.

Previous result after FIX-04B (retained):

2026-09-10: FIX-04B published in `fd77f05`; main and origin/main matched with a
clean tree after publication. Its manual completion retains the task-plan stop,
first NO-GO and both independent cycles. Final checks: 1597 offline, 2 integration,
compilation and 70 strict canonical specs. The operator's autonomous continuation
now selects FIX-02's remaining final evidence, then FIX-03 on completed dependency.

Earlier results (retained):


2026-09-10: FIX-04A completed the first of five additionally authorized repairs
and independent cycle 4 returned GO on C1–C4. The full list diagnostic family,
legacy compatibility and failed-launch cleanup are covered. Final postarchive
checks pass 855 offline and one integration case; strict specs, compile and
wiring pass. ChangeRail remains the verified executable rc.3 dependency.
Publication and exact final confirmation are recorded in the delivery evidence
root above. FIX-04B is the next prepared native candidate.

Earlier checkpoints (retained):

2026-09-10: the targeted manual exception was executed and ended in independent
NO-GO at cycle 3. Remaining R4 affects list diagnostic mode/availability; the
previous three findings are resolved. FIX-04A is not delivered and the exception
has no remaining attempt. Full retained result:
`.runtime/qa-roadmap/oss-00/fix-04a-operator-exception/terminal.json`.

2026-09-10 independent planning progressed FIX-04B to complete native artifacts
without moving it from backlog or implementing product changes. Defect
reproduction, strict validation and dry-run READY are retained under
`.runtime/qa-roadmap/oss-00/fix-04b-planning/`. This does not satisfy FIX-04A
review or publication gates.

2026-09-10 manual repair checkpoint: FIX-01 remains complete; FIX-02 is stopped
and FIX-03 retains that unresolved dependency. FIX-04A has completed implementation
and two independent reviews, with final NO-GO on C3. The operator authorized
manual R1/R3 fixes and fresh R2 evidence, now prepared locally alongside the
verified `2.0.0-rc.3` runtime installation. Evidence and exact validation results:
`.runtime/qa-roadmap/oss-00/manual-fix-04a-and-upgrade/completion.json`.
Both historical verdicts and attempt accounting remain unchanged. There is no
fresh GO, archive, final floor, product commit or push. Supported additional
review requires the separately planned ChangeRail exception mechanism; the
upgrade does not supply it. T0–T5 remains complete; native qualification and
release/cutover remain open.

Published milestones: OSS-01 through OSS-05 are published to `main`. The
standalone shared core, retired protected stack, authenticated HTTP/Docker
runtime, immutable runtime-target binding and independent public Windows host
bridge are published milestones, not a current correctness verdict. The
2026-09-05 review reproduced ten defects; FIX-01 through FIX-12 now define the
corrective work and fresh release qualification. OSS-06 has published the I11 private predicate correction;
exact I13 certification, the S4-R1 parent review/publication and final S7
certification remain incomplete after I15 admitted no Session-1 receipt or
candidate invocation. I16 records the explicit stable-profile/public-support
omission while preserving the dormant implementation and published
foundations.

## Next
- Admit/publish the FIX-08 producer-authority plan, then clean-start doctor/chrl-run with actual factory, exact failure and concurrency ownership proof.
- Continue FIX-09A/B/C and remaining actual cards by dependencies and Order Index. Preserve stopped/superseded sources, native attempts and separately counted local exceptions.
- Keep sync/handoff/archive/publication outside implementation checkboxes. Finalizers refresh typed proof after sync/Result/Log and archive using verbose terminal node receipts; recovered runs retain their own sync receipt. Test exact paired factory/consumer observations and meaningful negative controls.
- Resolve ordinary implementation/planning questions autonomously under the 2026-09-10 mandate. Preserve evidence, review accounting, one writer and target/preflight/recovery requirements; canceled ChangeRail maintenance and superseded aggregates remain excluded.

## Historical publication preparation after offline work

Historical proposed finalizer sequence below is superseded as the default next work by `docs/development/native-transition.md`; the exact evidence and publication gates remain mandatory.

This is a concrete preparation sequence, not authority to publish the dirty
tree or to mark its cards done. 03C and 03D are accepted offline; 03D corrects
the chosen delivery process, not a missing feature of 03C itself. The current
tree combines overlapping ownership in `scripts/changerail/local_delivery.py`,
its tests, guidance and canonical wiring spec, so whole-file staging would not
isolate 03C. The final exact candidate can only be frozen after the separately
authorized implementation/integration work below.

| Candidate unit | Current state and scope to reconcile | Publication evidence still needed |
| --- | --- | --- |
| Operator policy and CHRL-FIX-03A/B1/B2-P/B2-F/03C | Unpublished shared runner/FF code, schemas, tests and guidance; offline acceptance is retained for its recorded bytes | Explicitly list included hunks/paths and policy changes; map each accepted condition to the final candidate without promoting old GO |
| CHRL-FIX-03D and later publisher-fixture adaptation | Implemented and independently accepted offline at their respective recorded fingerprints | Map retained C1-C4 evidence and the separately reviewed test delta to the final candidate; old acceptance is not a fresh whole-tree GO |
| CHRL-FIX-02 and fixture-link integration | Finalizer redesigned but incomplete/disabled; original 27 findings corrected through test-only path construction | Approve expanded offline finalizer scope; prove exact lineage/adoption, 03D producer ownership and publication recovery; retain fixture correction evidence separately |
| Stopped OSS-FIX-01 | Unpublished target-configuration correction in `core/application.py`, `core/runtime_target.py`, `mcp_server.py`, affected tests/specs/policy and active card | Resolve original versus amended bytes against retained source; separately approve the exact finalization request and included support plans |
| Planning/guidance deltas | Board cards, roadmap/README, continuation prompt and process guidance | Enumerate their final hashes and provenance, retain historical logs; board text never supplies execution proof |

1. Preserve completed 03D C1-C4 acceptance and the later publisher-fixture
   acceptance at their recorded bytes. Neither included the finalizer or
   fixture-link correction; those remain separately attributable work.
2. Complete CHRL-FIX-02 and the separate fixture-reference correction under their
   own agreed scopes. Require actual bootstrap/adoption/publication evidence and
   genuine live-link negative controls. Leave the pilot stopped meanwhile.
3. Build a reviewable candidate from the retained baseline HEAD and current
   per-path/hunk provenance. For shared files, show the combined final delta and
   assign every included change to one unit above; list anything excluded and
   how it remains preserved. Use an isolated candidate if useful. Never infer
   adoption from a whole-file commit or clean the source checkout to pass a gate.
4. Obtain explicit agreement on that exact candidate and publication route,
   including auxiliary policy/runner/fixture changes and the stopped-card
   transition. Ordinary offline acceptance, this table and elapsed budget do
   not supply adoption or commit/push authority. Preserve old pilot manifests;
   a new scope index is not a refreshed recovery manifest.
5. On the frozen candidate, perform independent review with complete acceptance
   mapping and final configured checks. Revalidate 03D observations, all included
   corrections, source hashes and exact publication/restart preconditions; use
   new evidence for changed bytes and retain every earlier failed attempt.
   The known fixture-link failures must be resolved for full runner integration.
6. Only through the separately authorized, proven finalization transaction,
   perform the exact commit/push and appropriate card transitions. Verify commit
   identity and remote result; retain restart state on uncertainty. A separate
   ordinary Git snapshot route would need its own explicit agreed scope and
   checks and would not automatically make backlog cards done.

The current decision is step 2's redesigned finalizer implementation scope, not step 6.
No exact publication hash or recovery/adoption request is fabricated while its
required candidate changes remain unimplemented.

## Continuation Preconditions

- I16 and OSS-07-R1 are published. Do not treat retained foundations as
  hidden-route certification or resume exhausted source cards. Board inventory
  and planning do not authorize runtime retries or release publication.
- Full delivery requires clean synchronized `main`, satisfied dependencies and
  one active card through `./bin/chrl-run`. The present dirty/occupied tree is
  restricted to explicitly scoped ordinary offline work, not automatic recovery.
- The exhausted OSS-04 stashes remain historical lineage evidence only; do not
  restore or merge them into later cards.
- OSS-05 retains its own exact Windows build/lifecycle/display/recovery and
  owned-cleanup verification floor.
- Before stable release planning, record the OSS-06 delivered-or-omitted
  decision. No credentials or connection strings belong in Git or chat.

## Change Plan Notes
- Runtime Proxy/RPW, live-mcp, Team and AI for 1C cloud implementation stay in
  their owning private repositories. This epic owns only neutral public
  contracts and a downstream consumer fixture.
- Do not rewrite archived board/change history to erase former protection or
  licensing decisions. Remove obsolete behavior from active surfaces and
  document the superseding product model.
- The former all-in-one publication change is intentionally split across
  cards 406-408 and must be fast-forwarded one card at a time.

## Log

- 2026-09-11 FIX-07 published at `15ab9a7`: useful observed/missing/ambiguous window outcomes and private predicates through actual default factories/shared MCP/ScenarioRunner. Final 637 focused, 1435 affected offline, one integration, compile, 70 strict specs and diff passed. Actual independent sessions: one interrupted native and one manual cycle-2 GO, with same-thread postarchive confirmation; all 133 native files preserved. Operator-authorized manual completion, not native success. Publication: `.runtime/qa-roadmap/oss-00/fix-07-manual-completion/publication/publication.json`. Prepared FIX-08 on the clean published source with old-file/false-hash reproduction and coherent native C1-C3 plan.

- 2026-09-11 FIX-06 published natively at `79d0b92`: trusted window-list adapter preserves display failure verdicts, generic dictionaries stay data, and direct legacy results remain compatible. Independent cycle 1 and same-thread postarchive GO have no findings. Final checks: 950 offline, one integration, compile, 70 strict specs and diff passed. Publication: `.runtime/changerail/runs/20260911T003123Z-oss-fix-06-preserve-display-failure-verdicts/publication.json`. Reproduced FIX-07 with actual InitialUiContext/ActiveWindowContext and default executor/ScenarioRunner; prepared and admitted one native change with explicit safe states/predicate semantics and preserved class/public-boundary controls.

- 2026-09-11 Admitted FIX-06 as one native change/checkpoint after real composed typed/ordinary/empty/nonempty reproduction on `2405247`. Strict stock validation and closed C1-C3 evidence admission READY; focused policy replaces the historical full-suite draft.

- 2026-09-11 FIX-05 published natively at `8b6a873`: standalone captures retain readable images, while admitted bound sanitized/full_local policy stays intact. Independent cycle 1 and same-thread postarchive GO; final 942 offline and one integration, compile, strict specs and diff passed. Initial model-capacity stop and exact supported resume are retained. Publication: `.runtime/changerail/runs/20260910T234511Z-oss-fix-05-preserve-standalone-screenshot-evidence/publication.json`. Small fix without a card: corrected the test-only typed exception fixture and added a constructor precheck, with 2 targeted and 8 module passes and original-constructor negative control; no new independent review or changes to historical receipts. Selected FIX-06.

- 2026-09-10 Published FIX-04C at `2a4c159`: both native NO-GOs and 199 run files preserved; last per-owner C2 inventory gap repaired with a scoped test-only worker, sensitive foreign-marker mutation and one separately counted additional independent GO plus same-thread final confirmation. Final 1192 offline/2 integration/compile/70 specs passed. Selected FIX-05 and reproduced default/explicit returned paths already deleted through the real standalone factory; prepared one native change with coherent test selectors and focused policy/failure proof.

- 2026-09-10 Published FIX-03 natively at `f5ad9c0`: supported exact-run recovery refreshed proof after semantic sync; cycle-1 NO-GO R1-R3 repaired, cycle-2/postarchive GO, final 1311 offline/1 integration/compile/70 specs passed. Separately completed nonblocking R4 through a bounded test-only worker and supervisor strengthening at `1046b9f`: full paired routes/counts and same-scope restoration, sensitive missing-reset and swapped-pair controls, 42 offline passes. Selected FIX-04C and reconfirmed A/B/empty factory roots all resolving process env; prepared one native change with explicit final proof refresh guidance.

- 2026-09-10 Published FIX-02 at `289f432` through authorized manual final completion. Same cycle-2 reviewer accepted current C1-C3 and metadata; final 216 offline/1 integration, compile/spec/wiring passed. Preserved all 156 old run files, unsuccessful interrupted floor and exact suspended source in the hash-pinned archive. Selected FIX-03; real registered no-session click_command still reached its substituted native handler, confirming the defect before native planning.

- 2026-09-10 Published FIX-04B at `fd77f05` through the approved manual completion exception after a circular accepted task blocked native finalization. Preserved original run/admission, repaired review-cycle-1 F1/F2 with sensitive factory regressions, obtained cycle-2/prearchive and same-thread/postarchive GO, stock-archived exact artifacts and passed final 1597 offline + 2 integration checks. Updated active dependency links. Operator authorized autonomous completion of the remaining roadmap; next is retained FIX-02 final evidence, without treating old GO as current completion.

- 2026-09-10 Verified FIX-04A publication and clean remote `bd64e5a`. Reconfirmed FIX-04B through five real factories with sockets prohibited; refreshed its stale lane-blocker notes without changing acceptance or scope. Selected ordinary native admission/delivery under the standing OSS-00 authorization.

- 2026-09-10 Applied the operator's five-repair grant to comprehensive FIX-04A repair 1/5. Added 39 list-family and 28 failed-launch cleanup regressions, corrected stale QA consumer expectations, retained failed runs and refreshed source-bound evidence. Independent cycle 4 GO; stock archive and 855 offline + 1 integration final checks passed. No live runtime or ChangeRail development; same-session final confirmation and publication use the separate delivery ledger.
- 2026-09-10 Executed the explicit one-time local exception for FIX-04A without modifying installed ChangeRail or old receipts. Reserved cycle 3 before launch; fresh independent reviewer returned complete NO-GO with R4/C3, confirming R1–R3 resolved. Recorded terminal 3/3 accounting, exact unchanged payload, synthetic reproduction and source scope; no archive, fourth review, commit or push.
- 2026-09-10 Continued available OSS-00 planning while FIX-04A remains stopped. Rechecked main/remote, no writer, wiring and latest release; rc.3 still has no extra-review feature. Reproduced FIX-04B through five explicit factory settings with sockets prohibited, created one native change and closed evidence plan, passed strict validation and admission dry-run. No product edits, actual admission, runner, review, commit or push.
- 2026-09-10 Operator authorized the latest ChangeRail installation and manual FIX-04A repair. Installed verified rc.3, preserved predecessor bytes and 2/2 reviews, repaired R1/R3 and refreshed explicit C2 replacement/blocked-attach evidence. Upstream review-extension backlog card created separately; no runtime development, third review, archive or product publication. Retained manual evidence: `.runtime/qa-roadmap/oss-00/manual-fix-04a-and-upgrade/`.
- 2026-09-10 Started authorized OSS-00 orchestration from clean published `637e3aa`. Verified remote, writer ownership, installation content/wiring and repeated FIX-04A offline relevance; native dry-run READY. Refreshed baseline/authority notes without changing C1–C4 or product scope. Native admission moved FIX-04A to todo; preparing its separate planning commit/push.
- 2026-09-07T15:51:46Z Corrected the 27 synthetic fixture references without
  changing the production scanner, added genuine-link negative controls and
  refined disabled CHRL-FIX-02 into C1-C8/four Changes with explicit 03D and
  publisher-continuity obligations. Evidence retained under
  `.runtime/changerail/roadmap-next-L1dgyZ9e/`. No finalizer implementation,
  pilot/source mutation, board movement or publication in this continuation.
- 2026-09-07T15:42:44Z Reconciled accepted offline 03D (C1-C4) and the later
  independently accepted publisher-fixture adaptation with their retained reports.
  The operator approved the staged continuation plan. Started roadmap refresh,
  separate fixture-link correction and finalizer redesign planning; no pilot,
  source-manifest refresh, card transition or publication authorized by this update.
- 2026-09-07T07:41:01Z Completed operator-only 03D plan refinement against
  accepted offline interfaces: one C1-C4 invariant/two Changes, stage-aware
  typed proof and explicit activation/legacy policy. Added publication candidate
  units and six preparation gates for the accumulated overlapping changes.
  Next is separate 03D implementation authorization. Retained all prior logs,
  statuses and evidence; no code/spec/schema/skill implementation, runner,
  finalizer, pilot, staging, commit or push.
- 2026-09-07T07:16:05Z Reconciled accepted offline 03C and composed verification
  (2247 full-run passes plus its sole Xvfb rerun, coverage 74.69%). Advanced the
  immediate queue to 03D planning; retained unpublished/backlog state, stopped
  OSS-FIX-01, disabled finalizer and the independently rechecked 27 fixture-link
  findings. Added a bounded new-session prompt. Documentation only; no code,
  card moves, semantic re-review, runner action, pilot, commit or push.
- 2026-09-07T03:13:08Z Reconciled roadmap at operator request against current
  card locations, exact accepted offline assessments and the retained 2212-test
  floor. Corrected stopped FIX-01/occupied lane, added completed 03A/03B1/P/F and
  open 03C/03D/finalizer sequencing, distinguished CHRL/OSS namespaces and
  superseded numerical stop rules. Recorded the pre-existing fixture-reference
  integration warning separately from 03C. Board documentation only; no card move,
  implementation, new semantic verdict, pilot, finalizer, commit or push.
- 2026-09-05T16:14:23Z Operator-authorized deterministic FF accepted FIX-01
  from clean `17c569d`: READY, two Change checkpoints, three requirements,
  25 estimated minutes, three product files/180 estimated LOC, zero runtime
  contours and no LLM sessions. Publish only the planning transition and live
  links. Preserve the accepted card bytes and FF fingerprint; its old
  informational OpenSpec Stage text remains draft provenance, while Status,
  Result and the FF admission record establish the accepted plan. No product
  code, canonical specs, historical sources or pilot changed.
- 2026-09-05T15:50:57Z Operator authorized scoped publication of the verified
  CHRL-FIX-01 offline repair. Publication does not accept FIX-01, close any
  product review finding, create a runner-owned done verdict or authorize the
  migration pilot; recheck readiness on clean main after the push.
- 2026-09-05T09:48:06Z CHRL-FIX-01 offline implementation verified: 203 focused
  and 1814 non-live tests passed, coverage 74.67%; 70 canonical specs, wiring
  and public audit passed. Actual historical active-lane blocker removed
  without source/history edits; implementation is not committed/published.
  FIX-01 remains backlog and its exact pilot still needs separate agreement.
- 2026-09-05T09:13:11Z Linked CHRL-FIX-01 as a separately authorized planning
  task for frozen historical activity accounting. No workflow or historical
  payload changed, and the FIX-01 pilot remains unapproved.
- 2026-09-05T08:59:10Z Operator authorized a scoped commit/push of the corrective
  board plans and release dependencies. All corrective cards remain backlog;
  no implementation, acceptance, runtime or migration pilot is authorized.
- 2026-09-05T08:38:59Z Decomposed FIX-04 and FIX-09 into six bounded successor drafts; rewired both qualification prerequisites and retained the two aggregates as non-executable history. No code, admission, runtime or publication.
- 2026-09-05T08:11:47Z Added operator-requested FIX-01 through FIX-12 backlog
  plans and corrective release dependencies. FIX-04/FIX-09 are explicitly
  SPLIT_REQUIRED. No delivery, runtime, status moves or publication occurred.
- 2026-08-24 epic created for the approved public-upstream/private-downstream
  product model and the decision to retire source/data protection everywhere.
- 2026-08-24 initial `$changerail-ff` prepared five broad changes.
- 2026-08-24 roadmap corrected to a parent epic: four apply-ready technical
  cards, two existing public-core stories and three separately planned
  publication/cutover cards. Direct `$changerail-do` on the epic was removed.
- 2026-08-24 OSS-01 completed implementation, mandatory Windows-native proof,
  spec sync and archive; it remains in `3.inprogress` only for the independent
  review and publish gate. OSS-02 is the next sequential child card.
- 2026-08-24 OSS-01 passed independent rescue review cycle 2, was published
  into `4.done`, and unblocked OSS-02 as the next sequential child card.
- 2026-08-24 OSS-02 completed implementation, Windows-native verification,
  spec sync and archive; it is awaiting independent review and publish.
- 2026-08-24 OSS-02 passed independent review cycle 2 with all six acceptance
  criteria satisfied and no findings, then moved to `4.done` for publication.
- 2026-08-24 OSS-03 entered implementation after its artifacts were refreshed
  against the published OSS-01/02 contracts.
- 2026-08-24 OSS-03 passed independent rescue review cycle 2 with all five
  acceptance criteria satisfied and no findings, then moved to `4.done` for
  publication. OSS-04 is the next sequential planning card; OSS-05 remains an
  independently apply-ready sibling.
- 2026-08-25 OSS-04 review preflight measured `1265` added production LOC;
  operator-approved investigation split delivery into six sequential child
  cards, each capped at `300` production LOC. OSS-04A is next.
- 2026-08-25 OSS-04A passed independent review cycle 3 with all four
  acceptance criteria satisfied and no findings, then moved to `4.done`;
  OSS-04B is the next sequential child.
- 2026-08-25 OSS-04B entered bounded implementation after the published
  runtime-target contract.
- 2026-08-25 OSS-04B passed independent review cycle 5 with all five
  acceptance criteria satisfied and no findings, then moved to `4.done`;
  OSS-04C is the next sequential child.
- 2026-08-25 roadmap refreshed after OSS-04B publication: 04C-04F and OSS-05
  are apply-ready, shared-main execution remains sequential, and OSS-06-09 stay
  story-stage until their explicit dependency gates are met.
- 2026-08-25 OSS-04C passed independent review cycle 3 with all five
  acceptance criteria satisfied and no findings, moved to `4.done`, and
  unblocked OSS-04D as the next sequential payload.
- 2026-08-27 OSS-04F passed fresh critical review cycle 2 and published the
  final target-bound evidence/cleanup payload. Parent OSS-04 moved to
  `4.done`, immutable runtime-target binding is complete, and OSS-06 moved to
  `2.todo` as planning-ready because OSS-05 is already apply-ready; no next
  card was started.
- 2026-08-27 OSS-05 passed final critical review and published the independent
  open Windows bridge with exact `.204` lifecycle/display/relay/cleanup proof.
  OSS-06 is unblocked in `2.todo`; no planning artifacts or implementation were
  started.
- 2026-09-01 roadmap refreshed after S7 fixture repair. Both certification
  EPFs now have tracked source/binaries and a visibly proven non-empty managed
  form; S7 still requires the complete hidden Windows task-5 matrix, fresh
  critical review and publication. OSS-07 is confirmed as the next card by
  `Order Index`; actual post-I15 state remains a `1.backlog` story with no
  OpenSpec artifacts. No OSI license was inferred at that point.
- 2026-09-01 operator approved SPDX `Apache-2.0`; OSS-07 change 1 must bind the
  decision to its exact publication policy before legal files are installed.
- 2026-09-01 S7 exact diagnostics proved real S3 PASS but stable S4
  `main_not_ready`. Added apply-ready linked investigation `405.101`; OSS-07
  remains queued behind the card-405 delivery-or-omission outcome.
- 2026-09-01 S7-I1 published its bounded S4-R1 decision. S4-R1 passed offline
  composition and exact S3 but stopped safely when run-1 S4 exited before a
  positive marker receipt. Added linked investigation `405.103` for a typed,
  privacy-safe pre-receipt diagnostic; S4-R1, S7 and OSS-07 remain sequentially
  blocked behind that published decision.
- 2026-09-01 S4-R2 clean-base/offline floors and exact S3 passed; two passive
  rows agreed on `process_exit/candidate_exited_without_checkpoint` with zero
  action. Delivery stopped `NOT-VERIFIABLE`: owned task/stage/process residue is
  zero and config bytes/ACL are exact, but the original metadata timestamps
  were not retained for exact restoration. No review, commit or push occurred.
- 2026-09-01 S4-R2 supervised resume accepted the completed immutable receipt
  without a live rerun. Exact content, ACL, all-four-metadata and owned cleanup
  are proven; the curated decision limits the result to a pre-first-checkpoint
  exit and leaves S4-R1, S7 and downstream delivery stopped.
- 2026-09-02 published I11 commit `964e29f` closes the private predicate-
  equivalence defect and offline proof floor. I12 reconciles that evidence
  without claiming the still-unexecuted parent matrix and prepares exact
  certification-only I13 at `405.10196`; S4-R1 and S7 remain blocked.
- 2026-09-02 I13 exact preflight and S3 passed, then the first tracked S4 row
  exited before a receipt and protected unrelated-task topology drifted. I14
  retained the separate `NOT-VERIFIABLE` investigation at `405.10197`: simple
  excluded-task inclusion is ruled out, but no topology cause or candidate
  result is established and no certification was published.
- 2026-09-02 I15 exact source/contour preflight passed, then its one authorized
  original-route canary produced no typed Session-1 receipt. Candidate
  invocation remained zero, exact cleanup passed, topology attribution stayed
  `NOT-VERIFIABLE`, and I13/S4-R1/S7 remain blocked.
- 2026-09-02 I16 records `open_external_processor` omitted from stable
  standalone profile/public support after published I15. It corrects OSS-07 to
  its actual unplanned backlog state, carries operator-approved `Apache-2.0`
  into the next separate card and preserves I13/S4-R1/S7 incomplete.
- 2026-09-02 OSS-07-I2 published at `61b8d90`: the linked investigation closes
  the exhausted I1 false-PASS design class with an exact byte-frozen matrix,
  unchanged control and 23 hostile fail-closed mutations. It does not restore
  I1 or implement the broader parent; OSS-07 parent delivery is next and
  OSS-08/OSS-09 remain blocked.
- 2026-09-02 OSS-07 parent accepted into `2.todo` with four changes: exact
  Apache-2.0/publication policy, asset/evidence audit, public repository docs
  and isolated clean-snapshot proof. OSS-08/OSS-09 remain blocked.
- 2026-09-02 OSS-07 implemented, verified, synced and archived all four parent
  changes. The exact full non-live suite, public audit/provenance/docs,
  isolated package build and I2 23-mutation oracle are green; independent
  review and scoped publication remain before OSS-08 can start.
- 2026-09-03 OSS-07 review cycle 3 returned final `NO-GO` after both same-card
  rescues. Added linked replacement OSS-07-R1 at order `406.1` to adopt the
  unpublished snapshot and close scanner grammar/type/count, inline JSONL hash
  integrity and exact review-fingerprint handoff before OSS-08.
- 2026-09-03 OSS-07-R1 implementation, offline verification, spec sync and
  archive are complete: `1602 passed, 4 skipped`, audit/provenance/docs/I2 and
  standalone snapshot are GREEN. Exact-fingerprint independent review and
  publication remain before OSS-08.

- 2026-09-09 Operator-authorized reconciliation includes all accumulated repository changes, closes FIX-01 separately from its stopped pilot, and makes native FIX-02 the next product plan. All original attempts and four frozen records remain unchanged; no new product delivery or live qualification is implied.

- 2026-09-10 Reinspected OSS-00 continuation after T0–T5. Selected independent FIX-04A, confirmed its configuration-routing defect offline, and prepared one native change. Corrected the FIX-02 historical link and current sequence; preserved stopped records and prior logs. Planning only.
- 2026-09-10 Operator-authorized preparation for a new orchestrator: documented sequential native delivery, planning commits, child small-fix sessions and recovery boundaries; reconciled the CI specification with the affected-test policy. Small fix without a card: moved four Git/pytest selector cases into integration, retaining five pure offline cases; both groups passed. FIX-04A dry-run admission returned READY without moving the card. Accumulated baseline publication does not close FIX-02 or reopen canceled ChangeRail work; local preparation evidence is under `.runtime/oss00-orchestrator-preparation-20260910/`.


## ChangeRail maintenance cancellation (2026-09-09)

By explicit operator instruction, all 11 remaining CHRL-FIX cards are canceled in this repository. The descriptions above record historical work, not a current queue or permission to resume it. qa-mcp consumes only the executable ChangeRail distribution; development, repair, tests and fixtures belong to the ChangeRail source repository. Product OSS-FIX cards retain their separate scope and status.

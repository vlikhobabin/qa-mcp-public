# Eliminate Provisional Hidden-Worker Job-Handle Race

## Status
4.done

## Owner
unassigned

## Series
oss-06-s2-r1

## Order Index
405.51

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Replaces
- Unpublished exhausted
  `openspec/board/3.inprogress/oss-06-s2-extract-hidden-worker-lifecycle.md`.

## Source Lineage
- Latest safe published baseline and S1 replacement commit:
  `8b329a2bb539aad7f3a6719dead356f033efef90`.
- S2 final cycle-3 reviewed tree:
  `f348ca3cf235d26a46c2e13d463fda3efd64876a`; fingerprint:
  `sha256:de4699816ecb6cce695ec8db573b600e416df43deac9cfbcf5adbce2a02e9739`.
- Canonical predecessor verdict/history:
  `.runtime/changerail/reviews/oss-06-s2-extract-hidden-worker-lifecycle.json`
  and the adjacent history; review cycles `1–3` consumed rescue budget `2/2`.
- Exact retained S2 candidates before replacement: Windows test
  `0e41f7ad06534f72cede581cb0ff38fbc6d39ffd62c0a3771722be3a44efdc01`
  and host agent
  `29f1bdcd2c9827abea13a6caa7e3770153ae5d9ca82be82a681442a70dad0718`.
- Retained evidence index:
  `.runtime/changerail/evidence/oss-06-s2-extract-hidden-worker-lifecycle/index.json`.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Replacement lineage note: first linked replacement after exhausted S2.
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Publish the dormant S2 worker/job/TPort lifecycle through a clean linked
replacement that removes provisional remote handle ownership, reports every
terminate/wait failure and proves cancellation at the asynchronous transfer
boundaries while the controller remains alive.

## Final Predecessor Findings
1. Cancellation or timeout after worker-side `DuplicateHandle` but before
   admission can strand an unknown controller-side job handle and keep the
   exact child/listener alive.
2. Assignment and lifecycle cleanup ignore terminate failures, wait failures
   and a successful syscall returning `WAIT_TIMEOUT`.
3. The native matrix lacks controller-alive synchronization oracles at those
   transfer and cleanup-failure boundaries.

## Current Hypothesis
- The worker publishes only its worker-local job-handle value in an atomic
  authenticated response and never opens or duplicates into the controller.
- After response identity is authenticated, the controller duplicates that
  handle from the exact worker process into itself and immediately records it
  as lifecycle-owned before membership checks or any cancelable admission
  work. Before duplication, worker death closes the sole job handle; after
  duplication, controller cleanup knows and closes its exact handle.
- Controller cleanup removes both the final response path and its current-run
  temporary path, including abrupt worker termination during publication.
- One bounded wait helper treats `WAIT_OBJECT_0` as success and joins syscall
  error, `WAIT_TIMEOUT`, unexpected status and terminate failure with the
  original cause without skipping later exact-owned cleanup actions.

## Acceptance
- The replacement composes from published `8b329a2...` plus only its exact
  source/test/artifact paths and adopts the complete dormant S2 capability at
  no more than `300` physical added production lines.
- No worker-side operation creates a provisional controller handle. Response
  identity is authenticated before the controller duplicates from the exact
  worker, and a successful duplicate is recorded as lifecycle-owned before
  membership checks, cancellation or timeout can fail admission.
- Cancellation/timeout before duplication, after response publication and
  after local duplication each leave no exact worker, child, listener, job,
  desktop, response or temporary path while preserving a real unrelated
  process and handle.
- Assignment failure and lifecycle close retain terminate/wait errors and
  treat `WAIT_TIMEOUT` or any unexpected wait status as incomplete cleanup;
  every remaining exact-owned cleanup action is still attempted.
- Missing, malformed, stale, foreign-handle, wrong-token, wrong-port,
  ambiguous and truncated-listener cases remain fail-closed.
- The lifecycle remains dormant: no existing non-test caller, public API, wire
  schema, route/profile, window/UIA/prompt behavior, global input, foreground
  action or desktop switch changes.
- Exact focused/full Go, vet, Windows test/host cross-build, clean-baseline
  composition, exact-source historical-user controller-alive matrix, strict OpenSpec,
  manifest scope, production LOC and diff gates pass before one fresh
  ordinary/high independent replacement review.

## Scope
- Replace worker-to-controller provisional handle duplication with
  controller-initiated duplication from the exact authenticated worker.
- Make wait status and terminate/wait errors explicit in partial-start and
  idempotent lifecycle cleanup.
- Add bounded synchronization seams and hostile/native tests for cancellation
  before/after local handle ownership, temp-path cleanup and `WAIT_TIMEOUT`.
- Adopt only the existing eight S2 source/test paths plus replacement card,
  OpenSpec/spec and sanitized evidence/manifest lineage.
- Keep S3 window inventory and every S4-S7 observation/action/public route out
  of scope.

## Change Set
1. `eliminate-provisional-hidden-worker-job-transfer`

## Depends On
- Published S1 replacement
  `openspec/board/4.done/oss-06-s1-r1-certify-hidden-desktop-process-foundation.md`.
- Exhausted S2 cycle-3 verdict/history and retained exact candidate evidence.

## Blocks
- `openspec/board/1.backlog/oss-06-s3-extract-hidden-window-isolation.md`

## Verify
- RED commands for controller cancellation after response publication and
  after local duplication, plus terminate failure and `WAIT_TIMEOUT`.
- Ambient and published-HEAD-plus-exact-replacement-path focused/full Go, vet,
  Windows test/host cross-build and canonical production LOC `<=300`.
- Exact-source Windows-native selector on trusted `HISTORICAL-LAB-HOST\\historical-user`
  at its current endpoint, asserting resources before controller test exit.
- Exact-owned task/stage/process/path cleanup, listener `18081` preservation,
  no Docker mutation and no reboot.
- `bin/openspec validate --all --strict`, manifest working-tree scope-check,
  deterministic review preflight and `git diff --check`.

## Result
- published after independent review cycle 2 returned `GO` with `7/7`
  acceptance, zero findings and zero unbacked claims; the shared parser remains
  byte-identical to published HEAD, all asynchronous boundaries have complete
  resource oracles, timeout waits exact worker children, deterministic clean
  composition is retained, and production additions are `297/300`

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `eliminate-provisional-hidden-worker-job-transfer`

### Why
S2 fixed every explicit failure branch but its worker-first remote-handle
transfer still has an asynchronous interval where neither side can reliably
close the controller handle after cancellation.

### Goal
Publish the same dormant S2 capability with a transfer ordering in which job
ownership is always either worker-local or immediately controller-known, and
with truthful wait/termination cleanup semantics.

### Scope
- Add RED synchronization and cleanup-failure oracles first.
- Reorder handle transfer and exact ownership without adding authority.
- Rebuild and rerun the complete offline/Windows lineage.

### Acceptance
- All card acceptance criteria pass within one exact replacement lineage.
- Exhausted predecessor `NO-GO` and rescue budget remain immutable.
- A fresh independent replacement review returns `GO` before publication.

### Depends On
- Exhausted S2 review cycle 3.

### Related
- `openspec/changes/eliminate-provisional-hidden-worker-job-transfer/`

## Log
- 2026-08-30 operator authorized the linked S2 replacement after final cycle-3
  `NO-GO`; no third same-card fix, production change, S3 work, commit or push
  was started.
- 2026-08-30 RED candidate `ba0a2717...` ran on trusted historical-user and failed
  exactly three new controller-alive oracles: provisional cancellation retained
  both child and controller job handle, assignment cleanup lost terminate/wait
  outcomes, and `WAIT_TIMEOUT` returned cleanup success. The harness removed
  its exact leaked child/handle before returning; exact task/stage were then
  removed with owned/1C processes zero and listener `18081` preserved. Existing
  functional S2 cases remained green; production source and S3 were untouched.
- 2026-08-30 replacement moved handle duplication into the controller after
  authenticated response validation, recorded the local duplicate before any
  cancelable admission step, removed worker access to the controller, joined
  terminate/wait failures, rejected timeout/unexpected wait statuses and
  removed both response paths. Candidate `5673685f...` passed the exact native
  selector on `HISTORICAL-LAB-HOST\\historical-user`, including controller-alive cancellation
  before/after duplication and `.tmp` interruption. The final published-HEAD
  plus exact-eight-path candidates are test `d544a711...` and host-agent
  `e425af6d...`; both clean-composition Go matrices and the exact Windows run
  passed. Exact tasks/stages and owned processes were removed, 1C process
  count remained zero, listener `18081` remained present, and Docker/reboot were
  untouched. Production additions are `261/300`; S3 remains unstarted.
- 2026-08-30 archived
  `openspec/changes/archive/2026-08-30-eliminate-provisional-hidden-worker-job-transfer/`;
  ambient and published-HEAD-plus-eight-path focused/full Go, vet, Windows
  cross-build, strict OpenSpec `47/47`, manifest working-tree scope, LOC and
  diff gates passed. Delivery is ready for one fresh ordinary/high review.
- 2026-08-30 independent review cycle 1 returned `NO-GO`: the shared TCP
  parser changed existing production semantics, Windows boundary oracles did
  not cover the complete resource set, and the recorded clean-composition
  command omitted the module-aware layout. Same-card rescue attempt 1 restored
  the shared parser byte-for-byte and moved strict complete-table uniqueness
  into the dormant lifecycle, added complete publish/transfer/timeout resource
  assertions, and retained an executable module-aware clean-composition script.
- 2026-08-30 a deterministic pre-green historical-user run exposed the timeout race
  hidden by the earlier timing: the exact child could remain alive briefly
  after worker exit closed its job. The controller now opens synchronize-only
  handles for direct children of the still-live exact worker and boundedly
  waits kill-on-job-close convergence without new terminate authority. The
  final `-trimpath` clean candidates were reproducible across two fresh roots
  (`e033a702...` test, `08c44636...` host), and all 42 lifecycle cases passed
  on `HISTORICAL-LAB-HOST\\historical-user`. Exact tasks/stages were removed, owned and 1C
  processes are zero, listener `18081` is preserved, Docker was not mutated
  (its API remained unavailable), no reboot occurred, production is `297/300`,
  and S3 remains unstarted.
- 2026-08-30 independent review cycle 2 returned fresh `GO` for fingerprint
  `sha256:c2a581d7...`: `7/7` acceptance passed with zero findings and zero
  unbacked claims. Final clean composition, strict OpenSpec `47/47`, manifest
  staged scope and diff gates passed before scoped publication.
- 2026-08-30T19:56:44Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

# Publish Clean-HEAD Private Fenced Seam

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i6

## Order Index
405.1020

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/4.done/oss-06-s4-r1-i5-decide-publishable-private-fenced-seam.md`

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Successor authorization: `bounded post-investigation successor explicitly authorized by published I5 Outcome A`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Implementation classification: `one clean-HEAD private fenced-seam extraction/composition; not another unresolved repeated implementation`
- Authorization source: published I5 decision and curated findings at
  `875650a28c838580eb0b2b7516ddf7c274d8cb3d`

## Summary
Implement and publish exactly the private clean-HEAD fenced liveness,
inventory, diagnostic and transferred-observer ownership seam authorized by
I5 Outcome A. Compose it only at the two existing direct inventory boundaries
inside `observeHiddenDirectInWorker`, prove the connected hostile floor on the
exact staged tree and preserve every I5 dependency, privacy and behavior
ceiling.

## Source Lineage
- Published I5 decision and curated findings at
  `875650a28c838580eb0b2b7516ddf7c274d8cb3d`.
- Clean delivery baseline: `HEAD`, `origin/main` and live `origin/main` all
  equal `875650a28c838580eb0b2b7516ddf7c274d8cb3d` with an empty tree before
  this card was materialized.
- This card may recreate only I5's named private predicates against that clean
  baseline. It must not import or copy the dirty predecessor as a whole.

## Acceptance
- Modify only the seven existing clean-HEAD paths and named predicates in the
  `Exact Source Ownership` section. Change at most three non-test Go files and
  four test Go files, with at most 250 added non-test Go lines.
- Implement the exact private liveness/inventory/fenced status types and
  sample, private pre-receipt diagnostic ownership closure, exact
  process/job/TPort liveness fence and Windows wrapper, and transferred-
  observer validation/callback hold. Replace exactly the two clean-HEAD direct
  `inventoryHiddenWindowIsolation` calls inside
  `observeHiddenDirectInWorker` with connected fenced-wrapper calls.
- Add no package, module, dependency, public caller, route, wire field, marker
  derivation, action, retry, fallback, desktop/thread/window-station mutation,
  process/job ownership expansion, classifier cause mapping or live behavior.
  Exclude `main.go`, `testclient_launch.go`, every adapter/public path, S5,
  S7, fixtures, OSS-07/08 and every byte outside the named predicates.
- Retain a clean-HEAD RED proving all four seam families are absent and exactly
  two direct inventory calls exist, then a same-tree GREEN that compiles the
  exact seven-path tree and executes the actual two worker call sites.
- GREEN proves exactly two connected wrapper calls with no direct bypass; one
  inventory call per boundary; exact pre/post fence counts; child/listener
  live, exited and unknown; inventory error, empty and non-empty; post-fence
  change; main absent/exact; handle-close failure; malformed diagnostic; both
  first and second boundaries; zero retry/fallback/action; unchanged fail-
  closed and passive-UIA outcomes; exact transferred-observer job/TPort
  ownership; and privacy-safe diagnostics.
- Pass focused and full host-agent Go test and vet, Linux tests,
  deterministic Windows amd64/386 test cross-builds, strict OpenSpec,
  manifest scope, staged-tree compile, authorized-predicate hunk audit,
  diff/whitespace checks, all offline without launching Windows or 1C.
- Before review, the explicit-path staging plan contains only the seven owned
  Go paths plus this card, its own OpenSpec artifacts/spec updates and its own
  evidence documentation. Every Go hunk maps to one I5-authorized predicate.
- Any extra path, unowned hunk, ceiling breach, bypass, missing diagnostic
  connection, compile failure or hostile failure is the first safety stop.
- Do not launch 1C, connect to an endpoint, retry or confirm live behavior,
  mutate real Windows configuration, perform S7 work or use `User@192.*`.
  The retained `historical-user@192.0.2.201` identity is inaccessible evidence only.

## Exact Source Ownership
1. `host-agent/windows-display-agent/hidden_direct_execute_observation.go`
   - private liveness/inventory/fenced status types and constants;
   - `hiddenDirectLivenessSnapshot`, `hiddenDirectFencedSample`,
     `hiddenDirectPreLivenessStatus` and `observeHiddenDirectFencedSample`;
   - bounded private pre-receipt diagnostic schema, validator and
     stage/failure map needed to carry a later cause.
2. `host-agent/windows-display-agent/hidden_direct_execute_observation_test.go`
   - injected exclusive-state, call-count, no-retry and diagnostic hostile
     tests for only those predicates.
3. `host-agent/windows-display-agent/hidden_direct_execute_observation_windows_test.go`
   - exact process/job/TPort liveness-fence helpers and
     `observeHiddenDirectWindowsFencedSample`;
   - bounded diagnostic read/write/reporter helpers;
   - exactly two worker inventory-call replacements and only the
     worker/controller diagnostic lifecycle needed to keep a pre-receipt
     refusal observable.
4. `host-agent/windows-display-agent/hidden_desktop_worker_lifecycle.go`
   - exact transferred-observer validation helper.
5. `host-agent/windows-display-agent/hidden_desktop_worker_lifecycle_test.go`
   - hostile validation and ordering tests for that helper.
6. `host-agent/windows-display-agent/hidden_desktop_worker_lifecycle_windows.go`
   - one private transferred-observer callback and its invocation after exact
     acknowledgement while the local job handle is still held.
7. `host-agent/windows-display-agent/hidden_desktop_worker_lifecycle_windows_test.go`
   - exact observer-hold/cleanup injection test.

## Dependency Ceiling
- Clean published I5 HEAD plus only the seven owned paths.
- At most three changed non-test Go files, four changed test Go files and 250
  added non-test Go lines.
- Existing Go standard library and already-published `x/sys/windows` only.
- No authority, wire, public, mutation, ownership or live-behavior expansion.

## Change Set
1. `publish-clean-head-private-fenced-seam`

## Verify
- Retained clean-HEAD RED and same-tree connected GREEN with byte-identical
  worker-call-site execution, focused/full Go test and vet, 1,581 offline
  Linux tests, deterministic Windows amd64/386 test cross-builds, exact
  seven-path/122-line ceilings, strict OpenSpec, manifest scope, explicit
  staged-tree compile, hunk, diff and whitespace gates all passing.
- No Windows or 1C execution, endpoint connection, live retry/confirmation,
  real configuration mutation, S7 action or evidence-only target access ran.

## Archive
- `openspec/changes/archive/2026-09-01-publish-clean-head-private-fenced-seam/`

## Related
- `openspec/changes/archive/2026-09-01-publish-clean-head-private-fenced-seam/`
- `docs/protocol-research/evidence/private-fenced-seam-clean-head-publication-2026-09-01/evidence.md`
- `openspec/board/4.done/oss-06-s4-r1-i5-decide-publishable-private-fenced-seam.md`
- `docs/protocol-research/evidence/private-fenced-seam-publication-decision-2026-09-01/findings.md`
- `openspec/board/3.inprogress/oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause.md`
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Result
The I5-authorized private fenced seam is implemented on clean HEAD in exactly
seven owned Go paths. Both worker inventory boundaries use the connected
wrapper with no direct bypass; the existing private checkpoint schema retains
bounded failures, and transferred observation occurs after acknowledgement
while the worker-local job handle is held. Delivery is archived and finalized
for publication after fresh independent review cycle 3 returned `GO` with all
nine acceptance criteria passing and no findings.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `publish-clean-head-private-fenced-seam`

### Why
Published I5 Outcome A proves one bounded composition candidate exists on
clean HEAD and authorizes exactly one separately reviewed successor to publish
that private dependency before I4 can be replanned.

### Goal
Publish the exact connected private fence and diagnostic ownership closure,
with the two real worker boundaries protected by hostile offline verification.

### Scope
- Only the seven paths and predicates in `Exact Source Ownership`.
- Card-owned OpenSpec artifacts, synced spec updates and privacy-safe evidence.
- No live, target, public, classifier, marker, S5, S7, fixture or OSS-07/08
  surface.

### Acceptance
- All card-level acceptance and dependency ceilings pass on the exact staged
  tree.
- The seam is connected at both existing worker boundaries and remains
  private, fail-closed, passive and privacy-safe.

### Depends On
- Published I5 Outcome A at
  `875650a28c838580eb0b2b7516ddf7c274d8cb3d`.

### Related
- `openspec/changes/publish-clean-head-private-fenced-seam/`

## Log
- 2026-09-01 materialized as exactly one accepted clean-HEAD bounded successor
  authorized by published I5 Outcome A; no source or test implementation was
  imported from the dirty predecessor.
- 2026-09-01 fast-forwarded one apply-ready private seam change with the I5
  seven-path ceiling, exact connected hostile floor and offline-only staging
  gates; no implementation or runtime action occurred during planning.
- 2026-09-01 completed the bounded implementation, synced the new private seam
  capability and archived its change. RED/GREEN, exact two-call-site harness,
  Go/Linux/cross-build, scope/LOC, staged-tree, OpenSpec and privacy gates
  passed; card remains in `3.inprogress` for fresh independent review.
- 2026-09-01 review cycle 1 returned `NO-GO` on four hostile-path gaps:
  discarded reporter errors, permissive diagnostic JSON, static observer-hold
  proof and success-only worker-call-site execution. Same-card rescue attempt
  1 stayed within the seven I5 predicates, surfaced reporter failure, made the
  decoder strict, dynamically proved callback hold then release, and executed
  both refusal boundaries. Full Go/Linux/cross-build gates were rerun; no
  Windows, 1C, endpoint, target or live action ran.
- 2026-09-01 review cycle 2 returned `NO-GO` because the observer oracle still
  exercised synthetic generic orchestration and that orchestration exceeded
  the core file's exact validation-only predicate. Final same-card rescue
  attempt 2 removed the generic helper, kept callback/release sequencing in
  `runHiddenWorkerLifecycleWorker`, and added a byte-identical offline harness
  that blocks the actual worker callback while proving the exact job plus live
  listener/response TPort remain held until release and normal cleanup follows.
  Full Go/Python/cross-build/staged-tree gates were rerun without Windows, 1C,
  endpoint, target SSH-host or evidence-only identity access.
- 2026-09-01 fresh independent review cycle 3 returned `GO` on the exact
  fingerprint with nine of nine acceptance criteria passing, zero findings and
  zero unbacked claims.
- 2026-09-01T21:02:12Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

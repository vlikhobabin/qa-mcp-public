# S50-161: Fix Windows TestClient launch for disposable extension infobase

## Status
4.done

## Order Index
161

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Root tracker:
  `../openspec/board/1.backlog/s50-finans-extension-e2e-010-author-own-objects-and-real-cfe-roundtrip.md`
- Runtime evidence:
  `../admin-mcp/.runtime/changerail/evidence/s50-160-own-cfe-disposable-roundtrip/20260801T083429Z/windows/ui-proof-final-rerun/`

## Summary
The ambiguous S50 Windows failure is resolved. The host-agent now separates
broker failure, acknowledged platform early exit and live PID-handoff failure,
and treats the requested TPort owner as lifecycle authority. The supported
disposable path is a Windows-created file infobase restored from the retained
portable backup with explicit hardware-license search on this authorized
station. The final `.200` run owns a usable TestClient lifecycle, creates and
reads back one `S50ProofItems` item, retains screenshots, and leaves the exact
run namespace clean.

## Acceptance Criteria
- [x] Root-cause evidence distinguishes host-agent broker/PID handling from
  platform/file-infobase launch failure.
- [x] The supported S50 disposable infobase path is explicit: either a
  Windows-created/restored disposable infobase, or a validated copied infobase
  format that 1C on Windows can launch.
- [x] `launch_test_client` returns an owned lifecycle target for the S50
  disposable infobase on `User@192.0.2.200` with hostname
  `HISTORICAL-LAB-HOST`.
- [x] qa-mcp opens `Справочник.S50ProofItems`, creates one disposable item,
  reads it back from the list or visible cells, and captures ignored screenshot
  evidence.
- [x] Cleanup evidence confirms no exact S50 stage directory, scheduled task,
  host-agent process, proof TestClient process or proof ports remain.

## Change Set
- `s50-161-classify-windows-testclient-launch-failure`
- `s50-161-prove-windows-disposable-testclient-lifecycle`

## Change 1: `s50-161-classify-windows-testclient-launch-failure`

### Why
The final rerun does not reveal whether the broker supplied an unusable PID or
whether 1C accepted the launch and exited before opening TPort.

### Goal
Return bounded, secret-safe evidence that separates broker/PID handling from
platform/file-infobase early exit and preserve the actual listener owner as the
lifecycle PID.

### Scope
- Windows host-agent TestClient launch/PID classification.
- Focused Go regression tests and Windows-native proof.
- No new executable surface, customer data, or broad process cleanup.

### Acceptance
- The response distinguishes broker handoff failure from acknowledged 1C
  early exit before TPort.
- A live TPort owner remains authoritative when it differs from an
  acknowledged transient launcher PID.
- Diagnostics stay bounded and secret-safe.

### Depends On
- `s50-160-non-consuming-remote-launch-readiness`

### Related
- `openspec/changes/s50-161-classify-windows-testclient-launch-failure/`

## Change 2: `s50-161-prove-windows-disposable-testclient-lifecycle`

### Why
Root S50 needs a supported disposable Windows infobase and a complete UI
create/read proof, not only a more accurate launch failure.

### Goal
Restore a Windows-created disposable infobase from the retained extension proof,
launch it into an owned lifecycle, create/read one S50 catalog item, retain
ignored screenshots, and remove only exact run-owned resources.

### Scope
- Portable backup/restore into a Windows-created disposable file infobase.
- qa-mcp launch, catalog navigation, one disposable test item, readback and
  screenshots on `User@192.0.2.200` (`HISTORICAL-LAB-HOST`).
- Exact stage/task/process/tunnel/port cleanup with before/after inventory.

### Acceptance
- As in the card Acceptance Criteria.

### Depends On
- `s50-161-classify-windows-testclient-launch-failure`

### Related
- `openspec/changes/s50-161-prove-windows-disposable-testclient-lifecycle/`

## Verify
- `go test ./... -count=1` and `go vet ./...` passed for the host agent.
- Full Python regression passed: `907 passed`.
- Focused changed-surface Ruff and compile checks passed; the repository-wide
  Ruff baseline still has 35 unrelated pre-existing findings.
- Windows cross-test build, strict OpenSpec validation, scoped public/secret
  scan and `git diff --check` passed.
- Final live proof:
  `.runtime/changerail/evidence/s50-161-fix-windows-disposable-infobase-testclient-launch/20260801T193000Z/summary.json`
  reports `ok:true`, restore exit `0`, owned UI lifecycle, item readback,
  exact cleanup and clean rerun preflight.
- The official source-bound Windows-GUI bundle, manifest and SHA sidecar verify
  at `4af511830e771d3e585ada5319564570095ac80007f8722866dde7a8d43d7f47`.

## Archive
- `openspec/changes/archive/2026-08-01-s50-161-classify-windows-testclient-launch-failure/`
- `openspec/changes/archive/2026-08-01-s50-161-prove-windows-disposable-testclient-lifecycle/`

## Related
- Previous qa-mcp fix:
  `openspec/board/4.done/s50-160-non-consuming-remote-launch-readiness.md`
- Root tracker:
  `../openspec/board/1.backlog/s50-finans-extension-e2e-010-author-own-objects-and-real-cfe-roundtrip.md`

## Result
Implementation, runtime acceptance, spec sync and archive are complete.
Independent review cycle 4 returned `go` with zero findings and all five
acceptance criteria passed.

Published reviewed payload as `6a67517c153fbf0679acefb08f9cbd2ced401425`;
push status `pending` on `main`/`origin`.

## Next
- done

## Change Plan Notes
When fast-forwarding, split root-cause instrumentation from the final UI proof
only if the broker/file-infobase cause is not immediately isolated.

## Log
- 2026-08-01T12:45:00Z card created from S50 final Windows rerun blocker on
  `HISTORICAL-LAB-HOST`; cleanup evidence retained under the root runtime evidence
  path.
- 2026-08-01T13:10:00Z ChangeRail fast-forward split ambiguous launch
  classification from the supported Windows disposable-infobase/UI proof; the
  authorized `.200` preflight found the S50-161 stage/task/process/port namespace
  clean.
- 2026-08-01T16:30:00Z final authorized `.200` rerun restored a Windows-created
  disposable base, owned TestClient PID/TPort/lifecycle, created and read back
  `S50 proof item 20260801T163000Z`, stopped the lifecycle, removed the exact
  stage/task/tunnel namespace and passed a second clean preflight. `.201` and
  S40 were untouched.
- 2026-08-01T17:20:00Z independent review cycle 1 returned no-go: a live
  acknowledged PID could fall through after listener-owner timeout and later
  combine with an unrelated listener. The fix makes the caller-bounded owner
  wait fail closed, session-checks and terminates only the exact acknowledged
  process, and adds classifier plus production-wiring regressions.
- 2026-08-01T17:30:00Z source artifact
  `bafa2e56dc43d5b1271fde76cf36337840e0424085f3b0126391cdd4ab8ac58c`
  passed a fresh `.200` end-to-end run with item
  `S50 proof item 20260801T173000Z`, exact cleanup and clean rerun preflight.
  `.201` and S40 remained untouched.
- 2026-08-01T18:10:00Z independent review cycle 2 returned no-go: numeric PID
  retention across the owner wait could terminate a recycled same-session
  process, the timeout regression was a source sentinel rather than a behavior
  test, and the ignored bundle metadata was stale. The fix immediately opens
  and session-checks the acknowledged process, retains that exact Windows
  handle across owner resolution, uses a shared behavior-tested state machine,
  and regenerates the official GUI bundle plus matching manifest and sidecar.
- 2026-08-01T18:30:00Z verified source-bound GUI artifact
  `d2a5ecebc7ac2b1b29ab6a0158b066688cd8b39e50aa34430d880db3a1a8d157`
  passed a fresh `.200` end-to-end run: negative PID `9888` was classified as
  acknowledged platform early exit, positive PID `15120` owned TPort `15662`
  and its lifecycle, `S50 proof item 20260801T183000Z` with code `000000001`
  was read back in the UI, six screenshots were retained, and exact cleanup
  plus rerun preflight were clean. `.201` and S40 remained untouched.
- 2026-08-01T18:45:00Z independent review cycle 3 returned no-go: handle
  acquisition still followed registration completion and exact-task cleanup,
  leaving a numeric-PID-only interval immediately after acknowledgement. The
  fix makes immutable handle acquisition the first post-acknowledgement
  operation and behaviorally verifies ordering plus exact retained-handle
  cleanup for later registration/task failures.
- 2026-08-01T19:30:00Z verified source-bound GUI artifact
  `4af511830e771d3e585ada5319564570095ac80007f8722866dde7a8d43d7f47`
  passed a fresh `.200` end-to-end run: negative PID `24948` was classified as
  acknowledged platform early exit, positive PID `20516` owned TPort `15662`
  and its lifecycle, `S50 proof item 20260801T193000Z` with code `000000001`
  was read back in the UI, six screenshots were retained, and exact cleanup
  plus rerun preflight were clean. `.201` and S40 remained untouched.
- 2026-08-01T12:58:39Z independent review cycle 4 returned `go` with zero
  findings, all five acceptance criteria passed and no unbacked claims.
- 2026-08-01T13:03:30Z publish finalized card into `4.done` with commit
  `6a67517c153fbf0679acefb08f9cbd2ced401425` and push status `pending`.

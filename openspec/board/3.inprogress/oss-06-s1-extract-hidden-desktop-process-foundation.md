# Extract Hidden Desktop Process Foundation

## Status
3.inprogress

## Owner
qa-mcp

## Series
oss-06-s1

## Order Index
405.4

## OpenSpec Stage
superseded by linked replacement / final review no-go

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Latest verdict: final cycle 3 `NO-GO`; same-card rescue budget `2/2`
  exhausted. Publication is blocked pending a linked rescue/replacement.

## Summary
Extract independently testable Win32 desktop, process, environment and
run-identity primitives from the retained candidate without activating them in
the public host route.

## Acceptance
- Added production LOC is `<=300` by canonical preflight.
- The module is dormant outside focused internal tests and uses no global input.
- Existing host behavior and wire surface remain unchanged.

## Depends On
- `oss-06-a2-authorize-bounded-hidden-direct-execute-admission`

## Change Set
1. `extract-hidden-desktop-process-foundation`

## Verify
- Exact RED/GREEN focused identity, environment and Windows lifecycle tests.
- `cd host-agent/windows-display-agent && go test ./...`
- Windows test and host-agent cross-builds with `CGO_ENABLED=0`, `GOOS=windows`
  and `GOARCH=amd64`.
- Bounded Windows-native focused run with sanitized exact-owned cleanup
  evidence.
- Canonical `<=300` production LOC preflight, strict OpenSpec, manifest
  scope-check and `git diff --check`.

## Archive
- `openspec/changes/archive/2026-08-30-extract-hidden-desktop-process-foundation/`

## Related
- `openspec/changes/archive/2026-08-30-extract-hidden-desktop-process-foundation/`

## Result
Dormant bounded run-identity, reserved-environment, named-desktop and
windowless-process primitives are implemented without a production call site or
wire/public-route change. Focused/full Go verification, Windows cross-builds
and exact-source Windows-native lifecycle proof passed with exact-owned cleanup.
Cycle-2 code blockers were fixed at canonical `248/300` production LOC, but
final cycle 3 found one remaining evidence blocker: the exact-source Windows
GREEN regex did not select the separate terminate-failure cleanup test.

## Next
- Do not publish this exhausted card directly. Publication ownership moved to
  `oss-06-s1-r1-certify-hidden-desktop-process-foundation`; start S2 only after
  that linked replacement is independently reviewed and published.

## Change 1: `extract-hidden-desktop-process-foundation`

### Why
The retained combined candidate cannot be reviewed as a bounded foundation,
and later worker/window/prompt layers need one published exact-owned process
base.

### Goal
Publish dormant internal Win32 process primitives with deterministic hostile
tests and no current production caller.

### Scope
- Cross-platform run-identity and environment policy.
- Windows-only named-desktop and windowless-process mechanics.
- Focused offline/cross-build/native tests and sanitized evidence.
- No TestClient worker, TPort, window/UIA, prompt, receipt or route wiring.

### Acceptance
- Invalid identity, environment, desktop or executable input fails before
  launch.
- The exact windowless child starts on the named desktop and cleanup touches
  only current-call handles/process.
- No `SendInput`, cursor, foreground or desktop-switch action is introduced.

### Depends On
- `oss-06-a2-authorize-bounded-hidden-direct-execute-admission`

### Related
- `openspec/changes/archive/2026-08-30-extract-hidden-desktop-process-foundation/`

## Log
- 2026-08-30 A2 publication confirmed; S1 decomposed as one dormant bounded
  foundation change and apply-ready artifacts created.
- 2026-08-30 S1 implementation, spec sync and archive completed; focused/full
  Go, Windows cross-build and exact-source Windows-native lifecycle evidence
  passed with `229/300` production LOC. Independent review is pending.
- 2026-08-30 independent review cycle 1 returned `NO-GO` on three linked
  blockers: post-trim identity bounds, discarded thread-handle close failure,
  and a non-regression-sensitive windowless oracle.
- 2026-08-30 same-card rescue attempt 1 added exact RED mappings, raw-input
  bounds, fail-closed process/thread cleanup and a live console-child zero-window
  oracle. Focused/full Go, Windows cross-build, exact-source native proof and
  exact-owned cleanup passed at `251/300` production LOC; cycle 2 is pending.
- 2026-08-30 independent review cycle 2 returned `NO-GO` on three blockers:
  bounded whitespace identities could still collapse, terminate failure skipped
  both handle closes, and native evidence did not execute the process-contract
  oracle.
- 2026-08-30 same-card rescue attempt 2 rejected ASCII/Unicode edge whitespace,
  joined terminate/close errors while always attempting both exact handle
  closes, and ran both ProcessContract and NativeLifecycle on exact-source
  candidate `ef3292b8...`. Focused/full Go, Windows cross-build and exact-owned
  cleanup passed at `248/300` production LOC; final cycle 3 is pending.
- 2026-08-30 final independent review cycle 3 returned `NO-GO`: the native
  regex executed ProcessContract and NativeLifecycle but not the separate
  CleanupClosesHandlesWhenTerminateFails GREEN oracle. Same-card rescue budget
  is exhausted at `2/2`; S1 remains unpublished and S2 was not started.
- 2026-08-30 operator-authorized linked replacement S1-R1 adopted the exact
  four-file payload and obtained the missing hash-bound three-test Windows
  GREEN plus exact-owned cleanup. This exhausted card remains immutable NO-GO
  lineage and is not a direct publication target.

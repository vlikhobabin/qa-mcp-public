# Publish the Windows host-agent delivery as one atomic QA payload

## Status

4.done

## Owner

unassigned

## OpenSpec Stage

archived

## Problem

The Windows launch and host-agent packaging stories are one repository payload.
Their original delivery manifests overlap shared installer/host-agent files and
cannot independently stage the complete dirty tree without leaving unowned
paths. The technical findings have owner-local rescue changes; publication now
needs one coordination card and one exact manifest covering the entire QA diff.

## Scope

- Treat the two original QA stories and both rescue changes as one publish
  unit.
- Own every dirty QA repository path exactly once in the combined delivery
  manifest.
- Keep the original cards as technical audit records; do not publish either
  partial manifest.
- Do not commit, push, activate or publish before fresh review verdicts are go.

## Acceptance

- The combined manifest exactly covers all QA dirty paths with no unowned or
  out-of-scope file.
- All eight constituent changes are archived and their synced capabilities
  validate strictly.
- Full offline Python, native Go, Windows cross-build, focused Ruff, artifact
  double-build, shell syntax and `git diff --check` are green.
- Publication uses only this combined card after independent review.

## Change Set

1. `windows-testclient-interactive-task-launch`
2. `windows-testclient-authenticated-loopback-relay`
3. `windows-host-agent-windowless-helper-lifecycle`
4. `windows-testclient-relay-listener-only-readiness`
5. `windows-host-agent-release-artifact`
6. `windows-testclient-launch-fail-closed-cleanup`
7. `windows-host-agent-supplied-artifact-verification`
8. `windows-testclient-task-cleanup-runtime-proof`
9. `windows-host-agent-current-bundle-two-station-installer-proof`

## Verify

- `uv run pytest -q -ra -m 'not live'` -> 834 passed
- `go test ./...` in `host-agent/windows-display-agent` -> pass
- Windows `go test -c` cross-build -> pass
- focused release/artifact suite -> 24 passed
- focused Ruff -> pass
- `sh -n tools/release/publish_self_hosted.sh` -> pass
- `./bin/openspec validate --all --strict` -> pass
- `git diff --check` -> pass

## Result

All technical review findings are fixed and archived. The current source-bound
artifact SHA is `9c5e61ea...` with Go source fingerprint `63e8d407...`.
Windows-native cancel/failure/fallback scenarios, normal interactive launch,
exact-PID window stability through 62 seconds, exact cleanup and immutable
baseline comparison are all `ok`. The complete QA payload is represented by
one ignored runtime manifest reconstructed from exact machine-readable status
paths. No publication action has run.

Review cycle 2 then blocked atomic publication because current-artifact G12/G14
runtime proof covered only station B. Change 9 adds the missing production
installer registry surface and proves the exact current artifact on both
supported Windows builds. Both installer runs, G12/G14 health and the repeated
immutable cleanup audit are `ok`; publication remains disabled.

Published reviewed payload as `e53053b48a0f2d977f49d7193aa9bcaaaa0e1446`; push status `pending` on `main`/`origin`.

## Next

- done

## Archive

- `openspec/changes/archive/2026-07-14-windows-testclient-interactive-task-launch/`
- `openspec/changes/archive/2026-07-14-windows-testclient-authenticated-loopback-relay/`
- `openspec/changes/archive/2026-07-14-windows-host-agent-windowless-helper-lifecycle/`
- `openspec/changes/archive/2026-07-14-windows-testclient-relay-listener-only-readiness/`
- `openspec/changes/archive/2026-07-13-windows-host-agent-release-artifact/`
- `openspec/changes/archive/2026-07-14-windows-testclient-launch-fail-closed-cleanup/`
- `openspec/changes/archive/2026-07-14-windows-host-agent-supplied-artifact-verification/`
- `openspec/changes/archive/2026-07-14-windows-testclient-task-cleanup-runtime-proof/`
- `openspec/changes/archive/2026-07-14-windows-host-agent-current-bundle-two-station-installer-proof/`

## Change 1: `windows-testclient-interactive-task-launch`

### Related

- `openspec/board/3.inprogress/fix-windows-testclient-launch-and-solo-read-regression.md`

## Change 2: `windows-testclient-authenticated-loopback-relay`

### Related

- `openspec/board/3.inprogress/fix-windows-testclient-launch-and-solo-read-regression.md`

## Change 3: `windows-host-agent-windowless-helper-lifecycle`

### Related

- `openspec/board/3.inprogress/fix-windows-testclient-launch-and-solo-read-regression.md`

## Change 4: `windows-testclient-relay-listener-only-readiness`

### Related

- `openspec/board/3.inprogress/fix-windows-testclient-launch-and-solo-read-regression.md`

## Change 5: `windows-host-agent-release-artifact`

### Related

- `openspec/board/3.inprogress/package-current-windows-host-agent-binary.md`

## Change 6: `windows-testclient-launch-fail-closed-cleanup`

### Related

- `openspec/board/3.inprogress/fix-windows-testclient-launch-and-solo-read-regression.md`

## Change 7: `windows-host-agent-supplied-artifact-verification`

### Related

- `openspec/board/3.inprogress/package-current-windows-host-agent-binary.md`

## Change 8: `windows-testclient-task-cleanup-runtime-proof`

### Related

- `openspec/board/3.inprogress/fix-windows-testclient-launch-and-solo-read-regression.md`
- `openspec/board/3.inprogress/package-current-windows-host-agent-binary.md`
- `../.artifacts/openspec/windows-testclient-task-cleanup-runtime-proof/20260714T160743Z-current-source-bound-runtime-proof/runtime-proof-summary.json`

## Change 9: `windows-host-agent-current-bundle-two-station-installer-proof`

### Related

- `openspec/board/3.inprogress/package-current-windows-host-agent-binary.md`
- `openspec/changes/archive/2026-07-14-windows-host-agent-current-bundle-two-station-installer-proof/`
- `../.artifacts/openspec/windows-host-agent-current-bundle-two-station-installer-proof/20260714T170159Z-initial/runtime-proof-summary.json`

## Log

- 2026-07-14 opened from the independent review atomic-scope finding after both
  owner-local rescue changes passed and archived; no historical done card or
  archive was modified.
- 2026-07-14 review cycle 3 required current-fingerprint Windows cleanup
  evidence and production call-site sensitivity. Change 8 completed both,
  preserved exact cleanup/baseline state and left publication pending review.
- 2026-07-14 review cycle 4/atomic cycle 2 required production-installer G12/G14
  proof for the current artifact on both supported Windows builds. Change 9
  completed the two-station run and exact immutable cleanup without publication.
- 2026-07-14T19:09:40Z publish finalized card into `4.done` with commit `e53053b48a0f2d977f49d7193aa9bcaaaa0e1446` and push status `pending`.

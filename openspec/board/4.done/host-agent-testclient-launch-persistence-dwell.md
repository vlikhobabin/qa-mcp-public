# TestClient launch readiness must survive a persistence dwell, not just an instant (F3)

## Status
4.done

## Owner
unassigned

## Order Index
129

## OpenSpec Stage
archived. Follow-up to `host-agent-launched-testclient-persistence` (archived):
its honest-readiness classifier still returns `ready` for a client that binds its
TPort and then dies seconds later — the exact failure mode of that card.

## Change Set
- `host-agent-testclient-launch-persistence-dwell`:
  `openspec/changes/archive/2026-07-08-host-agent-testclient-launch-persistence-dwell/`

## Source
- 2026-07-08 real .205 / [redacted third-party configuration] E2E, host-agent `0.1.1-testclient-readiness`.

## Problem
`waitForTestClientReadiness` returns `"ready"` as soon as it observes, at a single
instant, that the process is alive AND the TPort is listening (with a non-blocking
`waitDone` re-check). On the real host the spawned client binds its TPort, is
briefly alive, then exits ~4 s later. The launch therefore returned
`ok:true, readiness:"ready", listening:true, alive:true` for a client that did
**not** persist — a false-positive for the brief-then-die case, which is precisely
this card family's symptom. The offline tests could not catch this because the
process fakes never bind-then-die on a real timeline.

This is distinct from F2 (which fixes *why* the client dies). F3 hardens the
*readiness signal* so that, regardless of the launch mechanism, `ready` is not
reported for a client that fails to persist.

## Scope
1. Require a **persistence dwell** before returning `ready`: after the TPort is
   first observed listening and the process alive, re-verify liveness + listening
   after a bounded dwell (e.g. re-check that the process is still alive and the
   port still listening a short interval later) before classifying `ready`.
2. If the process exits or the port drops during the dwell, classify
   `exited_early` / `not_listening` (honest failure), not `ready`.
3. Keep the launch bounded by `timeout_seconds` (works with F1's extended client
   timeout).

## Acceptance
- A client that binds its TPort and exits within the dwell is classified as a
  structured failure (`testclient-exited-early` / `testclient-not-listening`),
  never `ok:true, readiness:"ready"`.
- A genuinely persistent client is still classified `ready`.
- Go unit tests for the dwell (a fake that binds-then-exits during the dwell must
  not be reported ready).
- Live: on the real host, a non-persistent launch is reported as a failure, not
  `ready`.

## Change 1: `host-agent-testclient-launch-persistence-dwell`

### Why
Honest readiness must reflect *survival*, not an instantaneous listening probe;
otherwise the brief-then-die client this card family is about is reported ready.

### Goal
Add a bounded persistence dwell to the readiness classifier so `ready` implies the
client survived the dwell, and cover it with Go tests.

### Acceptance
- As in the card Acceptance.

### Depends On
- none. Complements `host-agent-testclient-persistence-fresh-session-context` (F2)
  and builds on `host-agent-launched-testclient-persistence` (archived).

### Notes For `$openspec-ff-change`
- Capability to modify: `qa-mcp-windows-host-agent-security` (readiness
  classification) and the `qa-mcp-tool-endpoint-contract` readiness scenarios.
- Add an offline Go test where the fake process binds the port then exits during
  the dwell → must classify as early-exit, not ready.

## Verify
- artifacts: `openspec validate host-agent-testclient-launch-persistence-dwell --strict`
  passed.
- matrix preflight:
  `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/matrix-preflight.json`
  passed with 4 rows and 1 explicit provider gap.
- RED Go: `cd host-agent/windows-display-agent && go test ./... -run TestTestClientReadinessRequiresPortPersistenceDwell`
  failed before implementation with `readiness = "ready", want exited_early`;
  retained in
  `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/host-agent-dwell-tests.md`.
- GREEN focused Go:
  `cd host-agent/windows-display-agent && go test ./... -run "TestTestClientLaunch(ReportsEarlyExitInsteadOfReady|ReportsNotListeningProcessInsteadOfReady|ReportsReadyOnlyWhenProcessAndPortLive|StartsDetachedAndRedactsSecrets)|TestTestClientReadiness(DoesNotTreatListeningPortAsAliveAfterExit|RequiresPortPersistenceDwell|DwellHonorsLaunchTimeout)"`
  passed.
- GREEN full Go: `cd host-agent/windows-display-agent && go test ./...`
  passed with `ok qa-mcp-host-agent 9.369s`.
- GREEN Windows cross-compile:
  `cd host-agent/windows-display-agent && GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-dwell.test.exe .`
  passed.
- Suite regression: `uv run --with pytest --with pyyaml pytest` passed with
  `790 passed in 49.97s`; suite drift passed with `result: OK (0 finding(s))`;
  `uv run --with pytest --with pyyaml pytest -m smoke` passed with
  `3 passed, 787 deselected in 2.80s`.
- Matrix archive gate:
  `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/matrix-archive-gate.json`
  passed with 4 rows and 1 explicit provider gap.
- Runtime live .205 confirmation was not run; provider gap retained at
  `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/windows-host-dwell-provider-gap.md`.
- Final OpenSpec: `openspec validate qa-mcp-windows-host-agent-security --strict`,
  `openspec validate qa-mcp-tool-endpoint-contract --strict`,
  `openspec validate --all`, and `git diff --check` passed.

## Archive
- `openspec/changes/archive/2026-07-08-host-agent-testclient-launch-persistence-dwell/`

## Result
Implemented timeout-bounded TestClient readiness dwell in the Windows
host-agent classifier, archived
`host-agent-testclient-launch-persistence-dwell`, and published the scoped
card-owned change set for `main`.

## Next
- none.

## Log
- 2026-07-08 filed from the .205 E2E; readiness returned `ready` for a client that
  died ~4 s after binding its TPort. Needs a persistence dwell before `ready`.
- 2026-07-08T12:53:49Z `$opsx-ff` prepared apply-ready artifacts and recorded
  live .205 confirmation as a qa-mcp provider gap for offline delivery.
- 2026-07-08T13:00:00Z `$opsx-do` implemented the dwell, verified offline Go
  and suite gates, synced specs, archived the change, and stopped awaiting
  external review per supervised-run instruction. No review, publish, commit
  or push was run.
- 2026-07-08T13:18:00Z external `$opsx-review` verdict was validated fresh:
  result `go`, cycle 1, findings 0. Publish docs pass found no separate durable
  docs update needed because the behavior is already synced into the main
  OpenSpec specs and the unavailable Windows .205 runtime proof remains a
  retained provider gap.
- 2026-07-08T13:25:00Z `$opsx-pub` final verification passed, staged only the
  card-owned manifest paths, and prepared the scoped publish commit for
  `origin/main`.

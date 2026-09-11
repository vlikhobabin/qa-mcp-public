# Design

## Context

The host-agent already performs an explicit exact-name unregister and a
deferred retry, but the helper-only test remains green if those production
calls disappear. The last release-ready T4 artifact is bound to the earlier Go
source fingerprint, so static checks cannot close the current delivery gate.

## Decisions

- Encapsulate idempotent explicit cleanup and deferred fallback in a small
  injectable guard. Successful explicit cleanup suppresses fallback; failed
  explicit cleanup is returned to the caller and leaves fallback armed.
- Keep a focused source-call-site contract test for both production invocations
  in the Windows launch file. Behavioral guard tests alone do not prove wiring.
- Compile an opt-in Windows test that registers only randomized
  `qa-mcp-testclient-launch-*` tasks. It cancels a parent context before calling
  the real unregister helper, then verifies the exact task is absent. A second
  task injects a first cleanup failure, proves that boundary returns failure,
  runs fallback, and verifies exact absence.
- Default the bridge token from the host token only when registry URL is
  non-empty. Otherwise all registration fields remain empty and the existing
  disabled solo client starts without registry I/O.
- Build the host-agent bundle and Windows test executable from the same current
  tree. Bind retained evidence to artifact SHA-256, VCS revision/modified state
  and the host-agent Go source fingerprint.
- Stage both binaries in an exact proof directory on station B. Run a dedicated
  interactive scheduled-task normal launch using the same product endpoint as
  M9, including exact-PID window and 62-second stability probes. Remove the
  exact task, PID, token and directory, then run the T4 post-cleanup comparison
  against the immutable initial preflight snapshot.

## Safety

The integration is opt-in, bounded and exact-name scoped. No wildcard or
name-wide cleanup is permitted. Test tasks contain no 1C password or product
launch command. The station executable is staged at an owned exact path and is
removed after execution. T4 cleanup restores the immutable pre-run station and
compose state; publication remains disabled.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | n/a_reason | residual_risk | provider_owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Current source-bound Windows host-agent transient scheduled-task cleanup | Build manifest-bound bundle/test binary; stage an exact proof directory; run normal launch plus cancellation and injected-cleanup-failure tests; exact cleanup and immutable-baseline comparison | `runtime_apply_log`, host-agent bundle manifest/SHA, source fingerprint, Windows test log/summary, normal-launch summary, exact cleanup and M10 comparison | `.artifacts/openspec/windows-testclient-task-cleanup-runtime-proof/<run-id>/` | provided | — | Windows Task Scheduler availability and station connectivity are external; all operations are bounded and fail closed | qa-mcp + root T4 |
| Managed form / TestClient | Normal source-bound TestClient process on station B | Direct authenticated product launch endpoint, exact-PID window and 62-second stability probe | `qa_testclient_scenario`, current-host-agent normal-launch summary | same evidence root | provided | — | Uses the existing demo target and starts no data-changing scenario | qa-mcp |
| BSL | — | — | — | — | n/a | No BSL source changes | none | qa-mcp |
| Metadata | — | — | — | — | n/a | No 1C metadata changes | none | qa-mcp |
| Role | — | — | — | — | n/a | No role changes | none | qa-mcp |
| Posting | — | — | — | — | n/a | No posting changes | none | qa-mcp |
| Report or DCS | — | — | — | — | n/a | No report or DCS changes | none | qa-mcp |
| Migration or compatibility | Windows artifact/source binding only | Compare manifest, staged/running host-agent SHA, Windows test SHA and source fingerprint | `compatibility_matrix` in evidence summary | same evidence root | provided | — | Dirty-tree builds are explicitly marked `vcs.modified=true` and allowed only for review evidence | qa-mcp |

## Context

The archived `host-agent-launched-testclient-persistence` change made
host-agent readiness honest for pre-listening early exit and not-listening
timeouts. The archived
`host-agent-testclient-persistence-fresh-session-context` change moved Windows
launches to an active interactive session token, but the real .205 failure
showed another gap: a child can bind the requested TPort, satisfy the current
instantaneous probe, then exit roughly seconds later.

This change is a suite/provider launch-readiness hardening. It does not create
new native TestClient protocol claims or new 1C business actions. The requested
delivery proof is offline-completable with Go tests; the live .205 confirmation
must remain a provider gap in this run.

## Goals / Non-Goals

**Goals:**

- Make `readiness: "ready"` mean the spawned TestClient remained alive and its
  TPort remained listening across a bounded persistence dwell.
- Classify process exit during the dwell as `exited_early`, not `ready`.
- Classify a listening port that drops during the dwell as `not_listening`, not
  `ready`, when the process has not reported exit.
- Keep the total readiness wait bounded by `timeout_seconds`.
- Add RED/GREEN Go coverage with a fake process that binds the TPort and exits
  during the dwell.
- Record live .205 confirmation as a provider/runtime gap instead of claiming
  runtime evidence that was not produced.

**Non-Goals:**

- No new TestClient wire-frame capture, replay template, dynamic-field claim or
  protocol-corpus update.
- No Python remote-client behavior change beyond preserving the existing
  structured host-agent failure contract.
- No business data mutation, managed form command click, posting, import/export
  or COM live write.
- No claim that the real Windows .205 host has been re-tested in this session.

## Decisions

### Dwell inside the readiness classifier

`waitForTestClientReadiness` will keep its public result labels and add a
bounded dwell after the first successful TPort probe. During the dwell it will
continue to watch `ctx.Done()`, `waitDone`, the launch deadline and TPort
state. It returns `ready` only after the dwell elapses while the process has
not exited and the TPort remains listening.

Rationale: the false positive is in the classifier, so the guard belongs at
the same boundary that decides `ready`. Keeping labels unchanged preserves the
HTTP response and Python remote-client error contract.

Alternative considered: add a second sleep-and-check in `launchHostTestClient`
after the classifier returns. That would duplicate timeout handling and make
the classifier still unsafe for direct unit tests and future call sites.

### Keep the dwell short and timeout-bounded

The dwell will be a small constant relative to launch timeout. The classifier
will not return later than the existing readiness deadline; if the deadline
expires before the dwell proves persistence, it returns `not_listening` unless
`waitDone` has already signaled process exit.

Rationale: launch calls already block synchronously and Python has an HTTP
timeout margin for that wait. The dwell should prevent the bind-then-die false
positive without turning every launch into a long runtime soak.

Alternative considered: require a 60-second dwell matching the manual Windows
smoke. That is too expensive for every launch and belongs to live runtime
acceptance, not the basic readiness classifier.

### Offline proof is authoritative for this delivery boundary

The Go test must spawn a real local fake that binds the requested TPort, stays
accept-capable briefly, then exits before the dwell can complete. The expected
result is `exited_early`, never `ready`.

Rationale: this reproduces the timing shape the prior offline tests missed
without requiring the unavailable Windows .205 host.

## Risks / Trade-offs

- The dwell may add a small delay to genuinely ready launches -> keep it short
  and covered by the configured launch timeout.
- A local port probe cannot prove GUI usability -> retain the live .205
  provider gap and do not claim runtime persistence.
- Already-listening TPort reuse does not have an owned process to dwell -> keep
  existing reuse semantics because the card targets newly spawned clients.
- A process that stays alive while another process owns the port can still
  satisfy a host-local TPort probe -> unchanged residual risk from the prior
  host-agent readiness contract.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | host-agent-launched Windows TestClient on real .205 host | Real-host smoke: launch through running host-agent, wait longer than the dwell, confirm the TestClient remains alive and TPort reachable, then attach/read through qa-mcp | Sanitized smoke transcript or provider-gap report | `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/windows-host-dwell-provider-gap.md` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real Windows .205 host unavailable in this session; runtime persistence remains unproven. |
| Delivery or runtime apply | Windows host-agent TestClient readiness classifier | Go unit tests for bind-then-exit-during-dwell, persistent ready, timeout boundedness and existing early-exit/not-listening behavior | `go test ./...` output and retained summary | `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/host-agent-dwell-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline tests prove classifier timing, not real Windows GUI persistence. |
| Native protocol claim | TestClient wire frames and replay templates | No protocol semantic change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No native TestClient protocol claim is made. | None for corpus coverage. |
| Business data mutation | Object writes, posting, delete/fill/import/export | No business mutation is part of this launch-readiness change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change launches/checks TestClient process and TPort liveness only. | None beyond process availability. |

## Migration Plan

1. Add the failing bind-then-exit dwell test.
2. Implement dwell-aware readiness while preserving current response labels.
3. Retain focused Go command summaries and provider-gap artifact under the
   planned evidence root.
4. Sync delta specs, archive, and stop for external review.
5. Later, run the real .205 host smoke and replace the provider-gap record with
   a sanitized proof bundle.

## Open Questions

- None for offline implementation. The remaining unknown is whether the real
  .205 launch survives after this classifier hardening; that is deliberately
  outside this supervised offline run.

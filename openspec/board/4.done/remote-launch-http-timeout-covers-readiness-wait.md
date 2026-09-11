# Remote launch_test_client HTTP timeout must cover the host-agent readiness wait (F1)

## Status
4.done

## Owner
unassigned

## Order Index
127

## OpenSpec Stage
archived; review passed; publishing. Follow-up regression from `host-agent-launched-testclient-persistence`
(archived) — the synchronous readiness wait it added broke the remote-launch HTTP
call under the default timeout. **The fix is already implemented in the working
tree** (see Source) and live-proven on .205; this card formalizes it (OpenSpec
change + test + review gate).

## Source
- 2026-07-08 real .205 / [redacted third-party configuration] E2E (host-agent `0.1.1-testclient-readiness`,
  user `Админ`, base `C:\Users\User\Documents\private-lab-infobase`).
- Card `host-agent-launched-testclient-persistence` made `/testclient/launch`
  **block synchronously** until the host-agent classifies TestClient readiness
  (up to its `timeout_seconds` launch wait). But the Python remote client
  (`RemoteAgentBackend`) sends every request with the single fixed
  `settings.host_agent_timeout` (default **10 s**). A real launch needs seconds
  for `1cv8` to start and bind its TPort, so the client HTTP request timed out
  before the host-agent could answer.

## Problem
Driving HEAD `launch_test_client` against the real .205 host-agent
(`QA_MCP_HOST_AGENT_TIMEOUT` unset → 10 s) failed **deterministically**:

```
TimeoutError: timed out
  ... urllib.request.urlopen(req, timeout=self.timeout) ...  # display_backend.py
```

The launch never returned the host-agent verdict even though the host-agent
spawned the client — the remote-launch path is unusable with the default
timeout. Raising `QA_MCP_HOST_AGENT_TIMEOUT` to 180 s made the same call return
`readiness: ready` in ~4 s, isolating the cause to the client-side timeout, not
the host-agent.

## Scope
1. The `/testclient/launch` request MUST use an HTTP timeout that covers the
   host-agent readiness wait (`timeout_seconds`) plus a margin, instead of the
   short default `host_agent_timeout` used for fire-and-forget primitives. Other
   primitive calls keep the short default.
2. Regression test that the launch request timeout is extended past the default.

## Implemented (working tree, uncommitted at filing)
- `src/qa_mcp/protocol/display_backend.py`: `LAUNCH_HTTP_TIMEOUT_MARGIN = 15.0`;
  per-call `timeout` threaded through `_request`/`_json`; the backend
  `launch_test_client` calls `/testclient/launch` with
  `timeout=timeout_seconds + LAUNCH_HTTP_TIMEOUT_MARGIN`. `_request` uses
  `max(self.timeout, timeout)` so a call never gets a *shorter* timeout.
- `tests/test_display_backend.py`: `test_remote_testclient_launch_uses_extended_http_timeout`
  (captures the timeout at the `_request` boundary, asserts `>= wait` and
  `> default`); the existing launch-payload test now also asserts the extended
  timeout.

## Acceptance
- `launch_test_client` in remote mode with the default `host_agent_timeout`
  completes and returns the host-agent readiness verdict for a launch whose
  readiness wait exceeds the default timeout (no client-side `TimeoutError`).
- Regression test guards the extended launch timeout.
- Live: proven on .205 — default-timeout launch returns the verdict in ~3 s
  (previously `TimeoutError` at 10 s).

## Change Set
- `remote-launch-http-timeout-covers-readiness-wait`

## Verify
- Focused pytest: `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py -k 'remote_testclient_launch'` -> `3 passed, 21 deselected`.
- Full pytest: `uv run --with pytest --with pyyaml pytest` -> `789 passed`.
- Suite drift: `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` -> `result: OK (0 finding(s))`.
- Smoke gate: `uv run --with pytest --with pyyaml pytest -m smoke` -> `3 passed, 786 deselected`.
- Matrix archive gate: `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py ... --mode archive --json` -> `ok: true`.
- OpenSpec: `openspec validate qa-mcp-tool-endpoint-contract --strict`, `openspec validate remote-launch-http-timeout-covers-readiness-wait --strict`, and `openspec validate --all` passed.
- `git diff --check` passed.
- Live regression proof recorded in archived `tasks.md`: before the fix, default-timeout remote launch failed with `TimeoutError: timed out`; after the fix, the same default-timeout launch on real `.205` / [redacted third-party configuration] returned the readiness verdict in about 3 seconds.

## Archive
- `openspec/changes/archive/2026-07-08-remote-launch-http-timeout-covers-readiness-wait/`

## Related
- `openspec/changes/archive/2026-07-08-remote-launch-http-timeout-covers-readiness-wait/`
- `openspec/changes/archive/2026-07-08-host-agent-launched-testclient-persistence/`
- `.runtime/opsx/delivery-manifests/remote-launch-http-timeout-covers-readiness-wait.json`

## Result
Delivered through `$opsx-ff`, `$opsx-do`, external review cycle 2, and
`$opsx-pub`: existing Python implementation and tests verified, endpoint
contract synced, OpenSpec change archived, manifest updated, and the review gate
validated fresh with `result: go`.

## Next
- none

## Change 1: `remote-launch-http-timeout-covers-readiness-wait`

### Why
The synchronous readiness launch made the fixed 10 s client timeout too short,
so the remote-launch tool always failed on a real host before the host-agent
could answer.

### Goal
Give the `/testclient/launch` call a timeout that covers its readiness wait; keep
other calls on the short default; add a regression guard.

### Acceptance
- As in the card Acceptance.

### Depends On
- none (follow-up to `host-agent-launched-testclient-persistence`, archived).

### Notes For `$openspec-ff-change`
- Capability to modify: `qa-mcp-tool-endpoint-contract` (remote `launch_test_client`
  HTTP timeout for the synchronous readiness launch).
- The fix is already in the working tree; `$opsx-do` should formalize the
  OpenSpec change/spec delta around it and keep the live evidence in the card.

## Log
- 2026-07-08 filed from the .205 E2E; fix implemented in the working tree and
  live-proven (default-timeout launch returns the verdict; previously
  `TimeoutError`). Awaiting formal OpenSpec delivery via the review-gated flow.
- 2026-07-08T09:12:25Z `$opsx-ff`: created OpenSpec artifacts for
  `remote-launch-http-timeout-covers-readiness-wait`; implementation remains the
  pre-existing working-tree diff.
- 2026-07-08T09:24:00Z `$opsx-do`: verified existing implementation, synced
  `qa-mcp-tool-endpoint-contract`, archived the OpenSpec change, and stopped at
  `awaiting external review` per supervised-run instruction. No review or
  publish was run by this session.
- 2026-07-08T09:38:50Z external `$opsx-review` cycle 2: verdict `go`, findings
  0; the cycle-1 blocker was closed by
  `test_remote_testclient_launch_urlopen_timeout_is_extended`, which observes
  the timeout passed to `urllib.request.urlopen`.
- 2026-07-08T09:46:51Z `$opsx-pub`: validated the fresh external verdict,
  confirmed the synced endpoint spec plus this board card are the durable docs
  for the behavior, and prepared scoped publish.

## Context

`host-agent-launched-testclient-persistence` changed the Windows host-agent
launch endpoint from a fire-and-forget primitive into a synchronous readiness
classification boundary. A real `.205` / [redacted third-party configuration] launch with
`QA_MCP_HOST_AGENT_TIMEOUT` unset still used the Python default 10 second
request timeout, while the host-agent was allowed to wait much longer for
`1cv8` startup and TPort readiness. The client-side HTTP timeout fired first,
masking the host-agent readiness result.

The fix was implemented during live E2E discovery before this OpenSpec change
was opened. There is no separate pre-implementation RED pytest run for this
card. The regression proof is the live before/after observation: before the fix,
default-timeout remote `launch_test_client` failed with `TimeoutError: timed
out`; after the fix, the same default-timeout launch on the real `.205` host
returned the host-agent readiness verdict in about 3 seconds.

## Goals / Non-Goals

**Goals:**

- Make the Python HTTP request timeout for `/testclient/launch` cover the
  caller's launch readiness wait plus a bounded margin.
- Preserve the short default `host_agent_timeout` for unrelated host-agent
  primitives.
- Keep existing exact host-agent auth, version compatibility, payload shape,
  readiness propagation, and container-side TPort checks unchanged.
- Guard the timeout routing with focused offline pytest coverage.

**Non-Goals:**

- No host-agent Go endpoint change.
- No new native TestClient protocol frames, captures, replay templates or
  protocol-corpus claims.
- No business-data mutation, form command click, posting, write, import/export,
  runtime apply, or COM live write.
- No claim that pytest was written before the live-discovered implementation;
  the live before/after evidence is the recorded regression proof for this
  already-implemented fix.

## Decisions

### Per-call timeout override

`RemoteAgentBackend._request()` and `_json()` accept an optional per-call
`timeout`. When omitted, they keep using `self.timeout`; when provided, they use
`max(self.timeout, timeout)` so a call cannot accidentally shorten an operator's
configured default.

### Launch timeout derives from readiness wait

`RemoteAgentBackend.launch_test_client()` sends `/testclient/launch` with
`timeout_seconds + LAUNCH_HTTP_TIMEOUT_MARGIN`. The margin is intentionally
small and local to the Python client, because the host-agent already owns the
actual readiness deadline and diagnostic result.

### Existing primitive behavior stays short

No other remote host-agent primitive passes the extended timeout. Health,
version, screenshot, click, foreground, refresh and other primitive calls still
fail quickly according to `host_agent_timeout`.

## Risks / Trade-offs

- Long launch waits now keep the HTTP call open for the configured readiness
  window -> this matches the synchronous host-agent contract and is bounded by
  the caller's launch timeout plus margin.
- A very high operator-supplied `host_agent_timeout` remains honored for all
  calls -> using `max()` preserves explicit operator configuration.
- Offline tests observe timeout plumbing, not a real Windows GUI launch -> the
  live `.205` before/after evidence is retained separately in task verification
  notes.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Python remote `launch_test_client` to Windows host-agent `/testclient/launch` on real `.205` / [redacted third-party configuration] host | Record live before/after launch observation from the same default-timeout path | Sanitized runtime evidence summary in tasks verification notes | `openspec/changes/archive/2026-07-08-remote-launch-http-timeout-covers-readiness-wait/tasks.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live proof is summarized from the discovery session rather than replayed in this delivery run. |
| Delivery or runtime apply | Python HTTP timeout routing for host-agent launch call | Focused pytest that captures the timeout passed to `_request` / `_json` | `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py -k 'remote_testclient_launch'` output | `.artifacts/ai-run/<trace-id>/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Mocked test proves client-side timeout routing, not host GUI readiness. |
| Native protocol claim | TestClient wire frames and replay templates | No protocol semantic change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This change modifies host-agent HTTP timeout selection only. | None for corpus coverage. |
| Business data mutation | Object writes, posting, delete/fill/import/export | No business mutation is part of this lifecycle timeout change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change launches/attaches to TestClient and does not execute business commands. | None beyond process availability. |

## Migration Plan

1. Verify the existing Python implementation and tests.
2. Sync the endpoint contract delta into the main
   `qa-mcp-tool-endpoint-contract` spec.
3. Archive this formalization change and hand the card to the external review
   gate before publish.

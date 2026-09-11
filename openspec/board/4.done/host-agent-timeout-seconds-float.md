# Host-agent agent_cli_execute: accept JSON float timeout_seconds

## Status
4.done

## Owner
codex

## OpenSpec Stage
archived

## Source
- Whole-product E2E on the real Windows box (historical-user, 2026-07-04): containerized
  `agentic-rag` `research.answer` calling the host-agent bridge failed with
  **HTTP 400** — `json: cannot unmarshal number 300.0 into Go struct field
  agentCompleteRequest.timeout_seconds of type int`.
- Follow-up to the delivered bridge (`83f1184` — `agent_cli_execute` /agent/complete).

## Summary
The `/agent/complete` handler decoded `timeout_seconds` into a Go `int`
(`agentCompleteRequest.TimeoutSeconds int`). But the consumer — agentic-rag's
`HostBridgeTransport` — sends `request.timeout_seconds`, which is a **float** on
the wire (e.g. `300.0`, because the transport request's `timeout_seconds` is a
float field). JSON `300.0` could not unmarshal into a Go `int`, so `decodeJSON`
failed and the bridge returned **HTTP 400 invalid-json** before any CLI ran.

This was a wire-contract type mismatch that both sides' unit tests missed: the
Python fake-bridge tests accepted any JSON body, and the Go handler tests sent
integer literals. It only surfaced on the real cross-process wire. Directly
reproduced before this fix: a body with `timeout_seconds: 300.0` -> HTTP 400;
`300` -> HTTP 200.

## Acceptance
- `POST /agent/complete` with `timeout_seconds: 300.0` (JSON float) is accepted
  and runs the CLI (no 400 invalid-json); `300` (int) also still accepted.
- `timeout_seconds` <= 0 / absent -> default timeout; huge value -> clamped to
  `maxAgentTimeout`; sub-second -> 1s floor (existing clamp behavior preserved).
- A handler/unit test posts a **float** `timeout_seconds` and asserts the request
  is decoded and dispatched (guards the regression).

## Scope
- Component-local (qa-mcp host-agent): `agent_cli.go` struct field +
  `normalizeAgentTimeout` signature + a decode test. Windows cross-compile build
  stays green.
- Out of scope: agentic-rag transport (it may additionally send an int, but the
  receiver must tolerate JSON floats regardless — this card fixes the receiver).

## Safety
- No behavior change to auth, allowlist, timeout clamps, redaction or fail-closed
  paths; only the numeric type of `timeout_seconds` on decode.

## Affected Repositories
- qa-mcp (host-agent).

## Change Set
- `host-agent-timeout-seconds-float` — `TimeoutSeconds float64` +
  `normalizeAgentTimeout(float64)` + float-timeout decode test
  (cap `qa-mcp-windows-host-agent-security`).

## Verify
- `go test ./...` from `host-agent/windows-display-agent` — passed.
- `GOOS=windows GOARCH=amd64 go build -ldflags "-H windowsgui" -o /tmp/qa-mcp-host-agent.exe .` from `host-agent/windows-display-agent` — passed.
- `openspec validate host-agent-timeout-seconds-float --strict` — passed before archive.
- `openspec validate qa-mcp-windows-host-agent-security --strict` — passed after spec sync.
- `openspec validate --all` — passed.
- `git diff --check` — passed.
- `uv run --with pytest --with pyyaml pytest` — passed, 687 tests.
- 1C runtime verification: not applicable; this card does not touch BSL,
  metadata, live infobase access or QA/TestClient UI automation.

## Archive
- `openspec/changes/archive/2026-07-04-host-agent-timeout-seconds-float/`

## Related
- `openspec/changes/archive/2026-07-04-host-agent-timeout-seconds-float/`
- scoped delivery commit

## Result
Implemented the host-agent `/agent/complete` receiver tolerance for decimal JSON
`timeout_seconds`, added a raw JSON float handler regression test, synced the
host-agent security spec, documented the receiver contract in the host-agent
README, and archived the OpenSpec change.

## Next
- none after push

## Change 1: `host-agent-timeout-seconds-float`

### Why
The host-agent receiver rejected decimal JSON numbers for `timeout_seconds`,
which broke the real agentic-rag host bridge even when the numeric value was
bounded.

### Goal
Accept JSON float timeout values at the `/agent/complete` boundary while
preserving all existing timeout clamps and safety checks.

### Scope
- Decode `timeout_seconds` as a numeric type that accepts `300` and `300.0`.
- Normalize the decoded value to `time.Duration` using existing default/min/max
  behavior.
- Add a regression test using a literal JSON float body.

### Acceptance
- JSON float `timeout_seconds` reaches CLI dispatch rather than `invalid-json`.
- Existing int timeout and fail-closed cases still pass.
- Windows cross-compile build remains green.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-04-host-agent-timeout-seconds-float/`

### Notes For `$openspec-ff-change`
- Modified capability: `qa-mcp-windows-host-agent-security`.
- No 1C runtime matrix is required for this host-agent HTTP decode fix.

## Log
- 2026-07-04T17:19:01Z artifacts prepared and moved to `2.todo`.
- 2026-07-04T17:23:16Z implemented, verified, synced specs, and archived as `openspec/changes/archive/2026-07-04-host-agent-timeout-seconds-float/`.
- 2026-07-04T17:26:45Z publish verification passed, including full pytest.
- 2026-07-04T17:28:06Z scoped commit prepared for push.

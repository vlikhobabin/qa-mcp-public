## Context

live-mcp must support COM-backed live reads and selected guarded COM probes even
when it runs inside the Linux qa-mcp container. The COMConnector runtime remains
on the Windows host, and qa-mcp already ships a Windows host-agent that provides
the authenticated host bridge for display input, screenshots, agent CLI
execution, and 1C platform command execution.

This change implements only the qa-mcp host side of the COM bridge. The actual
COM logic and PyInstaller-frozen worker are owned by live-mcp. The host-agent
must therefore treat the worker as an installed executable, preserve the
worker's JSON protocol exactly, and keep the same fail-closed security posture
as the other sensitive host-agent endpoints.

No native TestClient protocol capture, replay, frame-range claim, source XML
change, BSL diagnostic, Vanessa MCP proof, or live infobase mutation is part of
this change.

## Goals / Non-Goals

**Goals:**
- Register `POST /com/execute` behind the existing `withAuth` middleware.
- Validate the WorkerRequest `operation` against the fixed allowlist:
  `ping`, `connect_check`, `execute_query`, `metadata_snapshot`, and
  `guarded_posting_smoke`.
- Require non-empty operator-intent evidence before `guarded_posting_smoke`.
- Spawn only a host-configured `ai-com-worker.exe --worker`, never a
  container-provided executable path or argv.
- Send the original WorkerRequest body to worker stdin without logging secrets.
- Return valid worker stdout JSON as UTF-8 bytes without truncating,
  re-encoding, or applying platform CP866 fallback decoding.
- Kill the worker process group on timeout and return bounded fail-closed
  diagnostics for startup, timeout, missing-worker, empty-output, and invalid
  JSON failures.
- Report COM worker availability in authenticated `/health`.
- Update installer/docs/version compatibility and unit tests.

**Non-Goals:**
- No live-mcp Python COM worker implementation or PyInstaller build target.
- No host-side COM connection pool.
- No container-controlled executable path, arbitrary argv, or shell execution.
- No real COMConnector smoke in this Linux workspace.
- No native TestClient protocol evidence update.

## Decisions

### Fixed worker executable selected by host configuration

The host-agent resolves the COM worker from a fixed host-side setting:
`QA_MCP_COM_WORKER_EXE`, a `-com-worker` flag, or the default
`ai-com-worker.exe` next to the host-agent binary. The request body never
supplies an executable path or argv. The spawned command is always:

```text
<configured-worker> --worker
```

This mirrors the existing host bridge pattern: the container sends semantics,
and the host owns executable selection.

Alternative considered: let live-mcp send a path. Rejected because that would
turn the host-agent into a generic process launcher and bypass the installed
artifact trust boundary.

### Request validation before spawn

The handler decodes a bounded copy of the JSON request body, validates only the
fields needed for policy, and keeps the original bytes for worker stdin. Unknown
operations fail before spawn. `guarded_posting_smoke` is the only mutating
operation in this contract and requires operator-intent evidence.

The accepted evidence field is intentionally simple: a non-empty
`operator_intent` string at the top level or in `payload.operator_intent`.
That keeps this host-agent gate independent from live-mcp internals while still
failing closed when the mutating operation lacks explicit approval.

### UTF-8 JSON passthrough, not platform-output decoding

The COM worker writes `WorkerResponse` JSON as UTF-8. `/com/execute` returns
that JSON body exactly after verifying it is valid JSON. It does not call the
platform command decoder, does not use `maxPlatformOutputRunes`, and does not
apply CP866 fallback conversion.

This is necessary because query and metadata snapshots can be larger than
platform diagnostic output and can contain Russian text that is already valid
UTF-8.

### Secret-safe failure handling

WorkerRequest can contain infobase passwords, connection paths, and query text.
The handler does not log or echo the request body. Failures return stable
error codes and bounded diagnostics from startup/wait errors only. Worker
stderr is bounded and redacted for obvious password-like values before it is
returned as detail.

### Process lifetime follows existing host-agent command runners

The COM worker runs under a context timeout with the existing process-group
helpers. On timeout, the host-agent kills the process group and returns HTTP
504 with `timeout`.

### Health is readiness-only

Authenticated `/health` reports whether the configured worker file exists and,
on executable platforms, is executable. Optional COM registration checks can be
added later behind Windows build tags. The first implementation keeps health
bounded and avoids live COM activation.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `host-agent/windows-display-agent` `/com/execute` bridge for live-mcp COM WorkerRequest | Fake-worker Go tests for operation allowlist, operator-intent gate, UTF-8 passthrough, missing worker, invalid worker JSON, timeout kill, auth boundary, installer worker path, and health readiness; cross-compiled Windows host-agent build | scenario_file, scenario_log, runtime_apply_log | `.artifacts/openspec/host-agent-com-execute-endpoint/verification-summary.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real COMConnector registration and license smoke is owned by the paired Windows/live-mcp E2E card, not this Linux host-agent implementation. |

## Risks / Trade-offs

- Worker stdout could be huge -> keep request body bounded but do not apply the
  platform diagnostic truncation to successful worker JSON; rely on worker-side
  `maxRows` and operation contracts for result sizing.
- Worker stderr may contain sensitive values -> return only bounded, redacted
  diagnostics and never include the request body.
- Linux CI cannot activate COM -> use fake-worker subprocess tests for the
  host-agent boundary and record real COM registration as a paired Windows/E2E
  handoff.
- The host-agent version changes affect remote display handshake -> update the
  compatibility set so current containers accept the new bridge build.

## Migration Plan

1. Implement the handler, worker runner, health probe, and configuration
   plumbing.
2. Extend installer support for the installed COM worker path.
3. Update docs and host-agent compatibility.
4. Add fake-worker Go tests and run the Linux/cross-build verification gates.
5. Sync the capability delta into the main spec and archive the change.

Rollback is reinstalling the previous host-agent binary and SHA pin. The
endpoint is additive and does not change existing display, agent CLI, or
platform command endpoints.

## Open Questions

- None for this host-agent implementation. The real `ai-com-worker.exe`
  packaging and live-mcp remote transport are tracked by the paired live-mcp
  card.

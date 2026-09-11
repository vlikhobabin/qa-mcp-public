## Context

Card `remote-client-host-agent-testclient-launch` added the authenticated
host-agent `/testclient/launch` boundary and Python remote-client routing. The
2026-07-08 .205 [redacted third-party configuration] acceptance showed the command construction was
correct, but a `1cv8` child spawned by the already-running scheduled-task
host-agent exits within roughly four seconds without creating a visible
`V8TopLevelFrame*` window. The same command persists when launched from a fresh
interactive context or direct interactive scheduled task, which narrows the
remaining root cause to inherited process context, especially environment
block values used by GUI initialization.

This change is a suite/provider runtime behavior change, not a native protocol
frame change. The offline suite can verify command construction, child
environment selection, and honest liveness classification; the real persistence
proof requires the unavailable Windows .205 host and must stay recorded as a
provider gap for this run.

## Goals / Non-Goals

**Goals:**

- Start host-agent-launched TestClients with a bounded GUI child environment
  that supplies explicit user profile, app-data and temp directory values.
- Make host-agent launch readiness fail closed: success requires a live process
  and a listening TPort, while early process exit and timeout return structured
  `ok:false` diagnostics.
- Make `/testclient/status` expose process liveness when a PID is available.
- Make Python `launch_test_client` in remote-client mode trust the host-agent
  readiness classification and attach only after the container-side TPort check
  also succeeds.
- Preserve local Linux/Xvfb launch behavior and existing redaction/security
  boundaries.

**Non-Goals:**

- No new native TestClient protocol frames, captures, dynamic-field claims or
  replay templates.
- No business data mutation, form command click, posting, write, import/export
  or COM live write.
- No claim that Windows .205 persistence has been proven in this session.
- No broad host-agent refactor or replacement with a scheduled-task launcher
  unless the environment fix is insufficient in later runtime work.

## Decisions

### Bounded environment first

`launchHostTestClient` will build the `exec.Cmd` environment from the current
process environment plus normalized GUI-critical values: `USERPROFILE`,
`APPDATA`, `LOCALAPPDATA`, `TEMP`, `TMP`, `HOMEDRIVE`, `HOMEPATH` and `PATH`
where a safe value can be derived. Empty or obviously service-scoped values are
replaced from standard Windows user-profile paths when possible. The response
returns only a bounded list of environment keys supplied, never raw values.

Rationale: experiments ruled out stdin/stdout EOF, `/P`, and process-group flag
choice. A child environment fix is the smallest change that addresses the
remaining differentiator without adding a second launch mechanism.

Alternative considered: launching every TestClient through a transient
scheduled task or `CreateProcessAsUser`. That remains a follow-up route if the
real host proves the environment fix insufficient; it is not implementable or
verifiable in this Linux-only session.

### Readiness is a launch classification

For a new spawn, `/testclient/launch` will wait until one of three outcomes:

- the process remains alive and TPort is listening: `ok:true`, `listening:true`,
  `alive:true`, `readiness:"ready"`;
- the process exits before TPort is listening: `ok:false`,
  `error:"testclient-exited-early"`, `listening:false`, `alive:false`;
- the launch timeout expires while the process is still alive but TPort is not
  listening: `ok:false`, `error:"testclient-not-listening"`, `alive:true`.

Reusing an already-listening TPort remains a success with
`reused_existing:true`. Status requests use the same liveness helper when a PID
is supplied and never infer `alive:true` from a port probe alone.

### Python remote launch requires both host-agent and container evidence

`RemoteAgentBackend.launch_test_client()` will raise a structured
`DisplayBackendError` when the host-agent returns `ok:false`. The MCP
`launch_test_client` wrapper will then return its existing structured failure
shape with the host command fallback. When the host-agent reports success,
qa-mcp still performs the container-side TPort probe before recording an active
attachment.

### Version compatibility is bumped narrowly

The host-agent version and Python compatibility set will be bumped for this
contract. Exact operator version overrides and SHA pinning remain strict.

## Risks / Trade-offs

- Environment fallback may still be insufficient on the .205 host -> retain the
  provider gap and require a later Windows smoke before claiming persistence.
- Waiting inside the host-agent launch endpoint increases request duration ->
  keep timeout clamping and reuse the existing request timeout field.
- PID liveness checks are OS-specific -> use a small helper with a Windows
  implementation for real status and a conservative non-Windows implementation
  for offline tests.
- The host-agent can prove only host-local TPort liveness; qa-mcp must still
  prove container-to-host reachability before attaching.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | host-agent-launched Windows TestClient on .205 [redacted third-party configuration] | Real-host smoke: launch through running host-agent, wait >60s, confirm `V8TopLevelFrameSDI`, TPort reachable from container, then protocol read attach | Sanitized smoke transcript or provider-gap report | `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/windows-host-persistence-provider-gap.md` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real host unavailable in this session; runtime persistence remains unproven. |
| Delivery or runtime apply | Windows host-agent `/testclient/launch` and `/testclient/status` | Go unit tests for environment construction, early-exit/not-listening/ready classification, status liveness and redaction | `go test ./...` output and retained summary | `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/host-agent-launch-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline process fakes cannot prove real GUI persistence. |
| QA/TestClient UI automation | Python remote-client `launch_test_client` attachment behavior | Pytest coverage for host-agent early-exit propagation, host-agent success plus container TPort proof, and unchanged local launch path | `pytest` output and retained summary | `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/python-remote-launch-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline tests prove classification and routing, not real Windows GUI state. |
| Native protocol claim | TestClient wire frames and replay templates | No protocol semantic change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No new native TestClient protocol claim is made. | None for corpus coverage. |
| Business data mutation | Object writes, posting, delete/fill/import/export | No business mutation is part of this lifecycle change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change launches/attaches to TestClient and checks liveness only. | None beyond process availability. |

## Migration Plan

1. Implement and verify offline Go/Python behavior.
2. Archive with the Windows persistence proof recorded as a provider gap when
   the real host is unavailable.
3. Before runtime acceptance is claimed, run the retained Windows .205 smoke and
   replace the provider-gap report with a sanitized proof bundle.
4. If the environment fix fails on .205, open a follow-up card for a transient
   scheduled-task or `CreateProcessAsUser` launch path.

## Open Questions

- Which exact inherited environment value on the scheduled-task host-agent
  causes 1C GUI initialization to exit early? The offline change can expose and
  normalize the likely keys, but the real host must confirm the final cause.

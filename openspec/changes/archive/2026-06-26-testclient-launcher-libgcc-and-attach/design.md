## Context

The qa-mcp lifecycle module starts a native Linux 1C `/TESTCLIENT`, waits for
the configured TPort, and returns a process handle that later MCP calls use by
`host:port`. On this lab host, `1cv8` can crash during dynamic linking because
the platform-bundled `libgcc_s.so.1` is older than the system `libhwy.so.1`
requires. The existing lifecycle code does not prepare `LD_PRELOAD`, so the
operator only sees a generic TPort timeout.

Protocol tools already connect by `host:port`, but the lifecycle API only
models owned processes. A client started outside qa-mcp can be probed for port
liveness, yet there is no explicit attach handle for tools or MCP consumers to
record that the client is external, not owned by qa-mcp cleanup.

## Goals / Non-Goals

**Goals:**

- Mirror the maintained system-libgcc preload behavior used by suite platform
  launchers.
- Preserve the existing launched-client process ownership and cleanup rules.
- Surface bounded launch failure evidence from `client.out` and
  `testclient.out` when the TPort never opens.
- Expose an attach-to-running-client handle that can open the same
  `TestClientSession` protocol entry point without claiming process ownership.
- Verify the behavior with offline tests first, then retain live launch and
  protocol-drive evidence when the Linux runtime preflight allows it.

**Non-Goals:**

- Do not add Windows launcher or host-agent behavior.
- Do not add new protocol frame claims or rewrite replay templates.
- Do not run business-data mutation or destructive UI actions.
- Do not terminate unrelated 1C sessions during attach or cleanup.

## Decisions

### Launcher Environment

Add a small lifecycle helper that resolves a TestClient launch environment. It
will autodetect the first existing system libgcc path from:

- `/lib/x86_64-linux-gnu/libgcc_s.so.1`
- `/usr/lib/x86_64-linux-gnu/libgcc_s.so.1`

The helper uses `QA_MCP_TESTCLIENT_LIBGCC_PRELOAD` as the operator knob:

- unset: autodetect and prepend the system libgcc when found;
- empty string: explicit opt-out;
- non-empty string: use that path or colon-separated preload value.

If an existing `LD_PRELOAD` is present, the qa-mcp value is prepended rather
than replacing it. The returned MCP status should expose whether a preload was
applied and which non-secret path was used.

Alternative considered: require operators to set `LD_PRELOAD` externally. That
keeps code smaller, but it preserves the failure mode that prompted this card
and makes `launch_test_client` unreliable on the suite Linux lab contour.

### Launch Diagnostics

When launch times out, teardown still runs first so owned processes and Xvfb
are not leaked. The raised error should then include a bounded diagnostic
summary with:

- port and timeout;
- process return code when already exited;
- last lines from `client.out` and `testclient.out` if present;
- output directory path.

Passwords are not written to argv diagnostics or status summaries. The
existing `/Out` path is preserved for platform-level logs.

Alternative considered: return the full process log. That would make debugging
easy but risks copying large runtime logs through MCP responses.

### Attach Handle

Add an `attach_test_client(host, port, ...)` lifecycle function and MCP tool
that validates the TPort is listening and returns a `TestClientProcess`-shaped
handle marked as external:

- `pid` is optional and may be absent;
- `owns_process` is false;
- `attached` is true;
- `stop()` refuses to kill the external process unless a future explicit
  ownership token exists.

The handle's `connect()` method still returns `TestClientSession(host, port)`,
so existing protocol callers can use the same session factory. This is an
attach-to-endpoint contract, not a new low-level wire handshake.

Alternative considered: make every protocol tool silently attach when
`host:port` is listening. That hides ownership semantics and makes cleanup
audits weaker.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `launch_test_client` native Linux process lifecycle | Offline lifecycle tests plus Linux runtime preflight before live launch | `source_preflight`, offline pytest, retained launch status/log summary | `.artifacts/openspec/testclient-launcher-libgcc-and-attach/20260626-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live run can be skipped only if preflight reports a runtime gap before starting 1C. |
| QA/TestClient UI automation | attach/session protocol drive through `TestClientSession` | Launch or attach a listening TestClient, then run a read-only descriptor/window probe | `qa_testclient_scenario`, `active_window` or `form_tree`, bounded run log | `.artifacts/openspec/testclient-launcher-libgcc-and-attach/20260626-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Protocol replay quality is proven by existing read-only tools; this card only proves lifecycle/session access. |
| Business data mutation | object writes, posting, delete/fill/import/export | no business mutation is part of this lifecycle change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This change only launches or attaches to TestClient and runs read-only probes. | Residual risk is limited to process/runtime availability. |

## Risks / Trade-offs

- [Risk] The system libgcc path differs on another Linux distribution. ->
  Mitigation: keep an explicit environment override and no-op autodetect when
  no known path exists.
- [Risk] Failed-launch diagnostics could grow too large. -> Mitigation: report
  only bounded tail lines and retain full logs under ignored runtime paths.
- [Risk] Attach mode could be mistaken for ownership. -> Mitigation: expose
  `attached`/`owns_process` in status and make cleanup refuse external handles.
- [Risk] Live verification may be blocked by Apache/file-infobase contention or
  another 1C session. -> Mitigation: run preflight first and record a
  `runtime_gap` instead of discovering it mid-run.

## Migration Plan

1. Add lifecycle helpers and MCP fields without changing existing default
   method signatures for callers.
2. Add offline tests for env resolution, diagnostics, and attach ownership.
3. Run OpenSpec validation and focused pytest.
4. Run live launch/read-only proof only after the Linux runtime preflight
   succeeds; otherwise retain the preflight gap as verification evidence.

Rollback is deleting the new helpers/tool fields and returning to the prior
launcher environment behavior; no persisted data migration is involved.

## Open Questions

- None for implementation. Runtime evidence may still be gated by lab
  availability at verification time.

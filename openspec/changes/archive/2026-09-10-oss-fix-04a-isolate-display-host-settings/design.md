## Context

Re-inspected on 2026-09-10 against clean published baseline `637e3aa` after
T0–T5 test cleanup. The OSS-00 orchestrator repeated all four constructor
observations at this HEAD without HTTP/socket calls.
`create_mcp_server` and `bind_application_context` already carry explicit
Settings. `_display_backend` still calls `get_display_backend()` without them;
that factory and `RemoteAgentBackend.from_env` call `Settings.from_env`.
`_local_only_tool` and launch/attach/stop availability checks also read env.
`DisplayBackendError.to_result` derives mode from env, and remote client errors
can construct installation guidance through another env-dependent helper.

A local probe called an extra inspection tool through real FastMCP factories,
only constructing backend objects. With process mode local, explicit remote A
returned `local-xtest`. With process remote C, explicit remote A, local B and
empty remote settings all returned C's backend address. HTTP and socket entry
points were prohibited. This confirms selection leakage, not actual misdirected
Windows execution. Probe/source hashes are retained in
`.runtime/oss00-refresh-20260910/`; reproduction is restated here so those ignored
files are not prerequisites for implementation or review.

Existing tests cover explicit env constructors, compatibility pins, fake
factory state, and lifecycle windows. They do not prove end-to-end application
Settings ownership: several MCP tests replace the entire backend constructor.

## Goals / Non-Goals

Goal: one application's Settings and current attachment govern every composed
display and host-agent lifecycle request, guard and related configuration
diagnostic. Complete C1–C4 from the card through real factory calls.

Non-goals: transport/relay policy (FIX-04B), workspace roots (FIX-04C), a new
non-owned attach observer, private Runtime Proxy, Windows API/wire changes,
native qualification, ChangeRail changes or universal dependency injection.
Do not restore omitted external-processor support or resume FIX-02.

## Decisions

1. Add explicit Settings-based construction in `display_backend.py` and consume
   it from composition. Keep `from_env` as a legacy adapter outside composition.
   Existing Settings fields cover the required values; converting Settings to
   env or mutating process environment would reintroduce precedence ambiguity.
2. At composed entry points use `current_application_context().settings` for
   backend choice and availability. Pass Settings down to mode/install guidance
   only where consumed; avoid low-level imports of core/mcp_server or a second
   context registry. Review all referenced constructor/guard call sites, not just
   `_display_backend`. Retain `_remote_client_enabled` legacy behavior separately.
3. Create fresh per-operation remote backend state, or otherwise demonstrate
   equivalent isolation without shared mutable target/handshake fields. Bind
   the current validated attachment each call, including native client port
   versus relay port. Do not cache `client_target` across session changes.
4. Preserve semantics of existing port fallback, pin defaults, timeout behavior
   and window precedence from `from_env`; absence in explicit Settings means
   absence, not permission to consult another source. Remote-without-agent
   fails through existing bounded errors; local mode stays local.
5. Host lifecycle scope includes bound/unbound launch, status and stop, and
   the existing unbound attach compatibility route. Bound non-owned attach
   currently refuses missing observation before constructing a backend: retain
   that behavior and a zero-call control. Cleanup may use an already admitted
   synthetic attachment without claiming new attach support.

## Verification and test cost

Use fake HTTP at the request boundary to observe address, authentication,
timeout and target without replacing the constructor being verified. Fake X11,
socket probes and process signalling must forbid unintended real calls.
Two factories plus conflicting env are enough; vary independent settings in a
compact matrix rather than a Cartesian product of all fields. Test representative
display operations, every distinct lifecycle constructor/guard branch, valid
owned controls, rejected stale/foreign attachment, explicit empty values,
nested/async interleaving and exception restoration. Assert secret absence in
public error serialization using synthetic sentinel values.

Focused groups: `tests/test_shared_core_extension.py`,
`tests/test_display_backend.py`, selected lifecycle/cleanup nodes. Existing
target/evidence builders from `tests/support/` may be reused with fresh state.
Additional consumer tests follow actual modified-module selection; do not
restore an unconditional full suite/coverage floor. Record `--durations=10` and
JUnit for selected checks. No test is executed as part of this planning pass.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason / residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient orchestration | Python display/lifecycle routing, C1–C4 | Real factory regressions with fake HTTP/X11/signals | Focused pytest, request observations, JUnit, context restoration | `.runtime/qa-verification/oss-fix-04a/` | required | qa-mcp | Proves configuration routing only |
| Runtime apply / Windows desktop | No Windows or 1C code/deployment in this slice | Final-source qualification tracked by FIX-11/12 | No live proof claimed by this card | `openspec/board/1.backlog/oss-fix-12-verify-corrected-windows-runtime.md` | N/A | qa-mcp | No runtime deployment authorized; native desktop behavior remains unqualified by offline tests |
| BSL, metadata, forms, rights, posting, migration | No changes to these surfaces | No scenario for a changed 1C object | N/A | N/A | N/A | qa-mcp | No 1C object/data changes; routing correctness does not prove business outcomes |

Capture sources/frame ranges/replay: N/A, no protocol claim or frame change.
Runtime card size: one Python configuration invariant, two implementation
checkpoints; no combined BSL/apply/UI mutation work. Time and LOC estimates
are advisory, not stop conditions or an execution authorization.

## Risks / Trade-offs

- Configuration/input safety: wrong source can route UI or lifecycle effects
  to another host. C1–C3 use conflicting fake settings and inspect actual calls.
- Mutation/restart/external effects: consumers include input and launch/stop;
  C2 proves exact ownership with fake effects. No real process or business data
  is changed during offline verification.
- Concurrency: mutable attachment or backend state can leak between calls.
  C2/C4 cover replacement, interleaving and exceptional context exit.
- Publication: no artifacts/endpoints are published by this change's behavior;
  normal delivery transaction and later release qualification remain separate.
- Legacy compatibility: env-based direct callers stay supported, but they are
  not evidence that a composed factory observes explicit settings (C4).

## Migration Plan

No data migration. Land Settings construction and its guards, then lifecycle
consumers and final contract checks. Recheck the current source before applying:
the clean baseline already retains stopped FIX-02. Its presence does not
complete or adopt that stopped work; preserve its behavior and history. Rollback, if needed,
is a scoped code revert; it would restore the known routing gap, so release must
not claim the fixed invariant after rollback.

## Open Questions

No unresolved product choice is required for this Python slice. The clean, published source baseline and complete offline delivery authority
are verified; native admission is the next gate.
FIX-02's stopped state remains a blocker for its own dependants, not a reason
to make this independent configuration correction depend on it.

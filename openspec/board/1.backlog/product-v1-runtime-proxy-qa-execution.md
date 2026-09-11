# Product v1: QA execution through Runtime Proxy without a qa-mcp fork

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story / epic

## Source
- `/opt/ai-dev-suite-for-1c/docs/v1/020_runtime-proxy-vision.md`, section 10.
- Product architecture discussion on 2026-08-19.

## Summary
Adapt the existing native TestClient `qa-mcp` for Franchisee v1, where the
MCP, protocol engine, Gherkin orchestration and reports remain in the Linux
Tenant Cell while TestClient, desktop input and screenshots execute through
the Windows Runtime Proxy (RPW).

Do not create a Windows copy of `qa-mcp` and do not mirror 68 MCP tools as 68
RPW handlers. Introduce one executor boundary that supports both:

- local Linux TestClient/display execution for the future Team topology;
- target-bound lifecycle, protocol stream and desktop primitives through RPW
  for Franchisee v1.

The current Windows host-agent/remote-client implementation is a proof and
compatibility source, not the final transport: it uses inbound HTTP/TCP, while
RPW must connect outbound through Runtime Relay.

## Current Findings
- All 68 tools are registered unconditionally; there is no product/default,
  Team or extended registration profile.
- `QA_MCP_REMOTE_CLIENT=1` changes runtime behavior after registration and may
  expose tools which can only return an unavailable result.
- Fine-grained MCP calls share TestClient UI state but lack a formal QA session,
  exclusive lease, command sequence and reconciliation contract.
- `run_scenario(single_session=true)` keeps one protocol socket, but a feature
  call executes only its first scenario; tag selection is not exposed through
  MCP and action execution is split between several paths.
- The 100% corpus claim proves Gherkin phrase recognition, not universal live
  execution of every parsed step.
- `measure_scenario` is local-boot-only and unavailable in remote-client mode.
- Direct OData/COM tools, scenario data assertions and autofill reference
  resolution duplicate responsibilities now assigned exclusively to
  `live-mcp`.

## Scope
- Define a stable `QAExecutor`/transport boundary for local Linux and RPW
  execution without forking MCP semantics or TestClient protocol code.
- Replace the inbound host-agent transport with Runtime Relay integration:
  target-bound TestClient lifecycle, one bidirectional loopback TPort stream,
  desktop readiness/input/screenshot/UIA primitives and bounded artifacts.
- Add a product-level QA session with `environment_id`, proxy session,
  lifecycle target, target generation, exclusive desktop lease, monotonic
  operation sequence, deadline, cancellation and ambiguous-action recovery.
- Refactor reusable operation cores so fine-grained tools and scenario steps
  use the same executors and verdict semantics.
- Support full selected feature/suite execution, tags, setup/teardown, stable
  test-run identity, reports and cleanup evidence.
- Add profile-aware tool registration. The default product-v1 surface keeps
  real UI read/write/action, scenario, screenshot, smoke and reporting tools;
  research, capture, arbitrary external-file and migration-only compatibility
  tools require an explicit special profile.
- Remove direct OData/COM access from the default QA surface. Route data
  assertions and reference candidates through the typed `live-mcp` contract
  for the same environment.
- Qualify Windows coverage/performance measurement through a target-bound
  debug executor/channel or keep `measure_scenario` outside the Franchisee v1
  advertised profile until it is proven.
- Add RTT/backpressure tests and the required Windows desktop-state/E2E matrix.

## Out Of Scope
- Implementing Runtime Relay identity, generic artifact storage or RPW GUI in
  this component repository.
- A generic TCP proxy, arbitrary Windows process execution, arbitrary desktop
  input or unrestricted filesystem access.
- Copying the full scenario engine or MCP server into RPW.
- Moving `live-mcp` COM/HTTP provider code into the QA Adapter.

## Acceptance
- [ ] The same default QA tool semantics run through a local Linux executor and
  an RPW executor selected from immutable environment context.
- [ ] RPW needs only lifecycle, fixed-target protocol stream, desktop and
  artifact primitives; no per-MCP-tool Windows handler exists.
- [ ] A fine-grained sequence such as open -> input/click -> read message ->
  screenshot is ordered under one target-bound QA session and cannot hit a
  different TestClient or desktop application.
- [ ] Disconnect after a mutating UI action produces an explicit ambiguous or
  reconciliation verdict and does not retry the action automatically.
- [ ] A multi-scenario feature can be selected by tags, executed as one test
  run and exported as deterministic JUnit/Allure with step timing and artifact
  references.
- [ ] Scenario and fine-grained paths call the same operation cores and expose
  the same structured error taxonomy.
- [ ] Default product-v1 registration omits direct OData/COM, protocol research
  and unsupported tools instead of advertising structured unavailability.
- [ ] Cross-provider data assertions use `live-mcp` for the same
  `environment_id` and remain part of the unified QA report.
- [ ] Team Linux execution does not require RPW and does not use a separate MCP
  implementation.
- [ ] Franchisee Windows E2E proves lifecycle, protocol reads/actions, display
  primitives, point-command ordering, whole scenarios, cleanup, isolation and
  artifacts on the authorized Windows target.
- [ ] Locked/disconnected/logged-off/sleeping desktop states have explicit
  qualified results and can never yield a false pass.
- [ ] `measure_scenario` is either proven through the Windows executor or is
  absent from the advertised Franchisee v1 profile with an explicit capability
  reason.

## External Dependencies
- Root Runtime Relay and RPW identity/environment/session contracts.
- RPW QA Adapter implementation and Windows package.
- `live-mcp` product-v1 exclusive provider profiles and Runtime Proxy route.
- Root artifact retention and audit contracts.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- Suite-root card `runtime-proxy-v1-qa-adapter-epic` (owned by the suite repository).
- `openspec/board/4.done/119-2026-06-25-windows-thin-cross-machine-delivery.md`
- `openspec/board/4.done/120-2026-06-26-windows-host-input-screenshot-agent.md`
- `openspec/board/4.done/s50-120-bind-remote-ui-actions-to-lifecycle-window.md`
- Live-mcp card `product-v1-exclusive-live-profiles` (owned by the live-mcp repository).

## Result
not started

## Next
- Triage as an epic, then fast-forward only the first implementation slice plus
  one look-ahead slice.

## Change Plan Notes
Expected decomposition boundaries are executor abstraction, outbound
TestClient/display transport, session semantics, scenario unification,
profile/data-boundary cleanup, debug measurement and Windows qualification.
Keep each change independently testable and do not bundle root/RPW
implementation into qa-mcp-owned code.

## Log
- 2026-08-19 card created from the Runtime Proxy QA architecture investigation.

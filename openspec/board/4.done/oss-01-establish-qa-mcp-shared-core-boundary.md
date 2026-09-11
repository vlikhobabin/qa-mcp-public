# Establish qa-mcp shared-core boundary

## Status
4.done

## Owner
unassigned

## Series
oss-01

## Order Index
400

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Summary
Create the public composition seam that allows standalone qa-mcp and the
private AI for 1C product to consume one shared protocol/scenario core without
a source fork or reverse dependency on private components.

## Acceptance
- An application factory composes settings, executor, tool profile and optional
  integrations instead of relying only on import-time global registration.
- Public executor, result/error, target/session and artifact contracts contain
  no Runtime Proxy, Relay, live-mcp or Team-specific fields or imports.
- Standalone and research profiles register only their supported tools; omitted
  tools are absent rather than advertised as unavailable.
- Existing local Linux and standalone Windows behavior remains covered by the
  shared contract suite.
- A fake downstream executor passes the public consumer contract without
  importing private AI for 1C code.
- The generic target/session seam supports the follow-up immutable target
  binding without another application-factory redesign.

## Change Set
1. `establish-qa-mcp-shared-core-boundary` -
   `openspec/changes/establish-qa-mcp-shared-core-boundary/`

## Change 1: `establish-qa-mcp-shared-core-boundary`

### Why
The current module-global MCP composition mixes public protocol behavior,
runtime state and concrete transports, which would force standalone qa-mcp and
AI for 1C to evolve through a source fork.

### Goal
Establish one product-neutral composition, executor and tool-profile boundary
while preserving current standalone behavior and protocol semantics.

### Scope
- Add public target/session, result/error, artifact and executor contracts.
- Add an application/runtime context and explicit `create_mcp_server` factory.
- Register deterministic standalone and research tool profiles.
- Route representative MCP and scenario actions through shared operations.
- Adapt current local Linux and Windows-host behavior to the public contracts.
- Add consumer fixtures, dependency-boundary checks and extension policy docs.

### Acceptance
- Same as the card Acceptance section and the change delta specification.
- Existing protocol templates, replay algorithms and cleanup ownership do not
  change as part of the composition refactor.

### Depends On
- none

### Related
- `openspec/changes/establish-qa-mcp-shared-core-boundary/`

## Dependencies
- none

## Verify
- Focused application-factory, MCP, scenario and display contract suite:
  `uv run pytest -q tests/test_shared_core_extension.py
  tests/test_free_startup.py tests/test_mcp_server.py
  tests/test_scenario_actions.py tests/test_scenario_runner.py
  tests/test_display_backend.py` -> `295 passed`.
- Exact GitHub CI command: `uv run pytest -q -ra -m "not live"
  --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60` -> `951 passed`,
  coverage `73.04%`.
- `uv run python -m compileall -q src/qa_mcp`, `git diff --check`, strict
  change/spec validation and strict validation of all 26 final OpenSpec
  objects passed.
- Linux preflight selected the required `/opt/1c-dev/vanessa_client` contour,
  then an owned local lifecycle/read smoke passed through `LocalQAExecutor`:
  the TestClient became alive/listening, the read returned three windows with
  no business mutation, and cleanup stopped the owned TestClient/Xvfb,
  removed its output directory, freed port 15381 and restored active Apache.
- Two distinct injected `Settings` instances now control omitted MCP endpoint
  and template defaults in both execution and the advertised schema. A
  parameterized real FastMCP/`ScenarioRunner` test covers `success`, `blocked`,
  `ambiguous` and `failure` through the shared operation contract.
- Windows-native proof passed on `HISTORICAL-LAB-HOST\\historical-user` at
  `historical-user@192.0.2.204`, platform `8.3.27.2130` x64, target
  `C:\\1C_BASES\\vanessa_client`. The source-bound host-agent was built from
  `e0dd2e287ba446fe0d3332b7c27077592365a94a` as
  `0.1.11-lifecycle-window-target`, SHA-256
  `ba9e7218c5b4ec3813cc0f0f601a179e95aba3b2bd6f7ffecc4756885cf3d1ce`.
- `create_mcp_server` selected `WindowsHostQAExecutor`; lifecycle, read and
  display operations each returned `OperationVerdict.SUCCESS`. The owned
  launch was not reused, the read returned three TestClient windows without
  business mutation, and the lifecycle-targeted screenshot was retained only
  in ignored evidence.
- Cleanup stopped the owned TestClient through its lifecycle handle, stopped
  the pre-existing qa-mcp host-agent task, removed the owned staging and local
  token copy, and left no relevant process or listener on ports 8000, 8001,
  15381 or 15382. Sanitized evidence:
  `.runtime/changerail/evidence/oss-01-establish-qa-mcp-shared-core-boundary/`.

## Archive
- `openspec/changes/archive/2026-08-24-establish-qa-mcp-shared-core-boundary/`

## Related
- `openspec/board/1.backlog/oss-04-bind-testclient-to-declared-project-runtime-target.md`
- `openspec/board/1.backlog/product-v1-runtime-proxy-qa-execution.md`

## Result
Shared-core implementation, offline verification and mandatory Linux and
Windows-native lifecycle/read/display verification are complete. The delta
specification is synced to
`openspec/specs/qa-mcp-shared-core-extension/spec.md`, the change is archived,
and independent review cycle 2 returned a fresh `GO` for scoped publication.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-24 child card extracted from the open-source roadmap; its OpenSpec
  change is apply-ready.
- 2026-08-24 internal `chrl-deliver` fast-forward normalized the accepted card
  with an ordered, do-parseable change section; existing artifacts were reused.
- 2026-08-24 shared contracts, application composition, deterministic tool
  profiles and representative operation routing implemented; focused and full
  non-live verification passed.
- 2026-08-24 an earlier handoff classified Linux verification as a target
  mismatch without retaining evidence. The rescue review rejected that claim;
  a fresh exact preflight selected `/opt/1c-dev/vanessa_client`, followed by a
  successful owned local lifecycle/read smoke and complete cleanup evidence.
- 2026-08-24 the Windows proof target was changed to the owner's home-network
  host `historical-user@192.0.2.204`. Because that private network is not routable from
  the suite server, the active change and open task 4.3 are checkpointed for a
  local-network continuation; this is not a ChangeRail review or publish.
- 2026-08-24 PR validation exposed machine-specific bundled-template absolute
  paths plus cosmetic JSON Schema titles/order in the raw FastMCP schema.
  Profile snapshots now preserve the logical bundled path and all
  required/default/description/validation keywords while removing only the
  installation root and generator metadata; the exact CI command passes
  locally.
- 2026-08-24 local-network continuation verified the authorized Windows host,
  built and installed the source-bound host-agent from merge commit `e0dd2e2`,
  and passed owned lifecycle, read and display operations through
  `WindowsHostQAExecutor`. Exact lifecycle cleanup, post-cleanup process/port
  inventory and secret-safe evidence were retained under the ignored OSS-01
  evidence directory.
- 2026-08-24 focused and full non-live verification passed (`290` and `946`
  tests respectively; coverage `72.87%`), the shared-core delta spec was synced
  to the main spec, and the completed change was archived for independent
  review.
- 2026-08-24 independent review cycle 1 returned `NO-GO`: composed server
  defaults still came from import-time settings, real MCP/scenario taxonomy
  coverage was incomplete, and the Linux runtime-gap claim lacked retained
  evidence. The rescue binds endpoint/template defaults per server in runtime
  and schema, covers all four verdicts through real paths, and replaces the
  stale gap claim with retained Linux preflight, live proof and cleanup. The
  already-merged PR predates this review gate and is retained as a documented
  process exception; all rescue changes remain unpushed pending a fresh `GO`.
- 2026-08-24 independent review cycle 2 returned fresh `GO`: all six
  acceptance criteria passed, R1-R3 were verified fixed, and R4 remains a
  non-blocking historical process exception.
- 2026-08-24T12:30:33Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

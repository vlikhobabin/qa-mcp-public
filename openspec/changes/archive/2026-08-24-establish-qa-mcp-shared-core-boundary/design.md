## Context

The public and cloud products must share one protocol/scenario implementation,
but the current 68-tool server is composed at module import time around global
settings and concrete local/host-agent transports. The Runtime Proxy epic needs
generic session/executor seams, while private transport and provider code must
not enter the public repository.

This is an architectural refactor, not a new wire claim. Existing curated
captures, synthesized bootstrap frames and replay behavior remain the evidence
baseline; no frame ranges or dynamic-field rules change. Runtime cleanup must
continue to affect only lifecycle-owned TestClient and display state.

## Goals / Non-Goals

**Goals:**
- Make the public package the canonical owner of protocol, scenario and
  operation semantics.
- Compose MCP servers from explicit settings, executor and tool profiles.
- Give private downstreams a stable, neutral contract tested without their
  code being present.
- Preserve existing local and standalone behavior during the refactor.

**Non-Goals:**
- Implement Runtime Relay, RPW, live-mcp or Team behavior.
- Redesign protocol frames or broaden mutation authority.
- Complete the runtime-target or external-processor backlog stories.
- Guarantee a permanently frozen Python ABI before the first public release.

## Decisions

1. Introduce an explicit `create_mcp_server(...)` composition root. The module
   entrypoint remains a thin compatibility wrapper. This is preferred to
   environment-selected imports because profiles become inspectable and
   testable.
2. Define structural contracts for executor lifecycle, protocol connection,
   display primitives, target/session identity, operation verdicts and
   artifacts. Contracts use qa-mcp-owned neutral models; private identifiers
   remain opaque metadata or downstream state.
3. Move reusable behavior behind operation functions that return the shared
   models. MCP wrappers and scenario actions both call those operations.
4. Register tools from named profiles. `standalone` is the supported default;
   `research` is explicit. Downstream AI for 1C constructs its extended profile
   outside this repository.
5. Use explicit dependency injection rather than automatic third-party plugin
   discovery for the first release. A private package calls the public factory,
   avoiding import-time execution of unknown entry points.
6. Preserve current capture/template resolution and replay algorithms. Contract
   tests use fakes offline; live Linux and Windows smoke confirms routing only.

## Risks / Trade-offs

- [Risk] Extracting wrappers changes schemas or tool names. → Snapshot and
  compare every selected profile and retain focused FastMCP schema tests.
- [Risk] An executor abstraction becomes a mirror of all MCP tools. → Keep it at
  lifecycle/protocol/display/artifact primitive level; operations remain in
  public Python.
- [Risk] Global process state leaks between factory instances. → Move attachment
  and session state into an application/runtime context and test isolation.
- [Risk] Private needs force public contracts to contain product concepts. →
  Require generic upstream proposals and prohibit reverse imports in CI.

## Migration Plan

1. Add models/contracts and fake executor tests alongside current behavior.
2. Add the factory and profile registry, initially adapting current handlers.
3. Move attachment/session state into the application context.
4. Route local and host-bridge behavior through public executors.
5. Hand the generic target/session contracts to the independent runtime-target
   binding card; public binding remains descriptor-neutral and AI for 1C owns
   its project-descriptor adapter.
6. Keep the legacy entrypoint delegating to the standalone factory until all
   callers migrate; remove only after compatibility tests and release notes.

Rollback is a revert to the previous composition entrypoint because no stored
data or protocol asset format changes in this change.

## Open Questions

- Final public package API stability is declared by the publication change;
  this change establishes the first contract candidate.

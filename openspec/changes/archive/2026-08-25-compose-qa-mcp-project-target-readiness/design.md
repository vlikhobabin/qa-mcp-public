## Context

The resolved target is still inert after OSS-04B. This change wires it into one
application/server instance and readiness chain without granting lifecycle
authority.

## Goals / Non-Goals

**Goals:**
- Resolve once at composition and isolate target state per application.
- Surface ordered secret-safe doctor/readiness state.
- Prove adapter parity read-only on Linux and Windows.

**Non-Goals:**
- Launch, attach, drive or clean a TestClient.
- Hide project-mode tool arguments or add evidence artifacts.
- Change native TestClient protocol mappings.

## Decisions

1. Store the optional resolution in `ApplicationContext`; process globals were
   rejected because multiple server instances must not share a target.
2. Let `create_mcp_server` accept an explicit resolution or resolve configured
   environment once. Runtime calls cannot replace it.
3. Add the target check to the existing ordered doctor chain and expose only
   logical status/observation fingerprints.
4. Keep read-only host preflight evidence separate from reviewed source and do
   not count it as lifecycle proof.

## Risks / Trade-offs

- [Import-time defaults diverge from injected settings] → Composition tests use
  non-default values and inspect the registered instance.
- [Readiness accidentally touches lifecycle] → Spies assert zero process,
  listener, platform and host-agent calls.

## Migration Plan

Bound callers pass the OSS-04B resolution; existing standalone callers omit it.
Rollback omits the binding. No process cleanup is applicable.

## Open Questions

- None. No capture sources, frames, dynamic fields or replay changes exist.

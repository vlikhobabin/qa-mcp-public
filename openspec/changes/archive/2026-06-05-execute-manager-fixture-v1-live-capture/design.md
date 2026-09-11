## Context

The dry-run path proves the output contract, but the live path must start the
TestClient, proxy and manager, then invoke the custom manager harness so each
manifest command generates real TCP traffic. The default Vanessa EPF asset is
currently absent from the repository, so the live path must distinguish a
runtime-provider gap from a successful capture.

## Goals / Non-Goals

**Goals:**

- Run `manager-fixture-v1-readonly` as a non-dry-run capture scenario.
- Route the manager harness to the proxy TestClient port.
- Store manifest, events, result and proxy traffic under the same runtime run
  directory.
- Preserve owned-PID cleanup behavior.

**Non-Goals:**

- No frame-range join or normalization; that belongs to analyzer tooling.
- No full catalog execution until the bounded smoke succeeds.
- No safe-action or mutation behavior.

## Decisions

1. Keep live path fail-closed for missing runtime assets.
   Rationale: a missing EPF or manager runtime profile must not be reported as
   protocol evidence.

2. Treat Vanessa MCP smoke probes as secondary evidence.
   Rationale: the custom manager harness is the corpus generator for this
   controlled path.

3. Keep all raw outputs under the existing ignored runtime capture directory.
   Rationale: reviewed docs should link compact summaries, not raw payloads.

## Verification Matrix

The implementation change affects Windows runtime orchestration, 1C process
startup and manager harness invocation. Detailed rows are in `tasks.md`.

## Risks / Trade-offs

- Invoking the harness may require a Vanessa step, direct 1C command path or a
  follow-up provider capability. The implementation must record the chosen path
  and provider gaps explicitly.
- Live manager startup can be blocked by EPF/runtime profile gaps. That should
  produce a gap report, not partial success.

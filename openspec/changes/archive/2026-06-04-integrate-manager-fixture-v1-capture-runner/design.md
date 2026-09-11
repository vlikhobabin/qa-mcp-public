## Context

The current protocol capture path can start TestClient, proxy traffic and
manager-side tooling for earlier scenarios. Manager fixture V1 needs those
pieces to share one run id so side-channel command events can be joined to TCP
frames without committing raw captures.

## Goals / Non-Goals

**Goals:**

- Add a Windows-native capture scenario for manager fixture V1 read-only runs.
- Pass the proxy TestClient endpoint and runtime output directory to the
  manager harness.
- Keep proxy traffic, manager events and 1C logs under one capture/run id.
- Preserve bootstrap/open-form traffic separately from read-only command cases.
- Clean up only PIDs created by the runner.

**Non-Goals:**

- No 1C-side protocol parsing.
- No frame normalizer or replay renderer changes in this step.
- No business-data mutation or safe-action command cases.
- No raw capture publication.

## Decisions

1. Extend the existing capture runner instead of creating a second
   orchestration script.
   Rationale: PID ownership, proxy setup and runtime directory conventions
   already belong to the capture runner.

2. Use a scenario name such as `manager-fixture-v1-readonly`.
   Rationale: the scenario boundary lets existing connect-only and corpus
   paths keep their behavior while enabling a controlled manager harness path.

3. Keep all generated output below the selected runtime run directory.
   Rationale: OPSX/publication steps can then publish compact summaries while
   raw TCP streams, logs and PID files stay ignored.

4. Make frame joins a post-run concern.
   Rationale: the runner can preserve proxy chunk counters and event times
   without forcing the manager harness to understand proxy internals.

## Risks / Trade-offs

- If the manager process fails after the proxy starts, the run may contain
  partial traffic. Mitigation: write a failed `manager_harness_result.json`
  and stop only owned PIDs.
- If an existing TestClient session occupies the base or port, startup may be
  blocked. Mitigation: preflight port/base usage and record a skipped/blocked
  result instead of killing unrelated processes.
- Cross-process timestamps may drift. Mitigation: include proxy chunk counters
  when available and keep timestamp-only joins as lower-confidence.

## Migration Plan

1. Add the new runner scenario and manifest/output path wiring.
2. Add a focused dry-run path that validates manifest/output paths without
   starting live 1C when possible.
3. Run a live smoke with a small command subset.
4. Expand the scenario to the full manager V1 command manifest.

## Open Questions

- Whether the scenario should reuse the existing capture directory shape or
  write under `runtime/protocol-research/api-corpus/<run-id>/`.
- Whether the first live run should attach to an already-open client fixture
  session or always start a fresh TestClient owned by the capture runner.

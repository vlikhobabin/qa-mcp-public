## Context

This change is the first point where card 61 may mutate disposable demo10413
business data. It therefore depends on the target-selection and manifest
contract changes and must fail closed when runtime state or recovery details do
not match the reviewed row.

## Goals / Non-Goals

**Goals:**

- Execute zero or more reviewed first-row-set mutations, preferring one complete
  recoverable row over breadth.
- Retain pre/action/post/recovery evidence and owned-process cleanup proof.
- Use unique test markers for created data so cleanup can be verified.
- Preserve a blocked result when provider/runtime readiness is insufficient.

**Non-Goals:**

- Clicking arbitrary demo controls outside the manifest.
- Accepting protocol mappings from visual success alone.
- Running production or customer infobases.
- Adding new frame-isolation or publication logic beyond retained execution
  evidence.

## Decisions

- Run the live runtime preflight before any 1C interaction: capture mode when
  the run starts its own TestClient/proxy/manager processes, attach mode when
  probing an already-running TestClient. A failed preflight produces the
  blocked result before execution; the capture wrapper enforces the
  capture-mode preflight automatically.
- Treat the manifest as the only executable input. Missing, incomplete or
  unrecoverable rows produce a blocked result before action.
- Re-read active form/window and target pre-state immediately before execution.
  A mismatch fails closed.
- Require recovery execution or a documented acceptable residue for every row
  that mutates data.
- Keep raw runtime output under ignored `runtime/` or `.artifacts/` paths and
  retain only compact summaries for reviewed artifacts.
- Clean only owned PIDs and record cleanup status.

## Risks / Trade-offs

- [Risk] The action mutates more demo data than expected. Mitigation: require a
  reviewed recovery plan and use unique `QA_MCP_*` markers where new data is
  created.
- [Risk] Provider/runtime readiness blocks live execution. Mitigation: a
  precise blocked summary satisfies the pilot acceptance for this stage.
- [Risk] Recovery partially fails. Mitigation: record final state, owner and
  residual risk instead of hiding residue.
- [Risk] Runtime captures contain large or sensitive local payloads.
  Mitigation: raw output stays ignored; reviewed evidence is compact and
  sanitized.

## Migration Plan

- Run the live runtime preflight for the selected runtime route and retain
  `preflight_result.json`; stop with a `runtime_gap` blocker when it fails.
- Load the reviewed manifest and target-selection summary.
- Recheck runtime pre-state and target marker.
- Execute the reviewed row only when gates pass.
- Run recovery or cleanup and retain final-state evidence.
- Hand the compact execution or blocked bundle to frame isolation.

## Open Questions

- Which provider path is ready first for the live run: Vanessa UI automation,
  direct Python manager probing or a reviewed Windows wrapper?
- Should the first run execute only one row even if multiple candidates pass
  review?

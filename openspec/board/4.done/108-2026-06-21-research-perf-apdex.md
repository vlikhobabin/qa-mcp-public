# 108. E-XV RESEARCH — performance / APDEX measurement during a UI test run

## Status
4.done

## Order Index
108

## OpenSpec Stage
research

## Owner
unassigned

## Source
- 2026-06-21 project review: per-operation performance measurement / APDEX (замер производительности) during
  automated UI tests is NOT a Vanessa Automation capability. Whether the 1C debug/performance interface can
  surface timings alongside the native TestClient session is UNKNOWN. Feasibility SPIKE, not a delivery card yet.
- Parent epic: card 102. Shares the debug-protocol substrate with card 107 (coverage).

## Summary
Research whether the platform performance-measurement / APDEX facility (замер производительности) can be driven
alongside a qa-mcp scenario to attach operation timings to test steps, enabling perf-assertions (e.g. "this form
opens in < N s"). Produce a findings note + go/no-go; if feasible, a productize plan → a fresh delivery card.

## Acceptance (spike deliverable)
- A findings note: can замер производительности / APDEX timings be obtained for a headless TestClient session in
  our lab? Via the same debug interface as card 107 or a separate facility? Granularity (per-operation / per
  server call)? Overhead?
- A go/no-go + (if go) an ordered plan and the first capture target. (No capability shipped here — it gates one.)

## Change Set
- research only — no capability. Output is an evidence/feasibility note under
  `docs/protocol-research/evidence/`. Coordinate with card 107 (likely one shared debug-attach spike).

## Verify
- LIVE spike 2026-06-21 (shared with card 107) — the debug server (`dbgs`, HTTP `:1550`, `/e1crdbg/…`) attaches to
  the headless TestClient (`/DEBUG -http /DEBUGGERURL`): 8 established connections, 92 packets, a scenario passed
  while attached. Evidence: `evidence/card107-108-debug-attach-2026-06-21/`.

## Archive
- spike complete (go/no-go answered); the delivery is card 110.

## Result
**GO.** Per-operation timing rides the SAME facility as coverage — «Замер производительности» over the debug
session records per-line/per-call TIME alongside execution counts. So one debugger implementation (the `/e1crdbg/`
protocol, card 110) yields both perf/APDEX (108) and coverage (107). Findings:
`evidence/card107-108-debug-attach-2026-06-21/findings.md`.

## Next
- card 110 (shared delivery: decode + drive the `/e1crdbg/` debugger protocol → coverage + perf). Then perf-
  assertions ("form opens in < N s") on test steps.

## Related
- Parent: card 102. Sibling: card 107 (coverage — same debug substrate). Lab:
  [[linux-native-testclient-xvfb]], [[autonomous-1c-observability]]. Memory:
  [[surpass-vanessa-native-superset-goal]].

## Log
- 2026-06-21 research stub created (E-XV track). Feasibility spike only; no capability until findings say go.
- 2026-06-21 SPIKE DONE (shared with 107) → **GO** → 4.done. The debug attach is headless (`dbgs` HTTP `:1550`,
  `/e1crdbg/…`; TestClient registers via `/DEBUG -http /DEBUGGERURL`). Perf/APDEX rides «Замер производительности»
  (same facility as coverage; per-line/per-call time). One debugger-protocol delivery (card 110) covers both.
  Evidence `evidence/card107-108-debug-attach-2026-06-21/`.

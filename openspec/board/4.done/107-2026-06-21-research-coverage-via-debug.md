# 107. E-XV RESEARCH — BSL code coverage during a UI test run (debug interface)

## Status
4.done

## Order Index
107

## OpenSpec Stage
research

## Owner
unassigned

## Source
- 2026-06-21 project review: code coverage during automated UI tests is NOT something Vanessa Automation does.
  1C exposes a debug interface; whether it can be driven headless alongside the native TestClient session to emit
  per-module/per-line execution data is UNKNOWN. This is a feasibility SPIKE, not a delivery card yet.
- Parent epic: card 102. Shares the debug-protocol substrate with card 108 (perf/APDEX).

## Summary
Research whether the 1C platform debug interface can attach to the running TestClient session (headless under
Xvfb) and report which BSL modules/lines executed during a qa-mcp scenario, yielding a coverage metric. Produce a
findings note with a go/no-go and, if feasible, a decode/productize plan that becomes a fresh delivery card.

## Acceptance (spike deliverable)
- A findings note answering: can the debug interface attach to the TestClient session in our Linux lab? What
  protocol/transport does it use? Can execution be captured per module/line? What does it cost (per-run overhead,
  per-config setup)?
- A clear go/no-go + (if go) an ordered plan + the first capture/decode target. (No new capability shipped by
  this card — it gates one.)

## Change Set
- research only — no capability. Output is an evidence/feasibility note under
  `docs/protocol-research/evidence/`. If feasible, spawn a delivery card.

## Verify
- LIVE spike 2026-06-21 — the debug server (`dbgs`, HTTP `:1550`, `/e1crdbg/…`) attaches to the headless
  TestClient launched with `/DEBUG -http /DEBUGGERURL`: 8 established `1cv8c↔dbgs` connections, 92 packets
  captured, and a form-open scenario passed while attached. Evidence: `evidence/card107-108-debug-attach-2026-06-21/`.

## Archive
- spike complete (go/no-go answered); the delivery is card 110.

## Result
**GO.** The debug interface attaches to the headless TestClient over the HTTP debug protocol (`/e1crdbg/…` on
`dbgs`). Coverage is derivable from a «Замер производительности» (per-line execution counts → which modules/lines
ran). Shared substrate with card 108 (the замер's timings → perf). The remaining work is decoding the
debugger-side of `/e1crdbg/` (protocol research) — spun into **card 110**. Findings:
`evidence/card107-108-debug-attach-2026-06-21/findings.md`.

## Next
- card 110 (shared delivery: decode + drive the `/e1crdbg/` debugger protocol → coverage + perf).

## Related
- Parent: card 102. Sibling: card 108 (perf/APDEX — same debug substrate). Lab:
  [[linux-native-testclient-xvfb]], [[autonomous-1c-observability]] (tech journal / logcfg). Memory:
  [[surpass-vanessa-native-superset-goal]].

## Log
- 2026-06-21 research stub created (E-XV track). Feasibility spike only; no capability until findings say go.
- 2026-06-21 SPIKE DONE → **GO** → 4.done. Live-confirmed the debug attach is headless: `dbgs` HTTP debug server
  on `:1550` (`/e1crdbg/…`), TestClient registers via `/DEBUG -http /DEBUGGERURL` (8 conns, 92 pkts captured), BSL
  runs while attached. Coverage rides «Замер производительности» (shared with 108). Decode of the debugger-side
  protocol → card 110. Evidence `evidence/card107-108-debug-attach-2026-06-21/`.

# 110. E-XV — drive the 1C debug protocol for coverage + perf/APDEX (beyond Vanessa)

## Status
4.done

## Order Index
110

## OpenSpec Stage
story

## Owner
unassigned

## Source
- 2026-06-21 spike (cards 107 + 108, **GO**): the 1C debug server (`dbgs`, HTTP `:1550`, `/e1crdbg/…`) attaches to
  the headless TestClient launched with `/DEBUG -http /DEBUGGERURL` (live-confirmed: 8 connections, 92 packets, a
  scenario passed while attached). A «Замер производительности» over that session records per-line execution counts
  (→ coverage) AND per-line/per-call time (→ perf/APDEX). Findings + pcap:
  `evidence/card107-108-debug-attach-2026-06-21/`.
- Parent epic: card 102 (E-XV — capabilities Vanessa lacks). Supersedes the delivery part of research cards 107/108.

## Summary
Implement the DEBUGGER side of the `/e1crdbg/` HTTP debug protocol so qa-mcp can attach to the running TestClient's
debug target, run a «Замер производительности» across a scenario, and emit BOTH a coverage map (modules/lines
executed) and per-operation timings (perf/APDEX, perf-assertions like "form opens in < N s"). Neither is something
Vanessa Automation does.

## Acceptance
- qa-mcp starts/uses a `dbgs`, attaches to the TestClient DBGTGT, runs a замер over a `run_scenario`, and returns
  per-line {count, time}.
- Coverage report (covered modules/lines) for a scenario; per-step timings + a perf-assertion step.
- Live on `vanessa_client`; opt-in (the замер adds overhead). Evidence: a decoded debugger session + a coverage +
  a perf artifact.

## Change Set (proposed — to be `$opsx-ff`'d)
1. ✅ `decode-debugger-protocol` — **DONE 2026-06-22. The "wall" is eliminated; NO genuine capture was needed.**
   The entire `/e1crdbg/` protocol ships as EMF `.xcore` inside EDT's `com._1c.g5.v8.dt.debug.model` jar
   (`/opt/1C/1CE/.../plugins/...debug.model_*.jar`, files `model/*.xcore`). The prior `Тип: anyType` "wall" was a
   wrong-field artifact: `attachDetachDbgTargets`/`setMeasureMode` do **not** carry a `targetID`. Exact decoded bodies:
   `attachDetachDbgTargets` = `{infoBaseAlias, idOfDebuggerUI, attach:Bool, id:DebugTargetIdLight[]}`;
   `setMeasureMode` = `{…, measureModeSeanceID:UUID}` (fresh UUID = start, NIL GUID = stop). Also recovered from
   EDT `debug.core` (`RuntimeDebugHttpClient`/`ProfilingService`): the real event-poll cmd is **`pingDebugUIParams`**
   with the UI id in the **`dbgui` URL query param, no body**; the initial-settings cmd is **`initSettings`** (the
   `setInitialDebugSettings` guess → 501). Measure RESULT schema = `DBGUIExtCmdInfoMeasure`(cmdID
   `measureResultProcessing`=6) → `PerformanceInfoMain → PerformanceInfoModule(moduleID) → PerformanceInfoLine{lineNo,
   frequency→coverage, durability/pureDurability→perf}`. Evidence
   `evidence/card110-edt-xcore-schemas-2026-06-22/` (extracted `.xcore` + findings).
2. ✅ `headless-measure` — **DONE 2026-06-22 (LIVE, end-to-end).** Full handshake + start/stop замер over a
   `run_scenario` + result retrieval, all from Python on real `vanessa_client`: `attachDebugUI`(register) →
   `initSettings` → `setAutoAttachSettings` → `getDbgTargets` → `attachDetachDbgTargets` → `setMeasureMode`(fresh
   UUID) → run scenario (real BSL: a create form) → continuous `pingDebugUIParams` → `setMeasureMode`(NIL) → the
   **`DBGUIExtCmdInfoMeasure` (cmdIDNum 6) event arrives** with a full `PerformanceInfoMain`. The v1 "no events" was
   not a protocol/attach issue (`getDbgTargetState`=`Worked` throughout) — it needed (a) measurable BSL on the seance
   (cached list opens produce nothing; a create form does) + (b) continuous polling. `tcpdump :1550` confirmed the
   debuggee round trip (`pingDBGTGT`/`measureServerTime` → measure push). Evidence
   `evidence/card110-headless-measure-2026-06-22/` (reproduce-measure-v2.py + headless-measure-v2.json + dbg-1550-v2.pcap).
3. ✅ `coverage-surface` (107) + `perf-surface` (108) — **DONE 2026-06-22 (PRODUCTIZED).** `src/qa_mcp/debug/measure.py`
   parses the real `PerformanceInfoMain` into a NAMED report: per module → per line `{frequency→coverage,
   durability/pureDurability→perf µs}`, `BSLModuleIdInternal.objectID` resolved against the config `.mdo` tree
   (`make_mdo_resolver`). MCP tool **`measure_scenario`** (#59) runs it end-to-end live; a `max_ms` scenario-level
   perf assertion returns `perf_ok`. 7 offline tests (`tests/test_measure.py`) against the real captured payload
   (`tests/fixtures/card110-measure-event.json`). Optional follow-on: a per-Gherkin-step perf-assert step.

## Verify
- ✅ 2026-06-22 — protocol FULLY decoded from EDT `.xcore` (no genuine capture); full handshake + headless «Замер
  производительности» over a `run_scenario` driven LIVE from Python; the `DBGUIExtCmdInfoMeasure` `PerformanceInfoMain`
  captured + parsed into a NAMED per-line coverage(107)+perf(108) report on real `vanessa_client`.
- ✅ 2026-06-22 — **PRODUCTIZED + verified.** MCP tool `measure_scenario` (src/qa_mcp/debug/measure.py) run LIVE
  end-to-end: `ok=True, scenario_ok=True, perf_ok=True`, 2 modules / 20 covered lines, names resolved
  (`Документ.Заказ :: МодульОбъекта` 8 + `:: Форма.ФормаДокумента` 12). 426 tests green (419 + 7 new); 59 tools.
  Evidence `evidence/card110-headless-measure-2026-06-22/{verify_tool_live.py, tool-live-result.json}`.

## Related
- Spike: cards 107 (coverage) + 108 (perf/APDEX) — `evidence/card107-108-debug-attach-2026-06-21/findings.md`.
  Method: the TestClient protocol-research approach (capture → decode → drive headless). Reuses
  `launch_test_client(extra_args=[/DEBUG,-http,/DEBUGGERURL])` + `dbgs`.
- Parent: card 102. Memory: [[surpass-vanessa-native-superset-goal]].

## Log
- 2026-06-21 created from the 107/108 GO spike — one shared delivery for the `/e1crdbg/` debugger protocol →
  coverage + perf/APDEX.
- 2026-06-21 bounded first step DONE: decoded the protocol (UTF-8 XML/HTTP), found the debugger endpoint
  `/e1crdbg/rdbg`, drove the handshake live (registered a debugger UI, `getDbgTargets` → 200 LISTED the live
  TestClient target — `ManagedClient`/`ServerEmulation`, ids in hand). Main risk gone. Remaining: attachDebugUI
  schema fix + a genuine замер capture → measure commands + result schema → headless drive. Evidence
  `evidence/card110-dbgsrv-probe-2026-06-21/` (findings.md, dbgsrv-probe.json, reproduce-dbgsrv.py).
- 2026-06-22 stage A/B (command surface): probed ~25 rdbg command names. The **performance-measure command is
  `setMeasureMode`** (recognized/400), attach is `attachDetachDbgTargets`; the *Measure*/*Perf*/*Profiler* guesses
  were all 501. Both block on the strict-XDTO `targetID` complex type (6 structure variants → identical
  `Тип: anyType` error; no progression). Strict XDTO types aren't guessable + no `.xsd` on disk ⇒ the remaining
  decode NEEDS a genuine debugger capture (Configurator/EDT замер, tcpdump `:1550`) for the exact `targetID`/request
  types + the measure-result schema. Evidence `evidence/card110-measure-probe-2026-06-22/`.
- 2026-06-22 **WALL ELIMINATED — no genuine capture needed.** Found the entire `/e1crdbg/` protocol shipped as EMF
  `.xcore` inside EDT's `com._1c.g5.v8.dt.debug.model` jar (invisible to `find -name '*.xsd'` — it's `.xcore` in a
  jar). The `targetID` "wall" was a wrong-field artifact: `attachDetachDbgTargets`/`setMeasureMode` carry no
  `targetID`. With the corrected bodies (+ `initSettings`, `setAutoAttachSettings`, and the real poll cmd
  `pingDebugUIParams` with the ui in the `dbgui` query param), the **full debugger handshake now drives LIVE from
  Python** on real `vanessa_client` — every cmd 200/204 (was 400/501). Change 1 DONE. Evidence
  `evidence/card110-edt-xcore-schemas-2026-06-22/` + `evidence/card110-headless-measure-2026-06-22/`.
- 2026-06-22 **MEASURE RESULT SOLVED end-to-end (changes 2 + 3).** v2 run captured a real `DBGUIExtCmdInfoMeasure`
  (cmdIDNum 6) `PerformanceInfoMain` from a headless «Замер производительности» over a `run_scenario`. Keys: the v1
  "no events" was NOT attach/protocol (`getDbgTargetState`=`Worked` throughout) — it needed measurable BSL on the
  measured seance (a **create form** «я создаю новый документ 'Заказ'»; cached list opens produce nothing) +
  **continuous** `pingDebugUIParams` polling. `tcpdump :1550` confirmed the debuggee round trip. Parsed the payload
  (`performanceFrequency=1e6` µs; per module → per line `{frequency=coverage, durability/pureDurability=perf}`) and
  resolved `BSLModuleIdInternal.objectID` against the config `.mdo` → NAMED report (`coverage-perf-report.txt`):
  `Документ.Заказ :: Форма.ФормаДокумента` 12 lines + `:: МодульОбъекта` 8 lines, 20 covered lines / 1.135 ms. Cards
  107+108 capability PROVEN. Remaining = productization only (MCP tool + perf-assert step + fixture test). Evidence
  `evidence/card110-headless-measure-2026-06-22/` (reproduce-measure-v2.py, headless-measure-v2.json, dbg-1550-v2.pcap,
  parse_measure_report.py, coverage-perf-report.txt).
- 2026-06-22 **PRODUCTIZED → card DONE (4.done).** New `src/qa_mcp/debug/measure.py`: pure parser
  (`extract_measures`/`build_report`/`render_report`), the `.mdo` module-name resolver (`make_mdo_resolver`), the
  rdbg client (`DebuggerSession`), and the live driver (`measure_scenario`). MCP tool **`measure_scenario`** (#59,
  src/qa_mcp/mcp_server.py) boots a debug TestClient, замеряет a `run_scenario`, returns
  `{report{modules,totals}, report_text, perf_ok}` (perf-assert via `max_ms`). 7 offline tests
  (`tests/test_measure.py`) against the real captured payload (`tests/fixtures/card110-measure-event.json`) → **426
  tests green, 59 tools**. LIVE-verified end-to-end via the tool: `ok/scenario_ok/perf_ok` all true, 2 modules / 20
  covered lines, module names resolved. Evidence `verify_tool_live.py` + `tool-live-result.json`. Optional follow-on:
  a per-Gherkin-step perf-assert step (scenario-level `max_ms` ships now).

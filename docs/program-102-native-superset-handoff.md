# Epic 102 — native superset beyond Vanessa: handoff (HISTORICAL — epic 102 CLOSED)

> **⚠ EPIC 102 IS CLOSED (`4.done`, 2026-06-22).** This document is the historical record of how the native-superset
> tracks (E-FW + E-XV) were delivered — kept for provenance. **For CURRENT state start at:**
> [`qa-mcp-tool-reference.md`](qa-mcp-tool-reference.md) (the 61 MCP tools) and the **active roadmap card**
> `openspec/board/3.inprogress/111-2026-06-22-epic-productize-harden-extend.md` (post-102: productize / harden /
> extend — items 1–4, 6, 7 DONE; only the need-gated architecture refactor remains). New tooling since epic 102:
> the live-regression harness ([`live-regression.md`](live-regression.md)), protocol-version drift detection
> ([`capture-refresh-runbook.md`](capture-refresh-runbook.md)), CI quality gates (per-step perf-assert +
> coverage gate), and deeper data-layer asserts (count + role/security matrix). **State: 61 MCP tools, 475 offline
> tests green, corpus 100%.**

**Date:** 2026-06-22. **Purpose:** the historical entry point for the epic-102 delivery. Predecessor epic 82
(capture-free protocol driver) is closed; its handoff is `docs/protocol-research/capture-free-epic-session-handoff.md`.

> **State at epic-102 close:** **59 MCP tools, 426 offline tests green, real Vanessa corpus transpile 11.9% → 100%.**
> Board: **cards 103/104/105/106/107/108/109/110 → `4.done`**; epic **102 → `4.done`** (the successor is roadmap
> card 111). Everything below was LIVE-verified on the real `vanessa_client` lab.
> **2026-06-22: card 110 is DONE + PRODUCTIZED** — the `/e1crdbg/` protocol decoded from EDT's `.xcore` (no genuine
> capture needed), the full handshake + a headless «Замер производительности» drive LIVE from Python, and the new MCP
> tool **`measure_scenario`** (`src/qa_mcp/debug/measure.py`) returns a NAMED per-line coverage(107)+perf(108) report
> with a `max_ms` perf assertion (7 offline tests, live-verified). **With 110 done, the substantive E-XV/E-FW tracks
> are complete; what remains is breadth/polish on epic 102** (see "THE NEXT ACTION").

## The goal (north star)

qa-mcp must not just REPLACE Vanessa but EXCEED it via 1C-native capability. Three tracks:
- **Sense A — `vanessa-mcp` tool surface:** ~95% (epic 82).
- **E-FW — Vanessa-the-FRAMEWORK drop-in** (run existing `.feature` suites + CI). Corpus now **100%**.
- **E-XV — beyond Vanessa** (1C-native capability Vanessa lacks): data-layer assert, metadata-driven test gen,
  external-`.epf` open, and debug-based coverage/perf (card 110, in progress).

## THE NEXT ACTION — card 110 is DONE; pick the next epic-102 thread

**Card 110 = drive the 1C debug protocol for code coverage (107) + perf/APDEX (108)** — capabilities Vanessa
cannot do. **2026-06-22: DONE + PRODUCTIZED.** The protocol "wall" is eliminated (decoded from EDT's `.xcore`, no
genuine capture needed); the full handshake + a headless «Замер производительности» over a `run_scenario` drive LIVE
from Python; and the new MCP tool **`measure_scenario`** (`src/qa_mcp/debug/measure.py`) returns a NAMED per-line
coverage(107)+perf(108) report (module names resolved via the config `.mdo`) with a `max_ms` perf assertion. 7
offline tests (`tests/test_measure.py` + fixture `tests/fixtures/card110-measure-event.json`), live-verified
end-to-end. Card in `openspec/board/4.done/`.

**Next threads (no longer blocked on anything):** an optional per-Gherkin-step perf-assert step; the deeper 103 leg
(capture-backed single-frame click/select/input on a freshly-opened form); minor sense-A gaps
(`manage_command_interface`, async `stop_scenario`, role matrix). The history below records how card 110 was solved.

**The breakthrough:** the entire `/e1crdbg/` protocol ships as EMF **`.xcore`** (textual Ecore) inside EDT's
`com._1c.g5.v8.dt.debug.model_*.jar` (`/opt/1C/1CE/components/1c-edt-2026.1.1+1-x86_64/plugins/`, files
`model/*.xcore`) — invisible to `find -name '*.xsd'` because it's `.xcore` in a jar. The earlier `targetID …
Тип: anyType` "wall" was a **wrong-field artifact**: `attachDetachDbgTargets`/`setMeasureMode` carry NO `targetID`.

**Decoded + LIVE-verified (every cmd 200/204 on real `vanessa_client`, from Python):**
- Debug server `dbgs` headless on HTTP `:1550`; protocol = UTF-8 XML/HTTP, `/e1crdbg/rdbg?cmd=<cmd>`.
- TestClient attaches via `/DEBUG -http /DEBUGGERURL http://127.0.0.1:1550` (the `-http` sub-key is REQUIRED).
- Full handshake: `attachDebugUI`(400 but **registers** the ui — proven, same-ui ping/getDbgTargets then work) →
  **`initSettings`** (NOT `setInitialDebugSettings`→501) → **`setAutoAttachSettings`** → `getDbgTargets` (lists
  `ManagedClient`+`ServerEmulation` with full `DebugTargetId`) → **`attachDetachDbgTargets`**
  `{attach:true, id:DebugTargetIdLight[]}` → **`setMeasureMode`** `{measureModeSeanceID:<fresh UUID>}` start /
  `{NIL GUID}` stop → **`pingDebugUIParams`** (the REAL event poll — UI id goes in the **`dbgui` URL query param,
  NO xml body**; bare `pingDebugUI` is a 204 keepalive that never carries events).
- Measure RESULT schema = `DBGUIExtCmdInfoMeasure` (cmdID `measureResultProcessing`=6) → `PerformanceInfoMain →
  PerformanceInfoModule(moduleID) → PerformanceInfoLine{lineNo, frequency→coverage(107),
  durability/pureDurability→perf(108), serverCallSignal}`.

**SOLVED (v2):** the real measure result IS captured. The earlier "no events" was NOT attach/protocol
(`getDbgTargetState`=`Worked` throughout) — it needed (a) **measurable BSL on the measured seance** (a create form
`я создаю новый документ 'Заказ'` runs object-module fill + form `OnCreateAtServer`; cached list opens produce
nothing) and (b) **continuous `pingDebugUIParams` polling** to catch the async event. A `tcpdump :1550` confirmed
the debuggee round trip. The captured `DBGUIExtCmdInfoMeasure` `PerformanceInfoMain` parses 1:1 to `Measure.xcore`
and resolves to NAMED modules via the config `.mdo` (`BSLModuleIdInternal.objectID` → `<forms uuid=…>`/`<mdclass:…>`):
`coverage-perf-report.txt` shows `Документ.Заказ :: Форма.ФормаДокумента` (12 lines) + `:: МодульОбъекта` (8 lines),
20 covered lines / 1.135 ms. **Remaining = productization only:** an MCP tool (`measure_scenario` → coverage+perf), a
perf-assert Gherkin step, and a test using `headless-measure-v2.json` as the fixture — no research unknowns.
Evidence/recipe:
`evidence/card110-edt-xcore-schemas-2026-06-22/` (extracted `.xcore` + findings) +
`evidence/card110-headless-measure-2026-06-22/`: `reproduce-headless-measure.py` (handshake) +
**`reproduce-measure-v2.py` (the working end-to-end measure: tcpdump + continuous ping + create-form BSL)** +
`headless-measure-v2.json` + `dbg-1550-v2.pcap` + `parse_measure_report.py` + `coverage-perf-report.txt` + findings.

**Optional smaller follow-ons (not blocking):** EnumRef-style enum-value autofill is done; a config-agnostic live
arbitrary-field WRITE is done (`write_form_fields_by_label`); a deeper 103 leg (capture-backed single-frame
click/select/input on a freshly-opened form) remains optional.

## What is DONE (all LIVE-verified on `vanessa_client`)

- **103 (E-FW, `3.inprogress`)** — step-library + BDD + runner execution. Gherkin grew 11→broad canonical set
  (assert family, `expect_equals`, `assert_data`, open/close, tags/Background/DataTables/Outline/nested). Runner
  executes it; the **assert family + on-client ACTION execution** (`open_main_form` via `navigate_resolver` →
  `_open_form_by_link`/splice_navigate, capture-free) are LIVE. Sole residual was external-`.epf` → done as card
  109. Evidence `evidence/card103-{wave3,open-action}-live-2026-06-21/`.
- **104 (E-FW, `4.done`)** — JUnit + Allure reporting (`reporting.py` + `write_test_report` #53). LIVE: 3 real
  scenarios → `junit.xml` + `allure-results/*.json`. `evidence/card104-live-report-2026-06-21/`.
- **105 (E-XV, `4.done`)** — data-layer assert via a self-contained read-only OData client (`data/odata.py`,
  `assert_data` #54). LIVE incl. the **flagship UI→DB roundtrip** (write+save → assert in the DB).
  `evidence/card105-*-2026-06-21/`.
- **106 (E-XV, `4.done`)** — metadata-driven test gen (`smoke.py` #55 + `autofill.py` #56). LIVE: catalogs 8/8,
  broadening 12/12 (Документ `e1cib/list/`; Отчёт/Обработка `e1cib/app/` — NOT `e1cib/command/`), create forms 3/3
  (`e1cib/data/`), required-field autofill incl. **OData reference resolution** (Заказ 7/7) + **EnumRef** + the
  config-agnostic **arbitrary-field write by label** (`write_form_fields_by_label`). `evidence/card106-*/`.
- **107 + 108 (E-XV research, `4.done`)** — debug-attach spike → GO; delivery = card 110 (above).
- **109 (E-FW, `4.done`)** — open an external `.epf` the native, Vanessa-component-free way: tool
  `open_external_processor` drives «Главное меню → Файл → Открыть» → GTK chooser → Ctrl+L → Unicode-safe path →
  Enter. Closes the corpus to **100%**. `evidence/card109-open-epf-live-2026-06-21/`.

## Proven lab recipes

**Boot a TestClient (read/assert/open scenarios; xtest writes need `display`+matchbox):**
```python
from qa_mcp.protocol.lifecycle import TestClientTarget, launch_test_client, load_env_file
from qa_mcp import mcp_server
import subprocess, os, time
t = TestClientTarget.from_env(load_env_file('.ai1c/vanessa-qa-mcp.env'),
        host='127.0.0.1', port=15381, manage_apache=True, clear_lock=True, display='auto')  # display only for xtest
h = launch_test_client(t, wait_sec=120, settle_sec=6); d = h.display   # stops Apache; TPort :15381
# xtest only: wm = subprocess.Popen(['matchbox-window-manager','-use_titlebar','no'], env={**os.environ,'DISPLAY':d}); time.sleep(2)
try:
    mcp_server.run_scenario(feature_text="...", host='127.0.0.1', port=15381)   # reads/asserts/data/skip + OPEN actions
    # mcp_server.open_external_processor(path, display=d, expect_caption='...')                 # card 109 (xtest)
    # mcp_server.write_form_fields_by_label(open_link, labels, values, display=d)               # card 106 arbitrary write
finally:
    h.stop(); subprocess.run(['sudo','-n','systemctl','start','apache2'])      # ALWAYS restart Apache
```

**Debug measure handshake (card 110) — WORKS LIVE:** start `dbgs --addr=127.0.0.1 --port=1550 --ownerPID=<pid>`,
launch the client with `extra_args=['/DEBUG','-http','/DEBUGGERURL','http://127.0.0.1:1550']`, then POST UTF-8 XML to
`/e1crdbg/rdbg?cmd=…` in order: `attachDebugUI` (reuse ONE ui for everything) → `initSettings` → `setAutoAttachSettings`
→ `getDbgTargets` (JSON; grab each target's `id`) → `attachDetachDbgTargets` `{attach:true, id:[{id:<uuid>}]}` →
`setMeasureMode` `{measureModeSeanceID:<uuid>}` (start) / `{NIL}` (stop) → poll `pingDebugUIParams&dbgui=<ui>` (no body)
for the `DBGUIExtCmdInfoMeasure` event. The exact `.xcore` request/response/measure schemas:
`evidence/card110-edt-xcore-schemas-2026-06-22/`. Runnable end-to-end driver + captured run:
`evidence/card110-headless-measure-2026-06-22/reproduce-headless-measure.py`.

**Gotchas (HARD-LEARNED — read before booting):**
- Do boot+verify+teardown in ONE script (the handle does NOT survive across Bash calls) and ALWAYS guard teardown
  in `finally` + restart Apache. A killed/timed-out script leaves a stray `1cv8c` + `Xvfb` holding the infobase —
  clean up with `pkill -f '1cv8c.*TESTCLIENT'; pkill -f 'Xvfb :<N>'` then `sudo -n systemctl start apache2`.
- **`locate_text` (xtest) is SLOW** (imagemagick subimage-search over 1280×1024, ~10-20s each) — budget generous
  timeouts; many searches in one tool can exceed 200s.
- `locate_text` of a long typed value is font-sensitive (false negatives) — verify via screenshot, not value re-match.
- Cyrillic into GTK/xtest: plain `xdotool type` DROPS it — use `xtest_type_unicode` (per-char `key U<codepoint>`).
- The booted client lands on the real HomePage (not the bundled fixture); use real-config elements/catalogs.
- Lab access/contention: [[linux-native-testclient-xvfb]], [[opt-1c-dev-lab-layout]], [[ibsrv-odata-vs-httpservice]],
  [[lab-infobase-access]], [[autonomous-1c-observability]].
- **Lab side effects:** the live write demos created test currencies in `vanessa_client` — `QAROUNDTRIP2026` (105)
  and `QASMOKE` (106 autofill, saved). The read-only OData client can't delete them; clean via UI/admin if desired.

## Run / verify

```bash
. .venv/bin/activate
python -m pytest -q                                                      # 419 green
python tools/protocol-research/corpus_transpile_coverage.py --min 1.0    # lab corpus gate 100% (skips if /opt/1c-dev absent)
# data-layer assert, LIVE read-only (no Xvfb; Apache OData up on :8316):
QA_MCP_ODATA_URL="http://127.0.0.1:8316/vanessa_client/odata/standard.odata" \
QA_MCP_ODATA_USER="Администратор" QA_MCP_ODATA_PASSWORD="" python3 -c "import sys;sys.path.insert(0,'src');\
from qa_mcp.data import ODataClient,assert_data_value as a;\
print(a(ODataClient(),'Catalog_Банки','Description','ВнешИнвестСити Банк',filter=\"Code eq '000000005'\")['ok'])"
```

## Pointers

- **Cards:** `openspec/board/3.inprogress/103-*`; `openspec/board/4.done/{104,105,106,107,108,109}-*`;
  `openspec/board/1.backlog/{102-epic, 110-debug-protocol-coverage-perf}-*`.
- **Code:** `src/qa_mcp/scenario/{gherkin,model,runner,actions,replay,reporting,smoke,autofill}.py`,
  `src/qa_mcp/data/odata.py`, `src/qa_mcp/protocol/{lifecycle,native_xtest}.py`, `src/qa_mcp/mcp_server.py`
  (tools incl. `navigate_resolver`, `autofill_required_fields`, `open_external_processor`,
  `write_form_fields_by_label`; `_open_form_by_link`/`_foreground_form_by_link`). Parity: `docs/vanessa-mcp-parity.md`.
- **Evidence:** `evidence/card10{3,4,5,6,7-108,9}-*-2026-06-2{1,2}/`, `evidence/card110-*/`.
- **Memory:** [[surpass-vanessa-native-superset-goal]] (START), [[qa-mcp-capture-free-epic]] (epic 82), + the lab memories.

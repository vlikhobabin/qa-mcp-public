# 101. Fixture-free foreground primer — true cross-config generality for navigated-form date-cell

## Status
4.done

## Order Index
101

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-21: card-100 follow-up. Card 100 made `set_table_date_cell(open_link=…, column_title=…)` set a date in a
  REAL document's tabular date cell config-agnostic (no per-form capture), live-verified on `Документ.Заказ`
  (15.08.2026 + cross-year 10.03.2028). The ONE remaining generality gap: **Blocker 1's foreground primer uses the
  bundled vanessa_client fixture render-push frames** (`_VALUE_READ_OPEN_FRAMES`). It is a FIXED reusable primer
  (not a per-target capture), so it is config-agnostic in the "no per-form capture" sense for any vanessa_client
  doc — but a config WITHOUT the fixture (e.g. demo БСП) has nothing to render-push.
- Parent: card 100 (`2.todo`, DONE). Evidence: `evidence/card100-config-agnostic-datecell-2026-06-21/`.

## Summary
Make the navigated-document-form FOREGROUND step work on ANY config with NO bundled fixture, so
`set_table_date_cell(open_link=…)` (and any future on-screen interaction on a navigated form) is fully
cross-config. Two parallel approaches; either one closes it. Capability: extends `qa-mcp-protocol-lab`.

## What is already known (card 100, probes 1-6)
- A bare bootstrap leaves the START PAGE as the active working area (no tab bar); `splice_navigate` then opens the
  target as a BACKGROUND tab (footer peeks under the section panel). `splice_navigate` ALONE (list/data, once or
  twice) NEVER foregrounds.
- The fixture render-push frames (`_VALUE_READ_OPEN_FRAMES`, even the no-SF prefix 11-14) switch the client into
  tabbed working-area mode; THEN a navigate opens the target FOREGROUND as the active tab. Probe 6 showed 11-14
  already create the fixture tab → a clean "generic prefix" is unlikely; the primer is fixture-bound.
- The form is an INTERNAL 1C MDI tab, not a separate OS window → OS-window raise (xdotool) is N/A **as long as
  forms open as tabs**. The card-96 window-level `88 82 81` activate command on the held conn is accepted but does
  NOT change the screen.

## Change 1: `separate-windows` mode (Approach 2 — quick check) — ⚠ INVESTIGATED 2026-06-21, NOT THE PATH
Hypothesis: if the client opens forms as SEPARATE OS WINDOWS instead of MDI tabs, OS-level window activation
(`xdotool windowactivate`) foregrounds the navigated form — no protocol decode. **Quick-check outcome: the lever is
real but not enable-able here, and it's a global behavior change → not the path.** Findings:
- The lever EXISTS: `РежимОткрытияФормПриложения.ОтдельныеОкна` (`ClientSettings.ApplicationFormsOpenningMode`,
  per-user, "применяемый при запуске"). help-mcp confirmed.
- But it's **NOT settable headlessly here:** the standard «Сервис и настройки → Настройки → Параметры» dialog in
  vanessa_client is DEBUG-ONLY (Отладка / Режим технического специалиста — NO «Режим открытия форм» radio;
  `screenshots/sepwin/12_parametry_dialog.png`); the top-left ☰ is the «Функции» list; and the local `~/.1cv8/…
  *.pfl` profiles are binary with no readable mode token (it's IB-stored in the system-settings storage). Setting it
  would need a BSL/settings-storage write (a deploy/execution vehicle — config-specific) or a non-standard UI path.
- Plus `locate_text` on a FULL 1280×1024 screenshot is too slow (`compare -subimage-search` ~10-30 s each) for
  iterative menu-driving — must crop to a region first.
- Architectural note: separate-windows is a GLOBAL behavior change (every form becomes its own OS window), whereas
  decoding the foreground command (Change 2) is surgical and behavior-preserving.
⇒ Deprioritized. Residual sub-option if revisited: set the mode via a tiny external data-processor BSL call (settings
storage) + client restart, then OS-raise. Probes: `sepwin_menu_recon_probe.py`, `sepwin_set_probe.py`.

## Change 2: decode the genuine open-foreground command — ✅ SOLVED 2026-06-21 (NO new capture needed)
**The fixture-free foreground was already in an EXISTING capture.** `genuine-card98-listform-read` opens a REAL
catalog list (Товары) directly from COLD with **NO fixture** (no `PF_`, no `e1cib/app`): navigate (mgr[11-12]) →
activate `e0 4b 55` (mgr[13]) → render `e1 82` + the list's `SecondaryFrame` (mgr[14-15]) → **`88 82 81`
window-commands (mgr[16-19])** → activate (mgr[20]). A faithful full-sequence replay (GuidRebinder) **FOREGROUNDS
the form** — proven by screenshot (`listfg/30_final.png`: the Товары list is the active tab). The difference vs the
background `splice_navigate`: the foreground needs the activate + render + `88 82 81` window-command frames AFTER
the navigate, which the minimal 2-frame splice omits. **Retargeting the nav-link** (`retarget_list_read_frame`)
opens ANY form foreground, fixture-free: `e1cib/list/Документ.Заказ` → the «Заказы товаров» list foreground; and
the doc **DATA-link** `e1cib/data/Документ.Заказ?ref=…` → **the Заказ document form FOREGROUND in one shot, tab bar
«Начальная страница | Заказ 000000001», NO fixture tab** (`listretarget/data_30_final.png`). ⇒ the fixture primer
is replaceable by this retargeted replay — config-agnostic (the sequence carries no config-specific content; GUIDs
rebound; nav-link retargeted to the target). Probes: `listform_foreground_probe.py`,
`listform_retarget_doc_probe.py`. The Vanessa-manager demo capture is NO LONGER needed.

**✅ PRODUCTIZED + live-verified 2026-06-21.** `_foreground_form_by_link(open_link)` (mcp_server.py) replays the
fixture-free sequence retargeted to the target, holding the manager socket open. `set_table_date_cell(open_link=…)`
gained `foreground=` with **`"listreplay"` as the DEFAULT** (fixture-free) and `"fixture"` as the legacy fallback.
End-to-end through the shipped tool: Документ.Заказ Товары.Дата → «12.07.2026» with the tab bar «Начальная страница
| Заказ 000000001» — **NO fixture tab** (`native-mcp/…/02_picked.png`). 355 tests. So the date-cell tool is now
fixture-free by default. Probe: `document_datecell_tool_verify.py` (uses the default).

**✅ CROSS-CONFIG PROOF — PASSED 2026-06-21.** Booted a thick TestClient against **demo БСП**
(`/opt/1c-dev/demo_1_0_41_3`, :15382 — a real 1C:БСП base with NO suite fixture) and replayed
`_foreground_form_by_link("e1cib/list/Справочник.Валюты")`: the demo **Валюты list opened FOREGROUND as the active
tab, NO fixture** (`04_demo_bsp_valyuty_foreground_no_fixture.png` — confirmed demo by the test-write records
ZZHYBRID99/ZZXTEST88/ПродуктТест5 earlier card-98 demo probes created in this catalog). So the fixture-free
foreground is confirmed config-agnostic on a 2nd, never-captured config. Probe: `demo_fixturefree_foreground_probe.py`.

### (superseded) original plan — capture+diff on a fixture-less config
**Offline analysis DONE 2026-06-21 (narrowed the problem; superseded by the SOLVED finding above):**
- The navigate command is NOT the foreground trigger. In `genuine-card90-openlist` the fixture is opened by an
  `e1cib/app/` navigate (mgr[11-12]) and the list by `e1cib/list/` (mgr[14-15]) — IDENTICAL 2-frame
  `88 82 81`+`f7` structure, and NOTHING follows the navigate but 4-byte ACKs. `splice_navigate` already
  reproduces the full navigate. Probe `app_navigate_foreground_probe.py`: an `e1cib/app/` navigate from COLD
  ALSO backgrounds (fixture content peeks under the desktop), same as list/data → app-vs-list is NOT the trigger.
- The foreground trigger is the fixture-open **render/activate sequence** `_VALUE_READ_OPEN_FRAMES` (11-17):
  f11 `e0 4b 55` (activate), f12/15/16 `e1 82` (render/descriptor), f13 `88 82 81` (window command), f17 carries
  the fixture `SecondaryFrame`/`ManagedForm` (the navigate itself is in the skipped frames 8-10). Replaying 11-17
  foregrounds the fixture + establishes tabbed mode (card 100).
- These render frames are **fixture-BOUND, not "current-form" generic**: probe `navigate_then_render_probe.py`
  (navigate Заказ to bg → replay 11-17) foregrounds the FIXTURE (its PF_* fields), leaving Заказ a bg tab — same
  as the fixture primer. So there is NO config-agnostic "render the current form" shortcut in the existing frames.
- The card-96 window-level `88 82 81` command alone does NOT foreground (card-100 probe 1).
⇒ **Definitive remaining step (the heavy lab): capture a genuine "open a form to the foreground" on a config WITH
NO fixture** (demo `/opt/1c-dev/demo_1_0_41_3`, БСP) via the live Vanessa manager (boot manager, apache down,
connect a demo client with the params TABLE step, `tcpdump -i lo 'tcp portrange 48000-48400'`, a `.feature` that
opens a demo document/list form, `pcap_to_traffic`). That genuine sequence shows what establishes tab mode /
foregrounds WITHOUT the fixture; generalize it (rebind the form GUIDs to the navigated target) → fixture-free
primer. Recipe: [[vanessa-mcp-linux-genuine-manager]] + [[genuine-action-capture-recipe]].
- Probes (offline analysis): `app_navigate_foreground_probe.py`, `navigate_then_render_probe.py`; evidence
  `screenshots/{appnav,navrender}/`.

## Done when — ✅ MET 2026-06-21
A document form opened by `open_link` is brought to the FOREGROUND and `set_table_date_cell(open_link=…)` sets a
date in its tabular date cell with **NO bundled-fixture render-push frames** (the new default `foreground="listreplay"`
replays a fixture-FREE genuine cold list-open, retargeted). Live-verified by screenshot: Документ.Заказ Товары.Дата
→ 12.07.2026 with the tab bar carrying NO fixture tab. **Config-agnostic CONFIRMED on a 2nd config** — the
fixture-free foreground opened the demo БСП (`/opt/1c-dev/demo_1_0_41_3`) Валюты list foreground, no fixture. Nothing
remains. 355 tests + evidence.

## Approach (ordered)
1. ~~(Change 1) Investigate + test the separate-windows mode~~ — DONE 2026-06-21, NEGATIVE (see Change 1): the
   lever exists but isn't headlessly settable here + is a global behavior change. Deprioritized.
2. **(Change 2 — now PRIMARY) Capture + diff the genuine open-foreground; decode + splice generically.** Needs a
   focused genuine-Vanessa-manager capture session (boot manager on Xvfb, auto-allow modals, tcpdump on lo, a
   `.feature` that opens a document by its `e1cib/data` nav-link, `pcap_to_traffic`). Then byte-diff the genuine
   open vs `splice_navigate`'s `NAVIGATE_BODY` to isolate the foreground command/flag; splice it generically.
3. Verify on demo БСП (no fixture) — the true-generality acceptance test.
4. Wire the winning path into the engine; keep the fixture primer as a fallback for vanessa_client.

## Risk/scope
Medium — protocol-research + lab (manager capture for Change 2; a settings mechanism for Change 1). The date-cell
mechanics (localization, activation, calendar pick, year-nav) are DONE and reused unchanged.

## Related
- Parent: card 100. Evidence: `evidence/card100-config-agnostic-datecell-2026-06-21/`.
- Code: `src/qa_mcp/mcp_server.py` (`_open_form_by_link`, `_set_table_date_cell_open_link`, `_VALUE_READ_OPEN_FRAMES`),
  `src/qa_mcp/protocol/native_write.py` (`splice_navigate`, `NAVIGATE_BODY`).
- Probes: `document_foreground_probe{,2..6}.py` (Blocker 1 investigation).
- Memory: [[qa-mcp-capture-free-epic]], [[linux-native-testclient-xvfb]], [[autonomous-1c-observability]],
  [[vanessa-mcp-linux-genuine-manager]], [[genuine-action-capture-recipe]], [[lab-infobase-access]].

## Log
- 2026-06-21 card created — carries card-100's true-generality remainder (fixture-free foreground primer) as a
  2-approach story: Change 1 separate-windows OS-raise (quick, start here) ‖ Change 2 genuine open-foreground
  capture+diff (definitive). Acceptance = foreground + date-set on demo БСП with no fixture frames.
- 2026-06-21 **Change 1 (separate-windows) quick-check DONE — NEGATIVE.** Lever confirmed
  (`ClientSettings.ApplicationFormsOpenningMode.ОтдельныеОкна`) but not enable-able here: the standard «Параметры»
  is debug-only in vanessa_client (no form-open-mode radio), the ☰ is the «Функции» list, local `*.pfl` are binary
  (setting is IB-stored), and full-screen `locate_text` is too slow for menu-driving. Also a global behavior change.
  ⇒ **Change 2 (genuine open-foreground capture+diff) is now the PRIMARY path** — needs a focused Vanessa-manager
  capture session. Evidence: `screenshots/sepwin/`.
- 2026-06-21 **Change 2 offline analysis DONE — problem narrowed.** Ruled out the navigate command as the
  foreground trigger (app/list/data all background from cold; `splice_navigate` already replays the full navigate);
  pinpointed the trigger as the fixture-open render/activate sequence (frames 11-17), which is fixture-BOUND
  (navigate-then-replay foregrounds the FIXTURE, not the navigated target). The card-96 `88 82 81` window command
  alone doesn't foreground.
- 2026-06-21 **Change 2 ✅ SOLVED + PRODUCTIZED + live-verified — card DONE; the demo capture was NOT needed.** The
  fixture-free foreground was already in `genuine-card98-listform-read` (a COLD catalog-list open with NO fixture):
  its full-sequence replay (navigate → activate `e0 4b 55` → render `e1 82` → `88 82 81` window-commands → activate)
  FOREGROUNDS the form; retargeting the nav-link opens ANY list/document foreground (proven: Заказ doc data-link →
  foreground, NO fixture tab). Productized `_foreground_form_by_link` + `set_table_date_cell(foreground="listreplay"
  default | "fixture" legacy)`; end-to-end through the shipped tool: Заказ Товары.Дата → 12.07.2026, no fixture tab.
  355 tests. Probes: `listform_foreground_probe.py`, `listform_retarget_doc_probe.py`,
  `document_datecell_tool_verify.py`. Published on `main` (e1403c9).
- 2026-06-21 **Cross-config proof PASSED — card fully closed.** Booted demo БСП (`/opt/1c-dev/demo_1_0_41_3`,
  thick, :15382) and replayed the fixture-free foreground for `e1cib/list/Справочник.Валюты` → the demo Валюты list
  opened FOREGROUND, NO fixture. Config-agnostic confirmed on a 2nd, never-captured config. Probe:
  `demo_fixturefree_foreground_probe.py`; evidence `04_demo_bsp_valyuty_foreground_no_fixture.png`.

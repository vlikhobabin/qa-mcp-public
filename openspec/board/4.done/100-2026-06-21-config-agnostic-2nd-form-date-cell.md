# 100. Config-agnostic table date-cell on ANY form (Path B — true generality)

## Status
4.done

## Order Index
100

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-20/21: the card-99 change-2 "(ideally) a 2nd form" follow-up, scoped up to **Path B — true
  generality** at the operator's request ("B, настоящую общность"). The fixture date cell + on-screen
  localization + year-nav are DONE (card 99). This card makes `set_table_date_cell` work on ANY real form's
  tabular date cell **config-agnostic** (no per-form capture).
- Epic 82 (closed). Parent: card 99 (`4.done`). Evidence: `evidence/card99-2ndform-pathB-2026-06-20/`.

## ⚠ Precondition (external, blocks the END-TO-END)
Adding/deploying a date column needs the edt-mcp **deploy** surface, which is profile-gated. The session runs
`EDT_MCP_TOOL_PROFILES=agent-default` (`.mcp.json`), so `run_metadata_change_delivery` / `live-deploy` are
**hidden**. Set `EDT_MCP_TOOL_PROFILES="all"` in `.mcp.json` (+ `.codex/config.toml`) and **reconnect/restart**
the edt-mcp MCP server (tools register at connection). Headless Designer HANGS (card 81); `ibcmd` can't author
metadata. See [[edt-mcp-profile-and-deploy]].

## Summary
`set_table_date_cell` currently activates the date cell via the FIXTURE capture (`genuine-card90-table`). Make it
set a date in a tabular date cell on ANY navigated document form with **no per-form capture**: open the form
config-agnostically, foreground it, get a row, activate the date cell, then reuse the (already form-agnostic)
calendar localization + year-nav. Capability: extends `qa-mcp-protocol-lab`.

## What is ALREADY proven (key risk retired, card 99)
- **Config-agnostic OPEN of a real document works:** `read_form_descriptor(open_link=e1cib_data_link("Документ.Заказ", ref))`
  opens `Заказ 000000001` (78 elements: Table «Товары» cols ТоварыТовар/ТоварыЦена/ТоварыКоличество/ТоварыСумма,
  header «Дата») — handle resolved, descriptor read. (`document_form_introspect_probe.py`)
- The form CAN render foreground and its **date field activates + shows the calendar button** (after interaction).
- **Localization (calendar glyph) + year-nav are form-agnostic** — they work wherever the cell is once the calendar
  is open.

## The blocker chain (4 prerequisites — solve in order)

### Blocker 1: foreground the navigated form (NEW, found card 99 — the immediate wall)
`_open_form_by_link` (splice-navigate) **creates** the form (handle resolves, descriptor/reads work) but does NOT
make it the active VISIBLE form — the desktop sections panel stays foreground; blind clicks/keys hit it (a click
once opened the «Организации» list). settle 3s, clicks, and **Ctrl+F6/Ctrl+Tab did NOT foreground it**.
- **Why:** the genuine navigation likely sends a "show/activate form" command the splice does not replay.
- **✅ SOLVED 2026-06-21 (the wall is cleared).** Empirically (probes 1-6): the cause is the working-area MODE,
  not a per-window activate command. A bare bootstrap leaves the START PAGE as the active working area (no tab
  bar); `splice_navigate` then opens the target as a BACKGROUND tab (footer peeks under the section panel). Two
  routes that FAILED: (A) the card-96 window-level `…SecondaryFrame[S] 88 82 81 20 20 20` command on the held
  conn — accepted (resp refs the form's SF) but screenshot UNCHANGED; (B) OS-window raise — N/A, the form is an
  internal 1C MDI tab, NOT a separate OS window (only one OS window `Демонстрационное приложение` exists). **What
  WORKS:** replay the fixture-open render-push frames `_VALUE_READ_OPEN_FRAMES` (11-17; even the no-SF prefix
  11-14) FIRST to put the client into tabbed working-area mode (the tab bar appears), THEN `splice_navigate(target)`
  → the target opens FOREGROUND as the active tab, **fully rendered incl. the new Дата column** (screenshot
  `docforeground3/30_zakaz_open.png`, `docforeground6/30_nav_after_prefix.png`). Note `splice_navigate` ALONE
  (list or data link, once or twice) only ever makes a bg tab. **Generality:** the fixture frames are a FIXED
  reusable primer (not a per-target capture), so this is config-agnostic in the "no per-form capture" sense for
  any vanessa_client doc; a fixture-FREE primer for a config without the fixture (decode a genuine open-foreground
  via Vanessa-manager capture, Route B) is the remaining true-generality follow-up.
- Probes: `document_foreground_probe{,2,3,4,5,6}.py`; evidence dir `screenshots/docforeground{,2..6}/`.

### Blocker 2: dismiss the crypto nag dialog — ✅ NON-ISSUE 2026-06-21
No «Расширение работы с криптографией… ОК» modal appeared on open in this flow (it is a Сервис menu item, not an
on-open modal here). No dismissal needed; `answer_dialog` stays available if it recurs.

### Blocker 3: localize + activate the tabular date cell — ✅ SOLVED 2026-06-21
ON-SCREEN **double-click** activates the cell editor (inline date editor + its calendar button appear) — no protocol
write_block, no `genuine-card90-table` capture. The cell is **auto-located from the column header «Дата»**
(full-image `compare -subimage-search`, Liberation-Sans 13 — the table header WINS the global match over the
colon-suffixed doc-field label «Дата:», RMSE 0.143 vs 0.148), then the first data row = header center + one grid row
(≈28 px) via `table_cell_from_header`. The calendar button is then localized in the cell's ROW BAND (the doc-header
«Дата» glyph would else win the global search). Approach (a) column-header template-match chosen; keyboard (b)
unused. Helpers shipped: `native_xtest.locate_text` / `table_cell_from_header` / `xtest_double_click`.

### Blocker 4: a date column to target (deploy) — ✅ DONE 2026-06-21
Added a `Дата` (Date/DateTime) attribute to `Документ.Заказ` tabular section «Товары» (edt-mcp
`add_document_tabular_section_attribute`) + a `ТоварыДата` form column (hand-edited `Form.form`), **deployed** via
`tools/protocol-research/deploy_fixture.sh` (whole-config EDT export → ibcmd import → apply; gen
`d8a70b86…`→`8914b866…`; `run_metadata_change_delivery` profile was available but the proven ibcmd path was used).
Confirmed in the live descriptor (78→79 elements; EditField `ТоварыДата` present).

## Approach (ordered)
1. (Precondition) enable edt-mcp deploy profile + reconnect.
2. Add a Date column to `Заказ.Товары` + deploy; re-open the form, confirm the new column in the descriptor.
3. Solve Blocker 1 (foreground) — the make-or-break; decode+splice "activate form" (or generalize activate_window).
4. Solve Blocker 2 (nag) + Blocker 3 (cell activation) — column-header localization or keyboard nav.
5. Wire a config-agnostic activation path into `set_table_date_cell` (new param, e.g. `open_link=` instead of the
   fixture `capture`); reuse the calendar localization + year-nav.
6. Live-verify: set a date (incl. cross-year) in `Заказ.Товары`'s date cell with NO per-form capture; screenshot
   proof; evidence + tests.

## Done when — ✅ MET 2026-06-21
`set_table_date_cell(open_link="e1cib/data/Документ.Заказ?ref=…", column_title="Дата", date=…)` sets the date in a
real document's tabular date cell config-agnostically (no `genuine-card90-table` capture, auto-localized — no
measured coords), live-verified by screenshot, on a form OTHER than the fixture. **Live-proven both same-year
(15.08.2026) and cross-year (10.03.2028)** through the shipped tool. Tests (354, +3) + evidence
(`evidence/card100-config-agnostic-datecell-2026-06-21/`).

## Risk/scope
High — multi-step protocol research (foreground decode is the crux) + a metadata deploy. Multi-boot, likely a
focused multi-session effort. The localization + year-nav + calendar mechanics are DONE and reused.

## Related
- Parent: card 99 (`4.done`). Evidence: `evidence/card99-2ndform-pathB-2026-06-20/` (Заказ form rendered + descriptor).
- Code: `src/qa_mcp/mcp_server.py` (`set_table_date_cell`, `_set_table_date_cell`, `_open_form_by_link`),
  `src/qa_mcp/protocol/native_xtest.py` (`locate_calendar_button`, calendar geometry, year-nav),
  `src/qa_mcp/protocol/navigation.py` (`e1cib_data_link`).
- Probes: `document_form_introspect_probe.py`, `document_activate_experiment_probe.py`.
- Memory: [[qa-mcp-capture-free-epic]], [[edt-mcp-profile-and-deploy]], [[opt-1c-dev-lab-layout]].

## Log
- 2026-06-21 card created — carries the card-99 change-2 "2nd form" follow-up as Path B (config-agnostic, true
  generality). Key risk retired (config-agnostic open + date-field activation proven on `Заказ`); the 4-blocker
  chain (foreground → nag → cell-localize → deploy) + ordered approach captured. Blocked on the edt-mcp deploy
  profile reconnect for the date column.
- 2026-06-21 **DONE — functionally complete, all blockers cleared, live-verified.** (1) edt-mcp deploy profile
  confirmed `all`. (2) Added `Заказ.Товары.Дата` (Date/DateTime) + `ТоварыДата` form column; deployed (gen
  `8914b866…`); confirmed in the descriptor. (3) **Blocker 1 (THE WALL) SOLVED** — foreground via the fixture
  render-push tab-mode primer + navigate (two failed routes ruled out: window-level activate command, OS-window
  raise). (4) Blocker 2 a non-issue; **Blocker 3 SOLVED** (on-screen double-click + column-header auto-localization);
  Blocker 4 reused (card 99 calendar pick + year-nav). (5) **Productized** `set_table_date_cell(open_link=…,
  column_title=…)` (`_set_table_date_cell_open_link` + shared `_drive_calendar_pick`; `native_xtest.locate_text`/
  `table_cell_from_header`/`xtest_double_click`); 354 tests (+3), no regression. (6) **Live-verified through the
  shipped tool**: Документ.Заказ Товары.Дата → 15.08.2026 AND cross-year 10.03.2028 (screenshot proof). Evidence
  `evidence/card100-config-agnostic-datecell-2026-06-21/`. **Remaining (true-generality follow-up):** a
  fixture-FREE foreground primer for a config WITHOUT the bundled fixture (decode a genuine open-foreground, Route
  B). Ready for `$opsx-pub`.

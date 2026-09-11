# Capture-free epic — NEXT SESSION handoff (START HERE)

**Date:** 2026-06-21. **Purpose:** the single entry point to continue the capture-free epic in a fresh session.
Read this first, then `capture-free-epic-state.md` (decoded protocol model §3, code map §4, capture recipe §5,
decode→productize loop §6).

> **⭐⭐ EPIC + cards 96/97/98/99 + 100 + 101 ALL DONE. 52 MCP tools, 355 offline tests, no Vanessa.**
> Cards 100 + 101 DONE 2026-06-21 (on `main` per the publish): `set_table_date_cell(open_link, column_title)`
> sets a date in a REAL document's tabular date cell **config-agnostic, no per-form capture**, and the
> navigated-form FOREGROUND is now **fixture-free by default** and **cross-config-confirmed on demo БСП**. No open
> thread remains.

## ⭐ STATE (2026-06-21) — cards 100 + 101 DONE

> **Card 100 — config-agnostic tabular date-cell on ANY document form.** `set_table_date_cell(open_link=
> "e1cib/data/Документ.Заказ?ref=…", column_title="Дата", date=…)` sets the date in a real document's Товары.Дата
> cell, no per-form capture, **auto-localized** (column-header `compare -subimage-search` → `table_cell_from_header`,
> no measured coords). Live-verified same-year (15.08.2026) + cross-year (10.03.2028). The 4 blockers cleared:
> (1) FOREGROUND the navigated form (THE WALL); (2) crypto nag = non-issue; (3) on-screen double-click activates
> the cell + the calendar button (reuse `locate_calendar_button`); (4) deployed a `Дата` column to `Заказ.Товары`.
> Code: `_set_table_date_cell_open_link`, `_drive_calendar_pick`; `native_xtest.locate_text`/`table_cell_from_header`/
> `xtest_double_click`. Evidence `card100-config-agnostic-datecell-2026-06-21/`.
>
> **Card 101 — fixture-FREE foreground (closes card-100's generality remainder).** The navigated-form foreground
> no longer needs the bundled fixture: `_foreground_form_by_link(open_link)` replays the genuine COLD
> catalog-list-open sequence from `genuine-card98-listform-read` (navigate → activate `e0 4b 55` → render `e1 82`
> → `88 82 81` window-commands → activate, NO fixture) with the nav-link RETARGETED to the target — opens any
> list/document foreground. `set_table_date_cell` gained `foreground=` (`"listreplay"` DEFAULT fixture-free |
> `"fixture"` legacy). Live: Заказ Товары.Дата → 12.07.2026, tab bar with NO fixture tab. Evidence
> `card101-fixture-free-foreground-2026-06-21/`. **Key lesson:** the foreground trigger is the activate+render+
> `88 82 81` frames that follow a navigate — a minimal 2-frame `splice_navigate` omits them, so the form stays a
> background tab; the full genuine cold list-open sequence (retargeted) foregrounds any form fixture-free.
>
> **Deploy unblocked:** edt-mcp runs `EDT_MCP_TOOL_PROFILES="all"` (199 tools); the `Заказ.Товары.Дата` column was
> deployed via `tools/protocol-research/deploy_fixture.sh` (whole-config EDT export → ibcmd import → apply).
>
> Cold-client boundary stands (one materialised dynlist/record read per fresh `launch_test_client`; XTEST/calendar
> interaction is OS-level, not subject to it). Capture recipe: [[genuine-action-capture-recipe]] +
> [[vanessa-mcp-linux-genuine-manager]]; lab: [[opt-1c-dev-lab-layout]].
>
> **Cross-config CONFIRMED:** the fixture-free `foreground="listreplay"` opened the demo БСП
> (`/opt/1c-dev/demo_1_0_41_3`) Валюты list foreground with NO fixture (`demo_fixturefree_foreground_probe.py`;
> evidence `card101-fixture-free-foreground-2026-06-21/04_demo_bsp_valyuty_foreground_no_fixture.png`).

**Card 97 COMPLETE + closed.** **Card 98 (product boundary): changes 1, 2, 3, 4 DONE + published; change-5 GATE
(config-agnostic open) ✅ SOLVED + published 2026-06-20** (published work on `origin/main`; this session's dynlist
read + multi-column read + whole-grid read are uncommitted on `main`). **48 MCP tools, 336 tests.** Prior sessions shipped: change-1 Cyrillic-field read · change-2 tool-surface parity (5 tools incl.
`get_window_list_testclient`) · change-3 step library · the **change-1 generalization**
(`read_form_descriptor(enumerate_live=True)`) · the **open-any-form wrapper** (`read_form_descriptor(open_link=…)`).
This session also shipped: **change 4** (`agent_runtime` decision record, `docs/agent-runtime-decision.md`) · the
**navigated-record value-read mechanism** (zero-group field enumeration + newest-window open) · the
**dynlist-column read scoping finding**.

⭐ **CONFIG-AGNOSTIC OPEN — ✅ SOLVED + PRODUCTIZED + 2nd-config-verified 2026-06-20 (the change-5 gate is CLOSED).**
`read_form_descriptor(open_link=…)` now opens + introspects ANY form **without opening the fixture first**, so it
works on a config that has NO fixture. **The blocker was smaller than it looked:** the splice header is
`frame218[:cb-23-95]` and `cb 23 95` sits at **offset 48**, while the form-specific `managed_form_guid` (151) and
`secondary_frame_guid` (101) are BOTH **after** the marker — so the header [0:51] needs only `ack_guid` (@2,
bootstrap) + `sequence` (@19). Fix: render frame 218 with **placeholder** form GUIDs and slice the header
(`_splice_header_no_form`) — byte-identical to the fixture-rendered header, NO form open. The `open_link` path now
SKIPS fixture frames 11-17, window-lists the bare desktop for the LIVE MainFrame, and navigates from it
(`splice_navigate(main_frame=…)` retargets the desktop GUID). **Live-proven on TWO configs:** vanessa_client
without opening the fixture (Контрагенты → 79 elements) AND **demo_1_0_41_3 (БСП, never captured) → Валюты → 46
elements** — same productized tool. Evidence: `evidence/card98-config-agnostic-open-2026-06-20/findings.md`.

⭐ **TABLE-READ ✅ CAPTURED + DECODED + `read_table_cell` SHIPPED (form tables) 2026-06-20.** The genuine
table-cell read = `…Table[T] 88 81 81 e0 4b 55 eb 53 <column-name block> <pad> <tail>` (TABLE command by column
NAME, `e0 4b 55` read action); the response value rides the canonical `81 81 81 e0 4b 53 9a <len> <value>`
envelope (`extract_table_cell_value` decodes it). **MCP `read_table_cell(table,column,open_link?)` (#46) is
live-verified on the fixture form table** (PF_TABLE_TEXT="PF_ROW_001_TEXT", PF_TABLE_NUMBER="1,10"); 46 tools, 330
tests. ⭐⭐ **DYNLIST read ✅ SOLVED + PRODUCTIZED + GENERALIZED + value-verified (2026-06-20).** `read_list_column`
is rewired off the (non-working) splice onto a **FAITHFUL FULL-SEQUENCE replay** of `genuine-card98-listform-read`
— the WHOLE manager stream replays in the genuine order (navigate the `f7` nav-link → activate `88 81 81 e0 4b 55`
→ render/data-load → position to the first row `88 82 81` → read), with `GuidRebinder` rebinding the per-session
window GUIDs (the card-80 `set_reference_field`/`read_spreadsheet_cell` loop), nav-link + column re-targeted
in-frame (`retarget_list_read_frame`). Live (vanessa_client) **4/4 COLD cases** vs OData: Товары/Наименование→
**«Обувь»**, Товары/Код→**«000000001»**, Контрагенты/Наименование→**«Покупатели»**, Валюты/Наименование→**«EUR»**.
**Root cause of the 4 prior splice failures CONFIRMED — not the retarget, the SEQUENTIAL replay:** `verbatim#2`
(byte-identical to the working `verbatim#1`) ALSO returns None; on the 2nd+ replay against the same client the
render/data-load shrinks (343/467 B→118/182 B) so the dynlist current-row DATA isn't materialised and the read
echoes `88 81 81 e0 4b 55` (no value). ⚠ **COLD-CLIENT BOUNDARY: one dynlist read per fresh `launch_test_client`**
— reading several rows/columns in one client session (a cache reset between replays) is the open follow-up. Code:
`native_write.py` (`ReadListColumnTemplate` + `derive_read_list_column` + `read_list_column_replay` +
`retarget_list_read_frame`); MCP `read_list_column(column, open_link, capture_dir="genuine-card98-listform-read")`.
⭐ **MULTI-COLUMN ✅ `read_list_row(open_link, columns)` (MCP #47) — reads SEVERAL columns of the first row in ONE
cold session** (the cold-client boundary is per-CLIENT-PROCESS, so read everything inside the one materialised
session): cold full-replay through the captured read, then one extra read per column on the SAME socket — the trap
is the message-id (offset 2) is a session-validated correlation id, so **keep it** (regen → 481-byte error) and
bump the sequence. Live: `read_list_row(Товары,[Наименование,Код])`→`{«Обувь»,«000000001»}`. `read_list_column_replay`
delegates to `read_list_row_replay`. ⭐⭐ **WHOLE-GRID read ✅ `read_list_grid(open_link, columns, max_rows)` (MCP
#48) — reads MANY ROWS × columns in ONE cold session.** Captured + decoded the dynlist «перехожу к следующей
строке» (next-row) via the genuine Vanessa manager (`genuine-card98-nextrow`): the go-to-row 4-frame block's
`…e1…` frame carries a 16-byte ACTION GUID at offset 53 — `3e312772…`=first-row, **`d267315b…`=next-row** (constant
across calls; the read after it advances Обувь→Продукты→Услуги). `read_list_grid_replay` replays cold through the
first read, then loops (replay the next-row block, rebound+seq-bumped → read each column), stopping at max_rows or
a repeat/empty (end of list). **Live: Товары → 4 rows × {Наименование,Код}** (Обувь/Продукты/Услуги/**Электротовары**
— row 4 NOT in the capture ⇒ iterates beyond it; codes vs OData; auto end-of-list). Reads the current view/sort
order (Товары default = hierarchical → 4 top-level rows; nested items need flat view first). **48 tools, 336
tests.** Evidence `card98-dynlist-grid-2026-06-20`. **Row-by-VALUE earlier NEGATIVE (2026-06-20):** the
«перехожу к строке» (exact-match) command decoded from `genuine-card90-rowaddr` (FORM table) does NOT splice onto
a live DYNLIST (still read row 1); `where_*` wiring REVERTED (decode + constants KEPT, `row_select_from_read_frame`,
unit-tested). A genuine dynlist «перехожу к строке» capture would add row-by-value (now easy — same recipe).
Probes: `dynlist_fullreplay_read_probe.py` (verbatim), `dynlist_read_freshcase_probe.py` (4-case cold
generalization), `dynlist_read_diag_probe.py` (root-cause trace), `dynlist_multiread_variants_probe.py` (the
message-id finding). (NB the fixture's own dynlist
ДенамическийСписокИерархия has AUTO unnamed columns — even genuine Vanessa can't read it; use a real catalog LIST
form.) `read_table_cell` (form tables) unchanged. This also unblocks the NON-EMPTY navigated value-read.
Recipe: [[vanessa-mcp-linux-genuine-manager]] + [[genuine-action-capture-recipe]]. Evidence
`card98-tableread-decode-2026-06-20`.

Already DONE this session (don't redo): **change 4** (`agent_runtime` decision record — `docs/agent-runtime-decision.md`);
**navigated-record value-read MECHANISM** (`extract_descriptor_fields` now enumerates zero-group fields directly
under ManagedForm — a catalog RECORD form's object attributes, e.g. demo `Валюта (создание)` Код/Наименование;
columns still excluded; `_open_form_by_link` got a newest-window fallback for custom-caption forms). The mechanism
REACHES a real 2nd-config record form but its create-form fields are EMPTY — non-empty needs the table-read/ref
above (evidence `card98-navigated-record-valueread-2026-06-20`). Finding: a DataProcessor form opened by nav-link
returns a command-bar-only descriptor (body absent), so the fixture is not a navigated-value vehicle — a catalog
record form is.

Also still open: general `set_table_date_cell` (needs on-screen cell localization — element BOUNDS from the
descriptor, or a screenshot-localization step; same dependency as a general table-cell-by-coords tool). The
historical per-change detail follows.

Card-98 change detail (all ✅ DONE 2026-06-20 — historical reference):

1. ✅ **DONE 2026-06-20 — Cyrillic-named field refinement of `read_form_descriptor`.** Now sweeps Cyrillic fields:
   their query paths ride the `0x97 <char-count> <utf-16le>` envelope (vs ASCII `0x9a <byte-len> <latin1>`) — the
   genuine sweep queried `Контрагент`/`ПолеСоСпискомВыбораСтрока` (in `Group[Группа1]`, frames 296-303) but
   `_enumerate_capture_fields` (ASCII regex) + `_retarget_read_to_groups` (latin1 build) missed them. Added 4
   reusable `element_ref` helpers (`path_is_latin1`, `encode_element_path_block`, `extract_element_paths_utf16`,
   `retarget_element_path_reencode`); dual-encoding enumeration + retarget dispatch (ASCII→0x9a / non-latin1→0x97);
   the response parser needed NO change. **Live: 43/43 queried, 42/43 value-match** (the 1 diff = live-state
   PF_SELECTED_ROW_MARKER); both Cyrillic fields decoded (`""`) ⇒ **43/46** (the 3 `PF_DECORATION_LABEL*` are the
   Label-kind ceiling). 296 tests. Evidence: `evidence/card98-cyrillic-fields-2026-06-20/findings.md`.
2. ✅ **Increment 1 DONE 2026-06-20 — Change 2 MCP tool-surface parity** (state / results / infobase / window).
   4 new capture-free tools: `get_test_results` (session results aggregation via `_RESULTS_LOG`), `infobase_info`
   (profile metadata, password-redacted, + live listening), `get_state` (the `get_state`-equiv: connection +
   run-session + infobase identity), `get_window_list` (OS window enumeration via xdotool — new
   `protocol/windows.py`). 45 tools / 323 tests; live-verified (real client window enumerated; run-session
   aggregated). **`get_window_list_testclient` ✅ SHIPPED 2026-06-20** (MCP #45, the 1C-internal window/tab list —
   distinct from the OS `get_window_list`): booted the genuine Vanessa manager, captured + decoded the window-list
   call (window records `<Kind>[<guid>] 82 <fa|f7> <len> <caption>`, parser `extract_testclient_windows`), and
   replayed it by SPLICING the window-list command body onto a live-rendered value-read header (a raw replay is
   rejected «Сеанс завершен» — the client validates the session GUID; the command body is session-independent).
   Live: 3 windows (fixture form + desktop + home). Evidence: `evidence/card98-windowlist-decode-2026-06-20/findings.md`.
   ⭐ LEFT on change 2: only `ui_read_tree` (active-window element tree) — folds into the change-1 ANY-form
   generalization below. Evidence: `evidence/card98-{toolsurface-parity,window-enumeration}-2026-06-20/findings.md`.
3. ✅ **Change-1 generalization SOLVED 2026-06-20 — live field enumeration, NO per-form capture.**
   `read_form_descriptor(enumerate_live=True)` enumerates the open form's fields LIVE by splice-replaying the
   genuine `get_form_analysis` descriptor query (the same SPLICE technique that unlocked `get_window_list_testclient`
   — a raw/template replay DESYNCED, but grafting the descriptor command body onto a live value-read header, with
   the form path retargeted to the live S/F, works). The ≈71 KB descriptor response is the element tree
   (`(Group[g].)+EditField[name]`, ASCII + UTF-16); `extract_descriptor_fields` parses it → `[(name, groups)]`
   (the live `_enumerate_capture_fields`). Live: **46 fields / 46 queried** (vs the capture path's 43; found 3 the
   sweep lacked), 42/43 vs the oracle, Cyrillic decoded. **The field list is now capture-free.** Evidence:
   `evidence/card98-generalization-solved-2026-06-20/findings.md`. ✅ **Open-any-form wrapper — SOLVED 2026-06-20:**
   `read_form_descriptor(open_link="e1cib/list/Справочник.X")` opens ANY form by nav-link + introspects its full
   element tree, NO per-form capture. The ManagedForm-F blocker is solved by a decoded RESOLVE query (the sweep's
   first query, mgr#2: body `9a 34 SecondaryFrame[S]` S-only + opcode `e1 81`, vs the descriptor's `e1 82`; its
   response returns the form's `SecondaryFrame[S].ManagedForm[F]`). Chain (`_open_form_by_link`): `splice_navigate`
   (2-frame navigate, nav-link retargeted → opens the form) → `get_window_list_testclient` (the new window's S, by
   caption) → `splice_resolve_form_query` (S→S.F, match the TARGET's S not the first) → `splice_descriptor_query`
   (explicit S.F) → `extract_descriptor_elements` (full tree, ASCII+UTF-16). Live: Контрагенты → **79 elements**
   (Table[Список] + command buttons + view-mode group), a DIFFERENT form, capture-free. This also closes
   `ui_read_tree`. LEFT: VALUES of a navigated form (the value-read renders the fixture region — retarget its S.F)
   + a newest-window match for custom-caption forms. Evidence: `evidence/card98-open-any-form-solved-2026-06-20/findings.md`.
4. **Change 5 (2nd-config gate) — ✅ SOLVED 2026-06-20** (config-agnostic open): READ generalizes (prior),
   WRITE via XTEST hybrid (prior), and now the **form OPEN itself generalizes** — `read_form_descriptor(
   open_link=…)` introspects ANY form on ANY config with NO fixture, live-proven on demo БСП (Валюты → 46
   elements). The last gating step (a config-agnostic open) is closed; the generality matrix's lone ⚠ rows
   (`read_form_descriptor` / `open_link` fixture-bound) are now ✅. Evidence:
   `evidence/card98-config-agnostic-open-2026-06-20/findings.md`. **Change 4 (`agent_runtime`)** — a
   build-on-demand decision record (still CHARACTERIZED not built).
5. **General `set_table_date_cell` MCP tool** — the card-97 DATE grid cell is SOLVED as a mechanism
   (protocol-activate + mouse calendar pick) + the date→click geometry is shipped + tested
   (`calendar_{month,day}_cell`); a general tool needs on-screen cell localization (calendar-button + popup origin
   — the probe hardcodes fixture coords). Folds into card-98 introspection (element bounds).

**Card 97 detail (✅ all DONE 2026-06-19, historical — for reference):**
1. **Change 3 — reports / ТабличныйДокумент:** ✅ **FUNCTIONALLY COMPLETE.** report-RUN (`run_report`, #37 —
   PF_RUN_REPORT click_command fills the SpreadsheetDocument server-side; PF_LAST_ACTION="PF_RUN_REPORT") +
   spreadsheet CELL-read (`read_spreadsheet_cell`, #38 — live-verified PASS 4/4 R1C1…R2C2). ⭐ The "binary .mxl
   boundary" was a RED HERRING (that blob = the form-RENDER path): a cell is read by an IN-CLIENT 1C method —
   navigate «перейти к ячейке» (`EditField[PF_REPORT] 88 82 81 fa <len><addr>`) + the client's `9a <len><value>`
   echo (the card-79 value-read shape), a 6.5 KB exchange. So reading cells is capture-free with NO .mxl decode.
   ANY-length address works — the navigate's trailing `20 20 20` is structural (NOT padding), so the address
   re-target RESIZES the frame (the navigate tolerates resize, unlike a value-SET); live-verified across 4/5/6-char
   addresses on a 12×12-grid fixture. Fixture extended (PF_REPORT SpreadsheetDocument + PF_RUN_REPORT, 12×12 grid;
   gen `38bc7fac8858…`→`d8a70b862da9…`).
2. **Change 4 — dynamic-list ops: ✅ FUNCTIONALLY COMPLETE.** search-string (`search_list`, #34 — UTF-16 `b7`
   buffer at the SearchStringAddition, reuses set_reference_field; "Молоко"→1 row) · view-mode/grouping
   (`set_list_view`, #35 — «Режим просмотра» form BUTTONS, click = `…Button[<name>] 88 82 81 20 20 20` with a
   Cyrillic UTF-16LE leaf → GENERALIZED click_command to UTF-16 via `retarget_element_leaf_any` +
   encoding-agnostic `_find_element_command`; 3-way verified) · filter (`advanced_search`, #36 — the «Расширенный
   поиск» DIALOG = the "drive a modal dialog" pattern: open new window → SET Pattern → Find, reusing
   set_reference_field full-replay + GuidRebinder; live-verified by the filter chip «Код: Молоко»). period = N/A
   on the Catalog.Товары dynlist (no period dimension; the modal-dialog pattern is ready to drive the
   `…Интервал`/«Настроить список» dialogs once a periodic/settings flow is captured). All dynlist commands
   discovered via get_form_analysis (viewmode findings). **Lab gotchas:** `run_scenario` CACHES a feature by
   filePath — use a FRESH FILENAME after a failed edit; click a command BY NAME («с именем 'X'») when the caption
   differs from the name.
3. **Change 2 DATE grid cell — ✅ SOLVED 2026-06-19** (protocol-activate + pure-MOUSE calendar pick;
   live-verified row 1 `10.01.2026 9:00:00`→`15.08.2026 0:00:00`, committed). The path: (1) PROTOCOL — replay the
   `set_table_cell` `write_block` (activate+SET, NOT the commit) for PF_TABLE_DATE on a HELD connection → the
   inline date editor opens + a calendar dropdown button appears; (2) MOUSE — click the dropdown → click the
   month (`calendar_month_cell`) → click the day (`calendar_day_cell`, day-of-week→grid math) → `Return` commits.
   **Why mouse, not keys:** protocol text-SET is RULED OUT (committed=False even at fitting width vs number cell
   True; numdate «Неподходящий тип» = Vanessa's pre-check), and synthetic keystrokes (`type` AND per-`key`) do
   NOT reach 1C's masked date editor in any focus state — DECISIVE control: the same `xdotool type` DID land in
   the plain PF_EDIT_STRING field. Mouse events reach every control. Productized the date→click geometry
   (`calendar_{month,day}_cell` in native_xtest.py, +5 tests); a general MCP tool still needs on-screen cell
   localization (calendar-button + popup origin coords — the probe hardcodes them) → follow-up. Lab: needs
   matchbox (bare Xvfb has no keyboard focus + matchbox MAXIMIZES → coords shift). Evidence:
   `evidence/card97-date-gridcell-2026-06-19/findings.md`; probe `date_cell_calendar_probe.py`.
4. **Read-decode follow-ups** (raise the assert/wait #5 ceiling): (a) **cross-region value read** — ✅ **DONE
   2026-06-19** (live-verified): the value-read query carries the FULL element path
   (`Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[PF_EDIT_STRING]`); the old leaf-only retarget kept the
   `PF_GROUP_EDITS` container so PF_GROUP_MAIN markers resolved to an unreachable path → 0x88 stub. Fix =
   FULL-PATH retarget (`_retarget_read_to_groups`, the read query tolerates the resize like the spreadsheet
   navigate); `assert_form_value`/`wait_for_form_value`/`_read_field_value` gained a `groups` param. Live:
   `groups=["PF_GROUP_MAIN"]` → PF_FIXTURE_VERSION="protocol-fixture.v1", PF_LAST_ACTION="PF_STATE_INITIAL",
   PF_SELECTED_ROW_MARKER="PF_ROW_IDX_1:PF_ROW_001" (was None each). Auto group-discovery (no `groups` arg) is the
   only remainder → ties into card-98 form-introspection. Evidence:
   `evidence/card97-crossregion-read-2026-06-19/findings.md`. (b) **number/date value PARSER** — ✅ **DONE
   2026-06-19** (offline, no lab): the premise was STALE — number AND date already decode through the same
   `81 81 81 fa <len>` value shape as their formatted display text (genuine-capture verified:
   PF_EDIT_NUMBER→"120,50", PF_EDIT_DATE→"15.01.2026 10:30:00"). Fixed a latent parser bug (a value-read echoes
   the field NAME first as a `81 fa` descriptor — the old single-`find` landed on it and returned None; now
   `extract_edit_field_value` SCANS all occurrences + decodes the `e0 4b 53 9a` envelope + skips the `e2` stub)
   and added a `numeric` assert mode (`"120,50"`==`"120.5"`, space/NBSP thousands). 269 tests. Evidence:
   `evidence/card97-numdate-parser-2026-06-19/findings.md`.

⭐ **Cross-cutting lesson (this session) — padding-vs-resize and form-render-vs-in-client-read are PER-COMMAND.**
A value-SET frame DESYNCS on a frame resize (card 80), but the spreadsheet «перейти к ячейке» navigate frame
TOLERATES resize (so the cell address is any length). The full form-render carries a binary blob with NO cell
text (only a handle); a TARGETED in-client read returns the cell as a plain value. ⇒ don't carry a conclusion
from one frame/command type to another — TEST it side-by-side (`cell_resize_experiment.py` is the template: try
both approaches on one client). And when a value isn't in the form-render blob, look for the in-client
targeted-read path (small plain response) before assuming it's a deep binary decode.

Lab gotchas (capture recipe below): a REPLAY command-click capture must be **connect+open+click** (action-only
setup ≠ form-open) and **must NOT include a trailing get_form_analysis** (its descriptor dump re-emits every
Button/Table leaf and breaks `_find_command_click`'s last-run rule). **`run_scenario` CACHES a feature by
filePath — use a FRESH FILENAME after a failed edit** (or load_features). Click a command BY NAME («с именем
'X'») when the caption differs from the name. The deploy can hit a transient EDT-export glitch (`…Constant…
feature "type"` truncates an unrelated CommonForm → import fails) — just RETRY (a fresh export succeeds). The
fixture now carries: the row-op/select markers + `PF_TABLE_DATE` column, the **dynlist with a VISIBLE command
bar** (`commandBarLocation=Top` → search box + «Ещё» menu), and **`PF_REPORT` (a 12×12 SpreadsheetDocument) +
`PF_RUN_REPORT`** command. Latest deployed gen **`d8a70b862da9…`**.

## TL;DR — where we are

qa-mcp drives 1C forms over the native TestClient protocol **capture-free, NO Vanessa** — **45 MCP tools**,
**323 tests**. Card 97 COMPLETE (`4.done`): cross-region value read + number/date parser + `numeric` assert mode
+ DATE grid cell (protocol-activate + mouse calendar pick). **Card 98 in progress:** change 1 (form
introspection) DONE — **`read_form_descriptor`** (MCP #39), the capture-free `get_form_analysis` equivalent
(live-verified **43 fields / 42-of-43** vs the Vanessa oracle, ASCII + Cyrillic UTF-16 paths); change 3 (step library) DONE — **`search_for_steps`**
(MCP #40) + `docs/vanessa-mcp-parity.md` compatibility note + a Vanessa-style feature transpiling 100%; **change 2
(tool-surface parity) increment 1 DONE — `get_test_results` / `infobase_info` / `get_state` / `get_window_list`**.
LEFT on card 98: change 4 (`agent_runtime` on demand), change 5 (2nd-config gate — largely done); change 2 ✅ DONE
(incl. `get_window_list_testclient`); **change-1 generalization ✅ SOLVED** (`read_form_descriptor(enumerate_live=
True)` — live field enumeration via the descriptor-query splice, NO per-form capture; LEFT only a generic
open-any-form wrapper + the `ui_read_tree` element tree on the same descriptor). Shipped this epic: read · input+commit (string/number/date) · checkbox · choice · **search_list**
(dynlist search-string filter) · **set_list_view** (dynlist view-mode Список/Дерево/Иерархический) ·
**advanced_search** (dynlist «Расширенный поиск» dialog filter — the "drive a modal dialog" pattern) ·
**run_report** (fire a ТабличныйДокумент report) · **read_spreadsheet_cell** (read a spreadsheet cell by address,
in-client — NO .mxl decode) · page-switch · table-cell · page-field · open_list · **choose_from_list** (ПоказатьВыборИзСписка) ·
**choose_from_menu** (ПоказатьВыборИзМеню) · **answer_dialog** (real Да/Нет/ОК dialogs) ·
**set_reference_field** (CatalogRef by name) · **open_card** (drill list row → record card) ·
**close_window** · **activate_window** · **read_user_messages** (`Сообщить` / assertion read) ·
**write_form_value_xtest** (object-attr write via XTEST hybrid) · **delete_table_row** · **move_table_row** ·
**copy_table_row** (card 97 #1 row ops) · click_command · select_table_row · add_table_row · switch_page.

## ✅ Card 97 change 1 (table row operations) — COMPLETE 2026-06-19

`delete_table_row` / `move_table_row(up|down)` / `copy_table_row` (MCP #28–#30) + `select_all_table_rows`
(#31, multi-select). Each is the same
`…Group[PF_COMMAND_BAR_MAIN].Button[<CMD>]` command invoke (tail `88 82 81 20 20 20`, the card-96
window-command family — NOT the `88 81 81 e1` get_form_analysis re-render) replayed from ONE genuine
`PF_COPY_ROW` capture + length-aware Button-leaf retarget (`switch_page` twin). Fixture extended (custom
commands `PF_{DELETE,MOVE_ROW_UP,MOVE_ROW_DOWN,COPY}_ROW` + the `PF_TABLE_SNAPSHOT` read-back marker
`PF_TABLE[<n>]=<marker>|…`), deployed (gen b5802e…). Live-verified by screenshot: DELETE→`PF_TABLE[2]`,
MOVE_DOWN→`[002|001|003]`, COPY→`[…|PF_ROW_001_COPY|…]`. **Capture rule (re-learned):** the replay capture must
be **connect+open+click** (action-only setup ≠ form-open) and **must NOT include a trailing get_form_analysis**
(its descriptor dump re-emits every `Button[NAME]` and breaks `_find_command_click`'s last-run=click rule).
Verify a row op in the SAME session (read PF_TABLE_SNAPSHOT) — the effect is session-local form state. Detail:
`evidence/card97-rowops-2026-06-19/findings.md`.

**Multi-row select (#31 `select_all_table_rows`):** DECODED as a protocol TABLE-command — the genuine "выделяю
все строки" step is `…Table[PF_TABLE_ITEMS] 88 82 81 20 20 20` (addressed at the Table element, NOT a Button;
generalized via `_find_element_command` + `derive_table_command`). Fixture gained `PF_SELECTED_ROWS` +
`PF_REFRESH_SELECTION` (gen c94ebf…). ⚠️ **Read-back BOUNDARY (honest):** the multi-selection is transient
table-focus state — a SEPARATE focus-changing command (clicking PF_REFRESH_SELECTION to read it) collapses it to
the active row; **genuine == replay both read `PF_SEL[1]`** ⇒ 1C focus semantics, not a replay defect. A live
multi-selection isn't capture-free-readable across commands (the non-collapsing read is the in-session testing
API, Vanessa's domain); composing select-then-act must capture the WHOLE flow in one session.
`evidence/card97-multiselect-2026-06-19/findings.md`. Card 97 change 1 COMPLETE.

## ✅ Card 97 change 5 (waits + asserts) — SHIPPED 2026-06-19

`assert_form_value(field, expected, equals|contains|regex)` + `wait_for_form_value(…, timeout_sec, interval_sec)`
(MCP #32/#33) — first-class assert + WaitForCondition, built on the card-79 value-read (`_read_field_value`:
open form 11-17 → value-read 218-221, leaf retargeted to the field). **Fixed a real value-read parser bug:** the
value is **LEB128-length-prefixed**, NOT 0x14-delimited (0x14 was just len("PF_EDIT_STRING_VALUE")==20) → the old
parser read ONLY that field; now any same-region string parses, any length. ⚠️ **Read SCOPE (honest):** resolves
the **value-read region** (editable `PF_EDIT_*` strings — live-verified); PF_GROUP_MAIN status markers
(PF_LAST_ACTION / PF_TABLE_SNAPSHOT) return the **0x88 no-value stub** (other region — needs that region's
value-read capture), and number/date values are on the wire but need a per-type parser (→ #2). Each poll is a
full open+bootstrap+read (~5-7s), the practical poll floor. Detail:
`evidence/card97-waits-asserts-2026-06-19/findings.md`.

## ✅ Card 97 change 2 (number/date grid cells) — NUMBER SOLVED 2026-06-19, date bounded

**Number cell SOLVED, no new code:** the genuine PF_TABLE_NUMBER SET is BYTE-IDENTICAL to the string cell
(`e0 41 81 81 ba <len> <ascii>`, value as text) — the card's "different per-type buffer" assumption is DISPROVEN
for grid cells (true only for plain FIELDS, card 86c). `set_table_cell(value, column="PF_TABLE_NUMBER")` already
works (live-proven readback "999"); docstring updated. **Date cell bounded:** added a `PF_TABLE_DATE` column
(gen 5569447…) but the date control rejects text input («Неподходящий тип элемента управления») and Vanessa's
date step (`у поля календаря … я выбираю дату`) is calendar-field-only (not grid cells) → date grid-cell entry
is a follow-up (calendar pick / OS-level). Evidence: `evidence/card97-numdate-2026-06-19/findings.md`.

⏳ Next on card 97: change 2 DATE cell (deferred — calendar/OS) · change 3 (reports/ТабличныйДокумент) · change 4
(dynamic-list ops). Read-decode follow-ups: cross-region value read + number/date value PARSER (for assert/wait).

**Card 96 (interaction breadth) status:** change 1 (dialogs) ✅ · change 2 (list+menu+reference) ✅ ·
**change 3 (object navigation) ✅ DONE** — open_card (#23) · close_window (#24) · activate_window (#25), all
capture-free + live-verified · change 4 (keyboard) not started · **change 5 (read user messages) ✅ DONE** —
`read_user_messages` (#26) + the reusable `extract_user_messages` decoder (`cb 53 9a <byte-len> <UTF-8>`
envelope), live-verified; only a Cyrillic-message confirming capture is an optional follow-up.

## ✅ Task 1 (DONE 2026-06-18) — close_window + activate_window productized; the cold-cache "blocker" was a FALSE ALARM

Both shipped, live-verified (MCP tools #24/#25). Two findings:
1. **Descriptor-less replay WORKS — no cache-clear was needed.** The windows captures are descriptor-less (~31
   mgr chunks vs ~79 for open_card) because they were taken with a warm form-cache. But a REPLAY client shares
   the on-disk `~/.1cv8` form cache, so the capture replays as-is. Proven by `windows_explore_probe.py` replaying
   `genuine-card96-windows3` against a fresh client — session established through all window-close frames, zero
   divergence. The handoff's cold-cache fix was unnecessary; the cache was NOT cleared.
2. **⭐ close and activate are the SAME window-level command** `…SecondaryFrame[<window>] 88 82 81 20 20 20 …`
   (byte-diff: identical but the offset-19 seq counter + window GUIDs). Effect is contextual on z-order: on the
   ACTIVE/topmost window → close; on a BACKGROUND window → bring to front (activate). ("activate = e0 4b" was
   wrong — those are auto-activations on window open.)

Productized in `native_write.py` (`_window_sf_for_ref`/`_find_window_close`/`_next_sf_close_after`, `Close`/
`ActivateWindowTemplate`, `derive_`/`close_window`/`activate_window`) via the same full-replay + GuidRebinder
machinery as open_card. close verifies the target SF is reported BEFORE the close but gone AFTER (a DIFFERENT
window active); activate verifies the inverse (target becomes the last-reported active window). MCP tools, unit
tests, `{close,activate}_window_probe.py` + `run_*_test.sh`. Captures (genuine Vanessa manager, warm):
`genuine-card96-{windows4,activate}-20260618`; features `qa-card96-capture-{windows,activate}.feature`. Full
detail: `evidence/genuine-card96-opencard-2026-06-18/findings.md`.

## Then continue the roadmap (Task 1 is done)

- **Card 96 remainder:** change 5 (read user messages) ✅ DONE — `read_user_messages` + `extract_user_messages`
  (`cb 53 9a <byte-len> <UTF-8>`). LEFT: change 4 (keyboard Enter/Esc/Tab/arrows — decode the key-press command;
  needs a fresh genuine-manager capture and is largely covered by existing primitives — pull in "as needed");
  dialog Нет/Cancel + a confirmed QUESTION(Да) capture (same window-level mechanism); an optional Cyrillic
  `Сообщить` capture to confirm the message length-unit for multibyte text.
- **Card 97** (element-type & table/report/list completeness): table row ops (delete/move/copy/multi-select),
  number/date cells in the grid, reports/ТабличныйДокумент, dynamic-list ops, waits/asserts.
- **Card 98** (product boundary): general form introspection (`get_form_analysis`-equiv), MCP tool + Gherkin
  step-library parity, `agent_runtime` on demand, and 🚩 **change 5 — validate on a 2nd real config** (the gate
  on the "100% replacement" claim — the highest-value strategic item). **2026-06-18 (s3) — read DONE, UTF-16 fix
  DONE, write-commit gap found:**
  - ✅ **READ generalizes universally** — `read_active_window` established + read the real window of BOTH
    `/opt/1c-dev/demo_1_0_41_3` (БСП demo) AND `${QA_MCP_PRIVATE_CORPUS_ROOT}` (4.8 GB real 1С:Бух/[redacted third-party configuration]),
    NO config capture (bootstrap infobase-portable).
  - ✅ **Engine fix (headline):** element paths are UTF-16LE for **Cyrillic** field names (1-byte ASCII only for
    ASCII names like the fixture `PF_*`). The write deriver was ASCII-only → found nothing on real configs.
    Added `editfields_in` + UTF-16 in `read_field_value_near`/`derive_write_template`; derive now works on the
    real `Валюты` forms; 42 tests; fixture still commits (no regression).
  - ⚠️ **WRITE commit gap — ROOT-CAUSED (deep dive 2026-06-18 s3):** the replay reliably sets a field's
    EDIT-TEXT (SET echo) on any field incl. Cyrillic, but the **commit (edit-text→attribute) only reproduces
    for FORM-attribute fields** (the fixture's `PF_*`, which also have `OnChange`), **NOT for OBJECT-attribute
    fields** (`Объект.*` on catalog/document forms — the bulk of business data entry). Decisive proofs: the
    demo `Валюты.Наименование` (object attr, no `OnChange`) reads back EMPTY after replay; **`Записать` on
    replay did NOT persist the retargeted value to the demo DB** (DB check: only the genuine value present);
    fixture commits (control, no regression). **Fix (a) keyboard RULED OUT** — Vanessa keyboard input is the
    `VanessaExt` external component doing OS-level input inside the client (the typed value is in NO
    manager→client frame), so it can't be replayed via protocol capture. The object-attribute commit needs
    genuine client-side edit-mode/keystrokes the protocol doesn't carry; a full object-form write would need a
    HYBRID (protocol nav + real OS keystrokes), which re-introduces the OS-driving the engine set out to
    replace. On third-party-config the full-stream replay also CRASHES the client (busy 7-window home page → GUID
    desync). Evidence: `evidence/card98-2ndconfig-{read,write}-2026-06-18/findings.md`.
  - ✅ **Object-form write SOLVED via XTEST hybrid (2026-06-18 s3, DB-verified).** AT-SPI is no shortcut (1C
    exposes 0 accessible elements — `evidence/card98-2ndconfig-write…` + control GTK app registers fine), but
    the 1C X11 window IS OS-accessible. Proven end-to-end on demo `Справочник.Валюты.Наименование` (an object
    attribute): **protocol** open form + focus field BY NAME → **`xdotool type`** OS-keystrokes into the focused
    client window → **`xdotool key Tab`** blur → the OBJECT ATTRIBUTE commits (`get_form_analysis`: `Наименование
    стал равен "ZZHYBRID99"` — the exact thing protocol SetEditText could NOT do) → **`Записать`** → the row
    **persists in the DB** (appears in the `Валюты` list). This is Vanessa's mechanism (focus by API + OS input
    via VanessaExt) WITHOUT Vanessa. Prototype used the manager as the protocol driver; each protocol step has an
    our-engine equivalent (nav-link replay / activate-field / click_command). Evidence + screenshots:
    `evidence/card98-xtest-hybrid-2026-06-18/`.
  - ✅ **VANESSA-FREE hybrid proven end-to-end (2026-06-18 s3).** Step 1: OUR native /TESTCLIENT (`1cv8` thick;
    thin `1cv8c` refuses demo on config signature; default HOME for license) under Xvfb :89 + matchbox — our
    engine replayed the open+focus frames [0..17] and the form **rendered** with `Наименование` focused
    (screenshot). Step 2: `xdotool type "ZZXTEST88"` + Tab → object attribute commits (tab shows `*`) →
    `xdotool` `Записать` (Ctrl+S works) → **DB-persisted** (title `ZZXTEST88 (Валюта)` + "Создание: ZZXTEST88"
    notification). So: our engine (protocol open/focus/render by name) + xdotool (OS input) writes a real
    object-attribute field on a real config + saves to DB, **no Vanessa**. Tools: demo_render_probe.py /
    run_demo_render_test.sh, demo_xtest_write_probe.py / run_demo_xtest_write.sh. The object-form write surface
    is CLOSED for the "100% replacement" claim.
  - ✅ **PRODUCTIZED (2026-06-18 s3): `write_form_value_xtest` engine path + MCP tool #27.**
    `src/qa_mcp/protocol/native_xtest.py::write_form_value_xtest(capture, value, field, *, host, port, display,
    blur=True, save=False)` — one connection, inline: replay open+focus `[0..17]` (protocol, field by name) →
    `xdotool type` (Unicode/Cyrillic) → Tab (commit) → opt Ctrl+S (Записать→DB) → read-back via the IN-ORDER read
    sequence `[25..28]` (the single out-of-context frame returned empty; the sequence works), `committed` =
    value-in-readback. MCP tool `write_form_value_xtest` (pairs with `run_native_test_client(display=…)` +
    `capture_screenshot` + `stop_test_client`). 3 unit tests (239 suite, no regression). Live-verified
    Cyrillic: `write_form_value_xtest("genuine-card98-demo-write","ПродуктТест5","Наименование",…,save=True)` →
    committed+saved (title "ПродуктТест5 (Валюта)", Код auto "000000010", "Создание" notification). GOTCHAS in
    `run_xtest_write_test.sh`: demo holds an apache OData session @1936 (www-data) → stop apache for the boot;
    use `1cv8` thick (thin refuses demo signature) + default HOME (license) + matchbox (layout).

## The proven productize pattern (reuse for every action)

Each shipped action is `derive_<action>(capture_dir, …)` (locate the genuine command block) +
`<action>(template, …)` (replay setup → the command, retargeting/GuidRebinding) + an MCP tool + a unit test +
a `<action>_probe.py` / `run_<action>_test.sh` live-verify. Two flavours:
- **Block-retarget** (choose_from_list, set_table_cell, …): replay setup [0..setup_end] then a small command
  block with a value/leaf retarget.
- **Full-stream replay** (answer_dialog, open_card, set_reference_field): replay the WHOLE manager stream;
  GuidRebinder rebinds new-window GUIDs automatically (first-appearance) — use for new-window navigation
  (dialogs, cards, close/activate). Verify by a marker reading back (ASCII or UTF-16) or `accepted`.

## Lab recipe + gotchas (capture)

- Boot manager [[vanessa-mcp-linux-genuine-manager]]; drive via `tools/protocol-research/vanessa_mcp_call.py
  <tool> '<json>'` (the lazy `mcp__vanessa-mcp__*` wrapper is deferred on Linux). `search_for_steps_by_keywords`
  uses `search_name`/`search_description`/`search_type` (| = OR).
- apache holds vanessa_client at 8.3.27.1936 vs the 2130 client → `sudo -n systemctl stop apache2` before any
  native client / capture; restart after. The native replay client needs vanessa_client FREE (Vanessa down).
- `pcap_to_traffic.py <pcap> <client_port> <out> <manager_port>` — the 4th arg isolates the dominant 1C
  connection; strings are UTF-16LE on the wire (search both ASCII paths and UTF-16 values).
- Genuine-capture recipe + step fixes: [[genuine-action-capture-recipe]]. Click a command BY NAME («с именем
  'X'») when the caption is an auto-synonym. The fixture is `Обработка.ФикстураПротоколаTestClient` in
  vanessa_client; its EDT source (Module.bsl / Form.form) is at
  `/opt/1c-dev/vanessa_qa/vanessa_client/src/DataProcessors/ФикстураПротоколаTestClient/` (NOT git-tracked).
- Fixture edits deploy via `tools/protocol-research/deploy_fixture.sh` (manual ibcmd export/import/apply;
  `run_dev_infobase_apply` is workspace-locked). [[edt-mcp-profile-and-deploy]].

## Pointers

- **Code:** `src/qa_mcp/protocol/native_write.py` (all derive_*/<action> + GuidRebinder use), `mcp_server.py`
  (the 23 MCP tools), `protocol/{element_ref,navigation,bootstrap_synth,session}.py`.
- **Cards:** 82 (epic), 96 (interaction breadth — in progress), 97/98 (backlog).
- **Evidence (this epic):** `evidence/genuine-card96-{choicelist,dialogs,ref,opencard}-2026-06-18/`.
- **Docs:** this handoff, `capture-free-epic-state.md`, `capture-free-epic-next-roadmap.md`.
- **Memories:** [[qa-mcp-capture-free-epic]] (START HERE), [[genuine-action-capture-recipe]],
  [[vanessa-mcp-linux-genuine-manager]], [[linux-native-testclient-xvfb]], [[edt-mcp-profile-and-deploy]],
  [[lab-infobase-access]], [[ibsrv-odata-vs-httpservice]], [[autonomous-1c-observability]].

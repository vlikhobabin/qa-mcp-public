# 98. Product boundary — form introspection, MCP/step-library parity, cross-config generalization

## Status
4.done

## Order Index
98

## Owner
unassigned

## OpenSpec Stage
story

## Result
Done. All 5 changes + the 🚩 cross-config gate are delivered and published; `agent_runtime` is a decision
record (change 4). The capture-free engine is a drop-in Vanessa replacement for read/introspection across
configs: `read_form_descriptor` (any form on any config, no fixture), tool-surface parity (state/window/
results/infobase, incl. `get_window_list_testclient`), a searchable Gherkin step library, and the config-
agnostic open. The 2026-06-20 dynlist read follow-ups close the visible-grid gaps: `read_list_grid(flat=True)`
reads a hierarchical catalog's NESTED items, and `read_list_row(where={col: value})` positions a dynlist by
value — both live-verified vs OData. 340 tests.

## Next
None for the card. Optional deeper follow-ups (NOT blockers, can be a fresh card): the navigated-RECORD
value-read on a POPULATED record (open an existing record by ref/row-drill, not the empty create-form); a
general `set_table_date_cell` (needs on-screen cell localization / element bounds).

## Source
- 2026-06-17 (board triage): consolidates the "make it a drop-in product, not a lab demo" work into one story
  with a 5-item change set. Folds cards 87 (introspection), 89 (MCP/step parity), 77 (agent_runtime decision)
  and 94 (cross-config generalization — the GATE). Sources in `5.canceled`.
- Epic: card 82. Detail: `capture-free-epic-next-roadmap.md` §E4; the roadmap stages 87/89.

## Summary
Turn the proven capture-free engine into a drop-in Vanessa replacement: introspect ANY form, match the MCP
tool + Gherkin step surface agents expect, add the on-demand manager capabilities, and PROVE it all on a real
config beyond the single fixture. Change 5 (a second config) is the gate on the "100% replacement" claim.

## Changes (5)
1. **General form introspection — `get_form_analysis`-equivalent** (was card 87). Introspect ANY live form
   into a structured descriptor (element tree: names/types/captions/values/enabled/readonly + a Gherkin
   state), capture-free, spot-checked against the genuine manager as oracle. Feeds the action synthesizer
   (86) with element addressing. Independent of capture — a good parallel starter. **Inherits two card-97
   productization follow-ups that this descriptor unblocks:** (a) **automatic cross-region `groups` discovery**
   — card 97 #5 cross-region read works given a field's enclosing Group names (`_retarget_read_to_groups`); the
   descriptor's element tree supplies them so `assert_form_value`/`wait_for_form_value` need no `groups` arg;
   (b) **on-screen cell localization for `set_table_date_cell`** — the DATE grid cell is solved (protocol-activate
   + mouse calendar pick, `calendar_{month,day}_cell` geometry shipped) but a general MCP tool needs the cell's
   screen coords (calendar-button + popup origin); the descriptor (with element bounds, if derivable) or a
   screenshot-localization step is the missing piece.
2. **MCP tool-surface parity — state / window / results / infobase** (was card 89). qa-mcp exposes a subset;
   add session/run state (`get_state`-equiv), window/active-window data, infobase info, and test results to
   approach the vanessa-mcp surface. **2026-06-20: increment 1 SHIPPED + live-verified** — 4 new tools
   (`get_test_results`, `infobase_info`, `get_state`, `get_window_list` OS via xdotool); 44 tools / 309 tests.
   `get_window_list_testclient` ✅ SHIPPED 2026-06-20 (genuine-manager capture → decode → splice replay; 45
   tools / 315 tests). LEFT: only the active-window element tree (`ui_read_tree`, folds into change-1
   generalization). Evidence: `evidence/card98-toolsurface-parity-2026-06-20/findings.md` +
   `evidence/card98-windowlist-decode-2026-06-20/findings.md`.
3. **Searchable Gherkin step library + compatibility note** (was card 89). ✅ **SHIPPED 2026-06-20.** A
   discoverable step vocabulary (`search_for_steps` MCP tool #40, the `search_for_steps`-equiv) derived from the
   transpiler's `STEP_PATTERNS` (enriched with phrase/example/category/description) — the library IS the matcher,
   so it never drifts (a unit test pins every example to its kind). A vanessa-mcp→qa-mcp coverage note
   (`docs/vanessa-mcp-parity.md`: ✅ covered · 〜 partial · ❌ out-of-scope). A Vanessa-canonical sample
   `tools/protocol-research/qa-vanessa-style.feature` transpiles 100% (0 unmapped) + is runnable via
   `run_scenario`. 287 tests. Evidence: `docs/protocol-research/evidence/card98-step-library-2026-06-20/findings.md`.
4. **`agent_runtime` capabilities on demand** (was card 77 — a decision record). **✅ DONE 2026-06-20 — decision
   recorded.** The 11 manager-API members (file-dialog seeding Set/ClearFileDialogResult = medium; UI-log
   recording; perf counters; per-action timeout) are an accepted non-scope of protocol decoding, built only when
   a real scenario needs them; Connect/Disconnect are done; first build-out = SetFileDialogResult when a
   file-dialog test appears. The read/state side scenario authors reach for (get_state / get_test_results /
   infobase_info / window lists) shipped in change 2. Decision record: `docs/agent-runtime-decision.md`.
5. **🚩 GATE — validate capture-free synthesis on a 2nd config** (was card 94). Everything is proven on ONE
   fixture. Stand up a native client against another lab config (`/opt/1c-dev/{demo10413, redacted-third-party-config,
   demo_1_0_41_3}`), test read then write capture-free, and produce: a generality matrix (each shipped action
   ✅ generalizes / ⚠ needs a per-config capture / ❌ fixture-only) + a per-config onboarding recipe + an
   honest restatement of the capture-free claim. THIS is the lab-demo→product boundary.
   **2026-06-20: GATE CLOSED — CONFIG-AGNOSTIC OPEN ✅ SOLVED.** The last ⚠ row (the form OPEN was fixture-bound)
   is now ✅: `read_form_descriptor(open_link=…)` introspects ANY form on ANY config with NO fixture — render the
   value-read header with placeholder form GUIDs (`_splice_header_no_form`; the `cb 23 95` marker @48 precedes
   the form GUIDs @101/@151), skip fixture frames 11-17, retarget the navigate's MainFrame from a bare-desktop
   window-list. Live-proven on TWO configs: vanessa_client no-fixture (Контрагенты→79 el) + demo_1_0_41_3 БСП,
   never captured (Валюты→46 el). 325 tests. Evidence: `evidence/card98-config-agnostic-open-2026-06-20/findings.md`.
   LEFT on change 5: a navigated-RECORD value-read verify (lists have 0 `Group.EditField`).

## Notes / constraints
- Change 5 is the highest-value: the handshake may carry config metadata (infobase id/version) → a one-time
  per-config connect capture may be the onboarding cost; element addressing is by-NAME so likely generic.
- Mind W^X / exclusive IB access per config (memories ibsrv-odata-vs-httpservice, lab-infobase-access).
- Change 1 (introspection) is independent and needs no capture — start it in parallel.

## Plan for the new session (start here)
Read `capture-free-epic-next-roadmap.md` §E4 + `capture-free-epic-state.md`. Change 1 (introspection) can start
immediately; change 5 (2nd config) is the gating validation — do it once the action surface (cards 96/97) is
broad enough to be worth generalizing.

**Change 1 scoping (2026-06-19, offline, card-97 close-out):** FEASIBLE. The oracle (Vanessa
`get_form_analysis`) is a name→value Gherkin dump — `элемент формы с именем '<NAME>' стал равен "<VALUE>"` (+
`текст редактирования` for some) for EVERY element. The genuine `tm-v1-ro-batchQ3` value-read stream already
carries all field values (a form-analysis WAS run during that capture), so change 1 = **replay the form-analysis
query frames → parse the multi-field name→value dump → format the descriptor**, live-verified vs the oracle. A
prototype multi-field extractor pulled 41/46 fields (32 cleanly) from the capture; the **robust parser must handle
several encodings** the single-field parser (`extract_edit_field_value`) doesn't: strings/number/date ride the
`81 81 81 fa <len> <ascii-display>` shape (done), but **checkboxes are a UTF-16 bool** ("Да"/"Нет", `…\x97…`
marker), **decorations** are a label kind (not EditField), and **reference fields** (Контрагент) have their own
shape; also number has value ("120,5") vs edit-text ("120,50"). So this is a substantial multi-type parser +
query-replay + descriptor formatter — a dedicated session, not a quick increment. Once built, it directly
supplies (a) the auto cross-region `groups` (the dump's element paths carry the Group chain) and is the home for
(b) on-screen cell localization for `set_table_date_cell`.

**Change 1 progress (2026-06-19): increment 1 SHIPPED (offline), increment 2 SCOPED (lab).** Increment 1 =
`extract_form_field_values` (responses.py) — decodes the full-form name→value descriptor from the value-read
stream: 43/46 fixture fields, 43/43 value-match vs the Vanessa oracle (the 3 gaps are form decorations, a Label
kind, not EditField values). Handles the marker zoo (fa edit-text; e0 4b 53 with 9a single-byte / 97 UTF-16
checkbox / 8b short-number / 81 empty) over ASCII + UTF-16LE (Cyrillic) names, preferring the canonical «стал
равен» value. Also fixed a latent bug: the value length is a SINGLE byte (0..255), not LEB128 (a 143-char value
rides as `fa 8f 50…`) — `extract_edit_field_value` over-ran for 128..255-char values. 279 tests. Evidence:
`docs/protocol-research/evidence/card98-form-introspection-2026-06-19/findings.md` (commit 4d587b3). **Increment 2
SHIPPED + LIVE-VERIFIED:** `read_form_descriptor` MCP tool — opens the form then reads EVERY element on one
connection by looping the proven value-read (218-221) retargeted per field (`_retarget_read_to_groups`; field
list + Group chains from `_enumerate_capture_fields`), decodes with `extract_form_field_values`, returns
`{fields, field_count, queried}` + a Gherkin state block. (The trimmed template can't `run_segment` the raw
sweep, and a raw full-capture replay desyncs — hence the loop.) Live: **41 fields, 40/41 value-match vs the
Vanessa oracle** (the 1 diff = a live-state difference, PF_SELECTED_ROW_MARKER, the correct current value). Gaps:
3 decorations (Label kind) + 2 Cyrillic-named reference fields (ASCII-only enumerator) — refinements. 282 tests.
**⇒ Change 1 (form introspection) is functionally COMPLETE.** The remaining card-1 refinements (Cyrillic-field
enumeration; generalizing the sweep to ANY form, which then supplies auto cross-region `groups` + houses on-screen
date-cell localization) fold into the broader change-1/2 generalization.

**Change 1 Cyrillic-field refinement (2026-06-20): DONE + live-verified.** `read_form_descriptor` now sweeps
Cyrillic-named fields (UTF-16 `0x97` query-path envelope) — **live 43 fields / 43 queried, 42/43 vs the oracle**
(was 41/41), `Контрагент`/`ПолеСоСпискомВыбораСтрока` decoded (both `""`) ⇒ **43/46** (the 3 decorations are the
Label-kind ceiling). 4 reusable element_ref helpers + dual-encoding enumeration/retarget; 296 tests. Evidence:
`evidence/card98-cyrillic-fields-2026-06-20/findings.md`. LEFT on change 1: only the ANY-form generalization
(blocker characterized) + the Label decorations.

## Merged from (audit trail)
- card 87 (form introspection) → change 1
- card 89 (MCP tool-surface parity + step library) → changes 2, 3
- card 77 (agent_runtime parity decision) → change 4
- card 94 (cross-config generalization gate) → change 5

## Related
- Epic 82. `src/qa_mcp/mcp_server.py`, `src/qa_mcp/scenario/gherkin.py`. Oracle: genuine manager (card 81).

## Log
- 2026-06-17 card created by board triage — consolidates 87/89/77/94 (5-item change set; change 5 = the gate).
- 2026-06-18 change 5 (the gate) — substantial progress on 2 real configs (redacted-third-party-config, demo_1_0_41_3):
  READ generalizes universally to both (no config capture). Found + FIXED a real engine generalization gap:
  element paths are UTF-16LE for Cyrillic field names (the deriver was ASCII-only → found nothing on real
  configs); `editfields_in` + UTF-16 `read_field_value_near`/`derive_write_template`; 42 tests; fixture still
  commits (no regression). WRITE on a foreign config: engine establishes + the field ACCEPTS an arbitrary value
  (edit-text echo) but full COMMIT-persistence is NOT yet reproduced (focus-change commit fidelity on real
  grouped forms; third-party-config's busy home page crashes the full-stream replay). The honest claim today: read is
  universally capture-free; write sets the value by name on a foreign config after a one-time capture but
  committing reliably on real forms is OPEN. Evidence: `docs/protocol-research/evidence/card98-2ndconfig-
  {read,write}-2026-06-18/findings.md`. NEXT: focus-change commit fidelity; block-retarget write replay.
- 2026-06-18 change 5 — WRITE commit ROOT-CAUSED (deep dive). The replay sets a field's edit-text (SET echo)
  on any field incl. Cyrillic, but the commit (edit-text→attribute) only reproduces for FORM-attribute fields
  (the fixture's PF_*, which have OnChange), NOT for OBJECT-attribute fields (Объект.* on catalog/document
  forms = the bulk of business data entry). Decisive: demo Валюты.Наименование reads back EMPTY after replay;
  Записать on replay did NOT persist the value to the demo DB; fixture commits (control). Fix (a) keyboard
  RULED OUT — Vanessa keyboard input is the VanessaExt external component doing OS-level input inside the
  client (the typed value is in NO protocol frame), so it can't be replayed via capture. Object-attribute
  commit needs genuine client-side edit-mode/keystrokes the protocol doesn't carry; a full object-form write
  would need a HYBRID (protocol nav + real OS keystrokes), which re-introduces OS-driving. Bottom line: the
  "100% replacement" claim holds for read/introspection + form-attribute write; object-form data entry is the
  open boundary of the protocol-replay engine. Tools added: demo_{write_trace,write_poll,save}_probe.py,
  qa-demo-{write-save,emulate}.feature.
- 2026-06-18 change 5 — object-form write SOLVED via XTEST HYBRID (DB-verified). First confirmed AT-SPI is no
  shortcut (1C exposes 0 accessible elements; control GTK app registers fine — atspi_dump.py/atspi_control.py/
  run_atspi_probe.sh). Then proved the hybrid end-to-end on demo Справочник.Валюты.Наименование (object attr):
  PROTOCOL open form + focus field by name → xdotool type OS-keystrokes into the focused client window →
  xdotool Tab blur → the OBJECT ATTRIBUTE commits (get_form_analysis: «Наименование стал равен "ZZHYBRID99"»,
  which SetEditText could NOT do) → Записать → the row PERSISTS in the DB (Валюты list). This is Vanessa's
  mechanism (focus by API + OS input via VanessaExt) without Vanessa. Prototype used the manager as protocol
  driver; each step has an our-engine equivalent (nav-link replay / activate-field / click_command). Evidence:
  docs/protocol-research/evidence/card98-xtest-hybrid-2026-06-18/ (+ screenshots). NEXT: confirm native replay
  /TESTCLIENT renders the form, then a write_form_value_xtest(field,value) path (Vanessa-free). This closes the
  object-form write surface for the "100% test-manager replacement" claim. Tools: qa-demo-focus.feature,
  run_demo_xtest_hybrid.sh.
- 2026-06-18 change 5 — VANESSA-FREE hybrid proven END-TO-END. Step 1: our native /TESTCLIENT (1cv8 thick; thin
  1cv8c refuses demo on config signature; default HOME for license) under Xvfb :89 + matchbox — our engine
  replayed open+focus frames [0..17], the form RENDERED with Наименование focused (screenshot). Step 2:
  xdotool type "ZZXTEST88" + Tab → object attribute commits (tab '*') → xdotool Записать (Ctrl+S works) →
  DB-PERSISTED (title "ZZXTEST88 (Валюта)" + "Создание: ZZXTEST88" notification). So our engine (protocol
  open/focus/render by name) + xdotool (OS input) writes a real OBJECT-attribute field on a real config and
  saves to DB, NO Vanessa. The object-form write surface is CLOSED for "100% test-manager replacement". Tools:
  demo_render_probe.py/run_demo_render_test.sh, demo_xtest_write_probe.py/run_demo_xtest_write.sh. Evidence +
  screenshots (01..05): docs/protocol-research/evidence/card98-xtest-hybrid-2026-06-18/. Polish-LEFT: clean
  programmatic our-engine read-back (capture read frame mgr[28] is out-of-context; re-open list + read).
- 2026-06-18 change 5 — PRODUCTIZED write_form_value_xtest (engine path + MCP tool). New module
  src/qa_mcp/protocol/native_xtest.py: write_form_value_xtest(capture, value, field, *, host, port, display,
  blur=True, save=False) — one connection, inline: replay open+focus [0..17] (protocol, field by name) →
  xdotool type (Unicode/Cyrillic) → Tab (commit) → opt Ctrl+S (Записать→DB) → read-back via the IN-ORDER read
  sequence [25..28], committed = value-in-readback. MCP tool write_form_value_xtest (pairs with
  run_native_test_client(display=…)/capture_screenshot/stop_test_client). 3 unit tests (239 suite, no
  regression). Live-verified Cyrillic ("ПродуктТест5" committed+saved: title, Код auto "000000010", "Создание"
  notification). run_xtest_write_test.sh handles the apache@1936 demo-session contention (stop apache for the
  boot), 1cv8 thick + default HOME + matchbox. Object-form write surface CLOSED + productized.
- 2026-06-19 change 1 (form introspection) SHIPPED — `read_form_descriptor` (MCP #39), the capture-free
  get_form_analysis equivalent: opens the form + reads every element on one connection (looping the proven
  value-read retargeted per field; field list from `_enumerate_capture_fields`), decodes via
  `extract_form_field_values` (single-byte length fix). Live: 41 fields, 40/41 vs the Vanessa oracle. 282 tests.
- 2026-06-20 change 3 (step library) SHIPPED — `search_for_steps` (MCP #40) over the enriched STEP_PATTERNS
  (no-drift); `docs/vanessa-mcp-parity.md` coverage note; Vanessa-style feature transpiles 100%. 287 tests.
- 2026-06-20 change-1 GENERALIZATION characterized (not built). `read_form_descriptor` already generalizes under
  the one-time per-form capture model (`capture_dir`). NO-CAPTURE live enumeration: open enumerates 0 elements;
  the tree is one descriptor re-render (genuine send ~40, 45 elements); single-frame raw replay = ACK (stateful
  seq); a generated tm-v1-form-analysis template DESYNCS (the gen tool models only bootstrap/open/value-read
  dynamic fields — the descriptor re-render frames carry unmodeled dynamics → broken pipe). Blocker: model the
  descriptor frames' dynamic fields. Evidence: `evidence/card98-generalization-2026-06-20/findings.md`. Also open:
  Cyrillic-named reference fields (UTF-16 enumeration + query-path retarget).
- 2026-06-20 change 1 navigated value-read + change 5 generality matrix. (a) `_retarget_read_to_groups` gained a
  `form_ref` S.F override so the value-read targets a NAVIGATED form's field; `read_form_descriptor(open_link=…)`
  now value-reads the navigated form's EditFields too (returns {opened, elements, fields}). Live: Контрагенты → 79
  elements, 0 field-values (correct — a LIST has no Group.EditField form-fields; its dynlist columns are a
  Table[…].EditField surface). Mechanism integrated + regression-tested; reading actual VALUES off a navigated form
  is UNVERIFIED end-to-end (needs a navigable RECORD form — vanessa_client lists have 0 form-fields; record cards
  open by command/row-drill, not a bare nav-link). (b) Change-5 matrix: the session-level splice techniques
  (navigate / resolve / descriptor / window-list — no fixture paths) GENERALIZE to a 2nd config; the FIXTURE-specific
  OPEN frames (11-17) are the boundary — `read_form_descriptor`/`open_link` bootstrap by opening the fixture, so a
  config with NO fixture needs a CONFIG-AGNOSTIC open (bootstrap→desktop→navigate without the fixture open; blocked
  on rendering a session header without a form's managed_form_guid). That + a record-form value verify close change
  5. Evidence: `evidence/card98-navigated-valueread-and-gate-2026-06-20/findings.md`.
- 2026-06-20 change 1 OPEN-ANY-FORM wrapper — SOLVED. `read_form_descriptor(open_link="e1cib/list/Справочник.X")`
  opens ANY form by nav-link + introspects it (full element tree), NO per-form capture. The last blocker (the
  navigated form's ManagedForm F) is solved by a decoded RESOLVE query (sweep's first query, mgr#2: body
  `9a 34 SecondaryFrame[S]` S-only + opcode `e1 81`, vs the descriptor's `e1 82`) — its response returns the form's
  `SecondaryFrame[S].ManagedForm[F]`. Wrapper (`_open_form_by_link`): `splice_navigate` (2-frame navigate, nav-link
  retargeted → opens the form) → `get_window_list_testclient` (the new window's S, by caption) → `splice_resolve_form_query`
  (S → S.F, match the TARGET's S not the first) → `splice_descriptor_query` (explicit S.F) → `extract_descriptor_elements`
  (the full tree: EditField/Button/Table/Group/…, ASCII + UTF-16). Live: Контрагенты opened → **79 elements**
  (Table[Список] + command buttons + view-mode group) — a DIFFERENT form than the fixture, capture-free. SCOPE:
  structure (ui_read_tree) done; VALUES of a navigated form are a follow-up (value-read renders the fixture region).
  45 tools, 323 tests. Probe `open_any_form_probe.py` / `read_form_descriptor_openlink_verify.py`; evidence
  `evidence/card98-open-any-form-solved-2026-06-20/findings.md` (supersedes `…open-any-form-2026-06-20`).
- 2026-06-20 change 1 GENERALIZATION SOLVED — live form-field enumeration with NO per-form capture
  (`read_form_descriptor(enumerate_live=True)`). The earlier "blocked" characterization
  (`card98-generalization-2026-06-20`) is superseded: the window-list SPLICE technique unlocks it. Captured a
  genuine `get_form_analysis` via the manager; the DESCRIPTOR query (chunk#44) shares the `…cb 23 95` header and
  embeds the form path `9a 66 SecondaryFrame[S].ManagedForm[F]`; its ≈71 KB response is the element tree
  (`(Group[g].)+EditField[name]` paths, ASCII + UTF-16 — 46 EditFields + Buttons/Tables/Groups). REPLAY:
  `splice_descriptor_query` grafts the descriptor body (form path retargeted to the LIVE S/F) onto a live
  value-read header → the client returns the live descriptor (raw replay rejected «Сеанс завершен»);
  `extract_descriptor_fields` parses it → `[(name, groups)]`, the live `_enumerate_capture_fields`.
  `_enumerate_live_fields` + `read_form_descriptor(enumerate_live=True)`: **live 46 fields / 46 queried** (vs the
  capture path's 43; found PF_REPORT/PF_SELECTED_ROWS/PF_TABLE_SNAPSHOT the sweep lacked), 42/43 vs the oracle,
  Cyrillic decoded. The field list is now capture-free; the form OPEN stays form-specific (open via existing
  machinery, then introspect). 45 tools, 319 tests. Evidence: `evidence/card98-generalization-solved-2026-06-20/findings.md`.
- 2026-06-20 change 2 — `get_window_list_testclient` SHIPPED (MCP #45, the 1C-internal window list). Captured the
  genuine Vanessa `get_window_list_testclient` call (booted the genuine manager on Xvfb :77 / MCP :9874, connected
  a client + opened tabs, tcpdump'd the call → 4 windows). DECODED the response: a sequence of window records
  `<Kind>[<guid>] 82 <fa|f7> <len> <caption> …` (Kind ∈ SecondaryFrame/MainFrame/HomePage; caption fa=ASCII /
  f7=UTF-16) — parser `extract_testclient_windows` (deduped, matches the 4-window oracle). REPLAY: a raw replay is
  rejected («Сеанс работы завершен» — the client validates the session GUID), SOLVED by SPLICING the window-list
  command body onto a live-rendered value-read header (shared `…cb 23 95` header; the command body is
  session-independent — its nonce is echoed, not validated) → `splice_window_list_queries` +
  `WINDOW_LIST_QUERY_BODIES` (embedded, no capture dependency). Productized `get_window_list_testclient`
  (`_read_testclient_windows`): open form → live header → splice → parse. Live: 3 windows (fixture form + desktop
  + home) → PASS. 45 tools, 315 tests. Evidence: `evidence/card98-windowlist-decode-2026-06-20/findings.md`.
- 2026-06-20 change 2 remainder — window-enumeration INVESTIGATION (decisive lab finding, no code). Boot +
  `get_window_list` (3 OS windows) → `open_list` (Товары, accepted) → `get_window_list` again = STILL 3, no new
  window; the screenshot shows the list opened as an **MDI tab inside the main window** («Товары» tab). ⇒ 1C
  opens forms/lists/cards as MDI tabs (each a `SecondaryFrame`) inside ONE X11 window, so the OS-level
  `get_window_list` lists the app window, NOT the open 1C forms — `get_window_list_testclient` (the 1C-internal
  window/tab list) is a **genuine, distinct** capability, not redundant with the OS list. Build path characterized:
  primitive `_all_secondary_frames` in hand; missing = a multi-tab session capture + the frame that enumerates the
  SecondaryFrame set (the existing capture has only 1 SF). `ui_read_tree` folds into the change-1 ANY-form
  generalization. Probe `testclient_windows_probe.py`; evidence `evidence/card98-window-enumeration-2026-06-20/findings.md`.
- 2026-06-20 change 2 (tool-surface parity) increment 1 SHIPPED + live-verified. 4 new capture-free MCP tools
  close the named state/window/results/infobase gaps: `get_test_results` (aggregates the scenarios run this
  server session — a `_RESULTS_LOG` fed by `_run` + the write runner via `_record_result`), `infobase_info`
  (infobase/connection metadata from the `.ai1c` profile, password-redacted, + live listening), `get_state`
  (the `get_state`-equiv: connection + run-session + infobase identity + engine defaults), and `get_window_list`
  (OS window enumeration on the client display via xdotool — new `protocol/windows.py`; id/title/geometry).
  44 MCP tools, 309 tests. Live (fresh /TESTCLIENT): infobase_info/get_state listening=true; get_test_results
  after a real `read_active_window` run = 1 passed/1 step; get_window_list enumerated the real client window
  («Демонстрационное приложение» + geometry). LEFT: `get_window_list_testclient` (protocol-level SecondaryFrame
  set — decode follow-up) + `ui_read_tree` (active-window element tree — folds into change-1 generalization).
  Parity doc updated. Evidence: `evidence/card98-toolsurface-parity-2026-06-20/findings.md`.
- 2026-06-20 change-1 CYRILLIC FIELDS SHIPPED + live-verified. `read_form_descriptor` now sweeps Cyrillic-named
  fields: element paths with a Cyrillic group/leaf ride the `0x97 <char-count> <utf-16le>` envelope (vs ASCII
  `0x9a <byte-len> <latin1>`) — the genuine sweep queried `Контрагент`/`ПолеСоСпискомВыбораСтрока` (in
  `Group[Группа1]`, capture frames 296-303) but `_enumerate_capture_fields` (ASCII regex) + `_retarget_read_to_groups`
  (latin1 path build) missed them. Added 4 reusable element_ref helpers (`path_is_latin1`,
  `encode_element_path_block`, `extract_element_paths_utf16`, `retarget_element_path_reencode`); enumeration now
  finds both encodings; retarget dispatches ASCII→0x9a / non-latin1→0x97. De-risked offline (the retargeted UTF-16
  frame is byte-length-identical to the genuine Cyrillic read frame; encode round-trips the on-wire block exactly;
  the only skeleton diffs are the seq counter + per-read GUID the ASCII path already reuses). The response parser
  needed NO change (already decodes UTF-16 leaves + the `e0 4b 53 81` empty value). **Live: 43 fields / 43 queried,
  42/43 value-match vs the Vanessa oracle** (was 41/41; the 1 diff = live-state PF_SELECTED_ROW_MARKER); both
  Cyrillic fields decoded=True, value `""` matching the oracle ⇒ **43/46** (the 3 `PF_DECORATION_LABEL*` are the
  Label-kind ceiling). 296 tests. Evidence: `evidence/card98-cyrillic-fields-2026-06-20/findings.md`.
- 2026-06-20 change 5 (the 🚩 GATE) — CONFIG-AGNOSTIC OPEN SOLVED + PRODUCTIZED + 2nd-config-verified. The gate's
  last blocker (`read_form_descriptor`/`open_link` bootstrapped by opening the FIXTURE, so a config with no
  fixture couldn't be introspected) is gone. KEY: the splice header is `frame218[:cb-23-95]` and the `cb 23 95`
  marker sits at offset **48**, while the form-specific `secondary_frame_guid` (@101) + `managed_form_guid` (@151)
  are BOTH AFTER the marker — so the header [0:51] needs only `ack_guid` (@2, from bootstrap) + `sequence` (@19).
  Render frame 218 with PLACEHOLDER form GUIDs and slice the header (`_splice_header_no_form`) → a splice header
  byte-identical to the fixture-rendered one, with NO form open (offline-proven). The `open_link` path now SKIPS
  fixture frames 11-17 (navigates from the bare desktop), window-lists the bare desktop for the LIVE MainFrame,
  and retargets the navigate onto it (`splice_navigate(main_frame=…)` + `NAVIGATE_GENUINE_MAINFRAME`); it also
  points the session at the navigated form's S.F so a record form's value-read renders. **Live-proven on TWO
  configs:** vanessa_client WITHOUT opening the fixture (Контрагенты → 79 elements) AND demo_1_0_41_3 (a real
  1C:БСП base, NEVER captured) → Валюты → 46 elements — the SAME productized `read_form_descriptor(open_link=…)`.
  This closes the gate: structure introspection of any form generalizes to any real config. 45 tools, 325 tests
  (+2: header byte-identity, MainFrame retarget). Probes `config_agnostic_open_probe.py` /
  `config_agnostic_2nd_config_probe.py`. Evidence: `evidence/card98-config-agnostic-open-2026-06-20/findings.md`.
  LEFT: navigated-RECORD value-read verify (a record form by row-drill/record-link — lists have 0 form-fields).
- 2026-06-20 follow-up — DYNLIST positioning: the gap is the INTERACTION-ready open (full-sequence replay), not
  the read or the sequence. Decoded the genuine list-form command order: navigate (the `f7` nav-link) → activate
  [27] (`88 81 81 e0 4b 55`, no path) → render/data queries [29] (`e1 82 82 84` S-only) / [31] (`e1 82 82 86`
  S.F + references table «Список» — the dynlist DATA query) → position [33-39] (`88 82 81 20 20 20` pairs) → read
  [41]. Sequence counters increment +1 per frame. FOUR reconstruction attempts FAILED on the populated Товары
  list: (1) splice position+read one seq; (2) settle + table-activate; (3) INCREMENTING sequences (`_set_seq`);
  (4) replay activate [27] + render [29]/[31] (retargeted) + position + read, sequence-bumped. ⇒ piecemeal splice
  does NOT reproduce the genuine state — `_open_form_by_link` inserts window-list/resolve/descriptor queries the
  genuine INTERACTION flow doesn't, so the active-form/focus state differs and positioning never takes. The dynlist
  read needs a FAITHFUL FULL-SEQUENCE replay (navigate→activate→render→position→read via the card-80 full-stream
  replay + GuidRebinder), its own session. READ command + value parser verified («Обувь»); read_table_cell (form
  tables) unaffected + shipped. Probes dynlist_{seq_position,interaction_open}_probe.py. Evidence updated.
- 2026-06-20 follow-up — DYNLIST read DECODED on a REAL catalog list form — SAME command, value verified («Обувь»).
  Captured «Я открываю основную форму списка справочника "Товары"» + «перехожу к первой строке» + read (Товары:
  named columns + data) — the genuine read SUCCEEDED. Command [41] = `…ManagedForm[F].Table[Список] 88 81 81 e0 4b
  55 eb 53 97 0c Наименование …` — BYTE-IDENTICAL to `splice_table_cell_read(groups=[],"Список","Наименование")`;
  response [42] decodes via `extract_table_cell_value` to «Обувь» (first row). ⇒ the dynlist read is the SAME
  `e0 4b 55` mechanism as the form-table read (the prior "distinct surface" was WRONG). The gap is FORM STATE: a
  form table has row 1 current on open; a dynlist must be POSITIONED first, and positioning is a TABLE-ACTION (the
  `88 82 81` family — like the shipped row-ops, full-stream replay, NOT a splice; a preceding `88 81 81 e0 4b 55`
  activate [27]). So `read_list_column` returns None until the current row is positioned via that replay. READ +
  parser are done + value-verified; the bounded next step is positioning the dynlist current row as a table-action.
  Evidence updated in `evidence/card98-tableread-decode-2026-06-20/findings.md`. Capture genuine-card98-listform-read;
  feature qa-card98-capture-listform-read.feature.
- 2026-06-20 follow-up — DYNLIST current-row positioning DECODED; read-by-name does NOT reproduce (honest
  boundary). A FORM table has row 1 current on open (`read_table_cell` verified); a DYNLIST does not. Captured the
  fixture dynlist `ДенамическийСписокИерархия` (over Catalog.Товары) with «перехожу к первой строке» + the read →
  decoded the row-position commands (table-level `88 82 81 20 20 20` 2-frame pairs + an `88 82 81 e1` variant,
  `genuine-card98-dynlist-read` [33]/[35]/[37]/[39]). **But the genuine read FAILED** (`ПолучитьТекстЯчейки … В
  элементе управления отсутствует указанное значение` — the fixture dynlist's auto-generated columns aren't
  addressable by name even for Vanessa). Splicing the position pairs + the read yields NO value on every dynlist
  tried — demo Валюты (possibly empty) AND vanessa_client `Справочник.Товары` (definitely populated, named columns).
  ⇒ the `e0 4b 55` table-cell read is a FORM-TABLE mechanism; a dynlist column read is a DISTINCT surface (Vanessa's
  dynlist `ПолучитьТекстЯчейки`) not yet reproduced capture-free. `read_table_cell` (form tables) is the verified
  deliverable; `read_list_column` returns None pending that mechanism. Evidence updated in
  `evidence/card98-tableread-decode-2026-06-20/findings.md`.
- 2026-06-20 follow-up — `read_table_cell` MCP tool SHIPPED + live-verified (form tables). `extract_table_cell_value`
  decodes the response value (the `81 81 81 e0 4b 53` envelope after the Table path — extract_form_field_values'
  EditField anchor misses it). MCP `read_table_cell(table,column,open_link?)` + `read_list_column(column,open_link)`
  (#46/#47): open fixture/any form, auto-discover the table's groups (`_table_groups`), splice + decode. **46 MCP
  tools, 330 tests.** Live (fixture, 3 default rows, row 1 current): PF_TABLE_TEXT="PF_ROW_001_TEXT",
  PF_TABLE_NUMBER="1,10", PF_TABLE_MARKER="PF_ROW_001". A FORM table has row 1 current on open → reads the value;
  a DYNLIST opened by nav-link has no active current row yet (value None — `read_list_column` open follow-up:
  row-select/activate or read-after-load). Evidence: `evidence/card98-tableread-decode-2026-06-20/findings.md`.
- 2026-06-20 follow-up — TABLE-CELL READ command CAPTURED + DECODED (genuine manager). Booted the genuine Vanessa
  manager, ran a feature (connect + open fixture + add row + write `CELLREAD7` into PF_TABLE_TEXT + commit + READ
  the cell by name «я запоминаю значение поля с именем …»), tcpdump'd it (client 48001, mgr 35958) →
  `genuine-card98-tableread`. DECODED: the read COMMAND = `…Table[T] 88 81 81 e0 4b 55 eb 53 <column-name block>
  <pad> <tail>` (a TABLE command addressing the table + column NAME, the `e0 4b 55` read action — NOT a
  `Table[T].EditField[col]` path-leaf, which is why the value-read retarget failed); the RESPONSE carries the cell
  value in the canonical `e0 4b 53 9a <len> <value>` envelope (extract_form_field_values already decodes it — no
  new parser). Built `splice_table_cell_read` (dual-encoding ASCII/Cyrillic; +1 test → 327). Live replay on the
  demo Валюты dynlist: the command RESOLVES (path/opcode round-trip) but returns no value — a dynlist freshly
  opened by nav-link has no active/loaded CURRENT ROW (the genuine read a form table with the just-added row under
  the cursor). ⇒ decode + splice correct; end-to-end value needs a current row established first (row-select, or
  read after load), then the `read_table_cell`/`read_list_column` tool (also closes the non-empty navigated
  value-read). Evidence: `evidence/card98-tableread-decode-2026-06-20/findings.md`.
- 2026-06-20 follow-up — dynlist-column read: STRUCTURE done, VALUE needs a capture. A list's columns are
  enumerated from the descriptor (`Table[Список]` + `EditField[col]`, correctly excluded from form-field VALUES).
  Reading column VALUES via the value-read retargeted to `Table[Список].EditField[col]` FAILS: the query resolves
  the column (per-column responses) but returns no `e0 4b 53` value envelope — a dynlist cell is per-row data, not
  a single form attribute. ⇒ reading dynlist cells needs Vanessa's TABLE-read command (a genuine-manager capture +
  decode, its own session), then a `read_table_cell`/`read_list_column` tool. This also unblocks the non-empty
  navigated value-read (a list row's data is populated + gives a record ref). General `set_table_date_cell`
  unchanged: needs on-screen cell localization (element bounds). Probe `dynlist_column_read_probe.py`; evidence
  `evidence/card98-dynlist-column-read-2026-06-20/findings.md`.
- 2026-06-20 change 4 — `agent_runtime` DECISION RECORD finalized (`docs/agent-runtime-decision.md`). The 11
  manager-API members (Connect/Disconnect done; UI-log recording ×5, perf-counter reset, per-action timeout,
  Set/ClearFileDialogResult) are an accepted non-scope of protocol decoding + a deferred scope of the Vanessa
  replacement, built on demand (first = SetFileDialogResult for file-dialog tests). The read/state side
  (get_state / get_test_results / infobase_info / get_window_list[_testclient] / launch+stop lifecycle) already
  shipped in change 2. Change 4 = DONE (decision, no code). Card 77's per-member table is preserved in the doc.
- 2026-06-20 change 5 — navigated RECORD value-read: mechanism built + reaches a real 2nd-config record. `e1cib/
  data/Справочник.Валюты` on the demo opens a real catalog RECORD form (`Валюта (создание)`, 4 object-attribute
  EditFields). Root-caused `field_count=0`: a record's fields sit DIRECTLY under ManagedForm (no Group), and
  `extract_descriptor_fields` required `(Group…)+`; added zero-group enumeration (`ManagedForm[guid].EditField`,
  columns still excluded; +1 test = 326). The navigated value-read now reaches the form (per-field responses), but
  the create form's fields are EMPTY (no value envelope) → a non-empty read needs a POPULATED record (a ref /
  row-drill — the dynlist-column read supplies it). Also added a newest-window open fallback to `_open_form_by_link`
  (opens custom-caption forms like the fixture, whose caption is a synonym). Finding: a DataProcessor form opened by
  nav-link returns a command-bar-only descriptor (body absent), so the fixture is not a navigated-value vehicle — a
  catalog record form is. Evidence: `evidence/card98-navigated-record-valueread-2026-06-20/findings.md`.
- 2026-06-20 dynlist read follow-ups (handoff items 1+2) — NESTED rows + go-to-row BY VALUE, both SOLVED +
  PRODUCTIZED + live-verified, no Vanessa. (1) **Nested rows — `read_list_grid(flat=True)`.** `set_list_view`
  could NOT compose (it replays the FIXTURE form, never opens the target list; a view-switch splice onto a live
  dynlist doesn't take). Captured a genuine FLAT-view next-row sequence on Товары (`genuine-card98-nextrow-flat`:
  open → click «Список» = the standard catalog-list-form `ФормаСписок` command — recon caught that it's `Форма<Mode>`
  not `<dynlist><Mode>` — → first row → read → next-row ×2). The view-switch lands BEFORE the first read, so
  `read_list_grid_replay`'s cold full-replay already flattens — ZERO engine change; the capture drops in. Live
  (cold, max_rows=12): 12 NESTED rows (Bosch1234/Sony К3456P/Veko*/Босоножки/Ботинки/…, all in subgroups), codes
  all vs OData — invisible in the hierarchical baseline (4 folders). (2) **Go-to-row BY VALUE —
  `read_list_row(where={col: value})`.** Captured a genuine DYNLIST «перехожу к строке» (`genuine-card98-rowbyvalue`:
  Наименование=Сапоги/Туфли → read Код); decode-by-diff confirms the command is `…c0 4b 53 <WHERE col> eb 53
  <match value>` — the SAME shape `row_select_from_read_frame` decoded from the FORM table (so the byte structure
  was right; the splice failed only because a dynlist needs the full-sequence replay). New
  `read_list_row_by_value_replay` replays the genuine stream cold, match value retargeted; live (cold):
  Наименование=Молоко→Код 000000026 (= captured length) AND Наименование=Кроссовки→000000024 (≠ length → value
  resize tolerated), both vs OData. 340 tests (+4). Evidence:
  `evidence/card98-dynlist-nested-rowbyvalue-2026-06-20/findings.md`.
- 2026-06-20 `$opsx-pub` — card CLOSED → `4.done`. Docs updated (README dynlist line: flat/nested + row-by-value;
  handoff DO-NEXT marks items 1+2 done). Verified: `git diff --check` clean, `openspec validate --all` ✓, 340
  tests pass. Scoped commit + push to `origin/main`. Remaining deeper follow-ups (populated navigated-record
  value-read; general `set_table_date_cell`) recorded under Next as a possible fresh card — not blockers.

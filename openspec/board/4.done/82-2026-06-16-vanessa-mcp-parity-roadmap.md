# 82. ROADMAP — native qa-mcp as a 100% Vanessa Automation replacement

## Status
4.done

## Order Index
82

## Owner
unassigned

## OpenSpec Stage
epic

## Result — epic CLOSED 2026-06-20 (the honest "100% Vanessa replacement" restatement)

All stage cards are delivered: **83/84/85/86/90** (4.done) and the three consolidated forward stories
**96/97/98** (all 4.done as of 2026-06-20). **49 MCP tools, 342 tests, no Vanessa.** The capture-template-bound
gap of the original analysis is closed: the engine drives ARBITRARY real configs.

**What qa-mcp does capture-free across configs (no Vanessa, no per-form hand-authored capture):**
- **Session bootstrap** — one platform-version handshake capture, config/server/OS-independent.
- **Read / introspection** — `read_form_descriptor(open_link=…)` opens + introspects ANY form on ANY config
  with NO fixture (config-agnostic open): element tree + name→value descriptor + Gherkin state, ASCII + Cyrillic;
  field / spreadsheet / form-table reads; dynamic-list reads (column · row · whole grid · NESTED via `flat=True`
  · row BY VALUE via `where=`); `assert_form_value` / `wait_for_form_value`; `read_user_messages`; and the
  state / results / infobase / window-list surface.
- **Actions** — `click_command` (any command, capture-free synthesis 86a–e) · checkbox / choice / radio · page
  switch · table-cell + row ops · dynlist search / view-mode / advanced-filter · reports · dialogs
  (`answer_dialog`) · list / menu / reference selection · object navigation (`open_card` / `close_window` /
  `activate_window`) · string/number/date input + commit (form-attribute fields).
- **Parity** — 49 MCP tools, a searchable Gherkin step library (`search_for_steps`), a vanessa-mcp coverage note
  (`docs/vanessa-mcp-parity.md`), and `agent_runtime` as a decision record (built on demand).

**The honest boundary (an inherent 1C platform property, NOT a qa-mcp gap):** OBJECT-attribute data entry
(`Объект.*` on catalog/document forms) and RAW KEYBOARD keys are OS-level in 1C — Vanessa itself performs them
with the VanessaExt external component doing OS input INSIDE the client; the typed value/key is in NO
manager→client protocol frame. qa-mcp delivers them the SAME way Vanessa does (protocol open + focus-by-name →
`xdotool`/XTEST OS input: `write_form_value_xtest`, `send_keys`), DB-verified — Vanessa's mechanism WITHOUT
Vanessa, but it needs the client's X display, not just the protocol socket. Also: dynlist reads have a
cold-client boundary (one materialised read session per fresh client process — a 1C form-cache behavior).

**Optional deeper follow-ups (NOT blockers, could be a fresh card):** value-read of a POPULATED navigated record
(open an existing record by ref/row-drill, not the empty create-form); a general `set_table_date_cell`
(on-screen cell localization / element bounds).

## Source
- 2026-06-16: gap analysis after card 80 (Fork-2 value-write productized) + card 81 (genuine manager on
  Linux). This epic turns that analysis into an ordered set of stage cards (83-89).

## Summary
Goal: make qa-mcp a drop-in replacement for `vanessa-mcp` so AI agents test ARBITRARY real 1C configurations
through the native TestClient protocol with NO Vanessa Automation manager in the loop.

**Where we are (the hard protocol problems are SOLVED):**
- Capture-free session bootstrap (`synthesize_bootstrap`), live form READ with effect verification (card 79),
  and — new — live value-WRITE with COMMIT (card 80 Fork-2: `qa_mcp.protocol.native_write`). The thing once
  thought impossible (committing a typed value, no Vanessa) works + is productized + read-back verified.
- MCP server `qa_mcp.mcp_server` (FastMCP "qa-native-manager", stdio) exposes `transpile`/`run_scenario`/
  `run_step`. Scenario engine drives read + nav (open_list/select_row/open_card) + click + input.
- Genuine Vanessa manager also runs on Linux now (card 81) — useful as a reference oracle, not the product.

**The gap (why it is NOT yet a general replacement):** the scenario engine is CAPTURE-TEMPLATE-BOUND — every
read/click/write needs a genuine capture of that specific flow. Vanessa drives any form from its metadata/
live state via the platform `ТестируемоеПриложение` engine + a huge step library + screenshots + general
form-analysis + client lifecycle. qa-mcp reproduces the wire protocol for SPECIFIC captured flows only.

## Progress (2026-06-17) — state doc: `docs/protocol-research/capture-free-epic-state.md`

- **83/84/85/86/90 DONE** (4.done): write wired into runner+MCP; TestClient lifecycle; native screenshots;
  the ⭐ keystone capture-free action synthesis (86a–86e); and the fixture coverage for checkbox/choice/
  table-cell/page-field/open_list (90). **18 MCP tools live, no Vanessa, 223 tests.**
- **Board triage (2026-06-17):** the remaining forward stories were consolidated. The old per-theme stage
  cards 87/88/89 + the next-epic cards 91–95 (+ the agent_runtime decision 77) are folded into THREE
  5-change stories — **cards 96, 97, 98** — so the active backlog is this epic + those three.
- **Next:** card 96 (interaction breadth: dialogs/selection/navigation/keyboard/messages), then card 97
  (table-ops/reports/lists/waits), then card 98 (introspection + MCP parity + the 🚩 2nd-config GATE).

## Ordered stages

**DONE (4.done):**
- **83** Wire the commit-capable write (`native_write`) into the runner + MCP; generalize the template.
- **84** TestClient lifecycle — launch/connect/manage clients (profiles, ports, kinds).
- **85** Native screenshots tool (in-process, replacing external scrot).
- **86** ⭐ KEYSTONE — capture-free action synthesis (86a–86e): commands for arbitrary forms/elements,
  no per-flow capture.
- **90** Fixture coverage — checkbox/choice/table-cell/page-field/open_list, all live-verified.

**ACTIVE (1.backlog) — the consolidated forward stories (each 5 changes):**
- **96** Capture-free interaction breadth — dialogs, reference/value selection, object navigation, keyboard,
  user-messages. (folds old cards 91/92/93 + the 95 prerequisites)
- **97** Element-type & table/report/list completeness — table-row ops, number/date cells, reports,
  dynamic-list ops, waits/asserts. (folds the 95 remainder + 88 residue + 72 deferred)
- **98** Product boundary — general form introspection, MCP tool-surface + step-library parity,
  `agent_runtime` on demand, and the 🚩 2nd-config generalization GATE. (folds old cards 87/89/77/94)

Phasing: 96 = highest-frequency business actions (do first); 97 = the long tail; 98 = the lab→product
boundary, gated by change 98.5 (validate on a real config beyond the fixture).

## Acceptance
- ✅ All of 83-89 reach `4.done` — 83/84/85/86/90 done; 87/88/89 were consolidated into 96/97/98, all 4.done.
- ✅ **Definition of done — MET** (composed from per-leg verified evidence on `demo_1_0_41_3`, a real БСП config
  beyond the fixture, no Vanessa): **open + read + introspect** a never-captured form — `read_form_descriptor(
  open_link=…)` on demo Валюты → 46 elements, config-agnostic (card 98); **click/action** — capture-free
  `click_command` synthesis (86); **write a value that COMMITS + assert by read-back** — `write_form_value_xtest`
  on demo `Справочник.Валюты.Наименование`, DB-verified (committed + saved, e.g. ZZKBD51 / ПродуктТест5), the
  object-attribute commit pure protocol cannot reach. QUALIFICATION (honest): the object-attribute commit +
  raw keyboard go through the OS-input hybrid (protocol open + focus-by-name → XTEST), because 1C keyboard/
  object-edit is OS-level (VanessaExt) with no manager→client frame — this is how Vanessa works too, done
  WITHOUT Vanessa. Pure-protocol commit holds for FORM-attribute fields; READ/introspection/most actions are
  fully capture-free across configs.

## Related
- card 79 (native value-read effect), card 80 (Fork-2 value-write productized), card 81 (genuine manager on
  Linux), cards 71/72/77 (api-coverage / phase-3 / agent-runtime-parity — feed stage 86).
- `src/qa_mcp/mcp_server.py`, `src/qa_mcp/scenario/`, `src/qa_mcp/protocol/native_write.py`.

## Log
- 2026-06-16T00:00:00Z card created (roadmap from the post-card-80 gap analysis).
- 2026-06-17 board triage: 86 + 90 reached 4.done; the forward stories 87/88/89/91–95 (+ decision 77) were
  consolidated into three 5-change stories (cards 96/97/98). Stage list + progress updated above.
- 2026-06-20 EPIC CLOSED → `4.done`. The three forward stories all reached 4.done: 97 (table/report/list/waits),
  98 (introspection + tool/step parity + agent_runtime + the 🚩 config-agnostic-open GATE + dynlist nested/
  row-by-value reads), 96 (dialogs/selection/navigation/messages/keyboard via `send_keys`). 49 MCP tools, 342
  tests. Acceptance DoD MET on demo БСП (open+read+introspect+write-commit+read-back, no Vanessa) with the
  honest OS-input-hybrid boundary for object-write/keyboard (VanessaExt-equivalent, no protocol key frame).
  Result section above = the honest "100% Vanessa replacement" restatement. Close-out banner added to
  `docs/protocol-research/capture-free-epic-state.md`. `$opsx-pub`: scoped commit + push.

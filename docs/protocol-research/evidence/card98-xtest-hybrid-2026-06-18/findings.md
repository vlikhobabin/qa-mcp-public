# Card 98 — XTEST hybrid: capture-free WRITE into a real object-attribute field, COMMITTED + DB-persisted

**Date:** 2026-06-18. **Result:** the object-attribute write boundary (blocker #1) is **SOLVED via a hybrid** —
protocol for element addressing/focus + OS-level keystrokes (XTEST/`xdotool`) for the input. Proven end-to-end
on a real foreign config (`demo_1_0_41_3`, catalog `Справочник.Валюты`), committed at the form-data level AND
persisted to the database.

## Background (why a hybrid)

The pure protocol replay sets a field's edit-text (SET echo) but does NOT commit an OBJECT attribute
(`Объект.Наименование` on catalog/document forms) — the commit needs the field to be genuinely "user-edited",
which the programmatic SetEditText does not establish (see `card98-2ndconfig-write-2026-06-18/findings.md`).
AT-SPI is no shortcut (1C exposes no accessible elements). But the 1C client's X11 window IS OS-accessible, so
real keystrokes can be injected — exactly what Vanessa's `VanessaExt` component does (OS input on the shared
display). This validates doing the same WITHOUT Vanessa.

## The proven cycle (demo_1_0_41_3 · Справочник.Валюты · field Наименование)

1. **Protocol** — open the form + focus the field BY NAME: `e1cib/data/Справочник.Валюты` →
   activate window "Валюта (создание)" → activate field `Наименование`. Screenshot `01-*.png`: the form is
   rendered and `Наименование` is the focused (yellow) empty field.
2. **OS input** — `DISPLAY=:77 xdotool type "ZZHYBRID99"` (XTEST to the focused client window 4194666; 1C routes
   the keystrokes to its internally-focused control). Screenshot `02-*.png`: the field now shows `ZZHYBRID99`.
3. **Blur** — `xdotool key Tab` (move focus off the field → commit trigger).
4. **Verify commit (form data)** — `get_form_analysis`: `элемент формы с именем 'Наименование' стал равен
   "ZZHYBRID99"` — the ATTRIBUTE (not just edit-text) is committed. ← the exact thing the protocol SetEditText
   could NOT do.
5. **Save** — `Записать` (protocol command click) → window title changes from "Валюта (создание)" to
   **"ZZHYBRID99 (Валюта)"** (a new item shows "(создание)"; a saved one shows its name).
6. **Verify DB** — open `e1cib/list/Справочник.Валюты` (fresh DB read): the list contains **`ZZHYBRID99`** (1
   row) — the value is persisted in the database.

⇒ **Capture-free write into a real object-attribute field works** via protocol-addressing + OS-keystroke input.
This is Vanessa's mechanism (focus by automation API + OS input via the external component) reproduced WITHOUT
the Vanessa runtime — our engine for addressing, `xdotool` for the keystrokes.

## Honest status / scope of this prototype

- **Proven (the hard, uncertain part):** OS-level keystroke input into a 1C client's focused field, followed by
  a blur, COMMITS the object attribute and (after `Записать`) PERSISTS to the DB. This is the breakthrough — it
  removes the object-form write boundary.
- **Driver caveat:** this prototype used the genuine Vanessa **manager** as the protocol driver for the
  open/focus/`Записать` steps (fastest reliable renderer). Each of those is a protocol-level op with an
  our-engine equivalent: open = nav-link replay; focus = activate-field; `Записать` = `click_command`. So the
  full **Vanessa-free** hybrid is buildable from the existing engine + `xdotool`.
- **Remaining integration unknown:** whether OUR replay `/TESTCLIENT` renders the form window (so `xdotool` has
  a focused control to type into) the way the manager-launched client does. The genuine TestClient renders
  (screenshots prove it); the native replay client's rendering on form-open is the next thing to confirm when
  wiring the full hybrid.

## Tools / artifacts

- Feature: `tools/protocol-research/qa-demo-focus.feature` (connect + open + activate window + activate field).
- Flow (documented): `tools/protocol-research/run_demo_xtest_hybrid.sh` — boots the manager, runs open+focus,
  `xdotool type`+`Tab`, reads the committed attribute, `Записать`, and DB-checks the `Валюты` list.
- Screenshots: `01-form-open-field-focused.png`, `02-xdotool-typed-into-field.png`.
- AT-SPI experiment (why native introspection is no shortcut): `card98-2ndconfig-write-2026-06-18/findings.md`.

## Steps 1 + 2 DONE — Vanessa-free hybrid proven end-to-end (2026-06-18)

The hybrid was then wired to OUR engine (no Vanessa) and proven end-to-end on demo `Справочник.Валюты`:

**Step 1 — our replay `/TESTCLIENT` renders the form on a protocol open.** Booted a native `/TESTCLIENT`
(`1cv8` thick — the thin `1cv8c` refuses demo with "Цифровая подпись конфигурации неверна"; default `HOME` so
the license is found) under Xvfb :89 + matchbox. OUR engine replayed the demo capture's open+focus frames
`[0..17]` (connect → open `e1cib/data/Справочник.Валюты` → activate window → activate field `Наименование`)
with `GuidRebinder`, holding the connection. Screenshot `03-our-engine-renders-form.png`: the full
"Валюта (создание)" form is **rendered** with `Наименование` **focused** (cursor + highlight). ⇒ our
`/TESTCLIENT` renders + focuses by name, no Vanessa. Tools: `demo_render_probe.py`, `run_demo_render_test.sh`.

**Step 2 — `write_form_value_xtest` end-to-end, Vanessa-free + DB-persisted.** On the our-engine-opened+focused
form: `xdotool type "ZZXTEST88"` → `xdotool key Tab` (blur). Screenshot `04-our-engine-xdotool-committed.png`:
field = `ZZXTEST88`, the form tab shows **`Валюта (создание) *`** (the `*` = object modified/committed). Then
`xdotool` clicked `Записать` (Ctrl+S also works — discovered via the button tooltip). Screenshot
`05-our-engine-saved-to-db.png`: the tab title becomes **`ZZXTEST88 (Валюта)`** (the `*` is gone → saved) and a
**`Создание: ZZXTEST88`** notification confirms the record was **written to the DB**. Tools:
`demo_xtest_write_probe.py`, `run_demo_xtest_write.sh`.

⇒ **The full Vanessa-free cycle works:** OUR engine (protocol) opens the form + focuses the field by name +
renders → `xdotool` (OS keystrokes on the client's Xvfb) types + blurs → the OBJECT attribute commits → `Записать`
→ persisted to the DB. This is exactly Vanessa's mechanism (focus by automation API + OS input via VanessaExt),
reproduced with our engine + `xdotool`, no Vanessa runtime. The object-form write surface is closed for the
"100% test-manager replacement" claim.

NOTE: the programmatic our-engine read-back via the capture's read frame (mgr[28]) returns empty when replayed
out-of-context (the `запоминаю значение поля` server-call needs its setup frames); the commit + DB persistence
are proven visually (modified `*` → saved title → "Создание" notification). A clean programmatic verify (re-open
the `Валюты` list via the engine and read the row, or a value-mode read sequence) is a follow-up polish.

## PRODUCTIZED — `write_form_value_xtest` engine path + MCP tool (2026-06-18)

The hybrid is now a first-class engine path: `src/qa_mcp/protocol/native_xtest.py` —
`write_form_value_xtest(capture, value, field, *, host, port, display, blur=True, save=False, …)`. It holds ONE
manager connection and inline: replays the capture's open+focus prefix `[0..setup_stop]` (protocol, field by
name) → `xdotool type` the value into the focused client window on `display` (Unicode/Cyrillic-aware) → `Tab`
(blur → commit) → optional `Ctrl+S` (Записать → DB) → replays the read sequence `[read_start..read_frame]` and
returns `committed` (value present in the read-back). MCP tool `write_form_value_xtest` wraps it (pairs with the
existing `run_native_test_client(display=…)` + `capture_screenshot` + `stop_test_client`). Unit tests
`tests/test_native_xtest.py` (xdotool argv incl. Cyrillic; 239 full suite, no regression). Live-verify
`run_xtest_write_test.sh`.

Live result (productized path, **Cyrillic**): `write_form_value_xtest("genuine-card98-demo-write", "ПродуктТест5",
"Наименование", port=…, display=":89", save=True)` → `{committed: true, value_in_readback: true, saved: true,
diverged_at: null}`; the record saved to the DB (title "ПродуктТест5 (Валюта)", Код auto-assigned "000000010",
"Создание: ПродуктТест5" notification). The clean programmatic read-back uses the in-order read sequence
`[25..28]` (the single out-of-context frame returned empty); `committed` = value-in-readback (the
`read_field_value_near` string-extract is best-effort for the read-sequence format).

GOTCHA (baked into `run_xtest_write_test.sh`): demo_1_0_41_3 can hold an **apache OData session at 8.3.27.1936**
(`1Cv8tmp.1CD` owned by `www-data`) → file-base version contention blocks our 2130 `/TESTCLIENT`. The script
stops apache + clears the stale session files for the boot and restarts apache after (same pattern as the
vanessa_client contention). Also: thin `1cv8c` refuses demo on config signature → use `1cv8` thick; use the
default `HOME` (license); `matchbox-window-manager` so the form lays out.

## Original next (now done above)

# Card 90 — checkbox/choice step-gap resolved + Boolean toggle commit law decoded (findings)

Date: 2026-06-17. This is the card-90 "start here" diagnosis (step-research) plus a genuine capture and a
decisive decode of the **checkbox commit law**. Reproduce with the captures + scripts listed at the bottom.

## 1. Step-research result (the real blocker for checkbox/choice/tables was VOCABULARY, not the fixture)

The prior session reported "no «флажок» step" and parked checkbox/choice/tables on card 90 as possible fixture
gaps. Driving the genuine Vanessa manager (`search_for_steps_by_keywords`) shows the fixture needs **NO change**
for three of the four remaining types — the steps exist under different words:

| type | correct Vanessa step (by NAME — fits the `PF_*` convention) | category |
|---|---|---|
| checkbox (Boolean) | `Я устанавливаю флаг с именем 'ИмяФлага'` / `снимаю` / `изменяю` / `флаг с именем '…' равен "Истина"` | `UI.Формы.Поля.Флаги` |
| choice (radio) | `Я меняю значение переключателя с именем 'ИмяЭлемента' на 'Значение'` (by representation OR number) | `UI.Формы.Поля.Переключатели` |
| table add row | `в таблице "T" я добавляю строку` / `я нажимаю на кнопку "Добавить"` | `UI.Таблицы` |
| table cell edit | `в таблице "T" в поле с именем 'F' я ввожу текст "V"` | `UI.Таблицы` |

`флажок` → 0 hits; `флаг` → 18 hits. **The word is «флаг», not «флажок».** So checkbox/choice/table capture is
unblocked WITHOUT touching the fixture. Only **page-field input** and **open_list** remain genuine
fixture/scope gaps (unchanged from the card-90 plan).

## 2. Genuine capture (capture-free recipe, no fixture change)

Fixture `Обработка.ФикстураПротоколаTestClient` in `vanessa_client`. The checkbox controls already exist:
`EditField[PF_CHECKBOX_FALSE]` (starts "Нет"), `EditField[PF_CHECKBOX_TRUE]` (starts "Да"), inside
`Group[PF_GROUP_MAIN].Group[PF_GROUP_CHECKBOXES]`. Feature drove: set `PF_CHECKBOX_FALSE` (→Да) and clear
`PF_CHECKBOX_TRUE` (→Нет). Both **committed live** (Vanessa read-back): the server handler recorded
`PF_MUTATION_CHECKBOX_MARKER = "PF_CHECKBOX_TRUE=TRUE->FALSE;PF_CHECKBOX_FALSE=FALSE->TRUE"`.

Two captures (gitignored runtime, `runtime/protocol-research/captures/genuine-card90-20260617/`):
- `traffic/` — action-only (single clean connection 53586↔48001; the form was already open, so the connect
  step was skipped → no probe-connection pollution). Best for DECODE.
- `traffic-selfcontained/` — full connect+open+toggle (client 48003, dominant manager port 42676), so it
  carries the form-open handshake and is REPLAYABLE standalone (form-open prefix = first 41 m2c frames;
  `PF_CHECKBOX_FALSE` toggle block = m2c 41–49, `PF_CHECKBOX_TRUE` = 53–61). For PRODUCTIZATION.

## 3. Decode (decisive): a checkbox commits by ACTIVATE/TOGGLE, NOT by a value-SET

Element addressing is identical to text fields — the checkbox is an `EditField[…]`, so the 86a/86b path
addressing already covers it: `…Group[PF_GROUP_MAIN].Group[PF_GROUP_CHECKBOXES].EditField[PF_CHECKBOX_FALSE]`.

But the **value buffer is absent**. Diffing the per-type action frame (tail after the element path `]`):

| type | action frame tail (after `EditField[NAME]`) | meaning |
|---|---|---|
| string/number/date | `e0 41 81 81 ba <varint-len> <value> <pad>` | value SET (the 86c law) |
| **checkbox** | `e0 4b 55` (then `<pad> <nonce>`) | **value-free toggle** |
| choice (radio) | `e0 4b 53 <variant>` (observed `e0 4b 53 8b 33`) | activate + selected variant |

The `e0 4b 55` marker is **byte-identical for the set (FALSE→true) and the clear (TRUE→false)** — it carries
NO boolean value. There are NO "Истина"/"Ложь" bytes anywhere in the checkbox frames (verified: 0 frames).
⇒ **The checkbox value is implicit: the wire only says "act on this checkbox EditField"; the server toggles
the Boolean and fires ПриИзменении.** This is a NEW commit law, distinct from the value-SET types.

`e0 4b 5x` is an **activate-with-action** tag family (`55` = toggle Boolean, `53` = choose variant), separate
from the value-SET tag `41 81 81 ba`. Each genuine action is a ~5-frame block on one `EditField[NAME]`
(focus / focus / **the `e0 4b 55` action frame (+4 bytes)** / read / read).

This makes the checkbox structurally a twin of the card-86d **page-switch** (also a value-free activate-frame
whose element leaf is retargeted), differing only in `kind`: `EditField` vs `Group`.

## 4. Productization — DONE & LIVE-VERIFIED (capture-free, no Vanessa)

Implemented in `protocol/native_write.py`, mirroring `_find_page_switch`/`derive_page_switch`/`switch_page` +
`NativeWriteSession.switch_page` but keyed on `EditField[base_field]` and retargeting with `kind="EditField"`:
- `_find_checkbox_toggle(mgr, base_field)` — the contiguous `EditField[base_field]` run (the value-free
  `e0 4b 55` toggle + its focus/read frames) in `traffic-selfcontained`.
- `derive_checkbox_toggle(capture_dir, base_field="PF_CHECKBOX_FALSE")` → `CheckboxToggleTemplate`
  (`setup_end`=form-open prefix; for this capture: `setup_end=19`, `toggle_block=(20,24)`, toggle @22).
- `toggle_checkbox(template, target_field, …)` (standalone) + `NativeWriteSession.toggle_checkbox(target_field,
  base_field)`.
- MCP tool `toggle_checkbox(target_field, base_field, host, port, capture)` (qa-mcp now exposes **12 tools**).
- Unit tests: `tests/test_native_write.py::{test_derive_checkbox_toggle_locates_block,
  test_checkbox_toggle_retargets_editfield_leaf_keeps_toggle_marker}` (suite 210 passed).

**Live proof** (`tools/protocol-research/checkbox_toggle_probe.py` against a fresh `launch_test_client`, port
15381, apache managed). The Boolean itself reads back as Да/Нет (Cyrillic — the ASCII parser can't see it), so
verify via the server side-effect `PF_LAST_ACTION` (the fixture's ПриИзменении sets it to the toggled
checkbox's NAME). Reproduced on a fresh client (2 runs):

```
baseline PF_LAST_ACTION = 'PF_STATE_INITIAL'
after toggle PF_CHECKBOX_FALSE              -> PF_LAST_ACTION = 'PF_CHECKBOX_FALSE'   OK
after toggle PF_CHECKBOX_TRUE (RE-TARGETED) -> PF_LAST_ACTION = 'PF_CHECKBOX_TRUE'    OK
RESULT: PASS — capture-free checkbox toggle commits (base + re-targeted)
```

So qa-mcp toggles ANY Boolean checkbox by name, capture-free, and the toggle COMMITS server-side. (A 2nd
toggle on the SAME already-open client desyncs the read-back — the fresh-client requirement shared by all the
card-80/86 replays; the toggle frames are still `accepted=True`.)

## 4.1. Choice / radio (Переключатель) — DECODED + PRODUCTIZED + LIVE-VERIFIED

Step: `Я меняю значение переключателя с именем 'PF_CHOICE_MODE' на 'PF_CHOICE_A'` — the variant is addressed
by its **value NAME** (PF_CHOICE_A/B/C; the index form `'3'` is rejected: "отсутствует указанное значение").
Self-contained capture `genuine-card90-choice-20260617/traffic-selfcontained` (3 variant changes A→C→B).

Decode: unlike the value-free checkbox, a choice ACTIVATES the EditField and **carries the selected variant as
a length-prefixed string**: `…EditField[PF_CHOICE_MODE] … e0 4b 53 <0x9a><len><variant-value-name>` (e.g.
`e0 4b 53 9a 0b "PF_CHOICE_A"`). So `e0 4b 53` = choose (vs `e0 4b 55` = toggle); the variant rides as a
`<0x9a><len><name>` string. Setting any variant = the genuine choose block with its EditField leaf +
the variant string re-targeted (same-length swap via `build_write_frame` / `retarget_value`).

Productized: `_find_checkbox_toggle` (reused for the contiguous run) → `ChoiceSetTemplate` /
`derive_choice_set` / `set_choice` + `NativeWriteSession.set_choice` + MCP tool `set_choice` (qa-mcp now **13
tools**). Unit tests added (suite 212 passed). **Live proof** (`tools/protocol-research/choice_set_probe.py`,
fresh `launch_test_client`, 2 runs) — the choice value reads back as ASCII directly (no side-effect needed):

```
baseline PF_CHOICE_MODE = 'PF_CHOICE_B'
set PF_CHOICE_C -> PF_CHOICE_MODE = 'PF_CHOICE_C'   OK
set PF_CHOICE_A -> PF_CHOICE_MODE = 'PF_CHOICE_A'   OK
RESULT: PASS — capture-free radio choice-set commits
```

⚠ Lab note: the native replay client (`launch_test_client`, `vanessa_client`) needs the infobase FREE — boot
it with the Vanessa manager/client DOWN, else the second session crashes on infobase contention (observed).

## 5. Still genuinely blocked — all FIXTURE gaps (carry forward on card 90, edt-mcp)

- **table-cell edit (86e) — CONFIRMED the fixture table is READ-ONLY (2026-06-17 research):** `в поле с именем
  'PF_TABLE_TEXT' я ввожу текст` fails identically on EXISTING and NEW rows ("Метод ВвестиТекст не может быть
  вызван для данного объекта"), even after `я начинаю редактирование строки` (returns OK but cells stay
  read-only) and `в текущее поле я ввожу текст`. `я добавляю строку` returns OK but the row is NOT retained
  (count stays 3). `PF_MUTATION_SUPPORTED_TARGETS` excludes all table columns. ⇒ NOT a step gap — the table
  needs to be made editable in the fixture (ИзменятьСоставСтрок + a column ТолькоПросмотр=Нет) via edt-mcp,
  then capture→decode→productize the cell SET + row-add.
- **page-field input** and **open_list:** real fixture/scope gaps (see card 90 / state doc). All three now
  converge on edt-mcp fixture work; the card flags the decision to extend the fixture vs a new `…V5` processor.

## Reproduce

- Step research: boot manager (`vanessa-mcp/bin/start-vanessa-manager.sh` + `vanessa_auto_allow_dialogs.sh`),
  `vanessa_mcp_call.py search_for_steps_by_keywords '{"search_name":"флаг"}'` (and `переключ`, `в таблице`).
- Capture: `tools/protocol-research/qa-card90-checkbox-selfcontained.feature` via `run_scenario`, with
  `tcpdump -i lo 'tcp portrange 48000-48400'`, then `pcap_to_traffic.py <pcap> <client_port> <out> <mgr_port>`.
- Decode: `tools/protocol-research/card90_checkbox_decode.py`, `card90_checkbox_decode2.py`.

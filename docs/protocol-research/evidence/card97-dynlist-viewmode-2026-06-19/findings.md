# Card 97 change 4 — dynamic-list VIEW-MODE (grouping): capture → decode → productize

**Date:** 2026-06-19. **Scope:** the dynamic-list view-mode / grouping toggle (the «Режим просмотра» →
Список / Дерево / Иерархический список submenu — the user's Screenshot_152/153), capture-free, no Vanessa.
Target: `ДенамическийСписокИерархия` (Catalog.Товары). Builds on the card97-ch4 deploy (gen `08d5aabf7575…`)
that surfaced the dynlist command bar + «Ещё» menu.

## Command-surface discovery (get_form_analysis)

The dynlist's «Режим просмотра» entries are standard FORM BUTTONS (`{Тестируемая кнопка формы}`):
`ДенамическийСписокИерархияИерархическийСписок` / `…Список` / `…Дерево`. (Also discovered for later sub-ops:
`…Интервал` = «Период данных» (PERIOD exists — a group/dialog, NOT N/A as first guessed); `…НастройкаСписка` =
«Настроить список» (filter/sort/grouping config dialog); `…Найти` = «Расширенный поиск».) Vanessa addresses
them BY NAME — the caption is «Список»/«Дерево» so the by-NAME step is required:
`И я нажимаю на кнопку с именем 'ДенамическийСписокИерархияСписок'`.

## Capture (genuine Vanessa manager)

Feature `qa-card97-ch4-viewmode-byname.feature` (connect+open + click `…Список` then `…ИерархическийСписок`,
two different buttons for the byte-diff). ⚠️ GOTCHA: `run_scenario` CACHES a loaded feature by filePath — after
editing «по заголовку»→«по имени» it kept running the old step; use a FRESH FILENAME (or load_features) to force
a re-read. Result: **Success**. client TPort **48004**, dominant manager **43230** →
`runtime/protocol-research/captures/genuine-card97-ch4-viewmode-20260619/` (32 manager→client chunks).

## Decode (KEY) — view-mode is the `88 82 81` command family at a UTF-16LE Button leaf

Per-click manager→client (mgr ordinals):
- `#19` — `…Button[ДенамическийСписокИерархияСписок] 88 82 81 20 20 20` (the invoke).
- `#20` — same, `81 81 81 20 20 20` (the SET/invoke duplicate pair — as everywhere).
- `#27/#28` — the same for `…ИерархическийСписок`. The two clicks differ ONLY in the Button leaf.

So a view-mode change is the **`…Button[<name>] 88 82 81 20 20 20` command family** — IDENTICAL to the row ops /
close-window invoke — but the Button name is **Cyrillic → the element path is UTF-16LE** (the full path is
578 bytes, char-count prefix `21 01`=289; the ASCII `<0x9a><byte-len:1>` form is for ASCII names only). This is
the card-98 UTF-16 element-path situation, now in the command-click machinery.

## Productize — generalize `click_command` to UTF-16 + a thin `set_list_view`

- `element_ref.retarget_element_leaf_any(frame, old, new, kind)` — retarget a Button leaf whether the path is
  ASCII (latin1, 1-byte len) or UTF-16LE; the UTF-16 branch requires the SAME char length (a direct byte-replace
  that leaves the path's char-count prefix untouched). `Список`↔`Дерево` are both 6 chars → same-length swap.
- `native_write._find_element_command` is now encoding-agnostic (`_frame_addresses_leaf` checks ASCII + UTF-16),
  and `click_command` retargets via `retarget_element_leaf_any` → **click_command now works on Cyrillic-named
  commands** (generalizes the row-ops/command machinery to real configs — advances the card-98 "2nd config" goal).
- `set_list_view(capture_dir, mode, dynlist="ДенамическийСписокИерархия")` — Список / Дерево / Иерархический
  (also list/tree/hierarchical). Дерево = a same-length UTF-16 retarget of the captured Список click;
  Список / Иерархический = verbatim captured clicks. MCP tool `set_list_view` — the **35th** tool.
- Unit tests (4): retarget_element_leaf_any ASCII+UTF-16 same-length, UTF-16 different-length raises,
  _find_element_command locates a UTF-16 Button last-run, set_list_view rejects an unknown mode. Suite **258**.

## Live-verify ✅ (no Vanessa, 3-way screenshot proof)

Probe: `tools/protocol-research/set_list_view_verify_shot.py` (a fresh native client per mode → set_list_view →
screenshot). Result (`runtime/protocol-research/viewmode-shot/20260619-075608/`), all `accepted=True`, the
view-mode click re-renders + scrolls the dynlist into view — THREE distinct representations of the SAME Товары
list:
- `01-Список` — **flat list**: items listed directly (Bosch1234, Bosch15, Sony K3456P), no folders.
- `02-Дерево` — **collapsed tree**: a single tree root `⊕ 📁 Товары` (the same-char-length UTF-16 retarget of the
  captured Список click — proves the UTF-16 Button-leaf retarget).
- `03-ИерархическийСписок` — **expanded hierarchy**: `▾ 📁 Электротовары → ▾ 📁 Чайники → — Bosch1234`.

The three-way visual difference is the definitive proof: the capture-free view-mode command applies, both for
the verbatim captured clicks (Список / Иерархический) AND the UTF-16-retargeted one (Дерево).

## Honest boundaries / follow-ups

- **Read-back:** a view-mode change has no value read-back (verify by screenshot, like `click_command`).
- **UTF-16 retarget length:** the Дерево retarget works because `Список`/`Дерево` are the same char length; a
  different-length view-mode (or another config's) would need its own captured click or a char-count-prefix
  resize (documented refinement; `retarget_element_leaf_any` raises rather than corrupt the frame).
- **Remaining card-4 sub-ops** surfaced by the discovery: **filter** (`…НастройкаСписка` — list-settings
  dialog), **period** (`…Интервал` — period dialog; exists, not N/A). Both are dialog-driven (heavier than the
  button-command view-mode).

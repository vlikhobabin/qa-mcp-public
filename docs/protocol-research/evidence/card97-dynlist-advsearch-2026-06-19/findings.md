# Card 97 change 4 — dynamic-list FILTER via «Расширенный поиск» dialog: capture → decode → productize

**Date:** 2026-06-19. **Scope:** filter a dynamic list via the «Расширенный поиск» (advanced-search) DIALOG —
the reusable **"drive a modal dialog"** pattern — capture-free, no Vanessa. Target: `ДенамическийСписокИерархия`
(Catalog.Товары). Builds on the card97-ch4 deploy (gen `08d5aabf7575…`).

## Recon (get_form_analysis of the open dialog)

Clicking «Расширенный поиск» (`ДенамическийСписокИерархияНайти`) opens the standard `UniversalListFindExtForm`:
- `Pattern` («Что искать») — the search value (text input).
- `FieldSelector` («Где искать») — which field (default «Код»).
- `CompareType` («Как искать») — comparison mode.
- command bar: `Find` («&Найти», confirm) / `Cancel` («Закрыть»).

## Capture (genuine Vanessa manager)

Feature `qa-card97-ch4-advsearch-capture.feature`: connect+open → click «Расширенный поиск» → `в поле с именем
'Pattern' я ввожу текст 'Молоко'` → click `Find`. Result **Success**. client TPort **48002**, dominant manager
**37118** → `runtime/protocol-research/captures/genuine-card97-ch4-advsearch-20260619/` (38 manager→client).

## Decode (KEY) — open-dialog command + UTF-16 Pattern SET + Find command

mgr ordinals:
- `#19/#20` — `…Button[ДенамическийСписокИерархияНайти] 88 82 81 20 20 20` (UTF-16 leaf) → opens the dialog (a
  NEW SecondaryFrame).
- `#25/#26` — `…Field[Pattern] 88 82 81  e0 41 81 81 b7 06 <Молоко UTF-16LE> 20 20 20` — the Pattern value rides
  the **UTF-16 `b7` value buffer** (the SAME buffer as a ref/search value), and the element leaf `Pattern` is
  **ASCII** (the dialog's standard control names are English, unlike the dynlist's Cyrillic names).
- `#33/#34` — `…Button[Find] 88 82 81 20 20 20` (ASCII leaf) → confirm → the filter applies.

So the whole flow is: open-form → open-dialog (new window) → Pattern SET (UTF-16 b7) → Find (command). It is the
answer_dialog / open_card "new window" shape with a value SET inside the dialog.

## Productize — reuse the full-replay + GuidRebinder + retarget_ref_value machinery

- `protocol/native_write.py`: `AdvancedSearchTemplate` + `derive_advanced_search` + `advanced_search` — a
  WHOLE-STREAM replay (exactly the `set_reference_field` shape): `GuidRebinder` rebinds the new dialog window by
  first-appearance, and the Pattern value re-targets via `retarget_ref_value` (UTF-16, fixed-width — bounded by
  the captured "Молоко" length). MCP tool `advanced_search` — the **36th** tool.
- 1 unit test (derive validates the UTF-16 Pattern present / raises when absent). Suite **259**.

## Live-verify ✅ (no Vanessa, screenshot)

Probe `tools/protocol-research/advanced_search_verify_shot.py`: `advanced_search("Молоко")`, `echoed=True`.
Screenshot (`runtime/protocol-research/advsearch-shot/20260619-110841/01-advsearch.png`): the dynlist shows an
**active filter chip «Код: Молоко ⊗»** and the list is filtered (empty — "Молоко" is not a Код value). The
filter chip is the definitive proof: the modal-dialog flow applied a real list filter on the **Код** field with
the re-targeted value, capture-free.

## Honest boundaries / follow-ups

- **Default field:** the capture left `FieldSelector` at «Код», so the filter targets Код (hence "Молоко"→empty
  — a positive match needs a Код value, but those are 9 chars > the 6-char "Молоко" UTF-16 buffer). Searching
  another field (e.g. Наименование, where "Молоко" matches) = set `FieldSelector` first — a refinement (the
  field is a choice control; capture that step to parameterize the field).
- **Value length** bounded by the captured "Молоко" (fixed-width UTF-16 retarget), like the ref/search value.
- **No clean value read-back** — verify by screenshot (the filter chip + the narrowed list); `echoed` reports
  the Pattern echoed in the responses.
- ⭐ The "drive a modal dialog" replay (open new window → SET a field in it → click a button in it) is the
  REUSABLE pattern this proves — it generalizes to the «Настроить список» (full Отбор) and «Период данных»
  dialogs, and any modal form fill.

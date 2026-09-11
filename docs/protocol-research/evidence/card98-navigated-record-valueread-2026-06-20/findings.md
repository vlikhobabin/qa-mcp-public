# Card 98 change-5 follow-up — navigated RECORD value-read: mechanism built + reaches a real 2nd-config record

**Date:** 2026-06-20. **Result:** the navigated value-read now reaches a real catalog RECORD form on a 2nd config
(demo БСП), reading its object-attribute field set capture-free. Two productization gains shipped
(zero-group field enumeration + a newest-window open fallback); the remaining gap is reading a NON-EMPTY value
(the test form is a create/empty form). 45 MCP tools, **326 tests**.

## What was found (the chain, end to end)

1. **nav-link DOES open a real RECORD form** (not just lists). `e1cib/data/Справочник.Валюты` on the demo opens
   **`Валюта (создание)`** — a catalog object form with 4 real object-attribute EditFields: `Код`,
   `Наименование`, `НаименованиеОсновнойВалюты`, `НаименованиеРазменнойВалюты`. (Several other `e1cib/data/…`
   links did not open a record form — nav-link record-open is catalog-specific.)
2. **Root cause of `field_count=0` — zero-group fields.** A catalog record's fields sit DIRECTLY under
   ManagedForm: `SecondaryFrame[S].ManagedForm[F].EditField[Наименование]` — **no enclosing `Group`** (the
   fixture's fields were `Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[…]`). `extract_descriptor_fields`
   required `(Group[…].)+` (≥1 group), so it returned 0 specs → the value-read swept nothing. **Fixed:** added
   `_DESCRIPTOR_FIELD0_{ASCII,UTF16}_RE` matching `ManagedForm[<guid>].EditField[name]` (zero groups), anchored
   on `ManagedForm[guid].` so a dynlist COLUMN (`…Table[Список].EditField[col]`) is still excluded. The
   `_retarget_read_to_groups(groups=[], form_ref=(S,F))` path already builds `ManagedForm[F].EditField[name]`.
3. **The navigated value-read REACHES the record form.** With the fix, the descriptor enumerates the 4 fields and
   the value-read query runs per field against the navigated form's S.F — each gets a distinct response
   (~1.1–1.3 KB, growing with the field-name length, the field name echoed) — i.e. the retargeted path resolves
   to the navigated form (not the fixture region, not a rejection).
4. **The values are EMPTY** — `Валюта (создание)` is a NEW record, so its fields carry no `e0 4b 53` «стал равен»
   value envelope → 0 values parsed. That is a correct read of an empty form, but does not prove a non-empty read.

## Productization gains (shipped)

- **Zero-group form-field enumeration** — `extract_descriptor_fields` now captures fields directly under
  ManagedForm (catalog/document RECORD forms), not just group-nested ones; columns stay excluded. +1 test (326).
- **Newest-window open fallback** — `_open_form_by_link` now matches the target window by caption FIRST, then
  falls back to the SecondaryFrame that appeared AFTER the navigate (a window not present on the bare desktop).
  This opens **custom-caption forms** whose caption is a synonym (the fixture's `Фикстура протокола TestClient`
  caption doesn't contain the metadata name `ФикстураПротоколаTestClient`) — the caption-only match used to fail.

## Honest scope — the remaining gap

- A **NON-EMPTY** navigated value-read is not yet verified. The demo create form's fields are empty; an xtest-type
  attempt FAILED because the navigated form is not the focused OS window — after the nav-link open the demo showed
  the **«Поиск по функциям»** (All-functions) screen, so `xdotool type` landed in the function-search box, not the
  form (screenshot `02_after_type.png`). The protocol value-read reaches the form regardless of OS focus, but the
  form's fields were empty, and OS-input can't populate a non-focused form.
- ⇒ verifying a non-empty navigated value-read needs an **existing POPULATED record** opened so the value-read
  reaches it — a record ref (`e1cib/data/Справочник.X?ref=…`) or a list row-drill (`open_card`). The dynlist-column
  read (the next change) supplies a ref from the list; that unblocks this verify.

## Honest finding (DataProcessor nav-link)

- The vanessa_client FIXTURE DataProcessor opened by `e1cib/data/Обработка.ФикстураПротоколаTestClient` returns a
  **command-bar-only descriptor** (2109 B: `Group[ФормаКоманднаяПанель]` + the auto Изменить-форму/Справка/
  Создать-на-основании/Печать commands) — the body groups/EditFields are ABSENT (stable across settle retries, so
  not a render race). A LIST form's descriptor is the full tree; the frames-11-17 fixture open gives all 46
  EditFields. So a DataProcessor form opened by nav-link does not expose its body in the descriptor — the fixture
  is not a vehicle for the navigated value-read; a catalog record form (above) is.

## Artifacts

- Code: `src/qa_mcp/protocol/responses.py` (`extract_descriptor_fields` zero-group), `src/qa_mcp/mcp_server.py`
  (`_open_form_by_link` newest-window fallback).
- Tests: `tests/test_form_descriptor.py` (`test_extract_descriptor_fields_zero_group_record_form`).
- Probes: `demo_record_valueread_probe.py` (record forms), `navigated_fixture_blob_dump.py` (descriptor dump,
  port/ib args), `navigated_valueread_classify_probe.py` (resolve-vs-stub), `navigated_nonempty_valueread_probe.py`
  (xtest-type + read; the focus finding), `navigated_record_valueread_probe.py`, `navigated_fixture_settle_probe.py`.

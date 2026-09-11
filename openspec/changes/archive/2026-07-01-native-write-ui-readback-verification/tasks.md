## 1. Two-pass click geometry

- [x] 1.1 Restructure `write_form_fields_by_label` (`src/qa_mcp/mcp_server.py`) into pass 1 (locate every
  label, record `diag["box"]["right"]`) + pass 2 (click each non-date field into
  `input_column_x(right_edges, gap=input_column_gap)`; date fields click their own mask; 0/1 labels →
  legacy label-center + `input_offset`). Each item reports `geometry`.
- [x] 1.2 Expose `input_column_gap` (default 24) on the tool signature.

## 2. Honest protocol value-read verification

- [x] 2.1 `_sweep_form_field_values` factored out of `_read_form_descriptor` (shared value-read sweep).
- [x] 2.2 `_resolve_open_form_by_caption` — resolve an already-open form's (caption, S, F) by caption/newest,
  window-list + resolve, NO navigate.
- [x] 2.3 `_read_open_form_field_values` — fail-closed value-read of the open form on a fresh connection.
- [x] 2.4 `_value_matches_readback` + `_apply_readback_verification` — set honest `committed`/`readback_value`
  by VALUE presence.
- [x] 2.5 Wire the read-back into `write_form_fields_by_label` (after close; `all_committed` + `readback`
  block) and derive `committed` in `write_form_value` / `write_form_values` / `_open_link_field_write_result`
  from the read-back (`verification: value_readback`), removing the `committed == targeted` false positive.

## 3. OData deprecation (test-client-held base)

- [x] 3.1 `_mark_odata_deprecated` + docstring banners on `assert_data` / `assert_data_count` /
  `role_data_matrix`; module banner on `src/qa_mcp/data/odata.py` `ODataClient`. Additive `deprecated`/
  `deprecation` keys; behaviour unchanged (tools/tests retained). Full removal + runner/autofill cleanup is
  a later change.

## 4. Offline tests

- [x] 4.1 `test_write_form_fields_by_label_two_pass_clicks_shared_input_column` — two labels of different
  length click the same computed input column.
- [x] 4.2 `test_write_form_fields_by_label_committed_only_when_read_back` — committed True only when read
  back; targeted-but-absent → committed False.
- [x] 4.3 `test_value_matches_readback_verifies_by_value_presence` — value-presence match (reference/date/text).
- [x] 4.4 `test_mark_odata_deprecated_is_additive` — deprecation is additive, non-breaking.
- [x] 4.5 `test_read_open_form_retries_past_cold_client_zero` — the read-back retries past the cold-client
  boundary (field_count 0 → retry → values) and reports honest 0 when the client never materialises.
- [x] 4.6 Full suite green (578 passed).

## 5. Cold-client boundary (read-back retry)

- [x] 5.1 The first value-read on a freshly launched client enumerated the element tree (8 EditFields) but
  echoed EMPTY values (`field_count: 0`) — the cold-client boundary. `_read_open_form_field_values` retries
  the read on a fresh connection until it materialises values; live-proven the 2nd read returns all 8 field
  values. `_read_open_form_once` now also reports `element_count` so a zero read is diagnosable.

## 6. Live verification (demo10413)

- [x] 6.1 Catalog re-applied (194→233M, ibcmd import+apply, "Новый объект: Справочник.ДоговорыКонтрагентов").
- [x] 6.2 On a FRESH cold client, `write_form_fields_by_label` drove the real `Catalog.ДоговорыКонтрагентов`
  create form: «Наименование»/«Номер договора»/«Владелец» clicked the SHARED input column (x=378,
  `geometry: input_column`); «Дата договора» clicked its mask (`geometry: date_mask`); the open form's
  value-read (retry past the cold zero) returned all 8 fields, so every written field is
  `committed: true` with a matching `readback_value` (Наименование=QA-PROOF-125, НомерДоговора=QA-DOG-001,
  Владелец=«Корнет ЗАО», ДатаДоговора=30.06.2026). `all_targeted` + `all_committed` true. Evidence:
  `.artifacts/openspec/card125-followup-readback-live/20260701T054358Z/`
  (`write-result.json`, `final-form-filled.png`).
- [x] 6.3 demo10413 restored to the 194M baseline (cmp-identical to the pre-reapply snapshot, 202924032 bytes,
  snapshot removed).

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner |
| --- | --- | --- | --- | --- | --- | --- |
| managed form (click geometry) | two-pass input column for short/right-aligned labels | offline + live | offline shared-column test; live «Владелец» geometry `input_column`, x=378 | `.artifacts/openspec/card125-followup-readback-live/20260701T054358Z/` | done | qa-mcp |
| tool result contract (commit) | value-read verified `committed` (no false positive) | offline + live | offline positive/negative; live all 4 fields `committed:true` read back | `.artifacts/openspec/card125-followup-readback-live/20260701T054358Z/write-result.json` | done | qa-mcp |
| managed form (read-back) | cold-client-boundary retry on the open-form value-read | offline + live | offline retry test; live 1st read 0 → retry → 8 values | `.artifacts/openspec/card125-followup-readback-live/20260701T054358Z/` | done | qa-mcp |
| OData deprecation | test-client-held base guidance | offline | additive `deprecated` annotation | (offline) | done | qa-mcp |

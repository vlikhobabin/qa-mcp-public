## 1. Commit a date inline

- [x] 1.1 `write_form_fields_by_label` field-mode `"date"`: click the input MASK with a dedicated
  `date_input_offset` (avoiding the calendar button) and type the date as digit keys
  («30.06.2026» → keys 3,0,0,6,2,0,2,6) so the mask fills and commits; routed from
  `write_form_date(open_link=…)` via `_open_link_field_write_result(field_mode="date")`. (A
  deterministic calendar-pick fallback for fields where inline typing is not viable is a follow-up;
  the proven default is inline digit typing.)

## 2. Verify commit

- [x] 2.1 Live read-back: the field reads back the committed date; authoritative per-record commit is
  the post-save read-back in `native-write-demo10413-real-proof`.

## 3. Offline tests

- [x] 3.1 Regression covered by the full offline suite (570 passed) with the new `field_mode="date"`
  branch + `date_input_offset` param; a dedicated stubbed date-input unit test is a follow-up.

## 4. Live verification (demo10413)

- [x] 4.1 On the real create form `write_form_date(field="Дата договора", date="30.06.2026")` commits
  «30.06.2026» into the mask (click_xy=[388,487], NOT the calendar button) — no calendar left open.
  Evidence: `.artifacts/openspec/card125-live-do-session/20260701T034037Z/c3-date-committed-tool-route.png`.
- [x] 4.2 Evidence retained; demo10413 restored to baseline.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner |
| --- | --- | --- | --- | --- | --- | --- |
| managed form date input | `write_form_date` open-link route, `field_mode="date"` | offline suite + live | live «Дата договора»=30.06.2026 committed (mask, no calendar) | `.artifacts/openspec/card125-live-do-session/20260701T034037Z/c3-date-committed-tool-route.png` | done | qa-mcp |
| calendar-trap avoidance | date-field click uses `date_input_offset` into the mask | live | click_xy=[388,487] into mask, not the button (~468) | same bundle | done | qa-mcp |

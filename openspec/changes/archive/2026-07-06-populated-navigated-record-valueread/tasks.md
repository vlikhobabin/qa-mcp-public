## Archive Note (2026-07-06)

Archived during board hygiene as historical/superseded planning. The active
delivery is represented by done board card
`openspec/board/4.done/99-2026-06-20-navigated-record-read-and-date-cell.md`;
the unchecked checklist below is retained as the original plan, not as active
OpenSpec work.

## 1. Open route for a populated record

- [ ] 1.1 Confirm or extend the open-by-ref path so
  `read_form_descriptor(open_link="e1cib/data/Справочник.X?ref=<guid>")` reaches a
  populated record form's `S.F` (`_open_form_by_link`); decode/confirm the ref
  nav-link resolve if it differs from list/create nav-links.
- [ ] 1.2 Confirm the row-drill fallback: `read_list_row(where=…)` positions on a
  known record, then `open_card` opens that record's form (newest-window open
  fallback in `_open_form_by_link`).
- [ ] 1.3 Pick one real config + record + field with a stable, unambiguous OData
  oracle (e.g. `vanessa_client` Товары `Наименование`, or a demo БСП catalog
  record).

## 2. Value-read the populated record

- [ ] 2.1 Value-read the opened record's object-attribute fields against the
  navigated form's `S.F` (`_retarget_read_to_groups(form_ref=…)` +
  `extract_descriptor_fields` zero-group enumeration).
- [ ] 2.2 Ensure the result distinguishes "read succeeded, value empty" from
  "form not reached / read failed" so an empty-form read is never mistaken for a
  populated-record proof.

## 3. Oracle comparison + proof

- [ ] 3.1 Read the same record's same field from OData (`query_odata` / live-mcp).
- [ ] 3.2 Assert ≥1 non-empty value read back from the form matches the OData
  value on a live cold boot (honor the cold-client dynlist materialisation
  boundary; sequence open + read in one session).

## 4. Tests + evidence

- [ ] 4.1 Add/confirm a unit/shape test for the populated-record value-read path
  (decode + empty-vs-value distinction), runnable offline.
- [ ] 4.2 Retain evidence under
  `.artifacts/openspec/populated-navigated-record-valueread/<run-id>/` recording
  config/record identity, open route, fields+values read, and the OData match;
  cross-link `evidence/card98-navigated-record-valueread-2026-06-20/`.

## 5. Verification

- [ ] 5.1 Run the change's unit/shape tests green.
- [ ] 5.2 Run `openspec validate populated-navigated-record-valueread --strict`.
- [ ] 5.3 Run `git diff --check -- openspec/changes/populated-navigated-record-valueread openspec/board`.

## 6. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form (record) read | Existing populated catalog/document record form opened capture-free by ref nav-link or row-drill | Open-route record + field selection; navigated `S.F` retarget note | Live read transcript: opened record, fields read, each value, open route used | `.artifacts/openspec/populated-navigated-record-valueread/<run-id>/record-valueread/` | required | `project:qa-mcp` | N/A | Medium: ref nav-link `S.F` resolve may differ from list/create nav-links; row-drill fallback covers it |
| Live infobase read (OData oracle) | Same record's same object-attribute field read from OData | Oracle field selection with stable 1:1 identifier | OData response for the field + equality assertion vs the form read | `.artifacts/openspec/populated-navigated-record-valueread/<run-id>/odata-oracle/` | required | `project:qa-mcp`, `live-mcp` | N/A | Low: read-only; watch OData synonym-vs-identifier naming, compare on platform identifier |
| Python manager value-read | `read_form_descriptor` value-read, `extract_descriptor_fields` zero-group path, empty-vs-value distinction | Unit/shape test asserting decode + empty-vs-populated distinction | Offline unit/shape test green | `tests/` (populated-record value-read test) | required | `project:qa-mcp` | N/A | Low: covered by offline decode test |
| Runtime apply / mutation | None — record is read, never written | N/A for this read-only change | N/A | N/A | N/A | `project:qa-mcp` | This change reads an existing populated record and performs no mutation | Low: no write path exercised |
| Vanessa UI evidence | None — capture-free, no Vanessa | N/A | N/A | N/A | N/A | `project:qa-mcp` | The proof is native-protocol capture-free; Vanessa is explicitly out of scope | Low: native read already shipped, this change only proves it on a populated record |

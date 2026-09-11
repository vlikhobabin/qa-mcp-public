## Why

The demo10413 owner-create round closed the locate + owner-label + date blockers but left two named
residuals, and a fresh architectural review found a third problem:

- **Far-right-aligned short labels still under-reach their input column.** The prior change fixed
  localization of the short «Владелец» needle and delivered the date-mask offset, but its click
  geometry still derived the click point from a single label's center + a fixed `input_offset`.
  Managed-form inputs are right-aligned to the LONGEST label on the form, so a short label (e.g.
  «Код», «Владелец») whose own center + offset lands left of that column types into a neighbour
  field. This was the documented follow-up in `native-write-locate-short-reference-label`.

- **Open-link writes reported `committed`/`accepted` from on-screen TARGETING, not a read-back.**
  `write_form_value` / `write_form_values` / the open-link label writer set `committed = targeted`
  with `readback_value: null` — a false positive: a label located + typed is not proof the value
  reached the form model.

- **OData cannot verify a test-client-held base.** The data-layer tools (`assert_data`,
  `assert_data_count`, `role_data_matrix`, `ODataClient`) were positioned as the authoritative
  UI→DB read-back. But a file/server infobase opened by a «Клиент тестирования» is held under an
  EXCLUSIVE lock, so an out-of-process OData/COM reader cannot open it — an OData read-back of what
  the running test client just did is impossible on the same base.

## What Changes

- **Two-pass click geometry** in `write_form_fields_by_label`: pass 1 locates every label and records
  its right edge; pass 2 clicks each non-date field into the SHARED input column derived from the
  rightmost located label edge (+ `input_column_gap`), so short and long labels alike reach the
  right-aligned column. Date fields keep their input-mask offset; with 0/1 located labels the writer
  falls back to the legacy label-center + `input_offset`.

- **Honest protocol value-read verification**: after typing, `write_form_fields_by_label` value-READs
  the still-open form on a fresh manager connection (window-list → resolve the open form by
  caption/newest, no navigate — re-opening would spawn a blank form and lose the typed values) and
  sets each field's `committed` True ONLY when the requested value is actually read back from the
  form model (the «стал равен» value-read, matched by VALUE presence since the writer targets by
  on-screen label). The false `committed == targeted` in the open-link writers is removed.

- **Deprecate the OData data-layer tools for a test-client-held base**: `assert_data`,
  `assert_data_count`, `role_data_matrix` and `ODataClient` carry a deprecation banner and return an
  additive `deprecated: true` + guidance pointing to the same-client protocol value-read. The tools
  remain (valid only against a separately published, non-exclusive endpoint) pending the
  scenario/autofill/regression/gherkin cleanup — a later change.

## Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: add requirements for two-pass input-column click geometry, for honest
  protocol value-read verification of an open form-write (no false-positive `committed`), and for the
  OData test-client-held-base deprecation.

## Impact

- Python manager: `src/qa_mcp/mcp_server.py` (`write_form_fields_by_label` two-pass + read-back;
  `_read_open_form_field_values` / `_resolve_open_form_by_caption` / `_sweep_form_field_values` /
  `_value_matches_readback` / `_apply_readback_verification` helpers; the open-link writers'
  `committed`; the OData tool deprecation wrappers).
- Protocol helper: `src/qa_mcp/protocol/native_xtest.py` (`input_column_x`, `locate_text` box diag —
  delivered in the prior change, consumed here).
- Data client: `src/qa_mcp/data/odata.py` (module deprecation banner).
- Offline tests: two-pass geometry, read-back committed (positive + negative), value-presence match,
  OData deprecation annotation. Plus live demo10413 verification on the `ДоговорыКонтрагентов` create
  form (two-pass lands the fields; the value-read reports honest `committed`).
- Live 1C runtime required for the demo10413 leg (TestClient + display backend). No Vanessa/EDT/meta
  snapshots needed.

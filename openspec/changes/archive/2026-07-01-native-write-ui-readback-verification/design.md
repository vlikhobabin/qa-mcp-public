# Design — native write UI read-back verification + two-pass geometry + OData deprecation

## 1. Two-pass click geometry (`write_form_fields_by_label`)

**Problem.** Managed-form inputs are right-aligned to the LONGEST label on the form. The single-pass
loop clicked each field at `label_center + input_offset` (fixed 170 px). For a short label
(«Владелец», «Код») that lands LEFT of the right-aligned input column, so the value types into
whichever field had focus — a neighbour — and the field stays empty.

**Design.** Split the loop into two passes:

- **Pass 1 — locate all.** For every `(label, value, mode)`, screenshot + `locate_text` the label
  (colon-first, then bare; the create-splice activation retry is preserved). Record the matched box's
  right edge from `diag["box"]["right"]` (delivered in the prior change).
- **Compute the column.** `input_col_x = input_column_x(right_edges, gap=input_column_gap)` =
  `max(rightmost non-date located label edge) + gap`. Only non-date labels feed the column (a date
  field clicks its own mask). With `< 2` usable edges the column is `None` (unreliable) and the field
  falls back to the legacy `label_center + input_offset`.
- **Pass 2 — click + type.** Each located field clicks `(input_col_x, label_cy)` (geometry
  `input_column`); a `field_mode="date"` field clicks `(label_x + date_input_offset, label_cy)`
  (geometry `date_mask`, never the calendar button); the fallback is `label_offset`. Typing / Tab /
  reference-selection verify are unchanged.

This makes a short label reach the same column as the longest label. `input_column_gap` (default 24)
is exposed. Each result item reports its `geometry`.

## 2. Honest protocol value-read verification

**Problem.** OData cannot read a test-client-held base (exclusive lock), and the open-link writers set
`committed = targeted` with `readback_value: null` — a false positive.

**Design.** After typing (and any save), the foreground socket is closed (the form stays open as a
tab — closing a manager TCP socket does not tear down a client-side UI form), then the open form is
value-READ on a FRESH manager connection:

- `_resolve_open_form_by_caption(handle, caption_match)` — window-list the client, pick the
  SecondaryFrame by caption substring (empty → the NEWEST; after the writer's Escape sweep the fresh
  create form is the only/last one), resolve its ManagedForm. It does NOT navigate — re-opening a
  create form would spawn a second blank form and lose the typed values.
- `_read_open_form_field_values(host, port, caption_match)` — bootstrap a session, resolve the open
  form, enumerate its live EditFields off the descriptor, and run the value-read sweep
  (`_sweep_form_field_values`, factored out of `_read_form_descriptor`). Fail-closed: any error →
  `{opened: None}` so it never breaks the write.
- `_value_matches_readback(requested, readback_values)` — a write is verified when the requested value
  equals / is contained by / contains some read-back value (guarded against trivially-short matches).
  Verify by VALUE presence, not field name: the writer targets by on-screen LABEL, whose name differs
  from the descriptor field name (reference → its presentation «Корнет ЗАО»; date → «30.06.2026»;
  text → the string).
- `_apply_readback_verification(results, fields)` — set each targeted item's `committed`/`readback_value`
  from the value-read; a field targeted on screen but not read back is `committed=False`.

**Cold-client boundary (found live).** The FIRST descriptor value-read on a freshly launched client
enumerates the element tree (8 EditFields on the create form) but echoes EMPTY values (`field_count: 0`
with `element_count > 0`) — the same boundary `read_record` documents. A retry on a fresh connection
returns the materialised values (live: the 2nd read returned all 8 field values, including the resolved
reference «Корнет ЗАО» and «30.06.2026»). So `_read_open_form_field_values` wraps `_read_open_form_once`
in a bounded retry-until-a-value-reads loop (default 4 attempts, 3 s apart); it returns honest empty +
`read_attempts` when the client never materialises. `_read_open_form_once` reports `element_count` so a
zero read is diagnosable (tree present, values pending) vs a genuine miss (form not resolved).

`write_form_fields_by_label` returns `all_committed` + a `readback` block (`opened`, `field_count`,
`verified`, `fields`). The open-link writers (`write_form_value` / `write_form_values` /
`_open_link_field_write_result`) now derive `committed` from the read-back (verification
`value_readback`) instead of `targeted`.

### Why the same-client protocol value-read, not OData
A file/server infobase opened by a «Клиент тестирования» is exclusively locked; an out-of-process
OData/COM reader cannot open it. The genuine test client already holds the form model, and the
value-read query returns the current (typed-but-uncommitted) form-model values — the exact «стал
равен» surface. This is the same mechanism `read_record` / `read_form_descriptor` use, retargeted to
an already-open form instead of navigating to one.

## 3. OData deprecation (not removal)

`assert_data`, `assert_data_count`, `role_data_matrix` and `ODataClient` carry a deprecation banner
in their docstrings and return an additive `deprecated: true` + `deprecation` guidance (via
`_mark_odata_deprecated`) pointing to the same-client protocol value-read. Behaviour is unchanged
(the tools stay valid against a separately published, non-exclusive endpoint), so no tests break.

**Residual (later change).** Full removal + the scenario/autofill/regression/gherkin cleanup that
still route data-layer asserts through `ODataClient` is deferred; the runner's `assert_data` step and
`autofill` are unchanged here.

## Alternatives considered
- **Read the open form on the writer's own held socket** — rejected: the foreground socket is a raw
  listreplay socket, not a bootstrapped manager handle, so it cannot run the value-read query.
- **Read concurrently while the foreground socket is held** — rejected in favour of read-after-close
  to avoid any concurrent-manager-connection question; the UI form persists across manager reconnects
  (the same property `read_record`'s cold-client warming relies on).
- **Re-open the form to read it** — rejected: re-opening a create form spawns a second blank form and
  loses the writer's typed values.

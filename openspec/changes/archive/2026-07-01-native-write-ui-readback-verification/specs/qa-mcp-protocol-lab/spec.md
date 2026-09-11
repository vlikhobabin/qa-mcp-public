## MODIFIED Requirements

### Requirement: Form-write results label their verification honestly

A field write SHALL report its verification level truthfully. Reference fields SHALL report an explicit
`selected` check (the requested value located on screen after input). An open-link field write SHALL
report `committed: true` only when a protocol value-read of the open form confirms the value
(`verification: value_readback`); when the read-back is unavailable it SHALL fall back to
`verification: screen_targeted` (label located + value typed) and SHALL NOT claim `committed`. The
prior false `committed == targeted` (on-screen targeting reported as a commit) SHALL NOT be emitted.

#### Scenario: Reference input reports an explicit selected check

- **WHEN** a reference field value is typed by the open-link writer
- **THEN** the result reports `selected: true` only when the value is located on screen after input
- **AND** reports `selected: false` with a reason otherwise

#### Scenario: Commit is claimed only when the value is read back

- **WHEN** an open-link field is written and the open-form value-read returns the requested value
- **THEN** the result reports `committed: true` with `verification: value_readback`
- **AND** when the value is not read back the result reports `committed: false` (no false positive)

## ADDED Requirements

### Requirement: Two-pass geometry clicks short labels into the right-aligned input column

`write_form_fields_by_label` SHALL derive the input column from the located labels rather than a fixed
per-label offset. It SHALL locate every field label first, record each label's right edge, then click
each non-date field into a SHARED input column computed from the RIGHTMOST located label edge (plus a
configurable gap), so a short label (for example «Владелец» or «Код») reaches the same right-aligned
input column as the longest label instead of under-reaching into a neighbour field. A date-mode field
SHALL keep clicking its own input mask (never the calendar button); when fewer than two labels locate,
the writer SHALL fall back to the legacy label-center + input-offset. Each result item SHALL report the
geometry it used (`input_column`, `date_mask` or `label_offset`).

#### Scenario: Short owner label reaches the right-aligned input column

- **WHEN** `write_form_fields_by_label` writes the short label «Владелец» alongside longer labels on the
  demo10413 `Catalog.ДоговорыКонтрагентов` create form
- **THEN** «Владелец» is clicked into the shared input column (the rightmost located label edge + gap),
  not its own center + a fixed offset
- **AND** the reference value «Корнет ЗАО» lands in the «Владелец» field
- **AND** the item reports `geometry: input_column`

#### Scenario: Offline two-pass shares one column across labels of different length

- **WHEN** an offline test writes two labels whose located right edges differ
- **THEN** both fields are clicked at the same x = max(right edge) + gap
- **AND** both items report `geometry: input_column`

### Requirement: Form-write commit is verified by a protocol value-read of the open form

A form-field write SHALL report `committed: true` only when the requested value is confirmed by a
protocol value-read of the open form, not merely because the label was targeted on screen. After
typing, `write_form_fields_by_label` SHALL value-read the still-open form on a fresh manager connection
(resolving the already-open form by caption/newest, without navigating so the typed-but-unsaved
form-model values are preserved) and set each field's `committed`/`readback_value` from that read-back,
matched by VALUE presence (the writer targets by on-screen label, whose name differs from the descriptor
field name). A field targeted on screen but not read back SHALL be `committed: false`. The open-link
writers (`write_form_value` / `write_form_values`) SHALL derive `committed` from this read-back
(`verification: value_readback`), not from targeting alone.

#### Scenario: Committed only when the value is read back

- **WHEN** `write_form_fields_by_label` types a value and the open form's value-read returns that value
- **THEN** the item reports `committed: true` with `readback_value` equal to the read-back value
- **AND** `all_committed` is true and the `readback` block reports `verified: true`

#### Scenario: Targeted-but-not-read-back is not reported committed

- **WHEN** a field label is targeted and typed but the value-read of the open form does not return the
  requested value
- **THEN** the item reports `targeted: true` with `committed: false`
- **AND** `all_committed` is false (no false-positive commit)

#### Scenario: Live honest commit on the demo10413 create form

- **WHEN** the writer types Наименование/owner/date into the demo10413 `Catalog.ДоговорыКонтрагентов`
  create form and value-reads the open form
- **THEN** the fields read back from the form model are reported `committed: true` and the others
  `committed: false`, with retained evidence for the run

#### Scenario: The open-form value-read retries past the cold-client boundary

- **WHEN** the first value-read of the open form on a freshly launched client enumerates the element tree
  but echoes no values (`field_count: 0` with `element_count > 0`)
- **THEN** the read-back retries on a fresh connection until it reads at least one value or a bounded retry
  count is exhausted
- **AND** it reports the values (and `read_attempts`) once the client materialises them, or an honest empty
  read when it never does

### Requirement: OData data-layer tools are deprecated for a test-client-held base

The OData data-layer tools SHALL declare that they cannot verify a test-client-held infobase. The
`assert_data`, `assert_data_count`, `role_data_matrix` tools and the underlying `ODataClient` — a
file/server base opened by a «Клиент тестирования» is exclusively locked, so an out-of-process
OData/COM reader cannot open it. Each tool SHALL carry the deprecation in its description and return an
additive `deprecated: true` with guidance pointing to the same test client's protocol value-read. The
tools SHALL remain functional (valid only against a separately published, non-exclusive endpoint);
removal and the scenario/autofill/regression cleanup are a later change.

#### Scenario: OData tool result is annotated as deprecated

- **WHEN** an OData data-layer tool returns a result
- **THEN** the result additively carries `deprecated: true` and a `deprecation` message that references
  the exclusive test-client lock and points to the protocol value-read
- **AND** the tool's existing `ok`/values are unchanged (additive, non-breaking)

# Semantic Mapping Source Summary 20260603-opsx-do-semantic-mapping

Date: 2026-06-03.

This summary records sanitized provider facts used to build
`semantic_map.md`. Full provider responses, metadata payloads and local source
content are not committed here.

## Metadata Source

Provider: `meta-mcp`.

Owner route: `/opt/finshtab-1c`.

Configuration: `demo10413`.

Snapshot/build: `2026-05-24T000000Z-demo10413-edt`.

Source kind: EDT workspace.

External source root: `C:\1C_BASES\EDT\demo10413\demo10413`.

Readiness: ready during this run, with source freshness reported as fresh.

Sanitized facts used:

- Configuration summary resolved 179 metadata objects and 310 source files.
- Report inventory includes `Report.ДашбордПродажи` at
  `src/Reports/ДашбордПродажи/ДашбордПродажи.mdo`.
- `Report.ДашбордПродажи` has synonym `Продажи`, default form
  `Report.ДашбордПродажи.Form.ФормаОтчета` and form UUID
  `cb87512b-e166-46bf-8d8f-9a24fa9bc00a`.
- English/transliterated metadata searches for `DashboardSales` and
  `DashbordProdazhi` returned no objects. The stable metadata identity is the
  Russian object id from the report inventory.
- Metadata source locations identify the report object, object module and form
  module, but this summary does not copy source text or XML payloads.

## Help Source

Provider: `help-mcp`.

Owner route: `/opt/finshtab-1c`.

Platform version: `8.3.27.1786`.

Sanitized facts used:

- `TestedApplication` resolved to platform help entity
  `objects/catalog63/catalog2032/TestedApplication.html`.
- `TestedApplication.GetActiveWindow` resolved as the active-window API term.
- `TestedClientApplicationWindow` resolved as the active-window return object.
- `TestedForm` resolved as the active-form API object.
- `TestedFormField`, `TestedFormButton`, `TestedFormTable`,
  `TestedFormGroup` and `TestedFormDecoration` resolved as tested form
  element object terms.
- `FormGroupType.CommandBar`, `FormGroupType.Page` and
  `FormFieldType.CheckBoxField` resolved as platform element-kind terms.
- Semantic help search failed while looking for page terms because
  `EMBEDDING_API_URL` is not set. Exact local metadata lookup still resolved
  page-related terms.

## Protocol Evidence Inputs

Primary protocol evidence stays in:

- `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/`
- `docs/protocol-research/evidence/corpus/20260602-193802-expanded-readonly/`
- `docs/protocol-research/evidence/corpus/20260602-195407-expanded-readonly/`
- `docs/protocol-research/evidence/accepted-mappings/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`
- `docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/`

The semantic map does not change replay status, frame ranges, normalized
hashes, dynamic fields or accepted-mapping classification.

## Boundaries

- No live TestClient, Vanessa scenario, EDT mutation or runtime apply was run.
- No provider payload dumps, screenshots, full source files, raw captures,
  probe stdout or local credentials were committed.
- Unproxied-provider telemetry gaps were recorded in the OPSX trace and are
  separate from semantic mapping readiness.

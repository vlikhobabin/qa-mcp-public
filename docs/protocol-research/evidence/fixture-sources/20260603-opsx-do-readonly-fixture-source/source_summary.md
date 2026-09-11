# Fixture Source Readiness 20260603-opsx-do-readonly-fixture-source

## Inputs

- Fixture plan:
  `docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_plan.md`.
- Fixture case manifest:
  `docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_case_manifest.json`.
- External EDT source boundary:
  `C:\1C_BASES\EDT\demo10413\demo10413`.
- Local lab paths from `openspec/config.yaml` and `AGENTS.md`.

## Boundary

The external EDT source tree exists locally and contains `.project`, `DT-INF`,
`.settings` and `src`. It remains outside reviewed git changes. No generated
EDT workspace, infobase export, raw provider payload, platform log or raw UI
output is committed by this change.

Reviewed output for this readiness step is limited to this summary and
`source_scan.json`.

## Static Source Scan

A read-only PowerShell scan inspected `Form.form` files under the external
`src` tree for element-family markers. The scan found:

| Metric | Count |
| --- | ---: |
| Form files | 74 |
| Forms with `Button` markers | 48 |
| Forms with `Table` markers | 39 |
| Forms with `CommandBar` markers | 74 |
| Forms with `Page` markers | 11 |
| Forms with `Label` markers | 74 |
| Forms with `CheckBox` markers | 19 |
| Forms with all six target families | 3 |

Candidate forms with all six target families:

- `C:\1C_BASES\EDT\demo10413\demo10413\src\DataProcessors\УдалениеПомеченныхОбъектов\Forms\ОсновнаяФорма\Form.form`
- `C:\1C_BASES\EDT\demo10413\demo10413\src\DataProcessors\ЭлектроннаяПочта\Forms\Форма\Form.form`
- `C:\1C_BASES\EDT\demo10413\demo10413\src\Documents\ОперацияПоУчетуТоваров\Forms\ФормаДокумента\Form.form`

These candidate paths are source-readiness evidence only. They do not prove
that the forms are reachable in the live `vanessa_client` infobase or that the
native TestClient protocol exposes read-only rows for the families.

## Family Readiness

| Case id | Family | Source target | Expected read-only state | Expected response markers | Availability | Owner route | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `fixture-button-readonly` | `Button` | Candidate EDT form containing `form:Button` | Button metadata can be read; no click is executed | `Button`, `TestedFormButton` | `partial_source_candidate` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | Candidate form still needs live form-open and wire evidence |
| `fixture-table-readonly` | `Table` | Candidate EDT form containing `form:Table` | Table metadata can be read; no row edit or selection action is executed | `Table`, `TestedFormTable` | `partial_source_candidate` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | Live fixture reachability and stable sample data are unproven |
| `fixture-commandbar-readonly` | `CommandBar` | Candidate EDT form with `autoCommandBar` and buttons | Command bar and child command metadata are readable; no command is invoked | `CommandBar`, `TestedFormGroup`, `TestedFormButton` | `partial_source_candidate` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | Read-only metadata does not prove action safety |
| `fixture-page-readonly` | `Page` | Candidate EDT form containing page/group markers | Default page metadata is readable; page switching is not required | `Page`, `FormGroupType.Page`, `TestedFormGroup` | `partial_source_candidate` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | Page navigation with side effects remains out of scope |
| `fixture-label-readonly` | `Label` | Candidate EDT form containing label markers | Label text and visibility are readable | `Label`, `TestedFormDecoration` | `partial_source_candidate` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | Live form-open proof is still required |
| `fixture-checkbox-readonly` | `CheckBox` | Candidate EDT form containing `CheckBoxField` markers | Checkbox value, title, visibility and enabled/read-only properties are readable; no toggle is executed | `CheckBox`, `FormFieldType.CheckBoxField`, `TestedFormField` | `partial_source_candidate` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | Live fixture reachability and no-toggle behavior still need wire evidence |

## Provider And Lab Gaps

- `edt-mcp` validation was not run for this change. The read-only filesystem
  source scan is retained as the compact source-readiness evidence.
- Vanessa/runtime form-open proof is intentionally deferred to
  `run-readonly-fixture-capture-probes`.
- Raw protocol capture and direct Python-manager probing must remain usable
  without `edt-mcp`, `meta-mcp` or `vanessa-mcp` proxy telemetry.

## Safety

No 1C process was started and no UI action was performed for this readiness
step. No click, checkbox toggle, table edit, command execution, text input or
business-data mutation was performed.

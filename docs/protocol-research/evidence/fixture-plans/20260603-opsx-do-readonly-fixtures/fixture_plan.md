# Controlled Read-Only Fixture Plan 20260603-opsx-do-readonly-fixtures

## Scope

This plan closes the current `expanded-readonly` fixture gaps for `Button`,
`Table`, `CommandBar`, `Page`, `Label` and `CheckBox` by defining planned
read-only cases before any new live capture is accepted.

No live 1C, EDT or Vanessa validation was run for this planning change. The
rows below remain `pending` until a controlled fixture form is authored in an
external EDT workspace, captured through the Windows protocol tools and
confirmed by compact replay or direct Python-manager evidence.

## Fixture Source Boundary

The fixture source is planned as an external copy of the `demo10413` EDT
workspace, not as a reviewed git artifact:

- source baseline: `C:\1C_BASES\EDT\demo10413\demo10413`;
- working output: `.artifacts/openspec/plan-controlled-readonly-fixtures/20260603-opsx-do-readonly-fixtures/`;
- raw captures: `runtime/protocol-research/captures/<capture-id>/`;
- reviewed summaries: `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`.

The current accepted corpus target, the sales dashboard report form, only has
accepted `EditField` evidence. The planned fixture SHOULD be a separate
controlled read-only form or extension surface so accepted historical rows are
not rewritten while missing element families are being introduced.

## Family Plan

| Family | Case id | Fixture source or target form | Expected state | Expected response markers | Safety class | Planned evidence paths | Provider owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Button | `fixture-button-readonly` | Controlled fixture form with one visible button; suggested external source under the EDT working output | Button is visible and readable; no click is executed | `Button`, `TestedFormButton` | `read_only` | `fixture_case_manifest.json`; `runtime/protocol-research/captures/<capture-id>/`; `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | `pending` |
| Table | `fixture-table-readonly` | Controlled fixture form with one table containing stable sample rows | Table exists and read-only metadata can be queried; no row edit, selection action or write is executed | `Table`, `TestedFormTable` | `read_only` | `fixture_case_manifest.json`; `runtime/protocol-research/captures/<capture-id>/`; `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | `pending` |
| CommandBar | `fixture-commandbar-readonly` | Controlled fixture form with one command bar or command group containing disabled or inert commands | Command bar and child command metadata are readable; no command is invoked | `CommandBar`, `TestedFormGroup`, `TestedFormButton` | `read_only` | `fixture_case_manifest.json`; `runtime/protocol-research/captures/<capture-id>/`; `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | `pending`; command execution is out of scope |
| Page | `fixture-page-readonly` | Controlled fixture form with one active page group and at least one inactive page for metadata discovery | Active/default page metadata is readable; page switching is not required for acceptance | `Page`, `FormGroupType.Page`, `TestedFormGroup` | `read_only` | `fixture_case_manifest.json`; `runtime/protocol-research/captures/<capture-id>/`; `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | `pending`; navigation semantics remain out of scope if they alter state |
| Label | `fixture-label-readonly` | Controlled fixture form with one stable text decoration | Label text and visibility are readable | `Label`, `TestedFormDecoration` | `read_only` | `fixture_case_manifest.json`; `runtime/protocol-research/captures/<capture-id>/`; `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | `pending` |
| CheckBox | `fixture-checkbox-readonly` | Controlled fixture form with one checkbox field bound to inert fixture data | Checkbox value, title, visibility and enabled/read-only properties are readable; no toggle is executed | `CheckBox`, `FormFieldType.CheckBoxField`, `TestedFormField` | `read_only` | `fixture_case_manifest.json`; `runtime/protocol-research/captures/<capture-id>/`; `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | `pending` |

No family is blocked at the planning layer. Families remain unavailable in the
current live corpus until fixture source and compact evidence exist. Command
execution, checkbox toggling, table editing, page navigation with side effects
and text input are explicitly out of scope for this read-only plan.

## Verification Flow

1. Author the controlled fixture in an ignored EDT working copy.
2. Retain EDT validation output under
   `.artifacts/openspec/plan-controlled-readonly-fixtures/20260603-opsx-do-readonly-fixtures/edt-validation/`.
3. Launch only Windows-native capture/probe tooling and clean only owned PIDs.
4. Keep raw capture traffic under `runtime/protocol-research/captures/<capture-id>/`.
5. Write compact corpus evidence under
   `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`.
6. Accept a row only after reviewed evidence records frame range, normalized
   hash, dynamic fields, operation token, response markers and replay or direct
   Python-manager status.

## Current Validation Status

The local lab was not used during this planning delivery because no controlled
fixture source has been authored yet. The static fixture manifest was parsed
locally; live fixture validation is a required follow-up before these pending
cases can become accepted mappings.

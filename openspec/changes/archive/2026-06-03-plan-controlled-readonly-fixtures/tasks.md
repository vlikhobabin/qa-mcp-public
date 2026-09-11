## 1. Fixture Coverage Plan

- [x] 1.1 Add a controlled fixture coverage plan under `docs/protocol-research/evidence/fixture-plans/<run-id>/` for `Button`, `Table`, `CommandBar`, `Page`, `Label` and `CheckBox`.
- [x] 1.2 For each family, record case id, fixture source or target form, expected state, expected response markers, safety class, planned evidence paths, provider owner and status.
- [x] 1.3 Mark any family that cannot be represented safely as blocked or out of scope with owner route and residual risk.

## 2. Corpus Integration

- [x] 2.1 Add or update an explicit read-only corpus manifest or seeded case definition for covered fixture families without adding click, input, command execution or write semantics.
- [x] 2.2 Document how optional EDT authoring and validation output is retained outside git while compact summaries are linked from reviewed evidence.
- [x] 2.3 Update `docs/protocol-research/protocol-corpus-runner.md` and `docs/protocol-research/evidence-index.md` with the fixture plan and expected verification flow.

## 3. Verification

- [x] 3.1 Run `scripts\check.ps1`.
- [x] 3.2 If the local lab is ready, run the Windows-native fixture validation or corpus dry run and retain compact evidence under the planned fixture/corpus run id. No live fixture has been authored yet; the planned manifest was parsed statically and the live run is recorded as a follow-up in `fixture_plan.md`.
- [x] 3.3 Run `bin\openspec.cmd validate plan-controlled-readonly-fixtures --strict`.
- [x] 3.4 Run `git diff --check -- openspec/changes/plan-controlled-readonly-fixtures docs/protocol-research tools/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Controlled read-only fixture form shapes for `Button`, `Table`, `CommandBar`, `Page`, `Label` and `CheckBox` | Family-by-family fixture plan with target form/element state and expected markers | Fixture plan, optional EDT validation report, optional Vanessa form tree or retained UI smoke bundle when live validation runs | `docs/protocol-research/evidence/fixture-plans/<run-id>/fixture_plan.md`; `.artifacts/openspec/plan-controlled-readonly-fixtures/<run-id>/` | required | `/opt/edt-lab`, `/opt/vanessa-mcp-stack` | N/A | Medium: live form availability and fixture authoring may be environment-dependent |
| Metadata object | Optional demo metadata or EDT source used to author fixture form shapes | Metadata/EDT source summary and generated-output boundary | Sanitized source summary, EDT validation report when fixture source is authored, no full export committed | `docs/protocol-research/evidence/fixture-plans/<run-id>/source_summary.md`; `.artifacts/openspec/plan-controlled-readonly-fixtures/<run-id>/edt-validation/` | required | `/opt/finshtab-1c`, `/opt/edt-lab` | N/A | Medium: metadata source may not expose enough stable form-element identifiers |
| Delivery or runtime apply | Fixture-derived read-only corpus capture and direct Python-manager/replay confirmation | Windows-native capture/probe command plan with owned-PID cleanup expectation | Compact corpus evidence, replay/probe summary, cleanup proof; raw captures remain in ignored runtime paths | `docs/protocol-research/evidence/corpus/<run-id>-fixture-readonly/`; `runtime/protocol-research/captures/<run-id>/` | required | `project:qa-mcp` | N/A | Medium: live 1C startup and capture timing can fail and must be recorded as a provider/lab gap |
| Form module or command | Command execution and form-command handlers | N/A | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Fixture scope is read-only; command execution, clicks and input are reserved for the safe-action card | Medium: `CommandBar` read-only state may later need command-specific action evidence |

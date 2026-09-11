## 1. Source Boundary

- [x] 1.1 Identify the external fixture source under an ignored boundary such
  as `.artifacts/openspec/prepare-controlled-readonly-fixture-source/<run-id>/`
  or an explicitly documented EDT workspace outside git.
- [x] 1.2 Write
  `docs/protocol-research/evidence/fixture-sources/<run-id>/source_summary.md`
  with source location, provider owner, generated-output boundary and safety
  class.
- [x] 1.3 Record whether the source is based on the existing demo workspace,
  an external extension, or an existing controlled form.

## 2. Family Readiness

- [x] 2.1 For `fixture-button-readonly`, `fixture-table-readonly`,
  `fixture-commandbar-readonly`, `fixture-page-readonly`,
  `fixture-label-readonly` and `fixture-checkbox-readonly`, record target
  form/element, expected read-only state, response markers and availability.
- [x] 2.2 Retain compact EDT/meta/Vanessa validation summaries when they are
  used, without committing raw provider output.
- [x] 2.3 Mark unavailable families as `blocked`, `pending` or `partial` with
  owner route and residual risk.

## 3. Verification

- [x] 3.1 Run `scripts\check.ps1`.
- [x] 3.2 Run any available Windows-native source or EDT validation command and
  retain compact evidence, or record the provider/lab gap.
- [x] 3.3 Run
  `bin\openspec.cmd validate prepare-controlled-readonly-fixture-source --strict`.
- [x] 3.4 Run
  `git diff --check -- openspec/changes/prepare-controlled-readonly-fixture-source docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Controlled fixture form exposing `Button`, `Table`, `CommandBar`, `Page`, `Label` and `CheckBox` | Family readiness table with target form/element and expected state | EDT validation summary, Vanessa form tree or compact source summary | `docs/protocol-research/evidence/fixture-sources/<run-id>/source_summary.md`; `.artifacts/openspec/prepare-controlled-readonly-fixture-source/<run-id>/` | required | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: fixture form may not expose all families safely |
| Metadata object | Optional demo metadata or EDT source used to author fixture form shape | Source boundary and generated-output policy | Sanitized metadata/source summary; provider-gap record when unavailable | `docs/protocol-research/evidence/fixture-sources/<run-id>/source_summary.md` | required | `/opt/finshtab-1c`, `/opt/edt-lab` | N/A | Medium: metadata identifiers may not be stable enough for family targeting |
| Delivery or runtime apply | Live protocol capture and direct probe | N/A for this change | N/A | N/A | N/A | `project:qa-mcp` | This change prepares source readiness only; live capture is handled by `run-readonly-fixture-capture-probes` | Low: capture readiness is deferred to the next ordered change |
| Form module or command | Clicks, command handlers, checkbox toggles and input handlers | N/A | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Read-only fixture preparation excludes action/write semantics | Medium: command-bar read-only metadata may not prove command action safety |

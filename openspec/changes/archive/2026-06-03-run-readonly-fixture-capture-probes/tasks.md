## 1. Capture Preparation

- [x] 1.1 Confirm the fixture source readiness evidence from
  `prepare-controlled-readonly-fixture-source`.
- [x] 1.2 Select a run id and create ignored runtime output roots under
  `runtime/protocol-research/captures/<capture-id>/` and
  `runtime/protocol-research/python-manager-probe/<probe-id>/`.
- [x] 1.3 Confirm the case manifest path:
  `docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_case_manifest.json`.

## 2. Live Capture And Probe

- [x] 2.1 Run a Windows-native fixture corpus capture, for example:
  `python tools\protocol-research\protocol_corpus_runner.py --run-capture --capture-scenario form-analysis --case-manifest docs\protocol-research\evidence\fixture-plans\20260603-opsx-do-readonly-fixtures\fixture_case_manifest.json --evidence-dir docs\protocol-research\evidence\corpus\<capture-id>-fixture-readonly --json`.
- [x] 2.2 If the fixture form requires a different supported scenario or
  wrapper, record the exact command and owner route; do not accept rows that
  were not actually captured.
- [x] 2.3 Run direct Python-manager probe confirmation where supported, for
  example:
  `python tools\protocol-research\python_manager_probe.py --capture-dir runtime\protocol-research\captures\<capture-id> --manager-templates runtime\protocol-research\captures\<capture-id>\manager_frame_templates.json --query form-element-details --output-dir runtime\protocol-research\python-manager-probe\<probe-id> --json`.
- [x] 2.4 Retain compact corpus/probe summaries under reviewed evidence paths
  and keep raw payloads under ignored runtime paths.

## 3. Verification

- [x] 3.1 For every available family, record capture id, frame range, request
  and response sizes, normalized hash, dynamic fields, operation token,
  response markers and probe/replay status, or an unresolved reason.
- [x] 3.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 3.3 Run `scripts\check.ps1`.
- [x] 3.4 Run
  `bin\openspec.cmd validate run-readonly-fixture-capture-probes --strict`.
- [x] 3.5 Run
  `git diff --check -- openspec/changes/run-readonly-fixture-capture-probes docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Windows-native fixture capture/probe run against local TestClient lab | Command transcript summary, owned-PID cleanup expectation and runtime output boundary | Compact corpus evidence, compact probe evidence, cleanup proof; raw captures ignored | `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/`; `runtime/protocol-research/captures/<capture-id>/` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A | Medium: live 1C startup, fixture form targeting or timing may fail |
| Managed form layout | Fixture form elements for `Button`, `Table`, `CommandBar`, `Page`, `Label` and `CheckBox` | Read-only form/element query plan and expected markers | Form tree or equivalent compact runtime summary when available; corpus rows per family | `.artifacts/openspec/run-readonly-fixture-capture-probes/<run-id>/`; `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: element families may remain unavailable or ambiguous |
| BSL-only module edit | Python protocol tools only; no BSL source edit planned | N/A | N/A | N/A | N/A | `project:qa-mcp` | No BSL or 1C source code is changed by this capture/probe delivery | Low: runtime behavior is verified by live read-only evidence instead |
| Form module or command | Clicks, command handlers, checkbox toggles and input handlers | N/A | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Scope is read-only; action/write semantics are reserved for a separate safe-action card | Medium: read-only command-bar evidence does not prove command execution behavior |

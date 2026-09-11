## Context

After bare-create foregrounding works, the contract create form still needs the
owner reference `Владелец` set from the UI. The existing `set_reference_field`
path was built around a fixture reference field and fixed-length retargeting,
so it is not suitable for arbitrary open-link create forms or variable-length
counterparty names.

## Goals / Non-Goals

**Goals:**
- Add a create-form reference field step that can target a visible label such as
  `Владелец`.
- Accept variable-length display values and fail closed when a reference
  selector or field label cannot be resolved.
- Make the step usable from the open-link create scenario path.

**Non-Goals:**
- Do not replace the existing fixture-specific `set_reference_field` helper.
- Do not own save/persistence cleanup proof; this change stops at setting the
  owner on the foregrounded form.

## Decisions

- Represent reference input as an explicit step or field mode rather than
  overloading plain text input silently. That lets unsupported reference writes
  fail before save.
- Use the display backend and the existing label-location discipline for the
  field entry point, then drive the reference selector with a bounded,
  evidence-producing selection routine.
- Return a result per reference step with `label`, `value`, `targeted`,
  `selected`, and `reason` fields so scenario summaries can distinguish label
  location from selector failure.
- Keep fixture `set_reference_field` unchanged for captures that still depend
  on it.

## Risks / Trade-offs

- Reference chooser layouts can vary by configuration. Mitigation: require live
  proof on the demo10413 `Владелец` field and fail closed on missing selector
  markers.
- Selecting by display text can be ambiguous. Mitigation: record ambiguity in
  the result and do not continue to save when a selector reports ambiguity.
- Reference selection uses UI automation and therefore needs retained evidence.
  Mitigation: matrix requires scenario log plus active-window/form evidence.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI | `Владелец` reference field on `Справочник.ДоговорыКонтрагентов` create form | Live scenario foregrounds create form and selects a known `Контрагент` owner | `qa_testclient_bundle`, `scenario_log`, `active_window`, `form_tree`, `screenshot/fallback` | `.artifacts/openspec/native-write-open-link-reference-owner/20260630T113200Z/live-reference-owner.json` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Static/BSL | Python-only qa-mcp routing and tests | Offline pytest and source diff review | `source_preflight`, focused pytest output | `.artifacts/openspec/native-write-open-link-reference-owner/20260630T113200Z/pytest.log` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Live-read proof | Fixture owner availability | Read-only fixture probe identifies a usable `Контрагент` display value before UI selection | `live_read_proof` or retained fixture summary | `.artifacts/openspec/native-write-open-link-reference-owner/20260630T113200Z/fixture-owner.json` | required | `/opt/ai-dev-suite-for-1c/live-mcp` |  |  |
| Cleanup audit | Owner set without save | No record is persisted by this slice | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | reference selection proof stops before save | cleanup required by later save proof |

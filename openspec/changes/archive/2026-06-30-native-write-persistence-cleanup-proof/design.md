## Context

The create scenario runner accepts a `persistence_verifier`, but the MCP tool
currently reports a hard-coded provider gap for open-link create flows. The
card acceptance requires a real contract save, read-back of auto-built
`Наименование` and `Основной`, plus cleanup evidence for created demo10413 test
records.

## Goals / Non-Goals

**Goals:**
- Add a persistence verifier that can report read-back/list/data assertion
  evidence for created records.
- Require cleanup or explicit residual risk before accepting a mutation proof.
- Record first-contract and second-contract expectations for the same owner.

**Non-Goals:**
- Do not add broad live-write permission outside explicitly requested create
  scenarios.
- Do not commit raw runtime logs, screenshots, infobase dumps or credentials.

## Decisions

- Treat persistence verification and cleanup as explicit scenario options. A
  save claim without requested verification or cleanup evidence stays failed or
  provider-gap, not silently accepted.
- Use existing qa-mcp read helpers where possible for read-back and list-grid
  assertions; allow a read-only live route only when it records owner, command
  and artifact path.
- Model cleanup as a reviewed route with pre-state, created object identity,
  cleanup action and final-state check. Missing cleanup evidence blocks archive
  for the mutation proof.
- Keep raw evidence in `.artifacts/openspec/<change>/<run-id>/` and include
  only bounded summaries in docs/OpenSpec.

## Risks / Trade-offs

- Live writes can leave data if cleanup fails. Mitigation: run only after Linux
  runtime preflight and retain cleanup residuals before accepting proof.
- Read-back may not expose a stable record identifier from UI input alone.
  Mitigation: scenario output must record the identifying fields used by the
  read-back route.
- The first/second contract assertion depends on fixture state. Mitigation:
  preflight records owner contract count and cleanup isolates created records.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI | Full contract create/save scenario | Live scenario fills owner, date, number, saves, and records result statuses | `qa_testclient_bundle`, `scenario_log`, `active_window`, `form_tree`, `screenshot/fallback`, `junit_report` when available | `.artifacts/openspec/native-write-persistence-cleanup-proof/20260630T121500Z/live-summary.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Data assertion | Created `ДоговорыКонтрагентов` record | Read-back or list/data assertion checks `Наименование` and `Основной` for first and second owner contracts | `data_assertion`, `live_read_proof`, `ui_data_assertion` | `.artifacts/openspec/native-write-persistence-cleanup-proof/20260630T121500Z/data-assertion.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Cleanup audit | Created demo10413 contract records | Reviewed cleanup deletes/rolls back created records and checks unresolved leftovers | `cleanup_evidence`, final-state summary | `.artifacts/openspec/native-write-persistence-cleanup-proof/20260630T121500Z/cleanup-summary.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Static/BSL | Python-only qa-mcp routing and tests | Offline pytest and source diff review | `source_preflight`, focused pytest output | `.artifacts/openspec/native-write-persistence-cleanup-proof/20260630T121500Z/pytest.log` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Runtime apply | 1C configuration import/deploy | No 1C metadata or BSL source is changed | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | qa-mcp Python runtime only; demo10413 catalog already live from prior evidence | stale fixture state may still affect live proof and must be reported |

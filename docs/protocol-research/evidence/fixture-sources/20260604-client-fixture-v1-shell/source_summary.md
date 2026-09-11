# Client Fixture V1 Shell Source Summary

Дата среза: 2026-06-04.

## Scope

Change: `add-client-fixture-v1-processor-shell`.

This evidence records source-level readiness for the V1 client fixture
processor shell. It does not claim a live DB update, TestClient form-open
result, frame range, normalized hash or accepted protocol mapping.

## Source Boundary

- EDT workspace: `C:\1C_BASES\EDT\vanessa_qa`.
- EDT project: `vanessa_client`.
- Target context: `client`.
- Infobase binding from registry:
  `File="C:\\1C_BASES\\vanessa_client";`.
- Source object:
  `src/DataProcessors/ФикстураПротоколаTestClient/`.

## Implemented Shell Markers

| Marker | Source role | Status |
| --- | --- | --- |
| `PF_FORM_MAIN` | top-level form group/title marker | source-authored |
| `PF_FIXTURE_VERSION` | fixture version attribute and field | source-authored |
| `protocol-fixture.v1` | deterministic version value | source-authored |
| `PF_LAST_ACTION` | local fixture state field | source-authored |
| `PF_ACTION_COUNTER` | local fixture state field | source-authored |
| `PF_SELECTED_ROW_MARKER` | local fixture state field | source-authored |
| `PF_RESET_STATE` | future reset command hook | source-authored; not action-accepted |

## Verification Notes

- `validate_project_infobase_binding(target_id="client")` was invoked through
  the live `edt-mcp` tool and timed out after 120 seconds in this run.
- A prior bounded validation in this workspace proved the same `client`
  binding with `timeout_seconds=90`, but this run records the current tool
  timeout as a provider gap.
- No retrieve, DB update, hot deploy or runtime apply was performed during
  this change.
- No raw TCP capture or runtime log is committed.

## Provider Gap

```yaml
provider_gap:
  provider_id: edt-mcp
  owner_path: /opt/edt-lab
  matrix_row: delivery_or_runtime_apply
  missing_capability: bounded validate_project_infobase_binding was not available through the loaded tool schema
  missing_evidence_type: runtime_apply_log
  impact: live apply and TestClient form-open evidence are deferred
  current_workaround: source-level EDT authoring with compact evidence only
  source_card: openspec/board/2.todo/01-2026-06-04-client-fixture-v1-control-surface.md
  sanitized_evidence: docs/protocol-research/evidence/fixture-sources/20260604-client-fixture-v1-shell/source_summary.md
  sensitivity: no credentials or raw runtime payloads copied
```

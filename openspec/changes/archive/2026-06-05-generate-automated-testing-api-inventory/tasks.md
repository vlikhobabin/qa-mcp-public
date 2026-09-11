## 1. Inventory Generation

- [x] 1.1 Query `help-mcp` or the approved help source for automated-testing
  and client-agent API objects.
- [x] 1.2 Extract object names, aliases, members, constructors, parameters,
  return types and owner sections when available.
- [x] 1.3 Apply conservative default safety classes:
  `read_only`, `safe_ui_action`, `mutation`, `agent_runtime` or
  `unsupported_initial`.
- [x] 1.4 Write the inventory JSON under
  `docs/protocol-research/api-inventory/automated-testing-<platform>.json`.
- [x] 1.5 Write a compact summary and gap report under the same directory.
- [x] 1.6 Link the inventory from protocol research docs and the evidence
  index where appropriate.

## 2. Verification

- [x] 2.1 Validate inventory JSON syntax with a Windows-native parser.
- [x] 2.2 Check that every inventory row records source version or source gap.
- [x] 2.3 Review safety classification for the first read-only and safe-action
  candidate families.
- [x] 2.4 Run `openspec validate generate-automated-testing-api-inventory --strict`.
- [x] 2.5 Run `git diff --check -- openspec/changes/generate-automated-testing-api-inventory docs/protocol-research`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Live 1C runtime | N/A | N/A | N/A | N/A | `project:qa-mcp` | Inventory uses platform help and does not apply runtime changes | Low: no runtime behavior is changed |
| BSL-only module edit | 1C BSL source | N/A | N/A | N/A | N/A | `project:qa-mcp` | No BSL source is changed | Low: none |
| Metadata object | API inventory documentation artifact | Help-source extraction summary and gap report | `data_assertion`, `live_read_proof` when provider exposes source metadata | `docs/protocol-research/api-inventory/` | required | `/opt/finshtab-1c`, `project:qa-mcp` | N/A | Medium: help source version may differ from lab runtime version |
| Managed form layout | Managed forms | N/A | N/A | N/A | N/A | `project:qa-mcp` | No managed form layout is changed | Low: none |

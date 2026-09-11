# Manager Fixture V1 Side-Channel Form Path Contract

- Catalog version: `2026-06-06.3`
- Focused proof capture: `runtime/protocol-research/captures/20260606-side-channel-form-path-focused-proof`
- Focused proof report: `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-form-path-focused-proof/`
- Catalog drift check: `catalog_comparison.json`, status `ok`

## Accepted

| case id | side-channel marker | observed result preview | frame range | normalized hash |
| --- | --- | --- | --- | --- |
| `tm-v1-diag-window-get-form-path` | `form_path_attempted=` | `form_path_attempted=DataProcessor.ФикстураПротоколаTestClient.Form.Форма;form_title=QA MCP Protocol Fixture V1;child_count=2` | `16..326` | `0244782c3c4f28c8b3ad0bbf5dfaf37916cb642f0d82debe8543fdd08c71f85a` |

## Boundary

This row is accepted by typed manager side-channel evidence:
`manager_case_event.after.result_preview`. It is not claimed as a direct wire
marker observation. The command verifies that the manager harness can resolve
the active TestClient form by path/title and retain the joined protocol frame
range plus normalized hash for that diagnostic operation.

After this proof, all nine formerly pending manager fixture V1 readonly rows
from card `09-2026-06-06-manager-fixture-v1-promote-pending-readonly-rows.md`
have an accepted contract-backed mapping.

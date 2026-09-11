# Manager Fixture V1 Candidate Marker Contract Promotion

- Catalog version: `2026-06-06`
- JSON catalog: `tools/protocol-research/manager_fixture_v1_command_catalog.json`
- BSL catalog source: `C:\1C_BASES\EDT\vanessa_qa\vanessa_manager\src\DataProcessors\ProtocolFixtureTestManager\Forms\ManagerHarness\Module.bsl`
- Catalog drift check: `catalog_comparison.json`, status `ok`
- Dry-run manifest: `runtime/protocol-research/captures/20260606-promote-candidate-marker-contracts-dryrun`
- Focused proof capture: `runtime/protocol-research/captures/20260606-promote-candidate-marker-contracts-focused-proof`
- Accepted focused report: `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-promote-candidate-marker-contracts-focused-proof-accepted/`
- Direct probe summary: `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-promote-candidate-marker-contracts-focused-proof/summary.json`

## Applied Contract Changes

| case id | previous expected marker | corrected expected marker |
| --- | --- | --- |
| `tm-v1-diag-window-find-form-marker` | `PF_FIXTURE_VERSION` | `QA MCP Protocol Fixture V1` |
| `tm-v1-form-summary` | `PF_FIXTURE_VERSION` | `QA MCP Protocol Fixture V1` |
| `tm-v1-button-inert` | `TestedFormButton` | `PF_BUTTON_INERT` |
| `tm-v1-table-items` | `PF_ROW_001` | `PF_TABLE_ITEMS` |
| `tm-v1-group-main` | `PF_FORM_MAIN` | `PF_GROUP_MAIN` |

## Verification Result

The focused proof selected active-window plus the nine formerly pending rows.
All 10 command windows joined. Direct marker replay accepted six former pending
rows:

- `tm-v1-diag-window-find-form-marker`
- `tm-v1-form-summary`
- `tm-v1-checkbox-true`
- `tm-v1-button-inert`
- `tm-v1-table-items`
- `tm-v1-group-main`

Three former pending rows remain blocked:

- `tm-v1-diag-command-interface-dump`
- `tm-v1-diag-window-children`
- `tm-v1-diag-window-get-form-path`

The count rows expose the count in manager-harness side-channel preview, not
as a current direct wire marker. They need a typed side-channel/count contract
or a protocol collection-count parser before they can be accepted. The
form-path diagnostic row needs isolation or endpoint retargeting because the
candidate title marker was rejected and `PF_FIXTURE_VERSION` was not observed.

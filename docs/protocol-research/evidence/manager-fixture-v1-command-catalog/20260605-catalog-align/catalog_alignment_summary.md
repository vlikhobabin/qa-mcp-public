# Manager Fixture V1 Command Catalog Alignment

Run id: `20260605-catalog-align`

Reviewed source of truth:

- `tools/protocol-research/manager_fixture_v1_command_catalog.json`

Aligned consumers:

- PowerShell manifest generator:
  `tools/protocol-research/run_protocol_capture.ps1`
- Manager harness BSL catalog:
  `C:\1C_BASES\EDT\vanessa_qa\vanessa_manager\src\DataProcessors\ProtocolFixtureTestManager\Forms\ManagerHarness\Module.bsl`

Catalog decision:

- Full V1 read-only catalog contains 11 commands.
- First live smoke subset is recorded separately as:
  `tm-v1-active-window`, `tm-v1-active-form`, `tm-v1-field-version`.
- Target fixture path is the real client fixture runtime form:
  `DataProcessor.ФикстураПротоколаTestClient.Form.Форма`.
- V1 still rejects action/mutation command kinds:
  `text_input`, `click`, `page_switch`, `row_select`,
  `business_command`, `object_write`.

Verification:

- `manager_fixture_v1_command_catalog.json` parsed with Windows PowerShell
  `ConvertFrom-Json`.
- `run_protocol_capture.ps1 -Scenario manager-fixture-v1-readonly -DryRun`
  generated `manager_harness_manifest.json` with 11 commands and the three
  smoke subset case ids.
- `compare_manager_fixture_v1_catalog.ps1` compared BSL calls with the JSON
  catalog for `case_id`, `command_id`, `command_kind`, `target_marker`,
  `expected_marker` and `element_family`.
- Result: `catalog_comparison.json` status is `ok`, with 11 catalog commands
  and 11 BSL commands.

Runtime note:

- This is catalog/tooling evidence only. No live TestClient traffic, frame
  ranges, replay result or accepted protocol mapping is claimed here.

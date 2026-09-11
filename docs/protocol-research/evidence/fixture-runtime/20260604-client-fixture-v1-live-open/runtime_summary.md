# Client Fixture V1 Live Open Evidence

Date: 2026-06-04.

Scope:

- EDT project: `C:\1C_BASES\EDT\vanessa_qa\vanessa_client`
- Infobase: `C:\1C_BASES\vanessa_client`
- Fixture: `Обработка.ФикстураПротоколаTestClient`
- Form: `Обработка.ФикстураПротоколаTestClient.Форма.Форма`

## Result

The client fixture V1 was applied to the live `vanessa_client` infobase and
opened through Vanessa/TestClient.

Runtime proof:

- `validate_project_infobase_binding(target_id="client")` returned `ok=true`;
  binding status was `matched`, project `vanessa_client` was linked to
  infobase `vanessa_client`, and deploy was allowed.
- Initial EDT deploy returned `ok=true`, `outcome=updated`,
  `updateStatus.message="ОК"`, and changed synchronization state from
  `NOT_EQUAL/projectDirty=true` to `EQUAL/projectDirty=false`.
- First live open exposed a form-module bug:
  `PF_TABLE_ITEMS = Новый ТаблицаЗначений` attempted to replace a managed-form
  data object and raised `Нельзя изменять поле, содержащее объект данных формы`.
- The source fix changed table reset to `PF_TABLE_ITEMS.Очистить()` in
  `Module.bsl`.
- Follow-up EDT deploy returned `ok=true`, `outcome=updated`,
  `updateStatus.message="ОК"`, and synchronization state `EQUAL`.
- Vanessa step `И я открываю основную форму обработки "ФикстураПротоколаTestClient"`
  then completed successfully.
- Vanessa `get_form_analysis(format="full")` reported window
  `QA MCP Protocol Fixture V1` and form
  `Обработка.ФикстураПротоколаTestClient.Форма.Форма`.

Observed form markers:

- `PF_FIXTURE_VERSION = protocol-fixture.v1`
- `PF_LAST_ACTION = PF_STATE_INITIAL`
- `PF_ACTION_COUNTER = 0`
- `PF_SELECTED_ROW_MARKER = PF_ROW_NONE`
- edit fields: `PF_EDIT_STRING`, `PF_EDIT_NUMBER`, `PF_EDIT_DATE`,
  `PF_EDIT_READONLY`, `PF_EDIT_DISABLED`
- checkboxes: `PF_CHECKBOX_TRUE`, `PF_CHECKBOX_FALSE`,
  `PF_CHECKBOX_READONLY`, `PF_CHECKBOX_DISABLED`
- command bar: `PF_COMMAND_BAR_MAIN`, `PF_RESET_STATE`,
  `PF_COMMAND_ENABLED`, `PF_COMMAND_DISABLED`, `PF_COMMAND_POPUP`,
  `PF_COMMAND_POPUP_CHILD`
- table: `PF_TABLE_ITEMS` with rows `PF_ROW_001`, `PF_ROW_002`,
  `PF_ROW_003`
- pages/groups: `PF_PAGES_MAIN`, `PF_PAGE_A`, `PF_PAGE_B`,
  `PF_GROUP_DISABLED`

Runtime artifacts retained locally:

- Vanessa fallback form evidence:
  `runtime\protocol-research\fixture-v1-live-open\`
- TCP-only active-window probe:
  `runtime\protocol-research\python-manager-probe\client-fixture-v1-active-window-20260604-172832\`
- TCP-only active-form probe:
  `runtime\protocol-research\python-manager-probe\client-fixture-v1-active-form-20260604-172832\`
- TCP-only form-element-details probe:
  `runtime\protocol-research\python-manager-probe\client-fixture-v1-live-20260604-172806\`

## TCP Notes

The full `tools\protocol-research\run_protocol_capture.ps1` capture route was
not run during this check because it starts its own TestClient on the default
port and asserts that the target infobase is not already used by 1C processes.
At the time of testing, the live Vanessa TestClient and EDT Designer Agent were
already attached to `C:\1C_BASES\vanessa_client`.

Direct TCP probes were run against the already-open Vanessa TestClient port
`48001`. They do not start or stop 1C processes. The active-window probe
returned `status=ok`, `evidence_status=accepted`, sent 2548 bytes, received
3589 bytes, and included the fixture marker
`e1cib/app/Обработка.ФикстураПротоколаTestClient` plus the caption
`QA MCP Protocol Fixture V1` in decoded frame strings.

The older `active-form-context` and `form-element-details` templates still
resolve the previous dashboard managed form in part of their semantic result.
Treat that as a protocol-template gap for the next capture/probe iteration, not
as a fixture runtime-open failure.

## Tooling Gaps

- `deploy_infobase_probe` returned an early `WinError 2`; the direct
  `deploy_infobase` path was used instead.
- `sync_bsl_resource_meta` and `deploy_bsl_resource_direct_incremental` hit
  EDT 2026.1 internal API compatibility gaps.
- `validate_bsl_modules` timed out after 120 seconds.
- OS screenshot capture was disabled in the current lazy Vanessa manager
  session; Vanessa fallback evidence was accepted instead.

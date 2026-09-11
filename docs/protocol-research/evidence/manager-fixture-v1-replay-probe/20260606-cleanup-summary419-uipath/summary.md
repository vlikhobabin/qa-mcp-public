# Manager Fixture V1 Replay Probe: Summary 419 UI Path

Source capture:
`runtime/protocol-research/captures/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

Curated join evidence:
`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

## Outcome

- The replay sent 419 manager frames and received 419 responses with no
  `no_response` stop.
- Five additional rows are semantically confirmed by endpoint responses:
  `tm-v1-active-window`, `tm-v1-active-form`,
  `tm-v1-diag-window-find-field-marker`,
  `tm-v1-diag-form-find-field-marker` and `tm-v1-pages-main`.
- Runtime evidence is retained under
  `runtime/protocol-research/replay-probe/20260606-manager-fixture-cleanup-summary419-uipath-v1/`.

## Dynamic Fields

Successful replay command shape:

```powershell
python tools\protocol-research\replay_probe.py `
  runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly-cleanup `
  --port 15381 `
  --send-count 419 `
  --adapt-frame4-guid `
  --adapt-frame5-guid `
  --adapt-frame5-random-blocks `
  --adapt-binary-single-block-through 121 `
  --adapt-binary-single-block-frames '123-129,131-174,176-187,189-210,212-231,233-294,296-300,302-307,309-359,361-367,369-371,373-381,383,386,388-394,396-399,402-405,408-411,414-417' `
  --adapt-binary-guid-through 419 `
  --adapt-ui-path-guids `
  --stop-on-no-response
```

Observed in the successful replay:

- ACK GUID from response after send `3`:
  `65769232-e953-4b39-9eaf-8ba6df5faf1f`.
- `MainFrame` GUID from response after send `6`:
  `6ca75e50-62a3-4842-b6cd-b429f7591ef2`.
- `SecondaryFrame` GUID from response after send `15`:
  `2757ad56-6318-4d52-993f-6db40b2ba9db`.
- `ManagedForm` GUID from response after send `15`:
  `95d7e9d7-5ff3-476b-afc8-ffb2c084be35`.

## Accepted Case Results

| case_id | manager frames | response after send | normalized hash | accepted marker |
| --- | ---: | ---: | --- | --- |
| `tm-v1-active-window` | `16..16` | `16` | `957a636f135c2e62f55dd276f5e63e55c025f1b1f59c3bb27035f6bbd13f2276` | `QA MCP Protocol Fixture V1` |
| `tm-v1-active-form` | `17..17` | `17` | `ef520f4818b5280f39ccdc970dbb1bb4a4657f5a5e53a029679dd245f4cbf2da` | `QA MCP Protocol Fixture V1` |
| `tm-v1-diag-window-find-field-marker` | `110..112` | `112` | `2a8d204d56acf5dd4b277c94c471de02daa1851d747d5257b2fbb5101cd99641` | `protocol-fixture.v1` |
| `tm-v1-diag-form-find-field-marker` | `113..116` | `116` | `405796082d6061cd8656ec59db08b72eab762ccc112d5d72c2de06b8c13cd9b9` | `protocol-fixture.v1` |
| `tm-v1-pages-main` | `414..419` | `419` | `cd46b1bbc7b51ece7c7e6dfee8062d1f805a62113cf745b44aeb1b7a310aaee7` | `PF_PAGE_A` |

## Non-Accepted Observations

These rows replayed transport-level successfully but are not promoted because
their declared `expected_marker` was not present in the endpoint response:

| case_id | manager frames | observed marker | missing expected marker |
| --- | ---: | --- | --- |
| `tm-v1-checkbox-true` | `126..130` | `PF_CHECKBOX_TRUE` | `CheckBox` |
| `tm-v1-button-inert` | `131..390` | `pf_button_inert` | `TestedFormButton` |
| `tm-v1-table-items` | `396..401` | `PF_TABLE_ITEMS` | `PF_ROW_001` |
| `tm-v1-group-main` | `408..413` | `PF_GROUP_MAIN` | `PF_FORM_MAIN` |

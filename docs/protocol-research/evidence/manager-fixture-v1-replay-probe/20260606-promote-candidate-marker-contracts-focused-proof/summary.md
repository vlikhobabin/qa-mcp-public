# Manager Fixture V1 Candidate Marker Contract Focused Proof

- Source capture: `runtime/protocol-research/captures/20260606-promote-candidate-marker-contracts-focused-proof`
- Direct probe runtime: `runtime/protocol-research/manager-fixture-marker-probe/20260606-promote-candidate-marker-contracts-focused-proof`
- Transport status: `ok`
- Accepted previous pending rows: `6`
- Remaining previous pending rows: `3`

## Accepted

| case id | expected marker | frame range | normalized hash |
| --- | --- | --- | --- |
| `tm-v1-diag-window-find-form-marker` | `QA MCP Protocol Fixture V1` | `22..24` | `5d87ccd9f0c08ea313b9378dff7fe65abcfb3f3e5355bd15d3fb8e9294ca51f2` |
| `tm-v1-form-summary` | `QA MCP Protocol Fixture V1` | `365..367` | `33f8fb78e26a3aa64d0b111942140a3b19eba163e3e2ab875cfa81a5ccc1ad3f` |
| `tm-v1-checkbox-true` | `CheckBox` | `368..372` | `1ea7dc4c026fb1a000214163de81b6edf32751c0442ddf12de7d00e485e2987d` |
| `tm-v1-button-inert` | `PF_BUTTON_INERT` | `373..1020` | `926585521047f8e7e2abe2316dacbbf690142f04867c73cb12c172139a153e86` |
| `tm-v1-table-items` | `PF_TABLE_ITEMS` | `1025..1030` | `9c09bc0e84e5e14f6215ccb858e5d4cb07a0bd99bf0228b55256259c719e89a6` |
| `tm-v1-group-main` | `PF_GROUP_MAIN` | `1031..1036` | `88ffe72ff1b8392c56b8cf999151ef66b1db837e8edfee734a0d197d402e04b8` |

## Remaining Blocked

| case id | expected marker | observed markers | next route |
| --- | --- | --- | --- |
| `tm-v1-diag-command-interface-dump` | `ci_children_count=` | `homepage[<guid>], homepage, e1cib/navigationpoint/startpage` | Add a typed side-channel/count contract or protocol collection-count parser; direct wire marker replay does not expose ci_children_count=. |
| `tm-v1-diag-window-children` | `window_children_count=` | `homepage[<guid>], homepage, e1cib/navigationpoint/startpage` | Add a typed side-channel/count contract or protocol collection-count parser; direct wire marker replay does not expose window_children_count=. |
| `tm-v1-diag-window-get-form-path` | `PF_FIXTURE_VERSION` | `homepage[<guid>], homepage, e1cib/navigationpoint/startpage` | Isolate or retarget diagnostic_window_get_form_path; candidate title marker was rejected and current expected PF_FIXTURE_VERSION is not observed. |

## Notes

The active-window marker probe in this pass saw the fresh TestClient home page and is not counted in the pending-row promotion scope. Active-window remains covered by the existing cleanup replay/probe evidence.

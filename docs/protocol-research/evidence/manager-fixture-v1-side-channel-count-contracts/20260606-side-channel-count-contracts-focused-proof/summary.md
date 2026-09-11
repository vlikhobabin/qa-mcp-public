# Manager Fixture V1 Side-Channel Count Contracts

- Catalog version: `2026-06-06.2`
- Focused proof capture: `runtime/protocol-research/captures/20260606-side-channel-count-contracts-focused-proof`
- Focused proof report: `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-count-contracts-focused-proof/`
- Dry-run manifest: `runtime/protocol-research/captures/20260606-side-channel-count-contracts-dryrun`
- Catalog drift check: `catalog_comparison.json`, status `ok`

## Accepted

| case id | side-channel marker | observed result preview | frame range | normalized hash |
| --- | --- | --- | --- | --- |
| `tm-v1-diag-command-interface-dump` | `ci_children_count=` | `ci_source=active_window;ci_children_count=0` | `16..18` | `45b82b8a5f5febcc6ca5086bd872984206d54d3ffd7e3c6fa3e7546e4ee6311b` |
| `tm-v1-diag-window-children` | `window_children_count=` | `window_children_count=1` | `19..20` | `a606b8eda4f9e3a65f15110b36bb28b04a965c6b8d3bcae9a9b0319d7e6a973f` |

## Boundary

These rows are accepted by typed manager side-channel evidence:
`manager_case_event.after.result_preview`. They are not claimed as direct wire
marker observations. Direct marker replay still sees the current TestClient UI
markers for these endpoints, so accepting them as wire markers would be
incorrect.

After this proof, the only formerly pending manager fixture V1 row still
blocked is `tm-v1-diag-window-get-form-path`.

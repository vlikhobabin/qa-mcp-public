# Manager Fixture V1 Missing-Proof Runtime Gap

- Generated for card: `09-2026-06-06-manager-fixture-v1-promote-pending-readonly-rows`
- Source cleanup run: `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`
- Preflight run: `20260606-pending-readonly-runtime-preflight`
- Transport status: `runtime_gap`
- Missing asset: `Vanessa EPF`
- Accepted probe cases: `0`

## Rows

| case id | manager frames | normalized hash | expected marker | observed markers | status | next route |
| --- | ---: | --- | --- | --- | --- | --- |
| `tm-v1-diag-command-interface-dump` | `18..20` | `45b82b8a5f5febcc6ca5086bd872984206d54d3ffd7e3c6fa3e7546e4ee6311b` | `ci_children_count=` | none | `blocked_runtime_gap` | Restore runtime endpoint, then prove count-marker contract. |
| `tm-v1-diag-window-children` | `21..22` | `a606b8eda4f9e3a65f15110b36bb28b04a965c6b8d3bcae9a9b0319d7e6a973f` | `window_children_count=` | none | `blocked_runtime_gap` | Restore runtime endpoint, then prove window-children contract. |
| `tm-v1-diag-window-find-form-marker` | `23..25` | `5d87ccd9f0c08ea313b9378dff7fe65abcfb3f3e5355bd15d3fb8e9294ca51f2` | `PF_FIXTURE_VERSION` | `QA MCP Protocol Fixture V1` | `blocked_runtime_gap` | Restore runtime endpoint, then decide title/form marker versus version semantics. |
| `tm-v1-diag-window-get-form-path` | `26..106` | `0244782c3c4f28c8b3ad0bbf5dfaf37916cb642f0d82debe8543fdd08c71f85a` | `PF_FIXTURE_VERSION` | `QA MCP Protocol Fixture V1` | `blocked_ambiguous_range_and_runtime_gap` | Isolate broad range, then retry focused proof. |
| `tm-v1-form-summary` | `117..119` | `33f8fb78e26a3aa64d0b111942140a3b19eba163e3e2ab875cfa81a5ccc1ad3f` | `PF_FIXTURE_VERSION` | `QA MCP Protocol Fixture V1` | `blocked_runtime_gap` | Restore runtime endpoint, then run a current-run form-summary probe. |

## Acceptance Boundary

No row is promoted by this summary. The current cleanup `case_id`, manager
frame range and `normalized_hash` are retained for each blocked row so a later
runtime-restored probe can be validated without accepting joined evidence alone.

Older probe evidence remains supporting only unless it is reconciled with the
current cleanup frame range and normalized hash.

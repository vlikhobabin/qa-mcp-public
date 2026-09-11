# Manager Fixture V1 Ambiguous Range Isolation

- Source cleanup run: `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`
- Runtime preflight: `20260606-pending-readonly-runtime-preflight`
- Endpoint state: `runtime_gap`
- Accepted mappings from this isolation pass: `0`

## Rows

| case id | manager frames | chunks | request bytes | response bytes | normalized hash | markers | isolation result |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `tm-v1-diag-window-get-form-path` | `26..106` | `161` | `21059` | `17973` | `0244782c3c4f28c8b3ad0bbf5dfaf37916cb642f0d82debe8543fdd08c71f85a` | `QA MCP Protocol Fixture V1` | `not_isolated` |
| `tm-v1-button-inert` | `131..390` | `519` | `57888` | `48090` | `926585521047f8e7e2abe2316dacbbf690142f04867c73cb12c172139a153e86` | `PF_BUTTON_INERT` | `not_isolated` |

## Findings

- `tm-v1-diag-window-get-form-path` still spans 81 manager frames. Its corpus
  row has only envelope-level normalized signatures and the observed title
  marker; this is not enough to accept version or form-path semantics.
- `tm-v1-button-inert` still spans 260 manager frames. It repeatedly preserves
  the target marker `PF_BUTTON_INERT`, but target-marker repetition alone does
  not prove a minimal button-state operation shape.
- No action, click or command-execution semantics are claimed for
  `tm-v1-button-inert`; it remains a read-only observation row.

## Next Route

Both rows require runtime restoration and a focused rerun or narrower
side-channel boundary before replay/direct-probe acceptance can be considered.

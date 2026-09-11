# Demo Real Mutation UI Evidence

Run id: `20260610-blocked-pilot`

## Runtime UI Status

No live UI form tree or screenshot is claimed for the selected row. The
guarded pilot stopped before UI attach/click because the manifest row lacked a
reviewed live pre-state and recovery wrapper.

Retained runtime fact:

- `scripts\preflight-live-runtime.ps1 -Mode capture` passed and wrote
  `.artifacts/openspec/execute-demo-mutation-guarded-pilot/20260610-demo-real-mutation-pilot/runtime-pilot/preflight_result.json`.

## Source UI Status

The selected target is source-reviewed from card 60:

- source object:
  `Document.OperatsiyaPoUchetuTovarov.Form.FormaDokumenta`;
- element path:
  `TovarnyeZapasyKomandnayaPanel/PereklyuchitAktivnost`;
- visible marker: `PereklyuchitAktivnost`;
- source-visible/source-enabled state: true in the prior source review.

Source evidence is enough to retain a blocked mutation candidate. It is not
enough to execute the action or accept a protocol mapping.

## Provider Gap

| Provider | Owner route | Missing evidence | Impact |
| --- | --- | --- | --- |
| `vanessa` | `/opt/vanessa-mcp-stack` | live active-window/form tree, target marker and screenshot immediately before the action | blocks execution because a business mutation needs live pre-state proof |
| `project:qa-mcp` | `project-local` | reviewed action/recovery wrapper that records pre-state, post-state, cleanup and phase boundaries | blocks execution and frame isolation |

No UI action was performed.

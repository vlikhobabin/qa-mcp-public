# Manager Fixture V1 Replay Probe: Command Bar Main

Source capture:
`runtime/protocol-research/captures/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

Curated join evidence:
`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

## Outcome

- `tm-v1-commandbar-main` replay is semantically confirmed at manager frame
  `402..407`.
- The final response after send `407` is 2635 bytes and contains
  `PF_COMMAND_ENABLED`, `PF_COMMAND_DISABLED`, `PF_COMMAND_POPUP` and
  `PF_RESET_STATE`.
- The replay sent 407 manager frames, received 407 responses, had no
  `no_response` stop, and wrote runtime evidence to
  `runtime/protocol-research/replay-probe/20260606-manager-fixture-cleanup-commandbar407-uipath-v1/`.

## Dynamic Fields

Successful replay command shape:

```powershell
python tools\protocol-research\replay_probe.py `
  runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly-cleanup `
  --port 15381 `
  --send-count 407 `
  --adapt-frame4-guid `
  --adapt-frame5-guid `
  --adapt-frame5-random-blocks `
  --adapt-binary-single-block-through 121 `
  --adapt-binary-single-block-frames '123-129,131-174,176-187,189-210,212-231,233-294,296-300,302-307,309-359,361-367,369-371,373-381,383,386,388-394,396-399,402-405' `
  --adapt-binary-guid-through 407 `
  --adapt-ui-path-guids `
  --stop-on-no-response
```

Observed in the successful replay:

- ACK GUID from response after send `3`:
  `d77d8242-0f3b-42c4-95ea-95553e764b3c`.
- `MainFrame` GUID from response after send `6`:
  `6ca75e50-62a3-4842-b6cd-b429f7591ef2`.
- `SecondaryFrame` GUID from response after send `15`:
  `576ca02d-5064-4982-a2dc-880c0f4f5455`.
- `ManagedForm` GUID from response after send `15`:
  `a46eac50-71f0-495a-b7ea-dff953e08473`.

For the commandbar case itself, frames `402..405` used GUID+random-block
adaptation, while frames `406..407` used GUID-only adaptation plus UI path GUID
replacement. This matches the shape observed in the field replay: path
resolution and value or collection read frames need different dynamic handling.

## Case Result

| case_id | manager frames | normalized hash | replay result |
| --- | ---: | --- | --- |
| `tm-v1-commandbar-main` | `402..407` | `a34f368171635aed20a1162e50a32be4977bfe5d265e0881b128fb4df8c13397` | `accepted_probe`: response `407` has `PF_COMMAND_ENABLED`, 2635 bytes |

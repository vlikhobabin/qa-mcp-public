# Manager Fixture V1 Replay Probe: Cleanup Read-Only Fields

Source capture:
`runtime/protocol-research/captures/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

Curated join evidence:
`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

## Outcome

- `tm-v1-field-version` replay is semantically confirmed at manager frame
  `120..122`: response after send `122` contains `KS protocol-fixture.v1`.
- `tm-v1-field-string` replay is semantically confirmed at manager frame
  `123..125`: response after send `125` contains `KS PF_EDIT_STRING_VALUE`.
- The final successful replay sent 125 manager frames, received 125 responses,
  had no `no_response` stop, and wrote runtime evidence to
  `runtime/protocol-research/replay-probe/20260606-manager-fixture-cleanup-field-string125-uipath/`.

## Dynamic Fields

Successful replay command shape:

```powershell
python tools\protocol-research\replay_probe.py `
  runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly-cleanup `
  --port 15381 `
  --send-count 125 `
  --adapt-frame4-guid `
  --adapt-frame5-guid `
  --adapt-frame5-random-blocks `
  --adapt-binary-single-block-through 121 `
  --adapt-binary-single-block-frames 123-124 `
  --adapt-binary-guid-through 125 `
  --adapt-ui-path-guids `
  --stop-on-no-response
```

Observed in the successful replay:

- ACK GUID from response after send `3`:
  `82301f0b-dc72-4527-8ccd-0188a6d3f5d8`.
- `MainFrame` GUID from response after send `6`:
  `6ca75e50-62a3-4842-b6cd-b429f7591ef2`.
- `SecondaryFrame` GUID from response after send `15`:
  `cdc96779-e57e-40d1-ba0b-beecf6311c5f`.
- `ManagedForm` GUID from response after send `15`:
  `32d80370-d32e-4383-844f-0bd6e538b31a`.

The important protocol rule from this probe is that raw manager UI paths must
rewrite `SecondaryFrame[...]` and `ManagedForm[...]` GUIDs to the live values.
Replacing only `ManagedForm[...]` leaves value-read responses as `KU`; replacing
both produces `KS <value>`.

## Case Results

| case_id | manager frames | normalized hash | replay result |
| --- | ---: | --- | --- |
| `tm-v1-field-version` | `120..122` | `0e7805e358002583cf2d4b0c82ce8de49d806917f65fcc8424d4055e309ed596` | `accepted_probe`: response `122` has `protocol-fixture.v1`, 236 bytes |
| `tm-v1-field-string` | `123..125` | `4e1a884c0d235806670934dc2d442e93363ffe56196e6160aac9713f57228444` | `accepted_probe`: response `125` has `PF_EDIT_STRING_VALUE`, 255 bytes |

## Negative Controls

- `20260606-manager-fixture-cleanup-field-version122`: transport OK, but
  contiguous random-block adaptation through frame `122` returns `KU` without
  `protocol-fixture.v1`.
- `20260606-manager-fixture-cleanup-field-version122-guidonly122`: transport
  OK, but preserving the frame `122` block while leaving captured UI path GUIDs
  also returns `KU`.
- `20260606-manager-fixture-cleanup-field-version122-managedform`: transport
  OK, but replacing only `ManagedForm[...]` still returns `KU`.
- `20260606-manager-fixture-cleanup-field-version122-uipath`: replacing
  `SecondaryFrame[...]` and `ManagedForm[...]` returns `KS protocol-fixture.v1`.

These negative controls are retained under
`runtime/protocol-research/replay-probe/` and explain why
`--adapt-ui-path-guids` and range-based block adaptation were added to
`replay_probe.py`.

# Card 120 Windows Host-Agent Evidence

Date: 2026-06-26

## Result

The model-B display subset is recovered through a Windows host-side agent for
the primitive layer:

- `GET /version` and `GET /health` work from the Linux container route.
- `get_window_list` enumerates Windows top-level windows and identifies the 1C
  TestClient.
- `capture_screenshot` returns a host-rendered PNG from the Windows 1C window.
- `send_keys` targets the Windows 1C window through the agent.
- `write_form_value_xtest` routes text input through the remote backend; the
  final screenshot shows Unicode text `WOK-Ж120` in the `Наименование` field.

Final agent SHA256:
`1fe93f6f7e447dacdb536b1d6da3fd4e662e3b2450c045dcfe68e45f0c336d9f`.

## Final Live Proof

- Windows host: `historical-user@192.0.2.202`
- TestClient PID after restart: `12812`
- Agent endpoint: Windows `127.0.0.1:8001`, reached through Linux tunnel
  `127.0.0.1:18001`
- TestClient endpoint: Windows `127.0.0.1:15381`, reached through Linux tunnel
  `127.0.0.1:18081`
- Final raw screenshot:
  `.artifacts/openspec/remote-display-e2e/20260626-card120/write-form-value-final-clean-main.png`
- Screenshot SHA256:
  `abcc27e5f8c491151bdaec8d9be7a6e78b94054b98fc6dd49141488496e7e97b`

The screenshot shows form `Валюта (создание)` with `WOK-Ж120` in field
`Наименование`. The run used `save=false`, so it proves UI input delivery and
does not claim a persisted business-data mutation.

## Readback Status

The `write_form_value_xtest` protocol readback stayed false, as in the earlier
SendInput spike. That readback is sensitive to the contended Windows desktop
and form instance state. For this card the accepted assertion is the host-side
PNG: genuine Unicode input reached the target managed-form field through the
remote display backend.

## Operational Notes

During verification the initial 1C session was accidentally closed. The
card-owned scheduled task `qa-mcp-testclient-120` was restarted and the final
proof was rerun against the new PID. Only card-owned processes/tasks were
stopped or restarted.

Raw runtime output remains under `.artifacts/openspec/...`; this directory is
the curated committed summary.

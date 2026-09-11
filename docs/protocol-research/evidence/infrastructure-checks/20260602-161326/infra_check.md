# Protocol Lab Infrastructure Check 20260602-161326

Date: 2026-06-02.

This check verified the current qa-mcp lab infrastructure after refreshing the
Vanessa target bootstrap settings.

## Scope

- Static project checks: Python compile, MCP profile shape, target env
  contract, local lab paths and baseline template evidence.
- Live MCP readiness: filesystem, help-mcp, knowledge-mcp, meta-mcp, edt-mcp
  and vanessa-mcp.
- Live capture path: Vanessa TestManager attaches to a running TestClient
  through the TCP proxy.
- Direct Python manager path: Python sends the short read-only schedule to a
  live TestClient without a 1C TestManager instance.

## Static Checks

- `scripts\check.ps1`: passed; `pytest` was not installed and was skipped.
- `scripts\check-mcp-profile.ps1`: passed for `context7`, `edt-mcp`,
  `filesystem`, `help-mcp`, `knowledge-mcp`, `meta-mcp`, `vanessa-mcp`.
- `scripts\check-protocol-lab.ps1`: passed after adding the Vanessa target env
  contract check.
- Vanessa target env diagnostic:
  - profile: `qa-mcp`;
  - selected: `true`;
  - bootstrap mode: `ensure-profile`;
  - behavior: `ensure_profile_with_vanessa_step`;
  - missing fields: none;
  - no manager or TestClient was started by the static diagnostic.

## MCP Readiness

- `filesystem`: responded with the qa-mcp repository listing.
- `help-mcp`: default local platform help version is `8.3.27.1786`.
- `knowledge-mcp`: listed prepared knowledge bases including `1c-doc`,
  `metod8dev`, `edtdoc` and `v8std`.
- `meta-mcp`: runtime status `ready` for configuration `demo10413`, build
  `2026-05-24T000000Z-demo10413-edt`.
- `edt-mcp`: listed local infobases including `vanessa_manager`.
- `vanessa-mcp`: responded through the lazy project manager runtime. The
  editor state call reached Vanessa, but the active `memory:welcome` document
  reported a Vanessa editor `lineNumber` access error; this is separate from
  target bootstrap and did not block protocol capture.

## Live Capture

Capture id: `20260602-161326`.

Runtime path:
`runtime\protocol-research\captures\20260602-161326`.

Command shape:

```powershell
tools\protocol-research\run_protocol_capture.ps1 `
  -Scenario connect-only `
  -VanessaEpf C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\vanessa-mcp\releases\vanessa\single\vanessa-automation-single-51f920f-windows-screenshot-fixes.epf
```

Result:

- status: `ok`;
- TestClient port: `15381`;
- proxy port: `15382`;
- MCP port: `19874`;
- created PIDs: TestClient `19436`, proxy `19944`, manager `6696`;
- cleanup: all three created PIDs were stopped;
- remaining 1C process after cleanup: only the pre-existing lazy
  `vanessa-mcp` manager on port `49678`.

Captured traffic:

- manager-to-client chunks: `7`;
- client-to-manager chunks: `8`;
- manager-to-client bytes: `2152`;
- client-to-manager bytes: `1745`;
- first TestClient preface: `53 f5 c6 1a 7b`;
- `execute_step_from_text` attach-running result: `ok`.

Comparison with baseline `20260602-084433` kept the known session-field shape:

| field | baseline | new capture |
| --- | --- | --- |
| frame 4 sequence | `5466` | `20524` |
| ACK GUID | `92b71ecf-cd35-4052-abbd-48afc9134f7a` | `eaeba657-1520-4f7c-ac0d-fb76f14f84ad` |
| frame 5 sequence relation | `frame4_sequence_plus_1` | `frame4_sequence_plus_1` |
| frame 5 dynamic blocks | offsets `67`, `88` | offsets `67`, `88` |
| client frame 6 block echoes | positions `30`, `51` | positions `30`, `51` |

## Direct Python Manager Probe

Runtime path:
`runtime\protocol-research\python-manager-probe\infra-check-20260602-161326`.

Query:

- `form-element-details`;
- frame mode: `short`;
- schedule: captured bootstrap plus frames `8..17` and `101..106`;
- manager templates:
  `docs\protocol-research\evidence\templates\20260602-frames08-106-utf16-managedform\manager_frame_templates.json`.

Result:

- status: `ok`;
- sent bytes: `5449`;
- received bytes: `6986`;
- active form: `Otchet.DashboardSales.Form.ReportForm` in decoded stdout
  (`Otchet.DashbordProdazhi` transliterated here to avoid encoding ambiguity);
- active form caption: `Sales`;
- element count: `2`;
- element detail count: `2`;
- stopped created TestClient PID: `3392`.

## Conclusion

The qa-mcp lab can currently:

- validate the local MCP and Vanessa target bootstrap contract before live
  runs;
- capture manager-client traffic through the TCP proxy during a stock Vanessa
  attach-running flow;
- run the narrow read-only Python manager prototype directly against a live
  TestClient without a 1C TestManager instance.

The next protocol step should keep using short, labeled capture scenarios and
promote normalized evidence for each new TestedApplication/TestedForm API
family.

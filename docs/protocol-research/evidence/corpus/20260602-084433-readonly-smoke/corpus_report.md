# Protocol Corpus Report

- Generated at: `2026-06-02T14:23:03Z`
- Capture id: `20260602-084433`
- Capture dir: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260602-084433`
- Case count: `3`
- Case rows: `docs/protocol-research/evidence/corpus/20260602-084433-readonly-smoke/corpus_cases.jsonl`
- Case events: `runtime/protocol-research/captures/20260602-084433/case_events.jsonl`

## Case Rows

| case | api call | manager frames | request bytes | response bytes | hash prefix | replay | markers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| active-window-context | TestedApplication.GetActiveWindow + TestedClientApplicationWindow read-only properties | {"from": 8, "to": 11} | 400 | 995 | fd29166e5d156108 | accepted | 7 |
| active-form-context | TestedApplication.GetActiveForm + TestedForm read-only metadata | {"from": 12, "to": 17} | 801 | 2337 | 719ee3962749a0a2 | accepted | 14 |
| form-element-details | TestedForm.FindObject/GetChildObjects + form element read-only property probes | {"from": 101, "to": 106} | 2100 | 1910 | 6cd987cb4294867c | accepted | 3 |

## Notes

- Case events are side-channel evidence; no markers are injected into the TCP stream.
- Raw traffic remains under `runtime/protocol-research/captures/`.
- `accepted` replay status means the direct Python-manager probe returned the expected read-only data.

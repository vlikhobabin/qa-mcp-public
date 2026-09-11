# Protocol Corpus Report

- Generated at: `2026-06-02T17:04:05Z`
- Capture id: `20260602-193802`
- Capture dir: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260602-193802`
- Case count: `10`
- Case rows: `docs/protocol-research/evidence/corpus/20260602-193802-expanded-readonly/corpus_cases.jsonl`
- Case events: `runtime/protocol-research/captures/20260602-193802/case_events.jsonl`

## Case Rows

| case | family | availability | api call | manager frames | request bytes | response bytes | hash prefix | replay | markers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| active-window-context |  | supported | TestedApplication.GetActiveWindow + TestedClientApplicationWindow read-only properties | {"from": 8, "to": 11} | 400 | 995 | 62e03d159d511173 | pending | 7 |
| active-form-context |  | supported | TestedApplication.GetActiveForm + TestedForm read-only metadata | {"from": 12, "to": 17} | 801 | 2337 | e43ce48cedae7b6d | pending | 14 |
| form-element-details | EditField | supported | TestedForm.FindObject/GetChildObjects + form element read-only property probes | {"from": 101, "to": 106} | 0 | 0 | n/a | pending | 0 |
| typed-input-field-readonly | EditField | supported | TestedForm.FindObject/GetChildObjects + typed input EditField read-only property probes | {"from": 101, "to": 106} | 0 | 0 | n/a | pending | 0 |
| button-family-readonly-gap | Button | unsupported | TestedForm read-only property probes for Button controls | n/a | 0 | 0 | n/a | unsupported | 0 |
| table-family-readonly-gap | Table | unsupported | TestedForm read-only property probes for Table controls | n/a | 0 | 0 | n/a | unsupported | 0 |
| commandbar-family-readonly-gap | CommandBar | unsupported | TestedForm read-only property probes for CommandBar controls | n/a | 0 | 0 | n/a | unsupported | 0 |
| page-family-readonly-gap | Page | unsupported | TestedForm read-only property probes for Page controls | n/a | 0 | 0 | n/a | unsupported | 0 |
| label-family-readonly-gap | Label | unsupported | TestedForm read-only property probes for Label controls | n/a | 0 | 0 | n/a | unsupported | 0 |
| checkbox-family-readonly-gap | CheckBox | unsupported | TestedForm read-only property probes for CheckBox controls | n/a | 0 | 0 | n/a | unsupported | 0 |

## Notes

- Case events are side-channel evidence; no markers are injected into the TCP stream.
- Raw traffic remains under `runtime/protocol-research/captures/`.
- `accepted` replay status means the direct Python-manager probe returned the expected read-only data.
- `unsupported` family rows are explicit fixture gaps and intentionally have no frame range.

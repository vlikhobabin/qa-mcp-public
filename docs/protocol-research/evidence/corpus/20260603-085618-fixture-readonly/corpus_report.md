# Protocol Corpus Report

- Generated at: `2026-06-03T05:57:03Z`
- Capture id: `20260603-085618`
- Capture dir: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260603-085618`
- Case count: `6`
- Case rows: `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/corpus_cases.jsonl`
- Case events: `runtime/protocol-research/captures/20260603-085618/case_events.jsonl`

## Case Rows

| case | family | availability | api call | manager frames | request bytes | response bytes | hash prefix | replay | markers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixture-button-readonly | Button | pending | TestedForm.FindObject/GetChildObjects + button read-only property probes | n/a | 0 | 0 | n/a | pending | 0 |
| fixture-table-readonly | Table | pending | TestedForm.FindObject/GetChildObjects + table read-only property probes | n/a | 0 | 0 | n/a | pending | 0 |
| fixture-commandbar-readonly | CommandBar | pending | TestedForm.FindObject/GetChildObjects + command bar read-only property probes | n/a | 0 | 0 | n/a | pending | 0 |
| fixture-page-readonly | Page | pending | TestedForm.FindObject/GetChildObjects + page/group read-only property probes | n/a | 0 | 0 | n/a | pending | 0 |
| fixture-label-readonly | Label | pending | TestedForm.FindObject/GetChildObjects + decoration read-only property probes | n/a | 0 | 0 | n/a | pending | 0 |
| fixture-checkbox-readonly | CheckBox | pending | TestedForm.FindObject/GetChildObjects + checkbox read-only property probes | n/a | 0 | 0 | n/a | pending | 0 |

## Notes

- Case events are side-channel evidence; no markers are injected into the TCP stream.
- Raw traffic remains under `runtime/protocol-research/captures/`.
- `accepted` replay status means the direct Python-manager probe returned the expected read-only data.
- `unsupported` family rows are explicit fixture gaps and intentionally have no frame range.

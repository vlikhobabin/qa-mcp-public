# Protocol Corpus Report

- Generated at: `2026-06-03T10:45:15Z`
- Capture id: `20260603-134132`
- Capture dir: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260603-134132`
- Case count: `1`
- Case rows: `docs/protocol-research/evidence/corpus/20260603-134132-safe-action/corpus_cases.jsonl`
- Case events: `runtime/protocol-research/captures/20260603-134132/case_events.jsonl`

## Case Rows

| case | family | availability | api call | manager frames | request bytes | response bytes | hash prefix | replay | markers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| safe-activate-existing-window |  | supported | Vanessa MCP activate_window -> native TestClient internal window activation | n/a | 0 | 0 | n/a | pending | 0 |

## Notes

- Case events are side-channel evidence; no markers are injected into the TCP stream.
- Raw traffic remains under `runtime/protocol-research/captures/`.
- `accepted` replay status means the direct Python-manager probe returned the expected read-only data.
- `unsupported` family rows are explicit fixture gaps and intentionally have no frame range.

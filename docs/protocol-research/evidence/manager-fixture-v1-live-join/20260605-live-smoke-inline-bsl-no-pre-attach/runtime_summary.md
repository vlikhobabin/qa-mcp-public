# Manager Fixture V1 Runtime Summary

- Generated at: `2026-06-05T08:09:58Z`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-smoke-inline-bsl-no-pre-attach`
- Raw output policy: raw TCP streams, full event logs, platform logs and generated replay output stay under ignored runtime/protocol-research paths.

## Run

| field | value |
| --- | --- |
| run_id | 20260605-live-smoke-inline-bsl-no-pre-attach |
| run_status | partial |
| status_reason | some_commands_failed |
| fixture_version | protocol-fixture.v1 |
| command_catalog_version | qa-mcp.manager-fixture-v1.manifest.v1 |
| bootstrap_status | connect_before |
| command_count | 3 |
| readonly_event_count | 6 |
| accepted_protocol_mapping | False |

## Frame Join Counts

| join_status | count |
| --- | --- |
| unresolved | 3 |

## Reviewed And Runtime Files

| file | path |
| --- | --- |
| runtime_manifest | C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-smoke-inline-bsl-no-pre-attach\manager_harness_manifest.json |
| runtime_result | C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-smoke-inline-bsl-no-pre-attach\manager_harness_result.json |
| runtime_case_events | C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-smoke-inline-bsl-no-pre-attach\case_events.jsonl |
| reviewed_summary_markdown | C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\docs\protocol-research\evidence\manager-fixture-v1-live-join\20260605-live-smoke-inline-bsl-no-pre-attach\runtime_summary.md |
| reviewed_summary_json | C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\docs\protocol-research\evidence\manager-fixture-v1-live-join\20260605-live-smoke-inline-bsl-no-pre-attach\runtime_summary.json |
| reviewed_frame_join_markdown | C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\docs\protocol-research\evidence\manager-fixture-v1-live-join\20260605-live-smoke-inline-bsl-no-pre-attach\frame_join_report.md |
| reviewed_frame_join_json | C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\docs\protocol-research\evidence\manager-fixture-v1-live-join\20260605-live-smoke-inline-bsl-no-pre-attach\frame_join_report.json |
| reviewed_corpus_rows | C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\docs\protocol-research\evidence\manager-fixture-v1-live-join\20260605-live-smoke-inline-bsl-no-pre-attach\corpus_cases.jsonl |

## Gaps

| gap | owner route | reason | residual risk |
| --- | --- | --- | --- |
| no_chunks_in_case_window | project:qa-mcp | 3 command(s) unresolved with reason=no_chunks_in_case_window | command remains non-accepted until live range, replay or direct probe evidence is retained |

## Acceptance Boundary

No command from this run is published as an accepted protocol mapping. Accepted mappings still require frame ranges, dynamic-field evidence, normalized hashes and replay or direct Python-manager proof.

## Frame Join Report

See `frame_join_report.md`.

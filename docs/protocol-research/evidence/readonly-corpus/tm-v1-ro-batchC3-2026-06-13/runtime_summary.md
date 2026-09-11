# Manager Fixture V1 Runtime Summary

- Generated at: `2026-06-13T09:33:56Z`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchC3`
- Raw output policy: raw TCP streams, full event logs, platform logs and generated replay output stay under ignored runtime/protocol-research paths.

## Run

| field | value |
| --- | --- |
| run_id | tm-v1-ro-batchC3 |
| run_status | ok |
| status_reason | all_commands_completed |
| fixture_version | protocol-fixture.v1 |
| command_catalog_version | qa-mcp.manager-fixture-v1.manifest.v1 |
| bootstrap_status | connect_before |
| command_count | 4 |
| readonly_event_count | 8 |
| accepted_protocol_mapping | True |
| accepted_case_ids | ["ro-field-readonly", "ro-group-readonly", "ro-table-readonly", "ro-group-opened"] |

## Frame Join Counts

| join_status | count |
| --- | --- |
| joined | 4 |

## Reviewed And Runtime Files

| file | path |
| --- | --- |
| runtime_manifest | runtime\protocol-research\captures\tm-v1-ro-batchC3\manager_harness_manifest.json |
| runtime_result | runtime\protocol-research\captures\tm-v1-ro-batchC3\manager_harness_result.json |
| runtime_case_events | runtime\protocol-research\captures\tm-v1-ro-batchC3\case_events.jsonl |
| reviewed_summary_markdown | docs\protocol-research\evidence\readonly-corpus\tm-v1-ro-batchC3-2026-06-13\runtime_summary.md |
| reviewed_summary_json | docs\protocol-research\evidence\readonly-corpus\tm-v1-ro-batchC3-2026-06-13\runtime_summary.json |
| reviewed_frame_join_markdown | docs\protocol-research\evidence\readonly-corpus\tm-v1-ro-batchC3-2026-06-13\frame_join_report.md |
| reviewed_frame_join_json | docs\protocol-research\evidence\readonly-corpus\tm-v1-ro-batchC3-2026-06-13\frame_join_report.json |
| reviewed_corpus_rows | docs\protocol-research\evidence\readonly-corpus\tm-v1-ro-batchC3-2026-06-13\corpus_cases.jsonl |

## Gaps

| gap | owner route | reason | residual risk |
| --- | --- | --- | --- |

## Acceptance Boundary

Accepted case ids are published only where retained replay/probe evidence or typed side-channel evidence matches the command contract while joined frame range and normalized hash evidence are retained.

## Frame Join Report

See `frame_join_report.md`.

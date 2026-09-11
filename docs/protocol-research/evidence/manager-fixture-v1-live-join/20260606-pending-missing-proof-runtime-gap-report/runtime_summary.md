# Manager Fixture V1 Runtime Summary

- Generated at: `2026-06-06T16:20:03Z`
- Source runtime directory: `runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`
- Raw output policy: raw TCP streams, full event logs, platform logs and generated replay output stay under ignored runtime/protocol-research paths.

## Run

| field | value |
| --- | --- |
| run_id | 20260606-live-fixture-ci-bootstrap-full-readonly-cleanup |
| run_status | ok |
| status_reason | all_commands_completed |
| fixture_version | protocol-fixture.v1 |
| command_catalog_version | qa-mcp.manager-fixture-v1.manifest.v1 |
| bootstrap_status | connect_before |
| command_count | 17 |
| readonly_event_count | 34 |
| accepted_protocol_mapping | True |
| accepted_case_ids | ["tm-v1-active-window", "tm-v1-active-form", "tm-v1-diag-window-find-field-marker", "tm-v1-diag-form-find-field-marker", "tm-v1-field-version", "tm-v1-field-string", "tm-v1-commandbar-main", "tm-v1-pages-main"] |

## Frame Join Counts

| join_status | count |
| --- | --- |
| joined | 17 |

## Reviewed And Runtime Files

| file | path |
| --- | --- |
| runtime_manifest | runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly-cleanup\manager_harness_manifest.json |
| runtime_result | runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly-cleanup\manager_harness_result.json |
| runtime_case_events | runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly-cleanup\case_events.jsonl |
| reviewed_summary_markdown | docs\protocol-research\evidence\manager-fixture-v1-live-join\20260606-pending-missing-proof-runtime-gap-report\runtime_summary.md |
| reviewed_summary_json | docs\protocol-research\evidence\manager-fixture-v1-live-join\20260606-pending-missing-proof-runtime-gap-report\runtime_summary.json |
| reviewed_frame_join_markdown | docs\protocol-research\evidence\manager-fixture-v1-live-join\20260606-pending-missing-proof-runtime-gap-report\frame_join_report.md |
| reviewed_frame_join_json | docs\protocol-research\evidence\manager-fixture-v1-live-join\20260606-pending-missing-proof-runtime-gap-report\frame_join_report.json |
| reviewed_corpus_rows | docs\protocol-research\evidence\manager-fixture-v1-live-join\20260606-pending-missing-proof-runtime-gap-report\corpus_cases.jsonl |

## Gaps

| gap | owner route | reason | residual risk |
| --- | --- | --- | --- |

## Acceptance Boundary

Accepted case ids are published only where retained replay/probe evidence matches the joined frame range and normalized hash.

## Frame Join Report

See `frame_join_report.md`.

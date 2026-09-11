# Manager Fixture V1 Runtime Summary

- Generated at: `2026-06-04T19:04:00Z`
- Source runtime directory: `runtime\protocol-research\captures\opsx-manager-fixture-v1-dryrun`
- Raw output policy: raw TCP streams, full event logs, platform logs and generated replay output stay under ignored runtime/protocol-research paths.

## Run

| field | value |
| --- | --- |
| run_id | opsx-manager-fixture-v1-dryrun |
| run_status | dry_run_ok |
| status_reason | dry-run preflight wrote manager fixture manifest, event and result files without starting 1C |
| fixture_version | protocol-fixture.v1 |
| command_catalog_version | qa-mcp.manager-fixture-v1.manifest.v1 |
| bootstrap_status | dry_run_ok |
| command_count | 6 |
| readonly_event_count | 1 |
| accepted_protocol_mapping | False |

## Frame Join Counts

| join_status | count |
| --- | --- |
| blocked | 5 |
| unresolved | 1 |

## Reviewed And Runtime Files

| file | path |
| --- | --- |
| runtime_manifest | runtime\protocol-research\captures\opsx-manager-fixture-v1-dryrun\manager_harness_manifest.json |
| runtime_result | runtime\protocol-research\captures\opsx-manager-fixture-v1-dryrun\manager_harness_result.json |
| runtime_case_events | runtime\protocol-research\captures\opsx-manager-fixture-v1-dryrun\case_events.jsonl |
| reviewed_summary_markdown | docs\protocol-research\evidence\manager-fixture-v1\opsx-manager-fixture-v1-dryrun\runtime_summary.md |
| reviewed_summary_json | docs\protocol-research\evidence\manager-fixture-v1\opsx-manager-fixture-v1-dryrun\runtime_summary.json |
| reviewed_frame_join_markdown | docs\protocol-research\evidence\manager-fixture-v1\opsx-manager-fixture-v1-dryrun\frame_join_report.md |
| reviewed_frame_join_json | docs\protocol-research\evidence\manager-fixture-v1\opsx-manager-fixture-v1-dryrun\frame_join_report.json |

## Gaps

| gap | owner route | reason | residual risk |
| --- | --- | --- | --- |
| live_manager_fixture_smoke | project:qa-mcp | retained run is a dry-run because the configured Vanessa EPF was absent | live startup, attach timing and manager harness invocation still need one run |
| frame_join | project:qa-mcp | no proxy chunk counters exist for the retained dry-run | no command can be accepted as a protocol mapping from this run |

## Acceptance Boundary

No command from this run is published as an accepted protocol mapping. Accepted mappings still require frame ranges, dynamic-field evidence, normalized hashes and replay or direct Python-manager proof.

## Frame Join Report

See `frame_join_report.md`.

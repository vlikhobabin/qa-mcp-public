## 1. Frame Isolation

- [x] 1.1 Consume the focused live run output from
  `capture-focused-v2-safe-action-run`.
- [x] 1.2 Run the V2 reporter/frame-join tooling for the selected row or rows.
- [x] 1.3 Record action frame range, background ranges, recovery range,
  request/response sizes, dynamic fields and normalized hash candidates.
- [x] 1.4 Mark ambiguous, missing or incomplete joins with explicit
  non-accepted status and reason.

## 2. Reporter Compatibility

- [x] 2.1 Confirm V1 read-only reporter output remains compatible when V2
  safe-action rows are processed.
- [x] 2.2 Keep raw payloads and generated replay payloads under ignored runtime
  paths.
- [x] 2.3 Retain compact frame-isolation summaries for the proof handoff.

## 3. Verification

- [x] 3.1 Retain frame-join summary under
  `.artifacts/openspec/isolate-focused-v2-safe-action-frames/<run-id>/frame-review/`.
- [x] 3.2 Run `bin\openspec.cmd validate isolate-focused-v2-safe-action-frames --strict`.
- [x] 3.3 Run `git diff --check -- openspec/changes/isolate-focused-v2-safe-action-frames docs/protocol-research tools/protocol-research tests openspec/board`.

## Evidence

- Source run:
  `runtime/protocol-research/captures/20260607-first-focused-v2-safe-action-live-runner-2/`
- Reviewed report:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/safe_action_report.md`
- Corpus rows:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/corpus_cases.jsonl`
- Frame isolation summary:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/frame_isolation_summary.md`
- Handoff artifact:
  `.artifacts/openspec/isolate-focused-v2-safe-action-frames/20260607-first-focused-v2-safe-action-live-runner-2/frame-review/frame_isolation_summary.md`
- V2 reporter/tooling tests:
  `pytest -q tests/test_manager_fixture_v2_safe_action_report.py tests/test_v2_safe_action_tooling.py tests/test_v2_safe_action_live_runner.py -p no:cacheprovider --basetemp runtime/tmp/pytest`
  passed with 13 tests.
- V1 reporter compatibility:
  `pytest -q tests/test_manager_fixture_v1_report.py -p no:cacheprovider --basetemp .runtime/pytest-temp`
  passed with 12 tests.

## 4. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | V2 reporter and frame-join output for focused safe-action rows | Frame isolation report with action/background/recovery ranges and non-accepted reasons | Reporter output; frame-join summary; OpenSpec strict validation | `.artifacts/openspec/isolate-focused-v2-safe-action-frames/<run-id>/frame-review/` | required | `project:qa-mcp`, `/opt/ai-tools-1c` | N/A | Medium: joined frames can be over-interpreted without proof gates |
| Form module or command | Manager runner phase events consumed by frame join | Phase-to-frame correlation inputs for selected row ids | `case_events.jsonl` summary; action result marker summary | `.artifacts/openspec/isolate-focused-v2-safe-action-frames/<run-id>/phase-correlation/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: event boundaries can be too coarse for clean isolation |
| Managed form layout | Client fixture recovery/known-state traffic | Recovery frame range separated from action range | Recovery range summary and marker result summary | `.artifacts/openspec/isolate-focused-v2-safe-action-frames/<run-id>/recovery-frame-review/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Low: recovery evidence can be incomplete even when action range is isolated |

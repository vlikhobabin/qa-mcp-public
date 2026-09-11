## 1. Reporter Output

- [x] 1.1 Add a V2 safe-action reporter entrypoint or mode separate from the
  V1 read-only reporter.
- [x] 1.2 Emit `action_frame_range`, `background_frame_ranges`,
  `recovery_frame_range`, `action_result_markers`, `pre_state`,
  `post_state` and `recovery_result`.
- [x] 1.3 Preserve explicit non-accepted statuses and reasons for candidate or
  incomplete action rows.

## 2. Verification

- [x] 2.1 Retain a compact reporter proof bundle with sample safe-action rows
  and separated frame ranges.
- [x] 2.2 Verify existing V1 read-only reporter output remains stable.
- [x] 2.3 Run `bin\openspec.cmd validate add-v2-safe-action-evidence-reporter --strict`.
- [x] 2.4 Run `git diff --check -- openspec/changes/add-v2-safe-action-evidence-reporter openspec/board docs/protocol-research`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | V2 safe-action reporter output | Compact report rows with separated action/background/recovery ranges | Reporter sample bundle; Markdown/JSON summary; OpenSpec strict validation | `.artifacts/openspec/add-v2-safe-action-evidence-reporter/<run-id>/reporter-proof/` | required | `project:qa-mcp` | N/A | Medium: action joins can be ambiguous if side-channel timing is weak |
| Delivery or runtime apply | Existing V1 read-only reporter behavior | Regression check for V1 report compatibility | Focused V1 reporter smoke summary | `.artifacts/openspec/add-v2-safe-action-evidence-reporter/<run-id>/v1-regression/` | required | `project:qa-mcp` | N/A | Low: reporter split can accidentally change shared formatting |

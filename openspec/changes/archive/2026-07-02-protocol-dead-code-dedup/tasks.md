## 1. Dead-Code Verification

- [x] 1.1 Re-run source searches for `_RESOLVE_SF_RE`, `_CreateForegroundHold`, `_OPEN_LINK_LABEL_ALIASES`, `_splice_window_activate_command` and `mutation.py` imports.
- [x] 1.2 Delete only symbols proven dead in current code.
- [x] 1.3 Preserve `_splice_window_activate_command` and record why it remains live.

## 2. Duplicate Helper Cleanup

- [x] 2.1 Collapse exact duplicate date normalization, GUID substitution, capture chunk loading or LEB128 helpers where tests prove equivalence.
- [x] 2.2 Leave non-identical helpers in place with a short residual note.
- [x] 2.3 Confirm `mutation.py` removal is safe before deleting; otherwise leave it intact.

## 3. Verification

- [x] 3.1 Run `rg "_RESOLVE_SF_RE|_CreateForegroundHold|_OPEN_LINK_LABEL_ALIASES" src tests` and confirm zero matches.
- [x] 3.2 Run `rg "_splice_window_activate_command|render_write_frame|native_mutation" src/qa_mcp` and confirm live-path decisions.
- [x] 3.3 Run `uv run pytest -q`.

## Notes

- Removed `_RESOLVE_SF_RE` and `_OPEN_LINK_LABEL_ALIASES`; `_CreateForegroundHold` was already absent after the
  preceding extraction changes.
- Preserved `_splice_window_activate_command`; it remains exported through `mcp_server.py` and covered by
  `tests/test_mcp_server.py::test_splice_window_activate_command_targets_resolved_form`.
- Collapsed the exact form-date normalizer duplicate by reusing `scenario.normalize_form_date` from the MCP server.
- Left GUID substitution, capture chunk loading and LEB128 helpers separate because the current helpers are similar
  but not behavior-identical at their call sites.
- Left `mutation.py` intact because `native_mutation` imports and uses `render_write_frame` on the live write path.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient protocol runtime | dead helper removal and duplicate utility collapse | Offline pytest plus source searches for removed and preserved helpers | source_preflight, scenario_log | `.artifacts/openspec/protocol-dead-code-dedup/20260702-offline/evidence-summary.md` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live runtime smoke was not required; offline source checks and full pytest cover the private cleanup. |
| BSL and 1C metadata | N/A - Python protocol cleanup only | No BSL modules, metadata objects, roles, reports or migrations are changed | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change does not edit 1C configuration source or live infobase data. | Runtime behavior is covered by source checks and offline tests. |

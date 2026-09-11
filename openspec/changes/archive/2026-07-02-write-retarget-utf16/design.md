# Design - UTF-16 native write retargeting

## Problem

`build_write_frame` uses `retarget_element_leaf`, which only sees latin1 path envelopes. A real configuration can encode
the whole element path as UTF-16LE when the leaf is Cyrillic. The current broad `except ValueError: pass` was meant for
focus-change frames that address a different field, but it also hides a failed SET-frame retarget.

The unsafe behavior is: requested target `Контрагент`, base template `PF_EDIT_STRING`, SET frame still points at
`PF_EDIT_STRING`, result only reports a non-commit. The tool must either address `Контрагент` or fail before sending the
frame.

## Retarget helper contract

Native write code will use the existing `retarget_element_leaf_any(frame, old, new, kind="EditField")` for field leaves.
This preserves the latin1 behavior and adds UTF-16LE direct replacement for same-character-length Cyrillic leaves. The
first implementation can keep the helper's current documented limitation: UTF-16LE retargets with different character
lengths fail closed rather than resizing the UTF-16 path length prefix.

## Expected-miss contract

The write loop knows which manager frame classes are expected to contain the base field:

- write-block frames that activate or SET the captured field are expected to retarget;
- read-back frames for the captured field are expected to retarget;
- commit/focus-change frames can legitimately address the partner field and lack the base leaf.

`build_write_frame` should not blindly swallow missing leaves. It can accept an explicit `allow_missing_leaf` flag or
return metadata indicating whether retargeting changed the frame. The caller must mark only known commit/focus frames as
allowed misses. An unexpected miss returns a structured error such as:

```json
{
  "error": "retarget_failed",
  "field": "Контрагент",
  "base_field": "PF_EDIT_STRING",
  "frame_index": 12,
  "reason": "no element path with leaf EditField[PF_EDIT_STRING]"
}
```

The implementation should fail before `sendall` for the unsafe frame.

## Tests

Offline tests will construct representative write frames with UTF-16LE `EditField[<field>]` leaves and assert the SET
frame changes from the base leaf to the target leaf. A second test will assert that an unexpected missing leaf yields
`retarget_failed` and does not call the socket. Existing tests for focus-change frames should prove the allowed-miss path
still preserves the frame.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient protocol write | `NativeWriteSession.write`, `set_table_cell`, field leaf retargeting | Offline UTF-16 frame retarget tests plus live write regression row for a Cyrillic field | `source_preflight`, `qa_testclient_scenario`, `scenario_log`, `data_assertion` | `.artifacts/openspec/write-retarget-utf16/2026-07-02/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| BSL diagnostics | no BSL files changed | N/A because this change edits Python protocol code only | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | no BSL module is modified | no BSL behavioral surface |

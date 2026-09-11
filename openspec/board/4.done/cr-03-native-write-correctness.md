# CR-03 - Native write-path correctness (right field + honest `committed`)

## Status
4.done

## Order Index
3

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Multi-agent code review 2026-07-02, findings C1, C2, S2.
- Full report: `docs/code-review-2026-07-02.md`.

## Summary
The native write path can write into the wrong field silently and its `committed` flag is unreliable in both
directions. This is the core value proposition of the product: a write tool that writes the wrong field or
misreports success is worse than no tool. The delivery requires a live-regression run
(`python -m qa_mcp.regression --include-write`) against the lab client.

## Problems (verified against code)

### C1 - Cyrillic (non-ASCII) field name -> write lands on the wrong field
`src/qa_mcp/protocol/native_write.py:369`:
```python
out, _ = retarget_element_leaf(out, base_field, target_field)   # ASCII-only
...
except ValueError:
    pass                                                        # swallowed
```
`retarget_element_leaf` (`element_ref.py:98`) is latin1/ASCII-only and can never match a Cyrillic leaf; the
`ValueError` is swallowed (intended for the focus-change frame that legitimately lacks the leaf). So for
`write_form_value(field="Контрагент")` the SET frame is sent still addressed at the template's base field, the
value can commit into the wrong field, and the result reports `committed: false` with no error. A UTF-16-capable
`retarget_element_leaf_any` already exists (`element_ref.py:113`) but is not used here. Same ASCII-only retarget
exists in `set_choice` / `set_table_cell`.

### C2 - `committed` read-back: false positive and false negative
- False positive: `native_write.py:457` and `:569` use
  `committed = readback is not None and readback.startswith(value)`. Writing `"123"` into a field already holding
  `"123456"` can no-op yet read back the old value and report `committed: true`.
- False negative: `native_write.py:112-144` (`read_field_value_near`) accepts only a length byte in `2..40` followed
  by printable ASCII. A committed Cyrillic value, a 1-character value, or a value longer than 40 bytes always reads
  back `None`, so a real write can report `committed: false`.

### S2 - Create-form label-locate retry is dead code
`src/qa_mcp/mcp_server.py:1827`: the retry loop breaks unless
`foreground_meta["foreground_method"] == "create_splice"`, but no production path sets that string. The create path
sets `"create_listreplay"` and the list path sets `"listreplay"`. On a create form whose first screenshot races
render, `write_form_fields_by_label` reports `"label not located"` with `activation_retry: null` instead of retrying.

## Change Set
1. `openspec/changes/archive/2026-07-02-write-retarget-utf16/` - retarget native write frames through ASCII or UTF-16
   element leaves and fail closed on unexpected target misses.
2. `openspec/changes/archive/2026-07-02-committed-readback-honest/` - make protocol write read-back decode real values
   and require normalized own-field equality instead of prefix matches.
3. `openspec/changes/archive/2026-07-02-create-retry-fix/` - make the create-form activation retry reachable for
   actual foreground methods, with offline proof.

## Change 1: `write-retarget-utf16`

### Why
Cyrillic field leaves currently bypass ASCII-only retargeting and can leave the write SET frame addressed at the
template field.

### Goal
Use the existing ASCII/UTF-16 retarget helper on native write frames and fail loudly when a frame expected to carry the
base leaf cannot be retargeted.

### Scope
- `src/qa_mcp/protocol/native_write.py`
- `tests/test_native_write.py`
- `openspec/specs/qa-mcp-protocol-lab/spec.md`

### Acceptance
- Offline frame-level test proves a SET frame addressed to a Cyrillic target changes from the base leaf to the target
  leaf.
- Focus-change frames that legitimately do not contain the base leaf remain allowed.
- Unexpected retarget misses return a structured `retarget_failed` error instead of sending a frame to the base field.
- Live write regression includes a Cyrillic-named field case and records retained evidence.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-02-write-retarget-utf16/`

## Change 2: `committed-readback-honest`

### Why
Protocol writes can report false-positive commits through prefix matching and false-negative commits when the read-back
scanner cannot decode valid values.

### Goal
Decode native write read-back values for Cyrillic, single-character and long values, and report `committed: true` only
when the normalized read-back equals the normalized requested value for the target field.

### Scope
- `src/qa_mcp/protocol/native_write.py`
- shared value-match helper if needed
- `tests/test_native_write.py`
- `openspec/specs/qa-mcp-protocol-lab/spec.md`

### Acceptance
- `"123"` requested against read-back `"123456"` returns `committed: false`.
- Cyrillic, 1-character and >40-byte values read back correctly and can return `committed: true`.
- Table-cell and form-field protocol writes use the same honest matching rule unless a documented date/time formatting
  normalization applies.
- Live write regression is green and records retained evidence.

### Depends On
- `write-retarget-utf16`

### Related
- `openspec/changes/archive/2026-07-02-committed-readback-honest/`

## Change 3: `create-retry-fix`

### Why
The create-form label-locate retry is guarded by a foreground method string that no production path sets.

### Goal
Make the retry path fire for actual create/list foreground methods when the first create-form screenshot misses, or
remove the dead branch if retry is no longer needed.

### Scope
- `src/qa_mcp/mcp_server.py`
- `tests/test_mcp_server.py`
- `openspec/specs/qa-mcp-protocol-lab/spec.md`

### Acceptance
- A simulated first-screenshot miss on a create form retries activation and populates `activation_retry`, or the dead
  branch is removed and no unreachable `foreground_method` string remains.
- The retry remains scoped to foreground/render races and does not retry unrelated label misses indefinitely.
- Existing list and bare-create foreground behavior stays compatible.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-02-create-retry-fix/`

## Verify
- passed: `uv run pytest tests/test_native_write.py tests/test_mcp_server.py tests/test_element_ref.py -q` (130 passed).
- passed: `uv run pytest tests/ -q` (612 passed).
- passed: `uv run python -m qa_mcp.regression --include-write --odata-url "http://127.0.0.1:8316/vanessa_client/odata/standard.odata" --out .artifacts/openspec/write-retarget-utf16/2026-07-02/live-regression`
  (GREEN 8/8, platform 8.3.27.2130, report `20260702T054219Z`).
- passed: matrix preflight/archive gates for all three changes under `.artifacts/openspec/<change>/2026-07-02/`.

## Archive
- archived as `2026-07-02-write-retarget-utf16`
- archived as `2026-07-02-committed-readback-honest`
- archived as `2026-07-02-create-retry-fix`

## Related
- `docs/code-review-2026-07-02.md` (C1, C2, S2)
- Memory: card 125 label-route `_close_value_match`, 8.5 platform support.
- Reuses the shared validated helpers; coordinate with CR-02 if merged.
- `openspec/changes/archive/2026-07-02-write-retarget-utf16/`
- `openspec/changes/archive/2026-07-02-committed-readback-honest/`
- `openspec/changes/archive/2026-07-02-create-retry-fix/`

## Result
Implemented, verified, synced into `openspec/specs/qa-mcp-protocol-lab/spec.md`, and archived.

## Next
- none

## Log
- 2026-07-02 card created from the code-review report (C1, C2, S2).
- 2026-07-02 `$opsx-ff`: decomposed into three apply-ready changes, generated proposal/design/spec/tasks artifacts
  with verification matrix rows, and moved the card to `2.todo`.
- 2026-07-02 `$opsx-do`: moved the card to `3.inprogress` and started implementation.
- 2026-07-02 `$opsx-do`: implemented all three changes, retained green live-regression evidence, passed full tests and
  matrix archive gates, and archived the OpenSpec changes.
- 2026-07-02 `$opsx-pub`: moved the card to `4.done`.
- 2026-07-02 post-delivery verification (multi-agent): all four findings (C1
  wrong-field + fail-loud via `WriteRetargetError`, C2 false-positive, C2
  false-negative, S2 dead retry) confirmed fixed at code + frame-byte test level.
  Note: the `write_form_fields_by_label` false-positive that C2 Change-2 targeted
  was actually closed in commit `02ac07a` (delivered under the cr-04 banner) via
  `_values_equivalent` `allow_prefix` gating + `regression/checks.py` requiring
  `all_committed` — functionally complete, attribution only.
  Tail cleanup 2026-07-02: residual follow-ups closed. Added direct UTF-16LE
  Cyrillic read-back fixture coverage and replaced the fixed 96B/120B scanner
  window with a tail/next-field bounded scanner, including a regression for a
  value longer than the old window.

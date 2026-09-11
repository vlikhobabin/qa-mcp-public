# Card 97 #2-read — cross-region value read (read a field in another Group)

**Date:** 2026-06-19. **Result:** SOLVED + productized + live-verified. The card-79 value-read can now resolve a
field in ANY form Group, not just the captured editable `PF_EDIT_*` region — so the PF_GROUP_MAIN status markers
(PF_LAST_ACTION / PF_FIXTURE_VERSION / PF_SELECTED_ROW_MARKER / PF_TABLE_SNAPSHOT) are assertable capture-free.
This closes the last assert/wait read-ceiling follow-up. 272 tests.

## Root cause — the value-read query carries the FULL path, not just the leaf

Dumping the genuine value-read query frames (the manager→client sends 218-221) showed each carries the **whole
element path**, e.g.:

```
SecondaryFrame[<S>].ManagedForm[<F>].Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[PF_EDIT_NUMBER]
```

`_read_field_value` retargeted only the **leaf** (`retarget_element_leaf`: `EditField[PF_EDIT_STRING]` →
`EditField[<field>]`), leaving the parent `Group[PF_GROUP_EDITS]` in place. The status markers live one level up,
directly under PF_GROUP_MAIN:

```
Group[PF_GROUP_MAIN].EditField[PF_LAST_ACTION]   (and PF_FIXTURE_VERSION / PF_SELECTED_ROW_MARKER / PF_TABLE_SNAPSHOT)
```

So a leaf-only retarget produced `Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[PF_LAST_ACTION]` — an
unreachable path → the client answered with the `0x88` no-value stub. (Frame 218 of the genuine batch already
reads a DIFFERENT group, `Group[PF_GROUP_MAIN].Group[PF_GROUP_DIALOG_RECOVERY_V4].EditField[PF_V4_SUPPORTED_SCENARIOS]`,
which proved the read resolves whatever full path is in the query.)

## Fix — full-path retarget (swap the Group container too)

`_retarget_read_to_groups(payload, captured_leaf, field, groups)` rebuilds each captured `PF_EDIT_STRING` path as
`Group[groups…].EditField[field]` with `retarget_element_path` (preserves the live SecondaryFrame/ManagedForm
GUIDs, recomputes the 1-byte length prefix). The read query **tolerates the path-length resize** (card 86a;
dropping a whole `.Group[…]` segment), exactly as `read_spreadsheet_cell`'s navigate did and unlike a value-SET.
`_read_field_value` / `assert_form_value` / `wait_for_form_value` gained an optional `groups` param; `groups=None`
is the unchanged editable-region read.

## Live-verify (2026-06-19, `cross_region_read_probe.py`, fresh /TESTCLIENT, the SHIPPED code path)

| field | OLD leaf-only (`groups=None`) | full-path (`groups=["PF_GROUP_MAIN"]`) |
| --- | --- | --- |
| `PF_EDIT_STRING` (control, editable region) | `"PF_EDIT_STRING_VALUE"` | — |
| `PF_FIXTURE_VERSION` | `None` (0x88 stub) | `"protocol-fixture.v1"` |
| `PF_LAST_ACTION` | `None` | `"PF_STATE_INITIAL"` |
| `PF_SELECTED_ROW_MARKER` | `None` | `"PF_ROW_IDX_1:PF_ROW_001"` |

The OLD path returning None for each marker, and the FIX returning its value, proves the Group container was the
sole blocker. `PF_TABLE_SNAPSHOT` shares the same `Group[PF_GROUP_MAIN]` path (confirmed in the captures) so it
reads identically via `groups=["PF_GROUP_MAIN"]`.

## Ergonomics / scope (honest)

`groups` is supplied explicitly — the form designer/test author knows the field's group, or reads it from a form
descriptor. The open frames (11-17) carry only the `SecondaryFrame.ManagedForm` root, NOT the element tree, so a
fully **automatic** group discovery would need a separate descriptor/get_form_analysis query (a clean follow-up,
ties into the card-98 form-introspection item). The mechanism itself is general: any group depth works (a 2-group
subgroup case is unit-tested).

## Artifacts

- Code: `src/qa_mcp/mcp_server.py` (`_retarget_read_to_groups`, `_VALUE_READ_CAPTURED_GROUPS`, `groups` param on
  `_read_field_value` / `assert_form_value` / `wait_for_form_value`).
- Tests: `tests/test_assert_wait.py` (+3: drop-subgroup, other-subgroup, no-op) — 272 suite, no regression.
- Probe: `tools/protocol-research/cross_region_read_probe.py` (live verify).
- Evidence bytes: genuine query paths in `runtime/protocol-research/native-mcp/20260619-045702/steps/sent_218..221`.

## Remaining read-decode follow-up

- **Automatic cross-region** — discover a field's group path from a live form descriptor so `groups` need not be
  passed (a get_form_analysis-equivalent; card-98 form-introspection). The number/date parser (#3) and the
  cross-region read (#2) close the assert/wait read ceiling for explicitly-addressed fields.

# Card 86c — per-element-TYPE SET investigation (findings)

Date: 2026-06-17. Goal: make commit work for non-string field types (number/date/checkbox), not just the
PF_EDIT_STRING template type. Reproduce (lab-local): `tools/protocol-research/element_write_86c_diag.py`,
and a formatted-value sweep via `NativeWriteSession.write(field="PF_EDIT_NUMBER")`.

## Method

Address PF_EDIT_NUMBER capture-free (86b path retarget off the PF_EDIT_STRING SET template) and inspect: (a)
the SET frame's response (accepted vs rejected), (b) the read-back, (c) several value formats.

## Findings

**The SET mechanism is type-agnostic — the field ACCEPTS the edit-text.** The SET response for PF_EDIT_NUMBER
echoes the value with the SAME `ba` edit-text tag as a string:

```
PF_EDIT_STRING SET resp tail: 47 5f 53 54 52 20 a1 a3 …   ("…G_STR ")   -> read-back 'DIAG_STR'  (commits)
PF_EDIT_NUMBER SET resp tail: ba 03 37 37 37 20 a1 a3 …   ("ba<3>777 ") -> read-back transient, then reverts
```

**But the value does NOT commit for a number, at any format.** Writing `777`, `888,88`, `42`, `42,00`,
`100,00` to PF_EDIT_NUMBER all leave it at its prior value `120,50` (committed=False). So it is **not** a
value-format problem.

**Root cause: the value buffer is type-specific and baked into the captured SET frame.** The PF_EDIT_STRING
SET carries a fixed-width value buffer (13 chars + space padding = 16 wide); the number field's buffer is ~6
wide (`120,50`). `retarget_value` keeps the captured STRING buffer width constant (resizing desyncs — card
80), so a number field receives a 16-wide string buffer it cannot accept as its value. The string SET frame
**cannot be reformatted into a working number SET** by changing the value alone.

## Conclusion

86c genuinely needs **per-element-TYPE SET templates derived from genuine per-type INPUT captures** (one each
for number / date / checkbox / choice). The element ADDRESSING is solved (86a/86b: path retarget works for
all types — read-back confirms the field is correctly addressed); what differs per type is the SET frame's
value-buffer structure (width, and likely a type descriptor — the SET prefix `88 82 81 e0 41 81 81 ba` before
the value is a candidate). These differences are baked into the wire frame and are not derivable from the
string capture, so a genuine capture per type is required.

## Decided next step (capture orchestration)

Reuse the existing capture pipeline to record genuine per-type input:
`tools/protocol-research/capture_session.sh` boots TestClient + `protocol_proxy.py` (manager→proxy→client) and
the genuine Vanessa TestManager (memory `vanessa-mcp-linux-genuine-manager`) drives, through the proxy port, a
step like «в поле с именем 'PF_EDIT_NUMBER' я ввожу текст '777'». Diff the captured number SET against the
PF_EDIT_STRING SET (`genuine-commit-conn`) to decode the per-type buffer/descriptor, then add a per-type
template + `derive`/format step and verify commit live. Repeat for date and checkbox.

## What stands

Capture-free element ADDRESSING (read+write, 86a/86b) and same-type (string) COMMIT are unaffected and proven.
This investigation rules out the cheap path for other types and precisely scopes the genuine-capture work.

## UPDATE (same day) — BREAKTHROUGH: the number ALREADY commits; the "blocked" conclusion above was WRONG

The conclusion that per-type commit needs NEW genuine captures was an artifact of reusing the **string** SET
frame (16-wide buffer) for a number. The genuine `genuine-commit-conn` capture **already contains the genuine
PF_EDIT_NUMBER input** (card 80's two-input feature typed `777,77` into PF_EDIT_NUMBER, frames 353-356) — it
was merely UNCOMMITTED (no focus-change followed it). Critically, the genuine SET structure is **type-IDENTICAL**:

```
PF_EDIT_STRING SET (350): [PF_EDIT_STRING] 88 82 81 e0 41 81 81 ba 0d "QAGENUINE2026" 20 20 20
PF_EDIT_NUMBER SET (355): [PF_EDIT_NUMBER] 88 82 81 e0 41 81 81 ba 06 "777,77"        20 20 20
```

Same descriptor `88 82 81 e0 41 81 81 ba`; only the value + its varint length differ (variable-length, not
fixed-width — frame lengths differ by the value-length delta). The input sequence:
`activate STRING (348-9) → SET STRING (350-1) → activate NUMBER (353-4) [=STRING's commit] → SET NUMBER (355-6) → (no further activate) → NUMBER uncommitted`.

**The commit trigger is universal: "activate ANY other field."** So a number commits with: setup → activate
PF_EDIT_NUMBER + genuine number SET (value retargeted) → activate PF_EDIT_STRING (synthesized focus-change) →
read-back. Proven LIVE (`tools/protocol-research/element_write_number_probe.py`):

```
NUMBER write '777,77' : committed=True  readback='777,77'   (genuine value)
NUMBER write '555,55' : committed=True  readback='555,55'   (value retargeted, fresh session)
```

## Corrected conclusion

Per-type commit needs the field's OWN genuine SET frame (correct buffer/structure) + a synthesized
focus-change (activate any other field) — NOT a per-type type-descriptor and NOT necessarily a new capture
when the type is already present. number ✅ proven from the existing capture. date/checkbox/choice would need
their genuine SETs (not in this capture) — those still need a genuine multi-action capture (or a fixture that
includes them). The earlier "cheap path ruled out" applies only to RE-FORMATTING the string SET; using the
field's own genuine SET is the correct (and here, already-available) path.

## PRODUCTIZED (2026-06-17): commit-partner in NativeWriteSession + MCP-verified

`WriteTemplate.commit_block` + `derive_write_template(commit_partner_field, commit_partner_value)` +
`NativeWriteSession.write` (sends write-block → commit-block → read-back). `derive` locates the field's
activate+SET (its full contiguous input block, incl. the duplicated SET pair), the partner's ACTIVATE frames
(the frames just before the partner's SET — its read-sweep frames do NOT move focus), sets `setup_end` BEFORE
the earliest input (so neither input is in the replayed prefix; the inputs are re-sent out-of-order in
`write()`), and draws read-back from the field's value-mode sweep. Two pitfalls fixed along the way: the
partner's read-sweep frame is not an activate (must use its captured value to find the real activate); and the
replayed prefix must stop before BOTH inputs.

LIVE via the MCP tool: `write_form_value('314,15', field='PF_EDIT_NUMBER', base_field='PF_EDIT_NUMBER',
captured_value='777,77', commit_partner='PF_EDIT_STRING', commit_partner_value='QAGENUINE2026')` →
**committed=true, readback='314,15'**. Offline: a `derive` commit-partner unit test; full suite 206 passed.
number commit is now a product feature (no Vanessa). date/checkbox/choice await their genuine SETs.

# Card 97 change 5 — waits + assertions — SHIPPED capture-free (+ a value-read parser bug fixed)

**Date:** 2026-06-19. **Result:** first-class `assert_form_value` + `wait_for_form_value` (WaitForCondition)
productized capture-free (MCP #32/#33; 33 tools, 251 tests). Found + fixed a real value-read parser bug. The
honest read scope (value-read region; cross-group + number/date are follow-ups) is documented below.

## What shipped

| MCP tool | Behaviour |
| --- | --- |
| `assert_form_value(field, expected, mode)` | read ``field``'s LIVE value (card-79 value-read) + compare under `equals`/`contains`/`regex` → {field, expected, actual, mode, passed} |
| `wait_for_form_value(field, expected, mode, timeout_sec, interval_sec)` | poll the read until match or timeout → {…, satisfied, polls, elapsed_sec} (the our-engine WaitForCondition — re-read, not a manager callback) |

Built on `_read_field_value` (open+bootstrap → open the fixture form `run_segment(11-17)` → value-read
`run_segment(218-221)` with the element leaf retargeted to ``field`` → `extract_edit_field_value`). Orchestration
(compare modes, poll/timeout) is pure + unit-tested (7 tests, monkeypatched read); the parser fix has 2 tests.

## 🐞 Value-read parser bug FIXED (the headline)

`extract_edit_field_value` parsed only ONE field. The value wire shape is
``EditField[<field>] 81 81 81 [e0|fa] <LEB128 byte-len> <value> …`` — the old regex hard-coded ``\x14`` as a
"delimiter", but ``0x14`` is just **len("PF_EDIT_STRING_VALUE")==20**. So any field whose value length ≠ 20
(e.g. `PF_EDIT_READONLY_VALUE`, len 22) failed to parse → None. Rewrote it to read the **LEB128 length** then that
many value bytes (utf-8 / utf-16le / latin1). Now every same-region string field parses, any length. The card-79
test still passes; +2 tests (length-independent + multibyte LEB128).

## Read SCOPE (honest boundary)

The card-79 value-read query resolves the **value-read region** = the editable `PF_EDIT_*` group:
- **Readable (value-mode 0x81):** `PF_EDIT_STRING` / `PF_EDIT_READONLY` / `PF_EDIT_DISABLED` (strings, any
  length — live-verified pass/fail/contains/regex).
- **0x88 no-value stub (other region):** PF_GROUP_MAIN status markers `PF_FIXTURE_VERSION` / `PF_LAST_ACTION` /
  `PF_TABLE_SNAPSHOT` / `PF_SELECTED_ROW_MARKER` — the field NAME is echoed but the value is NOT returned
  (mode `88 81`, decisive: the value string is absent from the blob). Reading another region needs that
  region's value-read capture — a read-decode follow-up.
- **number/date:** the value IS on the wire (e.g. PF_EDIT_NUMBER → `120` present) but in a per-type buffer the
  string parser doesn't decode — ties into change #2 (number/date cells).

Latency: each poll/assert is a full open+bootstrap+read (~5-7s on the lab), so that read time — not
`interval_sec` — is the practical poll floor. The read opens a FRESH form (baseline/persistent state); to assert
a transient post-action effect, keep the action + read in ONE scenario session.

## Live-verify (2026-06-19)

`tools/protocol-research/assert_wait_verify.py` on a fresh /TESTCLIENT:
- assert equals PF_EDIT_STRING==PF_EDIT_STRING_VALUE → passed=True; PF_EDIT_READONLY==…_VALUE → passed=True
  (the parser fix); ==WRONG → passed=False; contains "DISABLED" → True; regex `PF_EDIT_\w+` → True.
- wait satisfy (immediate) → satisfied=True polls=1; wait timeout (NEVER) → satisfied=False.

## Artifacts

- Code: `src/qa_mcp/mcp_server.py` (`assert_form_value` / `wait_for_form_value` / `_read_field_value` /
  `_match_value` / `VALUE_READ_TEMPLATES`), `src/qa_mcp/protocol/responses.py` (`extract_edit_field_value` LEB128
  fix). Tests: `tests/test_assert_wait.py` (7), `tests/test_form_value_parser.py` (+2). Probe:
  `tools/protocol-research/assert_wait_verify.py`. Templates: `tm-v1-open-plus-valueread` (open 11-17 + 218-221).

## Deferred (read-decode follow-ups)

- Cross-region field read (capture a value-read of PF_GROUP_MAIN / arbitrary regions) so status markers
  (PF_LAST_ACTION / PF_TABLE_SNAPSHOT) are assertable capture-free.
- number/date value parser (per-type buffer) — pairs with change #2.

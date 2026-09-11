# Card 96 / E5 — read user messages (`Сообщить` / messages-to-user panel) capture-free: decode + productize + live proof

**Date:** 2026-06-18. **Card:** 96 (interaction breadth), change 5 (read user messages — the assertion read).
**Result:** `read_user_messages()` + the reusable `extract_user_messages(blob)` decoder are productized (MCP tool
#26, 233 tests) and LIVE-VERIFIED capture-free, no Vanessa. This is the capture-free ASSERTION read for «нет
сообщений пользователю» / reading `Сообщить` output — a success-criterion gap for "replace the test manager".

## Decode

The "messages to user" panel (`Сообщить` text) is reported by the client in the client→manager stream as the
envelope **`cb 53 9a <varint byte-len> <UTF-8 text>`** — `cb 53 9a` is the user-message string envelope, the
byte(s) after it are the 1C LEB128 byte-length, then the message as UTF-8 (NOT the UTF-16 used by form values).
Decoded 2026-06-18 from the two genuine messages already on the wire in the E2 captures (the choose callbacks
do `Сообщить(prefix + value)`):

- `genuine-card96-choicelist-20260618` cli[373] @124: `cb 53 9a 15` + `"PF_CHOICE=PF_CHOICE_B"` (len 0x15 = 21).
- `genuine-card96-menu-20260618` cli[27] @124: `cb 53 9a 11` + `"PF_MENU=PF_MENU_1"` (len 0x11 = 17).

The anchor is exact — `cb 53 9a` occurs exactly once per capture (one message each) and the byte-length is exact
(no padding inside the counted region). So a scan for the envelope cleanly extracts every message.

## Productize

`src/qa_mcp/protocol/native_write.py`:
- `extract_user_messages(blob) -> list[str]` — the reusable decoder: find each `cb 53 9a`, read the LEB128
  byte-length, take that many UTF-8 bytes, right-trim; de-duplicate adjacent repeats (a message echoes across
  consecutive poll responses). The core capability.
- `ReadUserMessagesTemplate` / `derive_read_user_messages(capture_dir, expected)` (validates the capture has the
  `cb 53 9a` envelope) / `read_user_messages(template, …)` — faithful full-stream replay of a genuine flow that
  raises a `Сообщить`, returning every message + `expected_found`.
- `choose_from_list` now also returns `messages` (the actual `Сообщить` text(s)) via the decoder — every action
  that elicits a message can report it (the real assertion capability).
- MCP tool `read_user_messages(expected)` (the **26th**). Unit test
  `test_extract_user_messages_decodes_cb539a_envelope` (ASCII + a >127-byte 2-byte-LEB128 Cyrillic message +
  adjacent-dedup + empty).

## Live proof (no Vanessa)

`tools/protocol-research/{read_user_messages_probe.py,run_read_messages_test.sh}`, fresh native client: replay
the choice flow → `count=1 messages=['PF_CHOICE=PF_CHOICE_B'] expected_found=True`. PASS.

## Notes / limitation

- Byte-length-prefixed UTF-8 is the standard 1C wire string form; proven on the ASCII fixture markers and on a
  SYNTHETIC 264-byte Cyrillic message (2-byte LEB128 length `88 02`) which roundtrips. A real Cyrillic `Сообщить`
  capture would CONFIRM the length-unit for multibyte text end-to-end — a cheap follow-up (add a Cyrillic
  `Сообщить` to the fixture or capture a validation message), not a blocker.
- `cb 53 9a` is the observed envelope for the `Сообщить` callbacks; other message sources (e.g. platform
  validation messages) should be spot-checked to confirm the same envelope.

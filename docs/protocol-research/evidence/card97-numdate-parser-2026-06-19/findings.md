# Card 97 #3 — number / date value PARSER (read side, for assert/wait)

**Date:** 2026-06-19. **Result:** the read-decode follow-up "number/date values are on the wire but the string
parser doesn't decode them" is **RESOLVED — and the premise was stale.** Number AND date value-reads already
decode through the existing value shape (verified from a GENUINE capture, fully offline, no lab needed). Fixed a
real latent parser robustness bug, added a `numeric` assert mode, pinned 8 regression tests to genuine byte
shapes. 269 tests pass (was 261).

## Headline — number & date decode as their formatted display text (NOT a per-type buffer)

The honest-scope note from change #5 said number/date "are present on the wire but need a per-type parser
(card 86c / #2)". **Decisively disproven offline** from the genuine value-read capture
`runtime/protocol-research/captures/tm-v1-ro-batchQ3` (the same capture `assert_form_value` replays). All three
editable fields surface their value in the **same** `81 81 81 fa <LEB128 len> <value>` shape, as the field's
formatted display text:

| field | wire shape (after `EditField[<field>]`) | decoded |
| --- | --- | --- |
| `PF_EDIT_STRING` | `81 81 81 fa 14` + `PF_EDIT_STRING_VALUE` | `"PF_EDIT_STRING_VALUE"` |
| `PF_EDIT_NUMBER` | `81 81 81 fa 06` + `31 32 30 2c 35 30` | `"120,50"` |
| `PF_EDIT_DATE`   | `81 81 81 fa 13` + `15.01.2026 10:30:00` | `"15.01.2026 10:30:00"` |

So a number rides the wire as its localized display text (RU comma decimal, format zeros, possible space/NBSP
thousands separators) and a datetime as its formatted text. No per-type binary decoder is needed for the read.
(Card 97 #2 already proved the SET side is byte-identical text for number grid cells; this is the symmetric READ
finding for plain fields.) `extract_edit_field_value` returns these correctly.

## 🐞 Latent parser robustness bug — FIXED (descriptor echo precedes the value)

A value-read response **echoes the field NAME first as a descriptor** —
`EditField[<field>] 81 fa 0c <name> fa 0c <name> …` — and the actual value (`81 81 81 fa …`) follows later in the
stream. `extract_edit_field_value` did a single `find(leaf)`, landed on the descriptor echo, saw it was not
`81 81 81`, and returned **None**. It only worked in practice because `_read_field_value` slices the blob to the
value-read segment (frames 218-221, after the descriptor frames). On the full genuine blob it returned None for
both number and date — a slice-boundary fragility waiting to bite.

**Fix:** scan ALL leaf occurrences and return the first carrying a real value; skip the descriptor echo
(`81 fa …`), the `88` out-of-region stub, and the `e2 20` empty stub. Also decode the alternate value shape
`81 81 81 e0 4b 53 9a <len> <value>` (the same value via the 0x9a string envelope). Proof, post-fix, on the FULL
genuine blob (was None before): `PF_EDIT_NUMBER → "120,50"`, `PF_EDIT_DATE → "15.01.2026 10:30:00"`,
`PF_EDIT_STRING → "PF_EDIT_STRING_VALUE"`.

## ✅ `numeric` assert mode (format/locale-robust number compare)

The value reads as localized text ("120,50"), so a plain `equals` assert is fragile across formats. Added a
`numeric` mode to `assert_form_value` / `wait_for_form_value` (`_match_value` + `_parse_1c_number`): parse both
sides as 1C numbers (comma OR dot decimal, space/NBSP/narrow-NBSP thousands, sign) to `Decimal` and compare by
value — so `"120,50"` matches `"120.5"` / `"120.50"` / `"120,5"`, and `"1 234,50"` matches `"1234.5"`. Dates stay
on `equals`/`contains`/`regex` (the formatted datetime string is config/locale dependent; a dedicated date-norm
mode is a small follow-up only if a non-default date format appears).

## Offline-decoded from stored streams (no lab)

Both the genuine capture `tm-v1-ro-batchQ3` and two live-replay number reads
(`runtime/protocol-research/native-mcp/20260619-045702` and `…-050135`, the change-#5 verify run) had already
captured the `PF_EDIT_NUMBER` value-read response on disk — so the whole decode + fix was done from stored bytes,
no TestClient boot.

## Artifacts

- Code: `src/qa_mcp/protocol/responses.py` (`extract_edit_field_value` scan-all + e0-envelope + descriptor-echo
  skip), `src/qa_mcp/mcp_server.py` (`_parse_1c_number`, `numeric` in `_match_value`, `assert_form_value` /
  `wait_for_form_value` docstrings + scope corrected).
- Tests: `tests/test_form_value_parser.py` (+5: number/date display-text, descriptor-echo-before-value, e0
  envelope, e2 stub), `tests/test_assert_wait.py` (+3: `_parse_1c_number`, `numeric` mode, assert numeric).
- Evidence bytes: `tm-v1-ro-batchQ3/connections/connection_0002_client_to_manager.bin` (offsets ~88260 number,
  ~90135 date), `native-mcp/20260619-045702/steps/response_after_send_219_client_to_manager.bin`.

## Remaining read-decode follow-up (still open)

- **Cross-region value read** — PF_GROUP_MAIN status markers (PF_LAST_ACTION / PF_TABLE_SNAPSHOT) still return
  the `88` no-value stub; reading another region needs that region's value-read capture (try the in-client
  targeted-read path first, like the spreadsheet cell). Number/date read scope is now CLOSED for the editable
  value-read region.

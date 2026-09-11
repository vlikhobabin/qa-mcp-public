# Card 98 #1 — general form introspection (SHIPPED: parser + `read_form_descriptor` MCP tool)

**Date:** 2026-06-19. **Result:** the capture-free `get_form_analysis` equivalent is SHIPPED and live-verified.
Increment 1 (offline) = `extract_form_field_values` (43/46 fields, value-accurate vs the oracle) + a real
single-byte-length bug fix. Increment 2 (lab) = the `read_form_descriptor` MCP tool — introspects a LIVE form into
a 41-field name→value descriptor + Gherkin state, **live-verified 40/41 value-match vs the Vanessa oracle** (the
1 diff is a live-state difference, not a decode error).

## Oracle (target shape)

Vanessa `get_form_analysis` returns a Gherkin dump: `элемент формы с именем '<NAME>' стал равен "<VALUE>"`
(+ `у элемента формы с именем '<NAME>' текст редактирования стал равен "<EDIT-TEXT>"` for some) for every form
element. Captured oracle: `runtime/protocol-research/captures/tm-v1-ro-batchQ3/mcp_manager_fixture_optional_form_analysis_gherkin.json`
(46 fields). So change 1 = produce that name→value map capture-free from our protocol streams.

## 🐞 Single-byte length — a latent bug in the shipped value parser, FIXED

The value-read length prefix is a **single byte (0..255)**, NOT LEB128. Decisive from the genuine capture:
`PF_V4_SUPPORTED_SCENARIOS` (143-char value) rides as `…fa 8f 50 46 5f…` — `0x8f` == 143 (literal length),
`0x50` == 'P' (value start). A LEB128 reader treats `0x8f`'s high bit as a continuation, consumes `0x50` as the
length's 2nd byte (→ length 10255), and over-runs. For values ≤127 single-byte and LEB128 are identical, so every
shipped live read (cross-region, assert/wait — all ≤127) was correct; the bug only bites 128..255-char values.
Fixed `extract_edit_field_value` to read a single-byte length (+ the new parser uses the same). (Values >255 are
unobserved in this response; the earlier "LEB128" framing came from a synthetic test, not real bytes.)

## Value markers (decoded)

After the `EditField[<name>] 81 81 81` value mode, the marker byte selects the encoding:

| marker | meaning | example |
| --- | --- | --- |
| `fa <len> <latin1>` | edit-text / display value (single-byte len) | `fa 14 "PF_EDIT_STRING_VALUE"` |
| `e0 4b 53 9a <len> <latin1>` | canonical «стал равен» single-byte (string/number/date) | `9a 13 "15.01.2026 10:30:00"` |
| `e0 4b 53 97 <charcount> <utf-16le>` | canonical UTF-16 (checkbox Да/Нет, Cyrillic) | `97 03 "Нет"` |
| `e0 4b 53 8b <digits>` | canonical short number (digits to the space pad) | `8b "0"` |
| `e0 4b 53 81 <pad>` | canonical empty value | reference field Контрагент |
| `e2 20` | empty / no-value stub (skip) | — |
| `8b 0a 81 81 e1` | checkbox bool RENDER (skip — its text is the `97` canonical) | — |

The **canonical (e0) value is the oracle's «стал равен»**; the `fa` value is the edit-text (they differ for
numbers: canonical "0" vs edit-text "0,00"; PF_EDIT_NUMBER "120,5" vs "120,50"). `extract_form_field_values`
prefers the canonical, falls back to the edit-text. Field NAMES are ASCII (`PF_*`) or UTF-16LE (Cyrillic, e.g.
`Контрагент`) — both leaf encodings are scanned (the UTF-16 leaf high byte is 0x04 for Cyrillic, not 0x00).

## Coverage vs the oracle

`extract_form_field_values` on the genuine capture: **43/46 fields, 43/43 value-match** (incl. the 143-char
PF_V4_SUPPORTED_SCENARIOS after the single-byte fix, checkboxes Да/Нет, the Cyrillic-named reference fields).
The 3 not extracted are **form decorations** (`PF_DECORATION_LABEL*` — a Label kind, not an EditField value) — a
legitimate gap (decorations are static captions, not field values).

## Increment 2 (SHIPPED, live) — the `read_form_descriptor` MCP tool

The genuine form-analysis is a **per-field value-read SWEEP** (Vanessa iterates every element: capture
`tm-v1-ro-batchQ3` has 304 manager frames; the sweep is frames 83-290, 41 distinct fields). **Gotcha:** the
value-read template (`tm-v1-open-plus-valueread`) is TRIMMED to the open + the ONE captured read (frames 218-221)
— `run_segment(18..290)` fails (`Manager template 18 not found`), and a raw-chunk full-capture replay DESYNCS
(connection reset). So the tool reproduces the sweep by **looping the proven per-field read** on ONE open
connection: open (frames 11-17) → for each field, replay the value-read (218-221) **retargeted to that field's
full path** (`_retarget_read_to_groups`, cross-region aware; field list + Group chains from
`_enumerate_capture_fields`, parsed from the capture's query paths) → decode each response with
`extract_form_field_values`. `read_form_descriptor` (MCP) returns `{fields, field_count, queried}` + a Gherkin
state block (`И элемент формы с именем 'X' стал равен "V"`) for Vanessa parity.

**Live-verify (`form_descriptor_verify.py`, fresh /TESTCLIENT):** 41 fields decoded / 41 queried; **40/41
value-match vs the Vanessa oracle**. All types correct live — PF_EDIT_NUMBER="120,5", PF_EDIT_DATE="15.01.2026
10:30:00", PF_CHECKBOX_TRUE="Да", PF_CHECKBOX_FALSE="Нет". The 1 "diff" is PF_SELECTED_ROW_MARKER
(got "PF_ROW_IDX_1:PF_ROW_001" — row 1 active during the live read — vs the oracle snapshot "PF_ROW_NONE"): a
LIVE-STATE difference, the correct current value, not a parser error.

**Scope / gaps (honest):** captures the 41 ASCII-named EditField values. NOT covered: the 3 form **decorations**
(Label kind, static captions — not field values) and the 2 **Cyrillic-named reference/combo fields** (Контрагент,
ПолеСоСпискомВыбораСтрока) — `_enumerate_capture_fields` matches ASCII query paths only; reading the Cyrillic
fields needs UTF-16 query-path retargeting (the offline `extract_form_field_values` already decodes UTF-16 leaves
in the response, so it's an enumeration/retarget refinement). The sweep is bound to the capture's form;
introspecting a DIFFERENT form needs that form's sweep — a generalization follow-up (which then also supplies the
auto cross-region `groups`).

## Artifacts

- Code: `src/qa_mcp/protocol/responses.py` (`extract_form_field_values`, `_value_after_leaf`, `_decode_value_bytes`;
  single-byte length fix in `extract_edit_field_value`), `src/qa_mcp/mcp_server.py` (`read_form_descriptor` MCP
  tool, `_read_form_descriptor`, `_enumerate_capture_fields`). Tests: `tests/test_form_value_parser.py` (+2
  form-values, single-byte-length), `tests/test_form_descriptor.py` (+3); 282 suite. Probe:
  `tools/protocol-research/form_descriptor_verify.py`. Oracle: the captured `…form_analysis_gherkin.json`.

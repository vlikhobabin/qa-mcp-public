# Card 98 #1 — Cyrillic-named fields in `read_form_descriptor` (SHIPPED, live-verified 43/46)

**Date:** 2026-06-20. **Result:** `read_form_descriptor` now sweeps **Cyrillic-named** fields, not just ASCII
`PF_*`. Live: **43 fields decoded / 43 queried, 42/43 value-match vs the Vanessa oracle** (was 41/41) — the 2
Cyrillic reference/combo fields `Контрагент` and `ПолеСоСпискомВыбораСтрока` are now read (both `""`, matching
the oracle). The single "mismatch" is the same live-state `PF_SELECTED_ROW_MARKER` (row 1 active during the
read), not a decode error. The remaining 3 `PF_DECORATION_LABEL*` are a Label-kind gap (out of the EditField
value surface) ⇒ **43/46**. This closes the bounded card-98 #1 refinement (the "would-be 43/46" target).

## Root cause (the gap that was left)

The genuine form-analysis sweep DID query the Cyrillic fields — frames **296-303** of `tm-v1-ro-batchQ3` are
value-reads of `EditField[ПолеСоСпискомВыбораСтрока]` (296-299) and `EditField[Контрагент]` (300-303). But two
links in the read path were ASCII-only:

1. **Enumeration** — `_enumerate_capture_fields` matched only the ASCII query-path regex
   (`Group[..].EditField[..]` in latin1). The Cyrillic query paths are a different on-wire encoding, so they
   were never added to the sweep's element list.
2. **Retarget** — `_retarget_read_to_groups` rebuilt the per-field read path with `ElementRef.path()` and
   `retarget_element_path`, which encode latin1. A Cyrillic `new_path.encode("latin1")` raises
   `UnicodeEncodeError` (a `ValueError` subclass) → silently swallowed → the field was skipped.

## The wire encoding (decoded from frames 218 vs 300)

An element path is a length-prefixed string block. The **string envelope tag** selects the encoding (the same
`0x9a`/`0x97` family seen on field VALUES):

| encoding | block | example (path string) |
| --- | --- | --- |
| ASCII | `9a <byte-len:1> <latin1>` | `…Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[PF_EDIT_STRING]` (171 B, `9a ab …`) |
| UTF-16 | `97 <char-count:1> <utf-16le>` | `…Group[Группа1].EditField[Контрагент]` (139 chars, `97 8b …`) |

The whole path is ONE encoding: because the leaf/group is Cyrillic, the entire path — GUIDs included — rides as
UTF-16LE under the `0x97` tag. The Cyrillic fields live in `Group[Группа1]` (a single Cyrillic group, not the
`PF_GROUP_MAIN/PF_GROUP_EDITS` chain).

**De-risk — the retarget is structurally identical to the proven ASCII path.** Stripping the path block from
the ASCII read frame 218 and the genuine Cyrillic read frame 300 leaves **byte-identical skeletons** except (a)
the seq counter at offset 19 and (b) a 16-byte per-read GUID block preceding the path — BOTH of which the
existing, working ASCII retarget already reuses from frame 218 across all 41 ASCII fields. So retargeting
218→a UTF-16 path reproduces exactly the genuine Cyrillic read. Confirmed offline: the retargeted frames are
byte-length-identical to the genuine ones (Контрагент 375 B = frame 300; ПолеСоСпискомВыбораСтрока 405 B =
frame 296), and `encode_element_path_block` round-trips the genuine on-wire block byte-exactly. The
`frame_rewriter` runs AFTER GUID rebind (`session.py:580`, on `rendered.payload`), so the rebuilt UTF-16 path
carries the LIVE GUIDs directly — no dependence on GuidRebinder seeing UTF-16 GUIDs.

## The fix

`src/qa_mcp/protocol/element_ref.py` (reusable, unit-tested):
- `path_is_latin1(path)` — predicate for ASCII (0x9a) vs UTF-16 (0x97) encoding.
- `encode_element_path_block(path)` — encode a path to its on-wire `<tag><len:1><bytes>` block (char-count =
  UTF-16 code units for the 0x97 form).
- `extract_element_paths_utf16(frame)` — the UTF-16 twin of `extract_element_paths` (finds `0x97`-tagged paths).
- `retarget_element_path_reencode(frame, old, new)` — swap an ASCII block for a re-encoded one when the
  encoding changes (tag byte included); raises if the ASCII block is absent.

`src/qa_mcp/mcp_server.py`:
- `_enumerate_capture_fields` also enumerates UTF-16 query paths → `Контрагент` / `ПолеСоСпискомВыбораСтрока`
  in `Группа1` (now 43 specs, was 41).
- `_retarget_read_to_groups` dispatches: latin1 target → existing `retarget_element_path` (0x9a, zero change);
  non-latin1 target → `retarget_element_path_reencode` (0x97). ASCII path untouched ⇒ no regression on the 41
  ASCII fields.

The response parser needed NO change: `extract_form_field_values` already decodes UTF-16LE leaves and the
`e0 4b 53 81` canonical-empty value (Контрагент/Поле are empty reference fields → `""`).

## Live verification

`tools/protocol-research/form_descriptor_verify.py` (fresh native /TESTCLIENT on :15381, apache managed):

```
descriptor: 43 fields decoded / 43 queried
oracle 46 fields; common 43; VALUE-MATCH 42/43
oracle NOT in descriptor: ['PF_DECORATION_LABEL', 'PF_DECORATION_LABEL_LINK', 'PF_DECORATION_LABEL_PICTURE_LINK']
mismatches: [('PF_SELECTED_ROW_MARKER', 'PF_ROW_IDX_1:PF_ROW_001', 'PF_ROW_NONE')]   # live-state, not a decode error
Cyrillic fields (card 98 #1 — UTF-16 0x97 query path):
  Контрагент                 -> ''  (decoded=True, oracle='')
  ПолеСоСпискомВыбораСтрока  -> ''  (decoded=True, oracle='')
```

## Scope / what's still a gap (honest)

- **3 form decorations** (`PF_DECORATION_LABEL*`) — a Label kind, static captions, not EditField values. The
  oracle reports them (their value = the caption), but they are out of the value-read EditField surface — a
  separate, lower-value follow-up (would need the Label render/caption decode) ⇒ 43/46 is the EditField ceiling.
- **Single-byte length cap (255):** `encode_element_path_block` / `extract_element_paths_utf16` assume a 1-byte
  length (matches every path in the fixture: max 154 chars). Real configs with deep group chains may exceed 255
  chars/code units → a multi-byte (varint) length is a generalization refinement (folds into card-98 #1/#3 ANY-
  form generalization).

## Artifacts

- Code: `src/qa_mcp/protocol/element_ref.py` (4 new helpers), `src/qa_mcp/mcp_server.py`
  (`_enumerate_capture_fields`, `_retarget_read_to_groups`, `read_form_descriptor` docstring).
- Tests: `tests/test_element_ref.py` (+7: path_is_latin1, encode ASCII/UTF-16, oversized reject, utf16 extract,
  reencode ASCII→UTF-16, absent-block raise, real-capture round-trip), `tests/test_form_descriptor.py` (+2:
  Cyrillic enumeration, Cyrillic retarget). **296 tests pass.**
- Probe: `tools/protocol-research/form_descriptor_verify.py` (now prints the Cyrillic fields explicitly).
- Oracle: `runtime/protocol-research/captures/tm-v1-ro-batchQ3/mcp_manager_fixture_optional_form_analysis_gherkin.json`.

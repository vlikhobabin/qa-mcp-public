"""Card 79 (Fork 1): value-read response parser — EditField data value vs the no-value stub."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol.responses import (  # noqa: E402
    extract_edit_field_value,
    extract_form_field_values,
    extract_table_cell_value,
    extract_testclient_windows,
    value_mode_present,
)

# The value-bearing shape proven live (card 79): element path + 0x81 value mode + 0xfa + length + value.
VALUE_BLOB = b"\x00\x00SecondaryFrame[030a5414].EditField[PF_EDIT_STRING]\x81\x81\x81\xfa\x14PF_EDIT_STRING_VALUE\xa1\x00"
# The no-value structure stub (form not realized): mode 0x88, no length-prefixed value.
STUB_BLOB = b"\x00\x00SecondaryFrame[030a5414].EditField[PF_EDIT_STRING]\x88\x81\x81\xe1\x00\x00"


def test_extract_value_from_value_mode_response() -> None:
    assert extract_edit_field_value(VALUE_BLOB, "PF_EDIT_STRING") == "PF_EDIT_STRING_VALUE"
    assert value_mode_present(VALUE_BLOB, "PF_EDIT_STRING") is True


def test_no_value_stub_returns_none() -> None:
    assert extract_edit_field_value(STUB_BLOB, "PF_EDIT_STRING") is None
    assert value_mode_present(STUB_BLOB, "PF_EDIT_STRING") is False


def test_other_field_not_matched() -> None:
    assert extract_edit_field_value(VALUE_BLOB, "PF_OTHER_FIELD") is None


# Card 97 #5: the value is LEB128-length-prefixed, NOT delimited by a literal 0x14 (which was merely
# len("PF_EDIT_STRING_VALUE")==20). A field whose value length != 20 must still parse.
READONLY_BLOB = (
    b"\x00\x00SecondaryFrame[030a5414].EditField[PF_EDIT_READONLY]"
    b"\x81\x81\x81\xfa\x16PF_EDIT_READONLY_VALUE\x20\xa1\x00"  # 0x16 = 22 = len(value)
)


def test_extract_value_independent_of_value_length() -> None:
    # the old 0x14-delimiter regex missed this (value is 22 chars, not 20); LEB128 length reads it
    assert extract_edit_field_value(READONLY_BLOB, "PF_EDIT_READONLY") == "PF_EDIT_READONLY_VALUE"
    assert value_mode_present(READONLY_BLOB, "PF_EDIT_READONLY") is True


def test_extract_single_byte_length_128_to_255() -> None:
    # card 98 #1: the value length is a SINGLE byte (0..255), NOT LEB128. A 143-char value rides as
    # `fa 8f <143 bytes>` (0x8f == 143 literal); a LEB128 reader would treat 0x8f's high bit as a continuation
    # and over-run. Single-byte is decisive from the genuine capture (`fa 8f 50…`, 0x50 == 'P').
    value = b"X" * 143
    blob = b"\x00EditField[PF_LONG]\x81\x81\x81\xfa\x8f" + value + b"\xa1"
    assert extract_edit_field_value(blob, "PF_LONG") == "X" * 143


# --- Card 97 #3: number & date decode through the same value shape (NOT a per-type buffer) ----------------
# Bytes mirror a GENUINE value-read capture (runtime/.../tm-v1-ro-batchQ3): a number rides the wire as its
# formatted display text "120,50" and a datetime as "15.01.2026 10:30:00", both in the 81 81 81 fa <len> shape.
NUMBER_VALUE_BLOB = b"\x00EditField[PF_EDIT_NUMBER]\x81\x81\x81\xfa\x06" + b"120,50" + b"\x20\xa1"
DATE_VALUE_BLOB = b"\x00EditField[PF_EDIT_DATE]\x81\x81\x81\xfa\x13" + b"15.01.2026 10:30:00" + b"\x20\xa1"


def test_number_value_decodes_as_display_text() -> None:
    assert extract_edit_field_value(NUMBER_VALUE_BLOB, "PF_EDIT_NUMBER") == "120,50"


def test_date_value_decodes_as_display_text() -> None:
    assert extract_edit_field_value(DATE_VALUE_BLOB, "PF_EDIT_DATE") == "15.01.2026 10:30:00"


# A value-read response echoes the field NAME first as a descriptor (EditField[<name>] 81 fa 0c <name> …,
# NOT a value); the value (81 81 81 fa …) follows. A single find() landed on the descriptor and returned None —
# the scan must skip the descriptor echo and land on the value. Bytes mirror the genuine capture occ1→occ2.
DESCRIPTOR_THEN_VALUE_BLOB = (
    b"\x00EditField[PF_EDIT_NUMBER]\x81\xfa\x0ePF_EDIT_NUMBER\xfa\x0ePF_EDIT_NUMBER"  # descriptor echo (no value)
    b"\x00\x00...padding...\x00\x00"
    b"EditField[PF_EDIT_NUMBER]\x81\x81\x81\xfa\x06" + b"120,50" + b"\x20\xa1"        # the actual value
)


def test_descriptor_echo_before_value_is_skipped() -> None:
    # regression: the name-echo occurrence precedes the value occurrence; scanning must return the value
    assert extract_edit_field_value(DESCRIPTOR_THEN_VALUE_BLOB, "PF_EDIT_NUMBER") == "120,50"


# The alternate value shape wraps the value in the 0x9a string envelope: 81 81 81 e0 4b 53 9a <len> <value>.
E0_ENVELOPE_BLOB = b"\x00EditField[PF_EDIT_NUMBER]\x81\x81\x81\xe0\x4b\x53\x9a\x05" + b"120,5" + b"\x20\x20\xa1"


def test_e0_string_envelope_shape_decodes() -> None:
    assert extract_edit_field_value(E0_ENVELOPE_BLOB, "PF_EDIT_NUMBER") == "120,5"


# The empty/no-value stub is 81 81 81 e2 20 — it must be skipped (return None when no real value follows).
E2_STUB_BLOB = b"\x00EditField[PF_EDIT_NUMBER]\x81\x81\x81\xe2\x20\xa1\xa3"


def test_e2_empty_stub_returns_none() -> None:
    assert extract_edit_field_value(E2_STUB_BLOB, "PF_EDIT_NUMBER") is None


# --- Card 98 #1: full-form descriptor parser (extract_form_field_values) -----------------------------------
# Bytes mirror the genuine form-analysis dump: each field's canonical «стал равен» value rides the e0 envelope
# (9a single-byte / 97 UTF-16 / 8b short-number / 81 empty); the 0xfa first occurrence is the edit-text.
def _ascii_leaf(name: str) -> bytes:
    return b"EditField[" + name.encode("latin1") + b"]"


def _u16_leaf(name: str) -> bytes:
    return ("EditField[" + name + "]").encode("utf-16-le")


FORM_DUMP = (
    b"\x00" + _ascii_leaf("PF_STR") + b"\x81\x81\x81\xe0\x4b\x53\x9a\x03ABC\x20"          # canonical string "ABC"
    + b"\x00" + _ascii_leaf("PF_NUM") + b"\x81\x81\x81\xe0\x4b\x53\x8b" + b"42\x20\x20"   # canonical short-number "42"
    + b"\x00" + _ascii_leaf("PF_CB") + b"\x81\x81\x81\xe0\x4b\x53\x97\x02\x14\x04\x30\x04\x20"  # checkbox UTF-16 "Да"
    + b"\x00" + _ascii_leaf("PF_EMPTY") + b"\x81\x81\x81\xe0\x4b\x53\x81\x20"             # canonical empty ""
    + b"\x00" + _ascii_leaf("PF_ETONLY") + b"\x81\x81\x81\xfa\x02XY\x20"                  # edit-text only "XY"
    # canonical PREFERRED over edit-text: the fa edit-text "0,00" then the e0 canonical "0"
    + b"\x00" + _ascii_leaf("PF_PREF") + b"\x81\x81\x81\xfa\x040,00\x20"
    + b"\x00" + _ascii_leaf("PF_PREF") + b"\x81\x81\x81\xe0\x4b\x53\x8b" + b"0\x20\x20"
    + b"\x00" + _u16_leaf("Контрагент") + b"\x81\x81\x81\xe0\x4b\x53\x81\x20"             # UTF-16 Cyrillic leaf, empty
)


def test_extract_form_field_values_all_markers() -> None:
    got = extract_form_field_values(FORM_DUMP)
    assert got["PF_STR"] == "ABC"
    assert got["PF_NUM"] == "42"
    assert got["PF_CB"] == "Да"          # UTF-16 boolean display
    assert got["PF_EMPTY"] == ""
    assert got["PF_ETONLY"] == "XY"      # 0xfa edit-text fallback when no canonical value
    assert got["Контрагент"] == ""       # UTF-16LE Cyrillic field name


def test_extract_form_field_values_prefers_canonical_over_edittext() -> None:
    # numbers differ: edit-text "0,00" vs canonical «стал равен» "0" — the descriptor takes the canonical value
    assert extract_form_field_values(FORM_DUMP)["PF_PREF"] == "0"


def test_truncated_form_field_value_returns_partial_result() -> None:
    blob = b"\x00" + _ascii_leaf("PF_TRUNC") + b"\x81\x81\x81"

    assert extract_form_field_values(blob) == {}


def test_truncated_window_caption_returns_partial_result() -> None:
    guid = b"11111111-1111-1111-1111-111111111111"

    assert extract_testclient_windows(b"SecondaryFrame[" + guid + b"]\x82") == []


def test_latin1_limited_field_scan_rejects_cyrillic_safely() -> None:
    assert extract_edit_field_value(VALUE_BLOB, "Контрагент") is None
    assert value_mode_present(VALUE_BLOB, "Контрагент") is False


def test_extract_table_cell_value() -> None:
    """Card 98 — the table-cell-read response value rides `81 81 81 e0 4b 53 <type> …` after the Table path (not
    an EditField leaf). extract_table_cell_value finds the envelope directly. Genuine: CELLREAD7 (chunk [74])."""
    genuine = bytes.fromhex("818181e04b539a0943454c4c5245414437eb539a0d50465f5441424c455f54455854")
    assert extract_table_cell_value(genuine) == "CELLREAD7"
    # number (short-number 8b) + empty (no current row → e0 4b 55 echo, no e0 4b 53 value)
    assert extract_table_cell_value(b"...Table[T]\x81\x81\x81\xe0\x4b\x53\x8b" + b"1,10\x20\x20") == "1,10"
    assert extract_table_cell_value(b"...Table[T]\x8a\x81\x81\xe0\x4b\x55\xeb\x53") is None  # no current-row value

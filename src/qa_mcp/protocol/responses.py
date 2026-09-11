"""Response summarization and read-only UI field extraction."""

from __future__ import annotations

import re
from typing import Any

from .frames import GUID_PATTERN, find_positions, preview_hex, sha256_hex, strip_tail


ASCII_STRING_RE = re.compile(rb"[ -~]{5,}")
UI_ASCII_MARKERS = ("MainFrame", "HomePage", "e1cib/", "navigationpoint")
FORM_ELEMENT_PATH_RE = re.compile(
    r"(?P<form>.+?\.ManagedForm\[" + GUID_PATTERN + r"\])\.(?P<element_type>[A-Za-z]+)\[(?P<name>[^\]]+)\]"
)


def ascii_strings(payload: bytes, limit: int = 24) -> list[str]:
    strings: list[str] = []
    for match in ASCII_STRING_RE.finditer(payload):
        value = match.group(0).decode("ascii", errors="replace")
        if value not in strings:
            strings.append(value)
        if len(strings) >= limit:
            break
    return strings


def allowed_utf16_char(char: str) -> bool:
    code = ord(char)
    if char in " \t\r\n.,:;_-\\/[](){}":
        return True
    if 0x30 <= code <= 0x39:
        return True
    if 0x41 <= code <= 0x5A or 0x61 <= code <= 0x7A:
        return True
    if 0x0400 <= code <= 0x052F:
        return True
    return False


def looks_meaningful_text(value: str) -> bool:
    stripped = value.strip()
    if len(stripped) < 4:
        return False
    letters = sum(1 for char in stripped if char.isalpha())
    return letters >= 3


def utf16le_strings(payload: bytes, limit: int = 24) -> list[dict[str, Any]]:
    body = strip_tail(payload)
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for offset in range(0, max(0, len(body) - 1)):
        if offset >= 2:
            previous = chr(int.from_bytes(body[offset - 2 : offset], byteorder="little"))
            if allowed_utf16_char(previous):
                continue
        chars: list[str] = []
        cursor = offset
        while cursor + 1 < len(body):
            char = chr(int.from_bytes(body[cursor : cursor + 2], byteorder="little"))
            if not allowed_utf16_char(char):
                break
            chars.append(char)
            cursor += 2
        if not chars:
            continue
        value = "".join(chars).strip()
        if not looks_meaningful_text(value) or value in seen:
            continue
        seen.add(value)
        found.append({"offset": offset, "text": value})
        if len(found) >= limit:
            break
    return found


def ui_identifiers(ascii_values: list[str], utf16_values: list[dict[str, Any]]) -> list[str]:
    identifiers: list[str] = []
    for value in ascii_values:
        if any(marker in value for marker in UI_ASCII_MARKERS) and value not in identifiers:
            identifiers.append(value)
    for item in utf16_values:
        text = item["text"]
        if text not in identifiers:
            identifiers.append(text)
    return identifiers


def semantic_guess(identifiers: list[str]) -> str:
    joined = "\n".join(identifiers)
    has_main_frame = "MainFrame" in joined
    has_home_page = "HomePage" in joined
    has_startpage = "e1cib/navigationpoint/startpage" in joined
    has_managed_form = "ManagedForm" in joined
    has_form_name = "\u0424\u043e\u0440\u043c\u0430" in joined
    has_form_elements = ".ManagedForm[" in joined and "[" in joined and "]" in joined
    if "EditField[" in joined:
        return "form_element_summary"
    if has_managed_form and has_form_name:
        return "active_form_descriptor"
    if has_form_elements:
        return "managed_form_ref"
    if has_main_frame and has_home_page:
        return "main_frame_with_home_page"
    if has_home_page and has_startpage:
        return "home_page_navigation_point"
    if has_home_page:
        return "home_page"
    if identifiers:
        return "ui_payload"
    return ""


def response_summary(send_index: int, response: bytes, replacements: list[dict[str, Any]]) -> dict[str, Any]:
    response_body = strip_tail(response)
    ascii_values = ascii_strings(response_body)
    utf16_values = utf16le_strings(response_body)
    identifiers = ui_identifiers(ascii_values, utf16_values)
    nonce_echoes = []
    for replacement in replacements:
        if not replacement["name"].startswith("nonce"):
            continue
        block = bytes.fromhex(replacement["replacement_hex"])
        nonce_echoes.append(
            {
                "manager_offset": replacement["offset"],
                "block_hex": block.hex(),
                "response_positions": find_positions(response_body, block),
            }
        )
    return {
        "send_index": send_index,
        "response_byte_count": len(response),
        "response_sha256": sha256_hex(response),
        "response_head_hex": preview_hex(response),
        "nonce_echoes": nonce_echoes,
        "ascii_strings": ascii_values,
        "utf16le_strings": utf16_values,
        "ui_identifiers": identifiers,
        "semantic_guess": semantic_guess(identifiers),
    }


def extract_edit_field_value(blob: bytes, field: str) -> str | None:
    """Return the LIVE data value of ``EditField[<field>]`` from a value-read response, or None
    when the response carries no value (the 0x88 / 0xe2 structure stub instead of the 0x81 value mode).
    Card 79: this is the wire shape that exposes a field's current value for effect verification.

    Value shapes after the ``EditField[<field>]`` leaf in a value-read response (client→manager):

    - ``81 81 81 fa          <byte-len> <value>`` — the formatted display value (primary shape)
    - ``81 81 81 e0 4b 53 9a  <byte-len> <value>`` — the SAME value via the 0x9a string envelope
    - ``81 81 81 e2 20 …``                          — empty / no-value stub
    - ``88 81 …``                                   — field outside the queried region (no value)

    Card 98 #1 correction: the value length is a **single byte (0..255)**, NOT LEB128. The earlier "LEB128"
    framing was indistinguishable for values ≤127 (single byte == LEB128 there) but WRONG for 128..255: a 143-char
    value rides as ``fa 8f <143 bytes>`` (0x8f == 143 literal), where a LEB128 reader treats 0x8f's high bit as a
    continuation and consumes the value's first byte → over-run. Single-byte length is decisive from the genuine
    capture (`fa 8f 50…`, 0x50 == 'P', the value start). (Values >255 are unobserved here.) Card 97 #3: number and
    date decode through this same shape — they ride the wire as their formatted display text (genuine-capture
    verified: ``PF_EDIT_NUMBER``→"120,50", ``PF_EDIT_DATE``→"15.01.2026 10:30:00") — so no per-type decoder is
    needed; use the ``numeric`` assert mode for format-robust number comparison. This **scans ALL leaf
    occurrences** and returns the first carrying a real value: a value-read response echoes the field NAME first as
    a descriptor (``EditField[<field>] 81 fa 0c <name>…`` — NOT a value), so a single ``find`` lands on the
    descriptor and (since it is not ``81 81 81``) returned None. Scanning skips the descriptor echo and the ``e2``
    empty stub and lands on the value."""
    try:
        leaf = b"EditField[" + field.encode("latin1") + b"]"
    except UnicodeEncodeError:
        return None
    start = 0
    while True:
        i = blob.find(leaf, start)
        if i < 0:
            return None
        start = i + 1
        p = i + len(leaf)
        if blob[p:p + 3] != b"\x81\x81\x81":  # descriptor echo (81 fa …) / 0x88 stub / unrelated — keep scanning
            continue
        marker = blob[p + 3:p + 4]
        if marker not in (b"\xe0", b"\xfa"):  # 0xe2 empty stub or other non-value mode — keep scanning
            continue
        q = p + 4
        if marker == b"\xe0" and blob[q:q + 3] == b"\x4b\x53\x9a":
            q += 3  # the e0 shape wraps the value in the 0x9a string envelope before the length
        if q >= len(blob):
            continue
        length = blob[q]  # single-byte value length (0..255), then that many value bytes
        q += 1
        raw = blob[q:q + length]
        if len(raw) < length:  # truncated at this occurrence — try the next
            continue
        for codec in ("utf-8", "utf-16-le", "latin1"):
            try:
                return raw.decode(codec).rstrip(" ")
            except UnicodeDecodeError:
                continue
        return raw.decode("latin1", "replace").rstrip(" ")


def value_mode_present(blob: bytes, field: str) -> bool:
    """True when ``EditField[<field>]`` is followed by the 0x81 value mode (a realized form read),
    not the 0x88 no-value stub. Card 79."""
    try:
        leaf = b"EditField[" + field.encode("latin1") + b"]\x81"
    except UnicodeEncodeError:
        return False
    return leaf in blob


def _decode_value_bytes(raw: bytes) -> str:
    """Decode a single-byte (latin1/utf-8) value run, right-trimming the field-width space padding."""
    for codec in ("utf-8", "latin1"):
        try:
            return raw.decode(codec).rstrip(" ")
        except UnicodeDecodeError:
            continue
    return raw.decode("latin1", "replace").rstrip(" ")


def _value_after_leaf(blob: bytes, p: int) -> tuple[str | None, str | None]:
    """Decode the value at an ``EditField`` value-mode occurrence starting at ``p`` (just past the leaf ``]``).
    Returns ``(kind, value)`` where kind is ``"canonical"`` (the e0 «стал равен» value) or ``"edittext"`` (the
    0xfa display text), or ``(None, None)`` for a descriptor echo / 0xe2 stub / bool-render. Card 98 #1: value
    lengths are a single byte. Markers after ``81 81 81``:
      ``fa <len> <latin1>``                  — edit-text / display value
      ``e0 4b 53 9a <len> <latin1>``         — canonical single-byte string / number / date
      ``e0 4b 53 97 <charcount> <utf-16le>`` — canonical UTF-16 value (checkbox Да/Нет, Cyrillic)
      ``e0 4b 53 8b <digits>``               — canonical short number (digits to the space pad)
      ``e0 4b 53 81 <pad>``                  — canonical empty value
    """
    if blob[p:p + 3] != b"\x81\x81\x81":
        return None, None
    q = p + 3
    if q >= len(blob):
        return None, None
    marker = blob[q]
    q += 1
    if marker == 0xE0:                                  # canonical value envelope: e0 4b 53 <type> …
        if blob[q:q + 2] != b"\x4b\x53":
            return None, None
        q += 2
        if q >= len(blob):
            return None, None
        t = blob[q]
        q += 1
        if t == 0x9A:                                   # single-byte string / number / date
            if q >= len(blob):
                return None, None
            ln = blob[q]
            q += 1
            raw = blob[q:q + ln]
            return ("canonical", _decode_value_bytes(raw)) if len(raw) == ln else (None, None)
        if t == 0x97:                                   # UTF-16LE (checkbox Да/Нет, Cyrillic value)
            if q >= len(blob):
                return None, None
            cc = blob[q]
            q += 1
            raw = blob[q:q + 2 * cc]
            return ("canonical", raw.decode("utf-16-le", "replace").rstrip(" ")) if len(raw) == 2 * cc else (None, None)
        if t == 0x8B:                                   # short number — single-byte digits to the space pad
            j = q
            while j < len(blob) and 0x20 < blob[j] < 0x7F:
                j += 1
            return "canonical", blob[q:j].decode("latin1").rstrip(" ")
        if t == 0x81:                                   # empty value
            return "canonical", ""
        return None, None
    if marker == 0xFA:                                  # edit-text / display value (single-byte length)
        if q >= len(blob):
            return None, None
        ln = blob[q]
        q += 1
        raw = blob[q:q + ln]
        return ("edittext", _decode_value_bytes(raw)) if len(raw) == ln else (None, None)
    return None, None


def extract_table_cell_value(blob: bytes) -> str | None:
    """Card 98 — decode the CURRENT ROW's cell value from a table-cell-read response (the reply to
    ``native_write.splice_table_cell_read``). The value rides the canonical ``81 81 81 e0 4b 53 <type> …``
    envelope — the SAME «стал равен» value a form field uses — but it follows the response opcode after the Table
    path, NOT an ``EditField[name]`` leaf, so ``extract_form_field_values`` (which anchors on EditField leaves)
    misses it. Find the ``81 81 81 e0 4b 53`` sequence and decode via ``_value_after_leaf`` (string / number /
    date / UTF-16 / empty). Returns the value, or None when there is no canonical value (e.g. no current row → the
    client echoes the command with ``e0 4b 55`` and no ``e0 4b 53`` value)."""
    anchor = blob.find(b"\x81\x81\x81\xe0\x4b\x53")
    if anchor < 0:
        return None
    kind, value = _value_after_leaf(blob, anchor)
    return value if kind == "canonical" else None


_EDITFIELD_ASCII_RE = re.compile(rb"EditField\[([\x20-\x7e]+?)\]")
_EDITFIELD_UTF16_RE = re.compile(
    rb"E\x00d\x00i\x00t\x00F\x00i\x00e\x00l\x00d\x00\[\x00((?:(?!\]\x00)..)+?)\]\x00", re.S
)


def extract_form_field_values(blob: bytes) -> dict[str, str]:
    """Card 98 #1 — decode EVERY form element's name→value from a form-analysis / value-read response: the
    capture-free equivalent of Vanessa ``get_form_analysis``'s «элемент формы с именем 'X' стал равен "V"» dump.

    Scans every ``EditField[<name>]`` value occurrence (names encoded ASCII or UTF-16LE for Cyrillic) and decodes
    its value via ``_value_after_leaf``, **preferring the canonical e0 «стал равен» value** over the 0xfa
    edit-text (they differ e.g. for numbers: canonical "0" vs edit-text "0,00"). Returns ``{name: value}``.
    Validated against the genuine fixture form-analysis oracle. Not included: form decorations (Label kind, not an
    EditField) and value-less reference/combo fields — out of the EditField value surface."""
    canonical: dict[str, str] = {}
    edittext: dict[str, str] = {}
    for regex, codec in ((_EDITFIELD_ASCII_RE, "latin1"), (_EDITFIELD_UTF16_RE, "utf-16-le")):
        for m in regex.finditer(blob):
            kind, value = _value_after_leaf(blob, m.end())
            if kind is None:
                continue
            name = m.group(1).decode(codec, "replace")
            target = canonical if kind == "canonical" else edittext
            target.setdefault(name, value)  # first value occurrence per field wins
    return {name: canonical.get(name, edittext.get(name)) for name in (set(canonical) | set(edittext))}


_DESCRIPTOR_FIELD_ASCII_RE = re.compile(rb"((?:Group\[[A-Za-z0-9_]+\]\.)+)EditField\[([A-Za-z0-9_]+)\]")
_DESCRIPTOR_FIELD_UTF16_RE = re.compile(
    rb"((?:G\x00r\x00o\x00u\x00p\x00\[\x00(?:(?!\]\x00)..)+?\]\x00\.\x00)+)"
    rb"E\x00d\x00i\x00t\x00F\x00i\x00e\x00l\x00d\x00\[\x00((?:(?!\]\x00)..)+?)\]\x00",
    re.S,
)
# Card 98 change-5 — form-fields DIRECTLY under ManagedForm (zero enclosing Group), e.g. a catalog RECORD form
# (`ManagedForm[F].EditField[Наименование]` — БСП object-attribute fields, no group). The `(Group…)+` patterns
# above require ≥1 group; these match the zero-group case. Anchored on `ManagedForm[<guid>].` so a dynlist COLUMN
# (`…Table[Список].EditField[col]`) is NOT matched (a column is preceded by Table, not ManagedForm directly).
_DESCRIPTOR_FIELD0_ASCII_RE = re.compile(
    rb"ManagedForm\[[0-9a-fA-F-]{36}\]\.EditField\[([A-Za-z0-9_]+)\]"
)
_DESCRIPTOR_FIELD0_UTF16_RE = re.compile(
    rb"M\x00a\x00n\x00a\x00g\x00e\x00d\x00F\x00o\x00r\x00m\x00\[\x00(?:[0-9a-fA-F-]\x00){36}\]\x00\.\x00"
    rb"E\x00d\x00i\x00t\x00F\x00i\x00e\x00l\x00d\x00\[\x00((?:(?!\]\x00)..)+?)\]\x00",
    re.S,
)
_DESCRIPTOR_GROUP_ASCII_RE = re.compile(rb"Group\[([A-Za-z0-9_]+)\]")
_DESCRIPTOR_GROUP_UTF16_RE = re.compile(rb"G\x00r\x00o\x00u\x00p\x00\[\x00((?:(?!\]\x00)..)+?)\]\x00", re.S)


def extract_descriptor_fields(blob: bytes) -> list[tuple[str, list[str]]]:
    """Card 98 change-1 generalization — enumerate ``(field_name, [enclosing Group names])`` for every EditField
    in a LIVE form-descriptor response (the get_form_analysis descriptor re-render, obtained capture-free by the
    splice-replay of the descriptor query). Each element rides as ``(Group[g]\\.)+EditField[name]`` — ASCII
    (latin1) for ASCII names, UTF-16LE for Cyrillic group/leaf names (e.g. ``Group[Группа1].EditField[Контрагент]``).
    Both encodings are scanned; first-seen order, deduped by name. This is the live equivalent of
    ``_enumerate_capture_fields`` (which reads the field list from a per-form capture) — feed the result to the
    value-read sweep to introspect ANY form with NO per-form capture."""
    specs: dict[str, list[str]] = {}
    for m in _DESCRIPTOR_FIELD_ASCII_RE.finditer(blob):
        name = m.group(2).decode("latin1")
        if name not in specs:
            specs[name] = [g.decode("latin1") for g in _DESCRIPTOR_GROUP_ASCII_RE.findall(m.group(1))]
    for m in _DESCRIPTOR_FIELD_UTF16_RE.finditer(blob):
        name = m.group(2).decode("utf-16-le", "replace")
        if name not in specs:
            specs[name] = [g.decode("utf-16-le", "replace") for g in _DESCRIPTOR_GROUP_UTF16_RE.findall(m.group(1))]
    # zero-group form-fields (directly under ManagedForm — catalog RECORD forms), value-read with groups=[]
    for m in _DESCRIPTOR_FIELD0_ASCII_RE.finditer(blob):
        specs.setdefault(m.group(1).decode("latin1"), [])
    for m in _DESCRIPTOR_FIELD0_UTF16_RE.finditer(blob):
        specs.setdefault(m.group(1).decode("utf-16-le", "replace"), [])
    return list(specs.items())


_DESCRIPTOR_ELEMENT_KINDS = (
    "EditField", "Button", "Table", "Group", "Page", "Pages", "Decoration", "CommandBar", "Hyperlink",
    "CheckBoxField", "RadioButtonField", "PictureField", "SearchStringAddition", "ViewStatusAddition",
)
_DESCRIPTOR_ELEMENT_ASCII_RE = re.compile(
    rb"(" + b"|".join(k.encode() for k in _DESCRIPTOR_ELEMENT_KINDS) + rb")\[([A-Za-z0-9_]+)\]"
)
_DESCRIPTOR_ELEMENT_UTF16_RE = re.compile(
    rb"(" + b"|".join(k.encode("utf-16-le") for k in _DESCRIPTOR_ELEMENT_KINDS) + rb")"
    rb"\[\x00((?:(?!\]\x00)..)+?)\]\x00",
    re.S,
)


def extract_descriptor_elements(blob: bytes) -> list[dict[str, str]]:
    """Card 98 change-1 — enumerate EVERY element of a LIVE form descriptor (the ``ui_read_tree`` surface): all
    ``<Kind>[name]`` leaves — EditField / Button / Table / Group / Page / Decoration / … — ASCII and UTF-16LE
    (Cyrillic), de-duplicated by (kind, name) in first-appearance order. Use to introspect ANY form's structure
    capture-free (e.g. a catalog list's dynlist Table + columns + command buttons, where there are no
    form-level EditFields). Returns ``[{kind, name}]``."""
    elements: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for m in _DESCRIPTOR_ELEMENT_ASCII_RE.finditer(blob):
        key = (m.group(1).decode("latin1"), m.group(2).decode("latin1"))
        if key not in seen:
            seen.add(key)
            elements.append({"kind": key[0], "name": key[1]})
    for m in _DESCRIPTOR_ELEMENT_UTF16_RE.finditer(blob):
        key = (m.group(1).decode("utf-16-le", "replace"), m.group(2).decode("utf-16-le", "replace"))
        if key not in seen:
            seen.add(key)
            elements.append({"kind": key[0], "name": key[1]})
    return elements


_WINDOW_RECORD_RE = re.compile(rb"(SecondaryFrame|MainFrame|HomePage)\[([0-9a-f-]{36})\]")


def extract_testclient_windows(blob: bytes) -> list[dict[str, str]]:
    """Card 98 #2 — decode the TestClient window list from a genuine `get_window_list_testclient` response
    (the 1C-internal window/tab set, the vanessa-mcp `get_window_list_testclient` equivalent). The response is a
    sequence of window records; each is a frame path ``<Kind>[<guid>]`` (Kind ∈ SecondaryFrame | MainFrame |
    HomePage) immediately followed by the window CAPTION as ``82 <marker> <len> <text>`` — marker ``fa`` = ASCII
    (byte length, latin1), ``f7`` = UTF-16LE (char count) — the same value-encoding family as the field-value
    markers. Returns ``[{kind, guid, caption}]``, de-duplicated by (kind, guid) in first-appearance order (a
    response can carry a record twice across TCP segments). Decoded from the genuine manager capture
    `genuine-card98-windowlist-20260620` (4 windows: Товары / QA MCP Protocol Fixture V1 /
    Демонстрационное приложение / Начальная страница), matching the Vanessa oracle."""
    windows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for m in _WINDOW_RECORD_RE.finditer(blob):
        kind, guid = m.group(1).decode("latin1"), m.group(2).decode("latin1")
        if (kind, guid) in seen:
            continue
        caption = _window_caption_after(blob, m.end())
        if caption is None:
            continue
        seen.add((kind, guid))
        windows.append({"kind": kind, "guid": guid, "caption": caption})
    return windows


def _window_caption_after(blob: bytes, p: int) -> str | None:
    """Decode the window caption at ``82 <marker> <len> <text>`` just past a ``<Kind>[<guid>]`` path
    (``fa`` = ASCII byte-length latin1, ``f7`` = UTF-16LE char-count). Returns None if the marker is absent."""
    if blob[p:p + 1] != b"\x82":
        return None
    if p + 2 >= len(blob):
        return None
    marker = blob[p + 1]
    ln = blob[p + 2]
    body = blob[p + 3:]
    if marker == 0xF7:                       # UTF-16LE caption (char count)
        raw = body[:2 * ln]
        return raw.decode("utf-16-le", "replace") if len(raw) == 2 * ln else None
    if marker == 0xFA:                       # ASCII caption (byte length)
        raw = body[:ln]
        return _decode_value_bytes(raw) if len(raw) == ln else None
    return None


def extract_active_form_fields(frame_summary: dict[str, Any]) -> dict[str, str | None]:
    form_marker = "\u0424\u043e\u0440\u043c\u0430"
    utf16_texts = [str(item.get("text", "")) for item in frame_summary.get("utf16le_strings", [])]
    active_form_name = next((text for text in utf16_texts if f".{form_marker}." in text), None)
    if active_form_name is None:
        active_form_name = next((text for text in utf16_texts if form_marker in text and "." in text), None)
    active_form_caption = next((text for text in utf16_texts if text and text != active_form_name), None)
    managed_form_ref = next(
        (identifier for identifier in frame_summary.get("ui_identifiers", []) if ".ManagedForm[" in identifier),
        None,
    )
    return {
        "active_form_name": active_form_name,
        "active_form_caption": active_form_caption,
        "managed_form_ref": managed_form_ref,
    }


def extract_active_window_fields(frame_summary: dict[str, Any]) -> dict[str, Any]:
    identifiers = [str(item) for item in frame_summary.get("ui_identifiers", [])]
    active_window_ref = next((item for item in identifiers if "MainFrame" in item or "HomePage" in item), None)
    return {
        "active_window_ref": active_window_ref,
        "active_window_markers": identifiers,
    }


def extract_form_elements(frame_summary: dict[str, Any]) -> list[dict[str, Any]]:
    utf16_items = [
        {"offset": int(item.get("offset", 0)), "text": str(item.get("text", ""))}
        for item in frame_summary.get("utf16le_strings", [])
    ]
    elements: list[dict[str, Any]] = []
    for index, item in enumerate(utf16_items):
        match = FORM_ELEMENT_PATH_RE.match(item["text"])
        if not match:
            continue
        caption = None
        for candidate in utf16_items[index + 1 :]:
            text = candidate["text"]
            if not text:
                continue
            if FORM_ELEMENT_PATH_RE.match(text):
                break
            caption = text
            break
        elements.append(
            {
                "type": match.group("element_type"),
                "name": match.group("name"),
                "caption": caption,
                "path": item["text"],
                "offset": item["offset"],
            }
        )
    return elements


def extract_element_details(frame_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}
    for frame in frame_summaries:
        if frame.get("semantic_guess") != "form_element_summary":
            continue
        elements = extract_form_elements(frame)
        for element in elements:
            path = element["path"]
            detail = by_path.setdefault(
                path,
                {
                    "type": element["type"],
                    "name": element["name"],
                    "path": path,
                    "captions": [],
                    "frames": [],
                },
            )
            caption = element.get("caption")
            if caption and caption not in detail["captions"]:
                detail["captions"].append(caption)
            detail["frames"].append(
                {
                    "send_index": frame.get("send_index"),
                    "response_byte_count": frame.get("response_byte_count"),
                    "semantic_guess": frame.get("semantic_guess"),
                    "caption": caption,
                    "utf16le_strings": frame.get("utf16le_strings", []),
                    "ui_identifiers": frame.get("ui_identifiers", []),
                }
            )
    return list(by_path.values())

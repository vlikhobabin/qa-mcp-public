"""Decode a captured flow into a semantic navigation plan.

1C navigation is driven by navigation links (``e1cib/<kind>/<metadata-path>``)
carried as UTF-16LE text in the manager command frames, plus FindObject-style
commands that carry their parameters as text (a row selector = column name +
value; a button = its title). This module extracts the structured part — the
navigation links — so the manager can see and re-target *which object* a flow
opens, the foundation for constructing navigation natively instead of replaying
opaque captured frames.

Decoded for the warehouse flow:
- ``e1cib/list/Справочник.Склады`` (open the warehouse list) at frame 8;
- the row selector (column ``Наименование`` + value) and the ``Изменить`` button
  are FindObject text commands handled by ``native_mutation.retarget_row_value``
  and friends.
"""

from __future__ import annotations

import re
import secrets
import uuid
from dataclasses import dataclass
from typing import Any

# e1cib/<kind>/<metadata path>. The path is letters/digits/dot/underscore
# (Unicode \w covers Cyrillic metadata names); it ends at the first other byte.
_NAV_LINK_RE = re.compile(r"e1cib/(?P<kind>[A-Za-z]+)/(?P<path>[\w.]+)", re.UNICODE)

# Decoded field map of the open-list command frame (manager ordinal 8 of the
# warehouse flow). The MainFrame GUID is the live home-window id learned in the
# handshake; the nav path is the semantic parameter (which list to open).
OPEN_LIST_MESSAGE_ID = (2, 16)
OPEN_LIST_SEQUENCE = (19, 2)
OPEN_LIST_NONCE = (68, 16)
OPEN_LIST_MAINFRAME_GUID_ASCII = (96, 36)
_GUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

_DASHED_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def e1cib_ref_hex(uuid_str: str) -> str:
    """Encode a dashed object reference UUID (the OData ``Ref_Key`` / ``УникальныйИдентификатор`` form) into the
    32-hex ``ref=`` token a 1C ``e1cib/data/<Type>?ref=…`` navigation link uses (card 99).

    The encoding was DECODED from the genuine open-card capture (``genuine-card96-opencard``), whose wire carried
    ``e1cib/data/Справочник.Контрагенты?ref=a9b000055d49b45e11db8c4c9d5c422d`` for «Покупатели»
    (Ref_Key ``9d5c422d-8c4c-11db-a9b0-00055d49b45e``). For UUID groups ``g1-g2-g3-g4-g5`` the link ref is the
    groups reordered **g4·g5·g3·g2·g1** (the clock-seq + node half first, then the time half reversed by group).
    Live-verified: «Покупатели», «Доставка (Товар)» open + value-read vs OData. Accepts an already-encoded 32-hex
    token unchanged (idempotent)."""
    s = uuid_str.strip()
    if _DASHED_UUID_RE.match(s):
        h = s.replace("-", "").lower()
        g1, g2, g3, g4, g5 = h[0:8], h[8:12], h[12:16], h[16:20], h[20:32]
        return g4 + g5 + g3 + g2 + g1
    low = s.lower()
    if len(low) == 32 and all(c in "0123456789abcdef" for c in low):
        return low                                  # already the 32-hex e1cib ref token
    raise ValueError(f"not a dashed UUID or 32-hex ref: {uuid_str!r}")


def e1cib_data_link(type_name: str, ref: str) -> str:
    """Build the ``e1cib/data/<Type>?ref=<hex>`` navigation link that opens an EXISTING object's record form
    (card 99). ``type_name`` is the metadata full name (e.g. ``Справочник.Товары``); ``ref`` is the dashed
    OData ``Ref_Key`` (auto-encoded via :func:`e1cib_ref_hex`) or an already-encoded 32-hex token."""
    return f"e1cib/data/{type_name}?ref={e1cib_ref_hex(ref)}"


@dataclass(frozen=True)
class NavigationLink:
    ordinal: int
    kind: str
    target: str
    link: str


def extract_navigation_links(manager_chunks: list[dict[str, Any]]) -> list[NavigationLink]:
    """Navigation links in command frames, in first-appearance order.

    ``manager_chunks`` is the manager_to_client stream (each item has a
    ``payload`` bytes field). UTF-16LE is decoded leniently.
    """

    seen: dict[str, NavigationLink] = {}
    for ordinal, chunk in enumerate(manager_chunks):
        text = chunk["payload"].decode("utf-16le", "ignore")
        for match in _NAV_LINK_RE.finditer(text):
            link = match.group(0)
            if link not in seen:
                seen[link] = NavigationLink(
                    ordinal=ordinal,
                    kind=match.group("kind"),
                    target=match.group("path"),
                    link=link,
                )
    return sorted(seen.values(), key=lambda nl: nl.ordinal)


def retarget_navigation_link(
    manager_chunks: list[dict[str, Any]], old_target: str, new_target: str
) -> tuple[list[dict[str, Any]], int]:
    """Re-point a navigation link's metadata path (length-preserving, UTF-16LE).

    E.g. open a different catalog list. The new target must be the same length so
    the command frame structure is preserved.
    """

    if len(old_target) != len(new_target):
        raise ValueError(
            f"navigation target length must match for in-place substitution: "
            f"{old_target!r}({len(old_target)}) != {new_target!r}({len(new_target)})"
        )
    old_b = old_target.encode("utf-16le")
    new_b = new_target.encode("utf-16le")
    out: list[dict[str, Any]] = []
    substitutions = 0
    for chunk in manager_chunks:
        payload = chunk["payload"]
        if old_b in payload:
            payload = payload.replace(old_b, new_b)
            substitutions += 1
        item = dict(chunk)
        item["payload"] = payload
        out.append(item)
    return out, substitutions


def retarget_nav_link(frame: bytes, old_link: str, new_link: str) -> tuple[bytes, int]:
    """Re-point an ``e1cib`` navigation link, VARIABLE-LENGTH (card 86d decode).

    A nav link is stored as ``<char-count:1 byte><utf-16le link text>`` — the byte immediately before the
    UTF-16LE link is its CHARACTER count (decoded 2026-06-17 from the genuine `e1cib/app/…` open command:
    the byte before the 47-char link was 47). Recomputing that count lets the new link be any length (≤255
    chars), lifting the same-length restriction of ``retarget_navigation_link`` / the catalog substitution in
    ``render_open_list_command``. Frames are tail-marker delimited (no total-length field), so the frame just
    grows/shrinks by the char-count delta. Returns ``(frame, substitutions)``; raises if the link is absent.

    NOTE: decoded offline; not yet live-verified — the lab captures contain no genuine ``e1cib/list/…``
    open-list flow (the fixture is a data processor opened via ``e1cib/app/…``). Verify against a genuine
    list capture before relying on it for open_list.
    """
    if len(new_link) > 255:
        raise ValueError("1-byte char-count prefix supports up to 255 characters")
    old_block = bytes([len(old_link)]) + old_link.encode("utf-16le")
    new_block = bytes([len(new_link)]) + new_link.encode("utf-16le")
    count = frame.count(old_block)
    if count == 0:
        raise ValueError(f"length-prefixed nav link {old_link!r} not found")
    return frame.replace(old_block, new_block), count


def _captured_main_frame_guid(template_body: bytes) -> str:
    offset, length = OPEN_LIST_MAINFRAME_GUID_ASCII
    guid = template_body[offset : offset + length].decode("ascii", "ignore")
    if not _GUID_RE.fullmatch(guid):
        raise ValueError(f"no MainFrame GUID at offset {offset} of the open-list template")
    return guid.lower()


def _captured_catalog(template_body: bytes) -> str:
    match = _NAV_LINK_RE.search(template_body.decode("utf-16le", "ignore"))
    if not match or match.group("kind") != "list":
        raise ValueError("open-list template has no e1cib/list/<path> nav link")
    return match.group("path")


def render_open_list_command(
    template_body: bytes,
    *,
    catalog: str,
    main_frame_guid: str,
    message_id: uuid.UUID | None = None,
    sequence: int | None = None,
    nonce: bytes | None = None,
) -> bytes:
    """Synthesize an open-list command for a chosen catalog and live session.

    Substitutes the live MainFrame GUID and the catalog metadata path into the
    decoded open-list command template, plus a fresh per-frame message id and an
    optional sequence / nonce. The catalog and MainFrame GUID must match the
    captured lengths (same-length in-place substitution; the frame's internal
    length fields are not yet decoded).
    """

    body = bytearray(template_body)
    old_guid = _captured_main_frame_guid(template_body)
    old_catalog = _captured_catalog(template_body)

    if len(catalog) != len(old_catalog):
        raise ValueError(
            f"catalog length must match captured {old_catalog!r}({len(old_catalog)}): "
            f"{catalog!r}({len(catalog)})"
        )

    # message id
    mid = (message_id or uuid.uuid4()).bytes_le[: OPEN_LIST_MESSAGE_ID[1]]
    body[OPEN_LIST_MESSAGE_ID[0] : OPEN_LIST_MESSAGE_ID[0] + OPEN_LIST_MESSAGE_ID[1]] = mid
    # sequence
    if sequence is not None:
        off, ln = OPEN_LIST_SEQUENCE
        body[off : off + ln] = int(sequence).to_bytes(ln, "little")
    # nonce
    off, ln = OPEN_LIST_NONCE
    body[off : off + ln] = (nonce or secrets.token_bytes(ln))[:ln]

    out = bytes(body)
    # MainFrame GUID: ASCII path text + binary LE form (utf-16le not present here)
    out = out.replace(old_guid.encode("ascii"), main_frame_guid.encode("ascii"))
    out = out.replace(old_guid.upper().encode("ascii"), main_frame_guid.encode("ascii"))
    try:
        out = out.replace(uuid.UUID(old_guid).bytes_le, uuid.UUID(main_frame_guid).bytes_le)
    except ValueError:
        pass
    # catalog (semantic parameter), UTF-16LE, same length
    out = out.replace(old_catalog.encode("utf-16le"), catalog.encode("utf-16le"))
    return out


# Standard dynamic-header field offsets shared by the form command frames
# (select_row, open_card, ...): message id, sequence, nonce. Session GUIDs
# (SecondaryFrame / ManagedForm) are carried as UTF-16LE path text and rebound
# via ``guid_map``; the semantic parameter (row value, button title) is a
# same-length UTF-16LE text substitution.
COMMAND_MESSAGE_ID = (2, 16)
COMMAND_SEQUENCE = (19, 2)
COMMAND_NONCE = (68, 16)


def _sub_guid_all_encodings(payload: bytes, old: str, new: str) -> bytes:
    if old == new:
        return payload
    out = payload
    for text in (old, old.upper()):
        out = out.replace(text.encode("ascii"), new.encode("ascii"))
        out = out.replace(text.encode("utf-16le"), new.encode("utf-16le"))
    try:
        out = out.replace(uuid.UUID(old).bytes_le, uuid.UUID(new).bytes_le)
    except ValueError:
        pass
    return out


def render_form_command(
    template_body: bytes,
    *,
    guid_map: dict[str, str] | None = None,
    text_params: list[tuple[str, str]] | None = None,
    message_id: uuid.UUID | None = None,
    sequence: int | None = None,
    nonce: bytes | None = None,
) -> bytes:
    """Generic form-command synthesizer (select_row, open_card, ...).

    Keeps the captured per-frame header values unless explicitly overridden, so
    a command stays byte-identical to the capture for the same target inside a
    rebound-replay chain. ``guid_map`` rebinds the live SecondaryFrame /
    ManagedForm GUIDs (all encodings); ``text_params`` re-targets same-length
    UTF-16LE semantic parameters (row value, button title).
    """

    body = bytearray(template_body)
    if message_id is not None:
        off, ln = COMMAND_MESSAGE_ID
        body[off : off + ln] = message_id.bytes_le[:ln]
    if sequence is not None:
        off, ln = COMMAND_SEQUENCE
        body[off : off + ln] = int(sequence).to_bytes(ln, "little")
    if nonce is not None:
        off, ln = COMMAND_NONCE
        body[off : off + ln] = nonce[:ln]

    out = bytes(body)
    for old, new in (guid_map or {}).items():
        out = _sub_guid_all_encodings(out, old, new)
    for old, new in text_params or []:
        if len(old) != len(new):
            raise ValueError(f"text param length must match: {old!r}({len(old)}) != {new!r}({len(new)})")
        out = out.replace(old.encode("utf-16le"), new.encode("utf-16le"))
    return out


def substitute_length_prefixed_string(payload: bytes, old: str, new: str) -> tuple[bytes, int]:
    """Replace a 1-byte-count-prefixed UTF-16LE string, lifting the same-length rule.

    Decoded: a length-prefixed string value is stored as ``<char_count:1 byte>``
    followed by the UTF-16LE text; frames are tail-marker delimited (no frame
    total-length field), so updating the count byte and the text is sufficient
    for an arbitrary-length re-target. Returns ``(payload, substitutions)``.
    """

    if len(old) > 255 or len(new) > 255:
        raise ValueError("1-byte count supports up to 255 chars")
    old_block = bytes([len(old)]) + old.encode("utf-16le")
    new_block = bytes([len(new)]) + new.encode("utf-16le")
    count = payload.count(old_block)
    if count == 0:
        raise ValueError(f"length-prefixed value {old!r} not found in command frame")
    return payload.replace(old_block, new_block), count


def render_select_row_command(
    template_body: bytes, *, old_value: str, new_value: str, guid_map: dict[str, str] | None = None, **kw: Any
) -> bytes:
    """Synthesize the row-select command, re-targeting the row value.

    Arbitrary-length: the value's 1-byte length prefix is updated, so the new
    value need not match the captured length.
    """

    body = render_form_command(template_body, guid_map=guid_map, **kw)
    if old_value == new_value:
        return body
    body, _ = substitute_length_prefixed_string(body, old_value, new_value)
    return body


def render_open_card_command(
    template_body: bytes, *, button: str = "Изменить", guid_map: dict[str, str] | None = None, **kw: Any
) -> bytes:
    """Synthesize the open-card command (identity for the standard Изменить button)."""

    return render_form_command(
        template_body, guid_map=guid_map, text_params=[(button, button)], **kw
    )

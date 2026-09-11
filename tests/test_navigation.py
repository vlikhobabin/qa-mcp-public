from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from qa_mcp.protocol.navigation import (
    COMMAND_MESSAGE_ID,
    COMMAND_SEQUENCE,
    OPEN_LIST_MAINFRAME_GUID_ASCII,
    NavigationLink,
    extract_navigation_links,
    render_form_command,
    render_open_card_command,
    render_open_list_command,
    render_select_row_command,
    retarget_nav_link,
    retarget_navigation_link,
    substitute_length_prefixed_string,
)


def test_retarget_nav_link_variable_length() -> None:
    # card 86d: <char-count:1><utf-16le link>; recomputing the count lifts the same-length restriction.
    link = "e1cib/list/Справочник.Склады"            # 28 chars
    frame = b"\xf7" + bytes([len(link)]) + link.encode("utf-16le") + b"\xa1tail"
    new = "e1cib/list/Справочник.Контрагенты"          # 33 chars (different length)
    out, n = retarget_nav_link(frame, link, new)
    assert n == 1
    assert bytes([len(new)]) + new.encode("utf-16le") in out
    assert link.encode("utf-16le") not in out
    assert len(out) == len(frame) + (len(new) - len(link)) * 2  # utf-16le: 2 bytes/char


def test_retarget_nav_link_absent_raises() -> None:
    with pytest.raises(ValueError):
        retarget_nav_link(b"no link", "e1cib/list/X", "e1cib/list/Y")


def _synthetic_open_list_body() -> bytes:
    guid = "6ca75e50-62a3-4842-b6cd-b429f7591ef2"
    body = bytearray(201)
    off, ln = OPEN_LIST_MAINFRAME_GUID_ASCII
    body[off : off + ln] = guid.encode("ascii")
    navlink = "e1cib/list/Справочник.Склады".encode("utf-16le")
    body[138 : 138 + len(navlink)] = navlink
    return bytes(body)


def _chunk(text: str) -> dict:
    return {"payload": text.encode("utf-16le")}


def test_extract_navigation_links_finds_list_link() -> None:
    chunks = [
        _chunk("noise"),
        _chunk("MainFrame[g] e1cib/list/Справочник.Склады \x00\x01padding"),
        _chunk("e1cib/list/Справочник.Склады again"),
        _chunk("e1cib/command/Документ.ОперацияПоУчетуТоваров.Создать"),
    ]
    links = extract_navigation_links(chunks)
    assert links[0] == NavigationLink(
        ordinal=1, kind="list", target="Справочник.Склады", link="e1cib/list/Справочник.Склады"
    )
    targets = {(l.kind, l.target) for l in links}
    assert ("list", "Справочник.Склады") in targets
    assert ("command", "Документ.ОперацияПоУчетуТоваров.Создать") in targets
    # dedup: the repeated list link appears once, at its first ordinal
    assert sum(1 for l in links if l.link == "e1cib/list/Справочник.Склады") == 1


def test_navigation_link_path_stops_at_binary() -> None:
    # the path must not swallow following binary bytes
    chunks = [_chunk("e1cib/list/Справочник.Склады") ]
    chunks[0]["payload"] += b"\x05\x00\x99\x01"
    links = extract_navigation_links(chunks)
    assert links[0].target == "Справочник.Склады"


def test_retarget_navigation_link_substitutes_same_length() -> None:
    chunks = [_chunk("e1cib/list/Справочник.Склады")]
    out, n = retarget_navigation_link(chunks, "Справочник.Склады", "Справочник.Товары")
    assert n == 1
    assert "Справочник.Товары".encode("utf-16le") in out[0]["payload"]
    assert "Справочник.Склады".encode("utf-16le") not in out[0]["payload"]


def test_retarget_navigation_link_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError):
        retarget_navigation_link([{"payload": b""}], "Справочник.Склады", "Справочник.Товар")


def test_render_open_list_synthesizes_fields() -> None:
    body = _synthetic_open_list_body()
    mid = uuid.UUID("11111111-2222-3333-4444-555555555555")
    new_guid = "abcdef01-2345-6789-abcd-ef0123456789"
    out = render_open_list_command(
        body,
        catalog="Справочник.Товары",  # same length as Склады
        main_frame_guid=new_guid,
        message_id=mid,
        sequence=42,
        nonce=bytes(16),
    )
    assert len(out) == len(body)
    assert out[2:18] == mid.bytes_le
    assert out[19:21] == (42).to_bytes(2, "little")
    # catalog re-targeted
    assert "Справочник.Товары".encode("utf-16le") in out
    assert "Справочник.Склады".encode("utf-16le") not in out
    # MainFrame guid re-targeted
    assert new_guid.encode("ascii") in out
    assert "6ca75e50-62a3-4842-b6cd-b429f7591ef2".encode("ascii") not in out


def test_render_open_list_rejects_catalog_length_mismatch() -> None:
    with pytest.raises(ValueError):
        render_open_list_command(
            _synthetic_open_list_body(),
            catalog="Справочник.Товар",  # 16 != 17
            main_frame_guid="6ca75e50-62a3-4842-b6cd-b429f7591ef2",
        )


def test_render_open_list_reproduces_real_captured_frame_if_present() -> None:
    cap = (
        Path(__file__).resolve().parents[1]
        / "runtime" / "protocol-research" / "captures"
        / "mut-warehouse-donotuse-20260610" / "traffic.jsonl"
    )
    if not cap.exists():
        return  # raw capture lives under ignored runtime/; skip when absent
    import base64

    man = [
        base64.b64decode(c["payload_b64"])
        for c in (json.loads(l) for l in cap.read_text(encoding="utf-8").splitlines() if l.strip())
        if c.get("event") == "chunk" and c["direction"] == "manager_to_client" and c.get("payload_b64")
    ]
    body = man[8]
    out = render_open_list_command(
        body,
        catalog="Справочник.Склады",
        main_frame_guid="6ca75e50-62a3-4842-b6cd-b429f7591ef2",
        message_id=uuid.UUID(bytes_le=body[2:18]),
        sequence=int.from_bytes(body[19:21], "little"),
        nonce=body[68:84],
    )
    assert out == body  # identity reproduces the captured open-list command


def test_render_form_command_identity_keeps_captured_bytes() -> None:
    body = bytearray(420)
    body[350 : 350 + 14] = "Средний".encode("utf-16le")
    body[2:18] = uuid.UUID("11111111-2222-3333-4444-555555555555").bytes_le
    captured = bytes(body)
    # no overrides, value unchanged -> identical
    out = render_select_row_command(captured, old_value="Средний", new_value="Средний")
    assert out == captured


def test_render_select_row_retargets_value_same_length() -> None:
    body = bytearray(420)
    body[349] = 7  # 1-byte char-count prefix
    body[350 : 350 + 14] = "Средний".encode("utf-16le")
    out = render_select_row_command(bytes(body), old_value="Средний", new_value="Большой")
    assert "Большой".encode("utf-16le") in out
    assert "Средний".encode("utf-16le") not in out
    assert len(out) == 420


def test_render_select_row_arbitrary_length_updates_count_prefix() -> None:
    body = bytearray(420)
    body[349] = 7
    body[350 : 350 + 14] = "Средний".encode("utf-16le")
    out = render_select_row_command(bytes(body), old_value="Средний", new_value="Малый")
    assert "Малый".encode("utf-16le") in out
    assert "Средний".encode("utf-16le") not in out
    # 5 chars vs 7 -> 4 fewer bytes; count prefix updated to 5
    assert len(out) == 420 - 4
    assert bytes([5]) + "Малый".encode("utf-16le") in out


def test_render_form_command_rebinds_guid_all_encodings() -> None:
    g_old = "5616f78b-8eba-46ff-bfb1-02e815b6122f"
    g_new = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    body = ("SecondaryFrame[%s]" % g_old).encode("utf-16le")
    out = render_form_command(body, guid_map={g_old: g_new})
    assert g_new.encode("utf-16le") in out
    assert g_old.encode("utf-16le") not in out


def test_render_form_command_overrides_header_fields() -> None:
    body = bytearray(100)
    mid = uuid.UUID("99999999-8888-7777-6666-555555555555")
    out = render_form_command(bytes(body), message_id=mid, sequence=7)
    o, ln = COMMAND_MESSAGE_ID
    assert out[o : o + ln] == mid.bytes_le
    o, ln = COMMAND_SEQUENCE
    assert out[o : o + ln] == (7).to_bytes(2, "little")


def test_render_select_row_raises_when_value_absent() -> None:
    with pytest.raises(ValueError):
        render_select_row_command(bytes(420), old_value="Средний", new_value="Малый")


def test_substitute_length_prefixed_string_shorter_and_longer() -> None:
    frame = b"head" + bytes([7]) + "Средний".encode("utf-16le") + b"tail"
    shorter, n = substitute_length_prefixed_string(frame, "Средний", "Малый")
    assert n == 1
    assert shorter == b"head" + bytes([5]) + "Малый".encode("utf-16le") + b"tail"
    longer, _ = substitute_length_prefixed_string(frame, "Средний", "Строящийся")
    assert longer == b"head" + bytes([10]) + "Строящийся".encode("utf-16le") + b"tail"


def test_substitute_length_prefixed_string_missing_raises() -> None:
    with pytest.raises(ValueError):
        substitute_length_prefixed_string(b"no value here", "Средний", "Малый")


def test_render_open_card_identity() -> None:
    body = bytearray(420)
    body[372 : 372 + 16] = "Изменить".encode("utf-16le")
    captured = bytes(body)
    assert render_open_card_command(captured) == captured


def test_e1cib_ref_hex_proven_control() -> None:
    # Decoded from the genuine open-card capture: «Покупатели» Ref_Key → the captured ?ref= token (card 99).
    from qa_mcp.protocol.navigation import e1cib_ref_hex

    assert e1cib_ref_hex("9d5c422d-8c4c-11db-a9b0-00055d49b45e") == "a9b000055d49b45e11db8c4c9d5c422d"
    # group reorder g4·g5·g3·g2·g1
    assert e1cib_ref_hex("a7a30aaf-321b-11dd-8d3a-000d8843cd1b") == "8d3a000d8843cd1b11dd321ba7a30aaf"


def test_e1cib_ref_hex_idempotent_and_validates() -> None:
    from qa_mcp.protocol.navigation import e1cib_ref_hex

    token = "a9b000055d49b45e11db8c4c9d5c422d"
    assert e1cib_ref_hex(token) == token            # already-encoded 32-hex is returned unchanged
    assert e1cib_ref_hex(token.upper()) == token    # case-normalized
    with pytest.raises(ValueError):
        e1cib_ref_hex("not-a-uuid")


def test_e1cib_data_link_builds_record_form_link() -> None:
    from qa_mcp.protocol.navigation import e1cib_data_link

    assert (
        e1cib_data_link("Справочник.Контрагенты", "9d5c422d-8c4c-11db-a9b0-00055d49b45e")
        == "e1cib/data/Справочник.Контрагенты?ref=a9b000055d49b45e11db8c4c9d5c422d"
    )

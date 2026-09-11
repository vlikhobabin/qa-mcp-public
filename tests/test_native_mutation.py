from __future__ import annotations

import uuid

import pytest

from qa_mcp.protocol.native_mutation import (
    GuidRebinder,
    ascii_guids_in_order,
    build_poll_skip_set,
    manager_originated_guids,
    poll_frame_ordinals,
    retarget_row_value,
    substitute_guid_all_encodings,
)


def test_ascii_guids_in_order_dedup() -> None:
    g1 = "11111111-1111-1111-1111-111111111111"
    g2 = "22222222-2222-2222-2222-222222222222"
    payload = f"SecondaryFrame[{g1}].ManagedForm[{g2}] {g1}".encode("ascii")
    assert ascii_guids_in_order(payload) == [g1, g2]


def test_substitute_all_encodings() -> None:
    cap = "aaaaaaaa-0000-0000-0000-000000000001"
    live = "bbbbbbbb-0000-0000-0000-000000000002"
    payload = (
        cap.encode("ascii")
        + b"|"
        + cap.encode("utf-16le")
        + b"|"
        + uuid.UUID(cap).bytes_le
    )
    out = substitute_guid_all_encodings(payload, cap, live)
    assert cap.encode("ascii") not in out
    assert cap.encode("utf-16le") not in out
    assert uuid.UUID(cap).bytes_le not in out
    assert live.encode("ascii") in out
    assert live.encode("utf-16le") in out
    assert uuid.UUID(live).bytes_le in out


def test_rebinder_learns_by_first_appearance_order() -> None:
    cap_a = "aaaaaaaa-0000-0000-0000-00000000000a"
    cap_b = "aaaaaaaa-0000-0000-0000-00000000000b"
    live_a = "cccccccc-0000-0000-0000-00000000000a"
    live_b = "cccccccc-0000-0000-0000-00000000000b"
    # captured client responses define the order: A then B
    client_chunks = [
        {"payload": f"resp[{cap_a}]".encode("ascii")},
        {"payload": f"resp[{cap_b}]".encode("ascii")},
    ]
    rebinder = GuidRebinder.from_client_chunks(client_chunks)
    assert rebinder.captured_order == [cap_a, cap_b]

    # live responses arrive in the same order -> positional mapping
    rebinder.observe_response(f"live[{live_a}]".encode("ascii"))
    rebinder.observe_response(f"live[{live_b}]".encode("ascii"))
    assert rebinder.guid_map == {cap_a: live_a, cap_b: live_b}

    # a subsequent command referencing the captured guids gets rebound
    cmd = f"cmd SecondaryFrame[{cap_a}] ManagedForm[{cap_b}]".encode("ascii")
    out = rebinder.apply(cmd)
    assert live_a.encode("ascii") in out
    assert live_b.encode("ascii") in out
    assert cap_a.encode("ascii") not in out


def test_rebinder_unlearned_guid_passes_through() -> None:
    rebinder = GuidRebinder(captured_order=[])
    payload = b"no mapping yet 33333333-3333-3333-3333-333333333333"
    assert rebinder.apply(payload) == payload


def test_retarget_row_value_substitutes_utf16le() -> None:
    # navigation frame carries the row value as UTF-16LE; an unrelated frame does not
    nav = b"Table[..]\x00column" + "Средний".encode("utf-16le") + b"\x00pad"
    other = b"unrelated frame without the row value"
    chunks = [{"payload": nav}, {"payload": other}]
    out, n = retarget_row_value(chunks, "Средний", "Большой")
    assert n == 1
    assert "Большой".encode("utf-16le") in out[0]["payload"]
    assert "Средний".encode("utf-16le") not in out[0]["payload"]
    assert out[1]["payload"] == other
    # length preserved (in-place substitution)
    assert len(out[0]["payload"]) == len(nav)


def test_retarget_row_value_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError):
        retarget_row_value([{"payload": b""}], "Средний", "Малый")


def test_poll_frame_ordinals_finds_dominant_repeated_form() -> None:
    # the poll form repeats with varying message id (offset 2) but same structure
    def poll(n: int) -> dict:
        body = bytearray(80)
        body[2:18] = n.to_bytes(16, "little")  # varying message id
        body[40:50] = b"POLLSTATE."
        return {"payload": bytes(body)}

    def command(tag: bytes) -> dict:
        return {"payload": tag + bytes(60)}

    chunks = [command(b"OPENLIST"), poll(1), poll(2), poll(3), command(b"SELECTROW"), poll(4)]
    polls = poll_frame_ordinals(chunks)
    assert polls == [1, 2, 3, 5]  # the 4 poll frames, not the commands


def test_manager_originated_guids_excludes_client_and_null() -> None:
    man_only = "aaaaaaaa-0000-0000-0000-000000000001"
    shared = "bbbbbbbb-0000-0000-0000-000000000002"
    null = "00000000-0000-0000-0000-000000000000"
    manager_chunks = [
        {"payload": f"{man_only} {shared} {null}".encode("ascii")},
    ]
    client_chunks = [{"payload": shared.encode("ascii")}]
    assert manager_originated_guids(manager_chunks, client_chunks) == [man_only]


def test_build_poll_skip_set_thins_polls_keeps_commands() -> None:
    def poll(n: int) -> dict:
        body = bytearray(80)
        body[2:18] = n.to_bytes(16, "little")
        body[40:50] = b"POLLSTATE."
        return {"payload": bytes(body)}

    chunks = [{"payload": b"CMD" + bytes(60)}] + [poll(n) for n in range(8)]
    skip = build_poll_skip_set(chunks, keep_every=4)
    assert 0 not in skip  # command never skipped
    # of 8 polls (ordinals 1..8), keep every 4th -> skip 6
    assert len(skip) == 6

"""Offline tests for qa_mcp.protocol.native_write (card 80 Fork-2 variable-length value retarget)."""
import base64
import json
import socket
import tempfile
from pathlib import Path

from qa_mcp.protocol.native_write import (
    ReadListColumnTemplate,
    build_write_frame,
    derive_write_template,
    encode_1c_length,
    read_list_grid_replay,
    read_field_value_near,
    read_table_cell_value,
    retarget_value,
)
from qa_mcp.protocol.frames import MANAGER_TO_CLIENT, TAIL_MARKER

_S = "782a8ba8-d60a-4fec-809a-4e2339cf9e31"
_F = "bf814b58-5d69-4ccf-b58d-9a4e23a01f05"


def _grid_read_frame(seq: int = 1) -> bytes:
    frame = bytearray(b"R" * 30 + b"\x88\x81\x81\xe0\x4b\x55\xeb\x53")
    frame[19:21] = seq.to_bytes(2, "little")
    return bytes(frame)


def _grid_value(value: str) -> bytes:
    raw = value.encode("latin1")
    return b"\x81\x81\x81\xe0\x4b\x53\x9a" + bytes([len(raw)]) + raw + TAIL_MARKER


class _GridSocket:
    def __init__(self, responses: list[bytes]) -> None:
        self.responses = list(responses)
        self.sent: list[bytes] = []
        self.timeouts: list[float] = []

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return None

    def setsockopt(self, *_args):
        return None

    def settimeout(self, timeout: float) -> None:
        self.timeouts.append(timeout)

    def sendall(self, payload: bytes) -> None:
        self.sent.append(payload)

    def recv(self, _size: int) -> bytes:
        if not self.responses:
            return b""
        return self.responses.pop(0)


def _run_grid(monkeypatch, responses: list[bytes], max_rows: int = 5) -> dict:
    import qa_mcp.protocol.native_write as nw

    manager = [b"H" * 30, _grid_read_frame(1), b"N" * 30, _grid_read_frame(2)]

    def fake_chunks(_capture_dir, direction):
        return manager if direction == MANAGER_TO_CLIENT else []

    monkeypatch.setattr(nw, "_read_chunks", fake_chunks)
    monkeypatch.setattr(nw.socket, "create_connection", lambda *_args, **_kwargs: _GridSocket(responses))
    template = ReadListColumnTemplate(Path("."), "e1cib/list/Справочник.Товары", "Name", "A")
    return read_list_grid_replay(template, columns=["Name"], max_rows=max_rows)


def _set_frame(field: str, value: str) -> bytes:
    """A synthetic SET frame: 21-byte header (offset-19 counter) + length-prefixed element path +
    fixed-width value block."""
    path = f"SecondaryFrame[{_S}].ManagedForm[{_F}].Group[PF_GROUP_EDITS].EditField[{field}]".encode("latin1")
    path_block = b"\x9a" + bytes([len(path)]) + path
    value_block = b"\x81\xba" + encode_1c_length(len(value.encode())) + value.encode() + b"\x20\x20\xa1"
    return b"H" * 21 + path_block + value_block + b"TAIL"


def test_encode_1c_length_leb128():
    assert encode_1c_length(0) == b"\x00"
    assert encode_1c_length(13) == b"\x0d"
    assert encode_1c_length(127) == b"\x7f"
    assert encode_1c_length(128) == b"\x80\x01"
    assert encode_1c_length(200) == b"\xc8\x01"
    assert encode_1c_length(16383) == b"\xff\x7f"


def test_read_list_grid_keeps_adjacent_duplicate_rows(monkeypatch):
    result = _run_grid(
        monkeypatch,
        [
            b"hello" + TAIL_MARKER,  # initial response after connect
            b"setup" + TAIL_MARKER,
            b"first-read-setup" + TAIL_MARKER,
            _grid_value("A"),
            b"next" + TAIL_MARKER,
            _grid_value("A"),
            b"next" + TAIL_MARKER,
            _grid_value("B"),
            b"next" + TAIL_MARKER,
            b"empty" + TAIL_MARKER,
        ],
    )

    assert result["rows"] == [{"Name": "A"}, {"Name": "A"}, {"Name": "B"}]
    assert result["row_count"] == 3
    assert result["truncated"] is False
    assert result["stop_reason"] == "empty_row"


def test_read_list_grid_empty_socket_response_is_truncated(monkeypatch):
    result = _run_grid(
        monkeypatch,
        [
            b"hello" + TAIL_MARKER,
            b"setup" + TAIL_MARKER,
            b"first-read-setup" + TAIL_MARKER,
            _grid_value("A"),
            b"next" + TAIL_MARKER,
            b"",
        ],
    )

    assert result["rows"] == [{"Name": "A"}]
    assert result["truncated"] is True
    assert result["stop_reason"] == "row_read_timeout"


def _frame_with(value: str) -> bytes:
    # mimic the SET-frame value field: <header><tag \x81\xba><varint len><value><trailer>
    body = b"\x81\xba" + encode_1c_length(len(value.encode())) + value.encode() + b"\x20\x20\xa1"
    return b"HEADER0123456789" + body + b"TAIL"


def test_retarget_same_length_preserves_size():
    frame = _frame_with("QAGENUINE2026")  # 13
    out = retarget_value(frame, "QAGENUINE2026", "ZZZRETARGET99")  # 13
    assert len(out) == len(frame)
    assert b"QAGENUINE2026" not in out
    i = out.find(b"ZZZRETARGET99")
    assert i > 0 and out[i - 1] == 13


def test_retarget_shorter_pads_fixed_width():
    # fixed-width field: shorter value keeps the FRAME size constant (padded with spaces), prefix fixed.
    frame = _frame_with("QAGENUINE2026")
    out = retarget_value(frame, "QAGENUINE2026", "AB")
    assert len(out) == len(frame)
    assert b"QAGENUINE2026" not in out
    i = out.find(b"AB")
    assert out[i - 1] == 2  # length prefix fixed to 2
    assert out[i + 2: i + 4] == b"\x20\x20"  # padded


def test_retarget_too_long_for_buffer_raises():
    # _frame_with has value(13)+2 spaces -> buffer width 15; 28 chars must not fit.
    frame = _frame_with("QAGENUINE2026")
    try:
        retarget_value(frame, "QAGENUINE2026", "RETARGETED_VALUE_LONGER_2026")
        assert False, "expected ValueError for over-long value"
    except ValueError:
        pass


def test_retarget_within_buffer_keeps_size():
    frame = _frame_with("QAGENUINE2026")  # buffer width 15
    out = retarget_value(frame, "QAGENUINE2026", "FIFTEEN_CHARSx")  # 14, fits
    assert len(out) == len(frame)
    i = out.find(b"FIFTEEN_CHARSx")
    assert out[i - 1] == 14


def test_retarget_absent_value_is_noop():
    frame = _frame_with("QAGENUINE2026")
    assert retarget_value(frame, "NOT_PRESENT", "X") == frame


def test_retarget_utf16_form():
    val = "QAGENUINE2026"
    seq = encode_1c_length(len(val.encode("utf-16-le"))) + val.encode("utf-16-le")
    frame = b"HDR" + seq + b"TAIL"
    out = retarget_value(frame, val, "NEW")
    assert val.encode("utf-16-le") not in out
    assert "NEW".encode("utf-16-le") in out


def _write_capture(mgr_frames: list[bytes]) -> Path:
    d = Path(tempfile.mkdtemp())
    with (d / "traffic.jsonl").open("w", encoding="utf-8") as fh:
        for n, p in enumerate(mgr_frames):
            rec = {"event": "chunk", "direction": "manager_to_client", "chunk_no": n,
                   "byte_count": len(p), "payload_b64": base64.b64encode(p).decode()}
            fh.write(json.dumps(rec) + "\n")
        # one client frame so GuidRebinder / readers have a cli stream
        fh.write(json.dumps({"event": "chunk", "direction": "client_to_manager", "chunk_no": 0,
                             "byte_count": 4, "payload_b64": base64.b64encode(b"clnt").decode()}) + "\n")
    return d


def test_derive_write_template_locates_block():
    val = "HELLO"
    val_seq = encode_1c_length(len(val.encode())) + val.encode()
    frames = [
        b"setup_handshake_0_padding",          # 0 setup
        b"setup_open_form_1_padding",           # 1 setup
        b"setup_2_padding_xxxxxxxxxx",          # 2 setup
        b"hdr EditField[MYFIELD] activate a",   # 3 activate field
        b"hdr EditField[MYFIELD] activate b",   # 4 activate field
        b"hdr EditField[MYFIELD] " + val_seq,   # 5 SET (carries the value)
        b"hdr EditField[OTHER] focuschange x",  # 6 focus-change (different field)
        b"hdr EditField[MYFIELD] readback xx",  # 7 read-back
    ]
    t = derive_write_template(_write_capture(frames), "MYFIELD", val, "DEFAULT")
    assert t.setup_end == 2
    assert t.write_block == (3, 6)
    assert t.read_frames == [7]
    assert t.field == "MYFIELD"


def test_read_field_value_near():
    blob = b"...EditField[PF_EDIT_STRING]\x81\x81\x81\xfa\rZZZRETARGET99 \xa1\xa3rest"
    assert read_field_value_near(blob, "PF_EDIT_STRING") == "ZZZRETARGET99"
    # \xe0-tail variant
    blob2 = b"x EditField[PF_EDIT_STRING]\x81\x81\x81\xe0KS\x9a\x02AB  \xa1"
    assert read_field_value_near(blob2, "PF_EDIT_STRING") == "AB"
    assert read_field_value_near(b"no field here", "PF_EDIT_STRING") is None


def test_read_field_value_near_decodes_cyrillic_value():
    value = "Привет"
    encoded = value.encode("utf-8")
    blob = (
        b"...EditField[PF_EDIT_STRING]\x81\x81\x81\xfa"
        + encode_1c_length(len(encoded))
        + encoded
        + b" \xa1rest"
    )
    assert read_field_value_near(blob, "PF_EDIT_STRING") == value


def test_read_field_value_near_decodes_utf16le_cyrillic_value():
    value = "Привет"
    encoded = value.encode("utf-16-le")
    blob = (
        b"...EditField[PF_EDIT_STRING]\x81\x81\x81\xfa"
        + encode_1c_length(len(value))
        + encoded
        + b" \xa1rest"
    )
    assert read_field_value_near(blob, "PF_EDIT_STRING") == value


def test_read_field_value_near_decodes_one_character_value():
    blob = b"...EditField[PF_EDIT_STRING]\x81\x81\x81\xfa" + encode_1c_length(1) + b"5 \xa1rest"
    assert read_field_value_near(blob, "PF_EDIT_STRING") == "5"


def test_read_field_value_near_decodes_long_value():
    value = "LONG-VALUE-" * 5
    encoded = value.encode("utf-8")
    blob = (
        b"...EditField[PF_EDIT_STRING]\x81\x81\x81\xfa"
        + encode_1c_length(len(encoded))
        + encoded
        + b" \xa1rest"
    )
    assert len(encoded) > 40
    assert read_field_value_near(blob, "PF_EDIT_STRING") == value


def test_read_field_value_near_decodes_value_beyond_legacy_window():
    value = "X" * 180
    encoded = value.encode("utf-8")
    blob = (
        b"...EditField[PF_EDIT_STRING]\x81\x81\x81\xfa"
        + encode_1c_length(len(encoded))
        + encoded
        + b" \xa1"
    )
    assert read_field_value_near(blob, "PF_EDIT_STRING") == value


def test_write_value_matches_readback_rejects_plain_prefix():
    from qa_mcp.protocol.native_write import _write_value_matches_readback

    assert _write_value_matches_readback("123", "123456") is False
    assert _write_value_matches_readback("123", "123") is True
    assert _write_value_matches_readback("30.06.2026", "30.06.2026 0:00:00") is True


def test_build_write_frame_same_field_retargets_value_and_seq():
    # target == base: no path retarget; value retargeted; offset-19 counter set
    frame = _set_frame("PF_EDIT_STRING", "QAGENUINE2026")
    out = build_write_frame(frame, "QAGENUINE2026", "NEWVAL", base_field="PF_EDIT_STRING",
                            target_field="PF_EDIT_STRING", seq=5)
    assert b"EditField[PF_EDIT_STRING]" in out
    assert b"NEWVAL" in out and b"QAGENUINE2026" not in out
    assert out[19:21] == (5).to_bytes(2, "little")


def test_build_write_frame_retargets_element_path_to_other_field():
    # card 86b: target != base -> the element-address path leaf is re-targeted, value retargeted, seq set
    frame = _set_frame("PF_EDIT_STRING", "QAGENUINE2026")
    out = build_write_frame(frame, "QAGENUINE2026", "777,99", base_field="PF_EDIT_STRING",
                            target_field="PF_EDIT_NUMBER", seq=9)
    assert b"EditField[PF_EDIT_NUMBER]" in out
    assert b"EditField[PF_EDIT_STRING]" not in out
    assert b"777,99" in out
    assert out[19:21] == (9).to_bytes(2, "little")
    # the path's own 1-byte length prefix stays consistent (same-length leaf names here -> same size)
    assert len(out) == len(frame)


def test_build_write_frame_reencodes_ascii_path_to_cyrillic_field():
    from qa_mcp.protocol.element_ref import extract_element_paths_utf16, parse_element_path

    frame = _set_frame("PF_EDIT_STRING", "QAGENUINE2026")
    out = build_write_frame(
        frame,
        "QAGENUINE2026",
        "777,99",
        base_field="PF_EDIT_STRING",
        target_field="Контрагент",
        seq=9,
        allow_missing_leaf=False,
    )

    assert b"EditField[PF_EDIT_STRING]" not in out
    paths = extract_element_paths_utf16(out)
    assert paths
    assert any(parse_element_path(path).name == "Контрагент" for path in paths)
    assert b"777,99" in out
    assert out[19:21] == (9).to_bytes(2, "little")


def test_build_write_frame_missing_expected_leaf_raises():
    from qa_mcp.protocol.native_write import WriteRetargetError

    raw_leaf_only = b"H" * 21 + "EditField[PF_EDIT_STRING]".encode("utf-16-le") + b"\rQAGENUINE2026"
    try:
        build_write_frame(
            raw_leaf_only,
            "QAGENUINE2026",
            "777,99",
            base_field="PF_EDIT_STRING",
            target_field="Контрагент",
            seq=9,
            allow_missing_leaf=False,
        )
        assert False, "expected fail-closed retarget error"
    except WriteRetargetError as exc:
        assert exc.base_field == "PF_EDIT_STRING"
        assert exc.target_field == "Контрагент"


def test_build_write_frame_noop_path_when_base_leaf_absent():
    # the focus-change frame addresses a DIFFERENT field -> path retarget is a no-op (must not raise)
    frame = _set_frame("PF_OTHER_FIELD", "QAGENUINE2026")
    out = build_write_frame(frame, "QAGENUINE2026", "X", base_field="PF_EDIT_STRING",
                            target_field="PF_EDIT_NUMBER", seq=1)
    assert b"EditField[PF_OTHER_FIELD]" in out  # untouched
    assert b"EditField[PF_EDIT_NUMBER]" not in out
    assert b"X" in out  # value still retargeted where the captured value appears


def test_native_write_session_retarget_failed_does_not_send_frame():
    from qa_mcp.protocol.native_write import NativeWriteSession, WriteTemplate

    class Rebind:
        def apply(self, payload):
            return payload

    class Sock:
        def __init__(self):
            self.sent = []

        def sendall(self, payload):
            self.sent.append(payload)

    sock = Sock()
    session = object.__new__(NativeWriteSession)
    session.t = WriteTemplate(
        capture_dir=Path("."),
        field="PF_EDIT_STRING",
        captured_value="QAGENUINE2026",
        read_frames=[],
        stop_after=0,
        setup_end=-1,
        write_block=(0, 0),
    )
    session._mgr = [b"H" * 21 + "EditField[PF_EDIT_STRING]".encode("utf-16-le") + b"\rQAGENUINE2026"]
    session._sock = sock
    session._rebinder = Rebind()
    session._seq = 1

    result = session.write("777,99", field="Контрагент")

    assert result["error"] == "retarget_failed"
    assert result["field"] == "Контрагент"
    assert sock.sent == []


def test_native_write_session_enter_closes_socket_on_setup_failure(monkeypatch):
    from qa_mcp.protocol.native_write import NativeWriteSession, WriteTemplate

    class FailingSetupSocket:
        def __init__(self):
            self.closed = False
            self.timeouts = []
            self.recv_calls = 0

        def setsockopt(self, *_args):
            return None

        def settimeout(self, timeout):
            self.timeouts.append(timeout)

        def recv(self, _size):
            self.recv_calls += 1
            return b"hello" + TAIL_MARKER if self.recv_calls == 1 else b""

        def sendall(self, _payload):
            raise RuntimeError("setup exploded")

        def close(self):
            self.closed = True

    import qa_mcp.protocol.native_write as nw

    sock = FailingSetupSocket()
    monkeypatch.setattr(nw.socket, "create_connection", lambda *_args, **_kwargs: sock)
    template = WriteTemplate(
        capture_dir=_write_capture([b"H" * 21]),
        field="PF_EDIT_STRING",
        captured_value="OLD",
        read_frames=[],
        stop_after=0,
        setup_end=0,
        write_block=(0, 0),
    )
    session = NativeWriteSession(template)

    try:
        session.__enter__()
        assert False, "expected original setup exception"
    except RuntimeError as exc:
        assert str(exc) == "setup exploded"

    assert sock.closed is True
    assert session._sock is None
    assert session._rebinder is None


def test_write_form_value_reports_send_timeout_not_divergence(monkeypatch):
    from qa_mcp.protocol.native_write import SEND_TIMEOUT_REASON, WriteTemplate, write_form_value

    class SlowSendSocket:
        def __init__(self):
            self.timeouts = []
            self.recv_calls = 0

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return None

        def setsockopt(self, *_args):
            return None

        def settimeout(self, timeout):
            self.timeouts.append(timeout)

        def recv(self, _size):
            self.recv_calls += 1
            return b"hello" + TAIL_MARKER if self.recv_calls == 1 else b""

        def sendall(self, _payload):
            raise socket.timeout("slow send")

    import qa_mcp.protocol.native_write as nw

    sock = SlowSendSocket()
    monkeypatch.setattr(nw.socket, "create_connection", lambda *_args, **_kwargs: sock)
    template = WriteTemplate(
        capture_dir=_write_capture([b"H" * 21 + b"OLD"]),
        field="PF_EDIT_STRING",
        captured_value="OLD",
        read_frames=[],
        stop_after=0,
    )

    result = write_form_value(template, "NEW")

    assert result["failure_reason"] == SEND_TIMEOUT_REASON
    assert result["send_timeout_at"] == 0
    assert result["real_divergence_at"] is None
    assert result["committed"] is False
    assert 10.0 in sock.timeouts


def test_legacy_write_form_value_committed_uses_decoded_readback_not_blob_prefix(monkeypatch):
    from qa_mcp.protocol.native_write import WriteTemplate, write_form_value
    import qa_mcp.protocol.native_write as nw

    class PrefixReadbackSocket:
        def __init__(self):
            self.responses = [
                b"hello" + TAIL_MARKER,
                b"...EditField[PF_EDIT_STRING]\x81\x81\x81\xfa\x06123456 \xa1" + TAIL_MARKER,
            ]
            self.timeouts = []

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return None

        def setsockopt(self, *_args):
            return None

        def settimeout(self, timeout):
            self.timeouts.append(timeout)

        def recv(self, _size):
            if not self.responses:
                return b""
            return self.responses.pop(0)

        def sendall(self, _payload):
            return None

    sock = PrefixReadbackSocket()
    monkeypatch.setattr(nw.socket, "create_connection", lambda *_args, **_kwargs: sock)
    template = WriteTemplate(
        capture_dir=_write_capture([b"H" * 21 + b"OLD"]),
        field="PF_EDIT_STRING",
        captured_value="OLD",
        read_frames=[0],
        stop_after=0,
    )

    result = write_form_value(template, "123")

    assert result["readback_value"] == "123456"
    assert result["new_in_readback"] is True
    assert result["committed"] is False


def test_derive_write_template_commit_partner_synthesizes_focus_change():
    # card 86c: a field whose genuine input has NO trailing focus-change (last input) -> commit_partner
    # supplies the focus-change (partner's activate). write_block = activate+SET only; commit_block = partner.
    nv = "777,77"; sv = "QAGENUINE2026"
    nseq = encode_1c_length(len(nv.encode())) + nv.encode()
    sseq = encode_1c_length(len(sv.encode())) + sv.encode()
    frames = [
        b"setup_0_xxxxxxxxxxxx",                  # 0 setup
        b"setup_1_xxxxxxxxxxxx",                  # 1 setup
        b"hdr EditField[PF_NUM] readsweep",       # 2 PF_NUM value-read (before input)
        b"hdr EditField[PF_STR] activate a",      # 3 partner activate
        b"hdr EditField[PF_STR] " + sseq,         # 4 partner SET
        b"hdr EditField[PF_NUM] activate a",      # 5 target activate
        b"hdr EditField[PF_NUM] " + nseq,         # 6 target SET (LAST, no focus-change)
        b"control_tail_nofields",                 # 7 tail
    ]
    t = derive_write_template(_write_capture(frames), "PF_NUM", nv, "DEF",
                              commit_partner_field="PF_STR", commit_partner_value=sv)
    assert t.field == "PF_NUM"
    assert t.write_block == (5, 6)        # activate + SET only
    assert t.commit_block == (3, 3)       # partner ACTIVATE (frame before its SET) = synthesized focus-change
    assert t.read_frames == [2]           # field's value-read from the sweep
    assert t.setup_end == 2               # before the earliest input (partner activate @3)


def test_derive_page_switch_locates_switch_block():
    from qa_mcp.protocol.native_write import derive_page_switch
    p = "SecondaryFrame[s].ManagedForm[f].Group[PF_GROUP_MAIN].Group[PF_PAGES_MAIN].Group[PF_PAGE_B]"
    frames = [
        b"setup_0_padding_xxxxxxxx",                 # 0 setup
        b"setup_1_padding_xxxxxxxx",                 # 1 setup
        b"HDR" + p.encode("latin1") + b" act1",      # 2 switch -> PF_PAGE_B
        b"HDR" + p.encode("latin1") + b" act2",      # 3 switch -> PF_PAGE_B (contiguous)
        b"control_tail_nofields",                    # 4 tail
    ]
    t = derive_page_switch(_write_capture(frames), "PF_PAGE_B")
    assert t.base_page == "PF_PAGE_B"
    assert t.switch_block == (2, 3)
    assert t.setup_end == 1


def test_derive_checkbox_toggle_locates_block():
    """Card 90: a checkbox toggle block = the contiguous EditField[base_field] run (value-free; the
    e0-4b-55 toggle frame carries no value buffer). Mirror of the page-switch locator, kind=EditField."""
    from qa_mcp.protocol.native_write import derive_checkbox_toggle
    p = ("SecondaryFrame[s].ManagedForm[f].Group[PF_GROUP_MAIN]."
         "Group[PF_GROUP_CHECKBOXES].EditField[PF_CHECKBOX_FALSE]")
    frames = [
        b"setup_0_padding_xxxxxxxx",                       # 0 setup (form open)
        b"setup_1_padding_xxxxxxxx",                       # 1 setup
        b"HDR" + p.encode("latin1") + b" focus",          # 2 toggle block: focus
        b"HDR" + p.encode("latin1") + b" \xe0\x4b\x55",   # 3 the value-free toggle frame (contiguous)
        b"HDR" + p.encode("latin1") + b" read",           # 4 read-back (contiguous)
        b"control_tail_nofields",                         # 5 tail
    ]
    t = derive_checkbox_toggle(_write_capture(frames), "PF_CHECKBOX_FALSE")
    assert t.base_field == "PF_CHECKBOX_FALSE"
    assert t.toggle_block == (2, 4)
    assert t.setup_end == 1


def test_checkbox_toggle_retargets_editfield_leaf_keeps_toggle_marker():
    """Card 90: a checkbox toggle for ANY field = the genuine toggle frame with its EditField leaf
    re-targeted (capture-free). The value-free e0-4b-55 marker must survive the retarget."""
    from qa_mcp.protocol.element_ref import retarget_element_leaf
    path = ("SecondaryFrame[s].ManagedForm[f].Group[PF_GROUP_MAIN]."
            "Group[PF_GROUP_CHECKBOXES].EditField[PF_CHECKBOX_FALSE]").encode("latin1")
    frame = b"\x9a" + bytes([len(path)]) + path + b"\xe0\x4b\x55"
    out, n = retarget_element_leaf(frame, "PF_CHECKBOX_FALSE", "PF_CHECKBOX_TRUE", kind="EditField")
    assert n == 1
    assert b"EditField[PF_CHECKBOX_TRUE]" in out
    assert b"EditField[PF_CHECKBOX_FALSE]" not in out
    assert b"\xe0\x4b\x55" in out  # the value-free toggle marker is preserved


def test_derive_choice_set_locates_block_and_variant():
    """Card 90: a radio choice-set block = the first contiguous EditField[base] run, which must carry the
    length-prefixed variant value-name (e0 4b 53 <0x9a><len><variant>)."""
    from qa_mcp.protocol.native_write import derive_choice_set, encode_1c_length
    p = ("SecondaryFrame[s].ManagedForm[f].Group[PF_GROUP_MAIN].EditField[PF_CHOICE_MODE]")
    var = encode_1c_length(len(b"PF_CHOICE_A")) + b"PF_CHOICE_A"
    frames = [
        b"setup_0_padding_xxxxxxxx",                                 # 0 setup
        b"setup_1_padding_xxxxxxxx",                                 # 1 setup
        b"HDR" + p.encode("latin1") + b" focus",                    # 2 activate
        b"HDR" + p.encode("latin1") + b"\xe0\x4b\x53\x9a" + var,    # 3 choose -> PF_CHOICE_A (contiguous)
        b"control_tail_nofields",                                    # 4 tail (breaks the run)
    ]
    t = derive_choice_set(_write_capture(frames), "PF_CHOICE_MODE", "PF_CHOICE_A")
    assert t.base_field == "PF_CHOICE_MODE"
    assert t.captured_variant == "PF_CHOICE_A"
    assert t.choice_block == (2, 3)
    assert t.setup_end == 1


def test_choice_set_retargets_variant_value_same_length():
    """Card 90: setting a different variant swaps the length-prefixed variant string (same length), keeping
    the choose tag — reuses build_write_frame (value retarget)."""
    from qa_mcp.protocol.native_write import build_write_frame, encode_1c_length
    p = ("SecondaryFrame[s].ManagedForm[f].Group[PF_GROUP_MAIN].EditField[PF_CHOICE_MODE]").encode("latin1")
    var = encode_1c_length(len(b"PF_CHOICE_A")) + b"PF_CHOICE_A"
    frame = b"H" * 21 + b"\x9a" + bytes([len(p)]) + p + b"\xe0\x4b\x53\x9a" + var + b"TAIL"
    out = build_write_frame(frame, "PF_CHOICE_A", "PF_CHOICE_C",
                            base_field="PF_CHOICE_MODE", target_field="PF_CHOICE_MODE", seq=7)
    assert (encode_1c_length(len(b"PF_CHOICE_C")) + b"PF_CHOICE_C") in out
    assert (encode_1c_length(len(b"PF_CHOICE_A")) + b"PF_CHOICE_A") not in out
    assert b"\xe0\x4b\x53" in out          # choose tag preserved
    assert len(out) == len(frame)          # same-length variant keeps frame size


def test_derive_choose_from_list_locates_click_through_pick():
    """Card 96 / E2: a choose-from-list block spans the command CLICK (Button[base_command], the LAST run)
    through the PICK frame (e0 4b 53 + the length-prefixed captured value, addressed at the ManagedForm — the
    popup reuses the form window, no element leaf)."""
    from qa_mcp.protocol.native_write import derive_choose_from_list, encode_1c_length
    btn = "SecondaryFrame[s].ManagedForm[f].Group[PF_COMMAND_BAR_MAIN].Button[PF_SHOW_CHOICE_LIST]".encode("latin1")
    form = "SecondaryFrame[s].ManagedForm[f]".encode("latin1")
    val = encode_1c_length(len(b"PF_CHOICE_B")) + b"PF_CHOICE_B"
    frames = [
        b"setup_0_xxxx",                                            # 0 setup
        b"HDR" + btn + b" render",                                  # 1 form-open render (earlier Button run)
        b"middle_no_button_xxxx",                                   # 2 gap
        b"HDR" + btn + b" \x88\x81\x81\xe1 click",                  # 3 CLICK (the last Button run)
        b"\x00\x00\x00\x04",                                        # 4 control / modal-open (<=16, kept in block)
        b"HDR" + form + b"\x88\x82\x81\xe0\x4b\x53\x9a" + val,      # 5 PICK -> PF_CHOICE_B
        b"post_pick_message_poll_read_xxxx",                        # 6 post-pick read (>16) -> elicits the msg
        b"\x21\x47\x54",                                            # 7 trailing 4-byte control -> stops the block
    ]
    t = derive_choose_from_list(_write_capture(frames), "PF_SHOW_CHOICE_LIST", "PF_CHOICE_B")
    assert t.base_command == "PF_SHOW_CHOICE_LIST"
    assert t.captured_value == "PF_CHOICE_B"
    # click run start -> the pick, EXTENDED through the post-pick substantive read (the message poll) that
    # elicits the Сообщить("PF_CHOICE=...") frame; stops at the trailing control frame.
    assert t.choose_block == (3, 6)
    assert t.setup_end == 2


def test_choose_from_list_retargets_picked_value_same_length():
    """Card 96 / E2: picking a different list item swaps the length-prefixed value (the PF_CHOICE_* items are
    same-length) and keeps the e0 4b 53 choose tag + the frame size — reuses retarget_value (no element leaf)."""
    from qa_mcp.protocol.native_write import retarget_value, encode_1c_length
    form = "SecondaryFrame[s].ManagedForm[f]".encode("latin1")
    val = encode_1c_length(len(b"PF_CHOICE_B")) + b"PF_CHOICE_B"
    frame = (b"H" * 21 + b"\x9a" + bytes([len(form)]) + form
             + b"\xe0\x4b\x53\x9a" + val + b"\x20\x20\x20\x20" + b"TAIL")
    out = retarget_value(frame, "PF_CHOICE_B", "PF_CHOICE_A")
    assert b"PF_CHOICE_A" in out and b"PF_CHOICE_B" not in out
    assert b"\xe0\x4b\x53" in out          # choose tag preserved
    assert len(out) == len(frame)          # same-length item keeps frame size


def test_choose_from_menu_reuses_choice_machinery_command_and_value_agnostic():
    """Card 96 / E2: ПоказатьВыборИзМеню is the wire twin of the choice list — `derive_choose_from_list` works
    unchanged with the menu command + value (the finder keys on `Button[base_command]` + `e0 4b 53` + the
    captured value, not on any list/menu-specific bytes). Only the result message prefix differs (PF_MENU=)."""
    from qa_mcp.protocol.native_write import derive_choose_from_list, encode_1c_length
    btn = "SecondaryFrame[s].ManagedForm[f].Group[PF_COMMAND_BAR_MAIN].Button[PF_SHOW_CHOICE_MENU]".encode("latin1")
    form = "SecondaryFrame[s].ManagedForm[f]".encode("latin1")
    val = encode_1c_length(len(b"PF_MENU_1")) + b"PF_MENU_1"
    frames = [
        b"setup_0_xxxx",                                            # 0 setup
        b"HDR" + btn + b" \x88\x81\x81\xe1 click",                  # 1 CLICK
        b"\x00\x00\x00\x04",                                        # 2 control / modal-open
        b"HDR" + form + b"\x88\x82\x81\xe0\x4b\x53\x9a" + val,      # 3 PICK -> PF_MENU_1
        b"post_pick_message_poll_read_xxxx",                        # 4 post-pick read -> elicits the msg
        b"\x21\x47\x54",                                            # 5 trailing control
    ]
    t = derive_choose_from_list(_write_capture(frames), "PF_SHOW_CHOICE_MENU", "PF_MENU_1")
    assert t.base_command == "PF_SHOW_CHOICE_MENU"
    assert t.captured_value == "PF_MENU_1"
    assert t.choose_block == (1, 4)   # click -> pick -> post-pick read
    assert t.setup_end == 0


def test_derive_answer_dialog_locates_dialog_window_and_close():
    """Card 96 / E1: a real dialog (ПоказатьВопрос/ПоказатьПредупреждение) opens a NEW SecondaryFrame (distinct
    from the form's most-referenced one); the answer is a WINDOW-LEVEL `88 82 81` command on that dialog SF (not
    a Button activate). derive_answer_dialog finds the dialog SF + the close frame."""
    from qa_mcp.protocol.native_write import derive_answer_dialog
    form = "aaaaaaaa-1111-2222-3333-444444444444"
    dlg = "bbbbbbbb-5555-6666-7777-888888888888"
    mgr = [
        f"HDR SecondaryFrame[{form}].ManagedForm[f] setup".encode("latin1"),                  # 0 form (most common)
        f"HDR SecondaryFrame[{form}].Group[X].Button[PF_V4_WARNING] click".encode("latin1"),  # 1 raise click
        f"HDR SecondaryFrame[{form}] read".encode("latin1"),                                  # 2 form again
        f"HDR SecondaryFrame[{dlg}] ".encode("latin1") + b"\x88\x82\x81 close",               # 3 window-level close on the dialog SF
    ]
    t = derive_answer_dialog(_write_capture(mgr), "PF_V4_WARNING", "PF_V4_WARNING_ACK")
    assert t.dialog_sf == dlg          # the NON-most-common SecondaryFrame = the dialog window
    assert t.close_frame == 3          # the `88 82 81` window-level command on the dialog SF
    assert t.raise_command == "PF_V4_WARNING" and t.result_marker == "PF_V4_WARNING_ACK"


def test_retarget_ref_value_fixed_width_utf16():
    """Card 96 / E2: a reference choice-by-string value (`<char-count><utf-16le name><space pad>`) retargets
    fixed-width — same length is a clean swap; a different length adjusts the trailing ASCII-space padding to
    keep the frame size constant; absent -> no-op."""
    from qa_mcp.protocol.native_write import encode_1c_length, retarget_ref_value
    val = encode_1c_length(2) + "АБ".encode("utf-16le")          # a 2-char ref name
    frame = b"\xe0\x41\x81\x81\xb7" + val + b"\x20\x20\x20" + b"TAIL"
    same = retarget_ref_value(frame, "АБ", "ВГ")                 # same length (2 chars)
    assert "ВГ".encode("utf-16le") in same and "АБ".encode("utf-16le") not in same
    assert len(same) == len(frame)
    shorter = retarget_ref_value(frame, "АБ", "Я")               # 1 char -> trailing padding grows
    assert "Я".encode("utf-16le") in shorter and len(shorter) == len(frame)
    assert retarget_ref_value(frame, "ЗЗ", "ВГ") == frame        # absent -> no-op


def test_derive_set_reference_field_validates_utf16_value():
    """Card 96 / E2: derive_set_reference_field requires the captured name to be present as a UTF-16
    choice-by-string value (`<char-count><utf-16le name>`)."""
    from qa_mcp.protocol.native_write import derive_set_reference_field, encode_1c_length
    name = "Корнет ЗАО"
    val = encode_1c_length(len(name)) + name.encode("utf-16le")
    mgr = [b"setup_frame", b"\xe0\x41\x81\x81\xb7" + val + b"\x20\x20", b"read_frame"]
    t = derive_set_reference_field(_write_capture(mgr), "Контрагент", name)
    assert t.field == "Контрагент" and t.captured_value == name
    failed = False
    try:
        derive_set_reference_field(_write_capture([b"no choice value here"]), "Контрагент", name)
    except ValueError:
        failed = True
    assert failed


def test_derive_open_card_validates_windows_and_marker():
    """Card 96 / E3: open-card requires multiple windows (form + list + card) and the card marker present as a
    UTF-16 string in a client frame; missing either -> ValueError."""
    from qa_mcp.protocol.native_write import derive_open_card
    f1 = "aaaaaaaa-1111-2222-3333-444444444444"
    f2 = "bbbbbbbb-5555-6666-7777-888888888888"
    mgr = [f"HDR SecondaryFrame[{f1}] form".encode("latin1"),
           f"HDR SecondaryFrame[{f2}] list open-card cmd".encode("latin1")]
    cli = [b"resp", "ФормаГруппы".encode("utf-16le")]   # the card marker in a client frame
    d = Path(tempfile.mkdtemp())
    with (d / "traffic.jsonl").open("w", encoding="utf-8") as fh:
        for n, p in enumerate(mgr):
            fh.write(json.dumps({"event": "chunk", "direction": "manager_to_client", "chunk_no": n,
                                 "byte_count": len(p), "payload_b64": base64.b64encode(p).decode()}) + "\n")
        for n, p in enumerate(cli):
            fh.write(json.dumps({"event": "chunk", "direction": "client_to_manager", "chunk_no": n,
                                 "byte_count": len(p), "payload_b64": base64.b64encode(p).decode()}) + "\n")
    t = derive_open_card(d, "ФормаГруппы")
    assert t.result_marker == "ФормаГруппы"
    failed = False
    try:
        derive_open_card(d, "НетТакогоМаркера")          # marker absent -> raises
    except ValueError:
        failed = True
    assert failed


def test_derive_close_window_locates_close_and_truncates_before_next():
    """Card 96 / E3: close_window finds the window-level `88 82 81` close on the SecondaryFrame that co-occurs
    with ``window_ref`` (the card's record data ref), and truncates the replay just before any SUBSEQUENT
    window-close so only the target window is closed (the windows capture closes the card then the fixture)."""
    from qa_mcp.protocol.native_write import derive_close_window
    f_list = "aaaaaaaa-1111-2222-3333-444444444444"   # the catalog list window
    f_card = "bbbbbbbb-5555-6666-7777-888888888888"   # the record card window (closed)
    f_fix = "cccccccc-9999-0000-1111-222222222222"    # the fixture form window (closed AFTER the card)
    ref = "e1cib/data/Справочник.Контрагенты"
    mgr = [
        f"HDR SecondaryFrame[{f_list}] open list".encode("latin1"),                  # 0
        f"HDR SecondaryFrame[{f_card}] ".encode("latin1") + ref.encode("utf-16le"),  # 1 card opens (data ref)
        f"HDR SecondaryFrame[{f_card}] ".encode("latin1") + b"\x88\x82\x81",          # 2 CLOSE the card
        b"HDR poll",                                                                  # 3 (no close)
        f"HDR SecondaryFrame[{f_fix}] ".encode("latin1") + b"\x88\x82\x81",           # 4 CLOSE the fixture
    ]
    cli = [b"resp", ref.encode("utf-16le")]
    d = Path(tempfile.mkdtemp())
    with (d / "traffic.jsonl").open("w", encoding="utf-8") as fh:
        for n, p in enumerate(mgr):
            fh.write(json.dumps({"event": "chunk", "direction": "manager_to_client", "chunk_no": n,
                                 "byte_count": len(p), "payload_b64": base64.b64encode(p).decode()}) + "\n")
        for n, p in enumerate(cli):
            fh.write(json.dumps({"event": "chunk", "direction": "client_to_manager", "chunk_no": n,
                                 "byte_count": len(p), "payload_b64": base64.b64encode(p).decode()}) + "\n")
    t = derive_close_window(d, window_ref=ref)
    assert t.window_sf == f_card           # the SF co-occurring with the card's data ref
    assert t.close_frame == 2              # the 88 82 81 on the card SF
    assert t.stop_after == 3               # one before the SUBSEQUENT fixture-close at index 4
    failed = False
    try:
        derive_close_window(d, window_ref="e1cib/data/Справочник.НетТакого")  # ref absent -> raises
    except ValueError:
        failed = True
    assert failed


def test_derive_activate_window_locates_command_on_target_sf():
    """Card 96 / E3: activate_window finds the window-level `88 82 81` command on the SecondaryFrame that
    co-occurs with ``window_ref`` (the buried target). activate and close share that command; on a background
    window it brings it forward."""
    from qa_mcp.protocol.native_write import derive_activate_window
    f_list = "dddddddd-1111-2222-3333-444444444444"   # the catalog list window (on top)
    f_fix = "eeeeeeee-5555-6666-7777-888888888888"     # the buried fixture form window (activated)
    ref = "e1cib/app/Обработка.ФикстураПротоколаTestClient"
    mgr = [
        f"HDR SecondaryFrame[{f_list}] open list".encode("latin1"),                   # 0
        f"HDR SecondaryFrame[{f_list}] ".encode("latin1") + b"\x88\x82\x81",           # 1 list command (not target)
        f"HDR SecondaryFrame[{f_fix}] ".encode("latin1") + ref.encode("utf-16le"),    # 2 fixture referenced
        f"HDR SecondaryFrame[{f_fix}] ".encode("latin1") + b"\x88\x82\x81",            # 3 ACTIVATE the fixture
    ]
    cli = [b"resp", ref.encode("utf-16le")]
    d = Path(tempfile.mkdtemp())
    with (d / "traffic.jsonl").open("w", encoding="utf-8") as fh:
        for n, p in enumerate(mgr):
            fh.write(json.dumps({"event": "chunk", "direction": "manager_to_client", "chunk_no": n,
                                 "byte_count": len(p), "payload_b64": base64.b64encode(p).decode()}) + "\n")
        for n, p in enumerate(cli):
            fh.write(json.dumps({"event": "chunk", "direction": "client_to_manager", "chunk_no": n,
                                 "byte_count": len(p), "payload_b64": base64.b64encode(p).decode()}) + "\n")
    t = derive_activate_window(d, window_ref=ref)
    assert t.window_sf == f_fix            # the SF co-occurring with the fixture app ref
    assert t.activate_frame == 3           # the 88 82 81 on the fixture SF (not the list one at index 1)
    failed = False
    try:
        derive_activate_window(d, window_ref="e1cib/app/Обработка.НетТакого")  # ref absent -> raises
    except ValueError:
        failed = True
    assert failed


def test_extract_user_messages_decodes_cb539a_envelope():
    """Card 96 / E5: a user message (Сообщить) rides as `cb 53 9a <varint byte-len> <UTF-8 text>`. The decoder
    extracts each message (right-trimmed), handles a multi-byte LEB128 length (long messages), decodes Cyrillic
    UTF-8, and de-duplicates adjacent repeats (the same message echoes across poll responses)."""
    from qa_mcp.protocol.native_write import extract_user_messages, encode_1c_length
    def env(text: str) -> bytes:
        b = text.encode("utf-8")
        return b"\xcb\x53\x9a" + encode_1c_length(len(b)) + b
    short = "PF_CHOICE=PF_CHOICE_B"
    long = "Поле не заполнено. " * 12            # >127 bytes -> 2-byte LEB128 length; Cyrillic UTF-8
    blob = (b"\x00\x01junk" + env(short) + b"\x99poll" + env(long) + b"\xa1"
            + env(long) + b"tail")               # the long message repeated (adjacent) -> de-duped
    msgs = extract_user_messages(blob)
    assert msgs == [short, long.rstrip()]        # both decoded, adjacent repeat collapsed, order preserved
    assert extract_user_messages(b"no envelope here") == []


def _cell_frame(table: str, column: str, value: str) -> bytes:
    """A synthetic table-cell SET frame: 21-byte header + length-prefixed element path whose leaf is the
    column EditField inside a Table[<table>] segment + fixed-width value block (card 90 / 86e)."""
    path = (f"SecondaryFrame[{_S}].ManagedForm[{_F}].Group[PF_GROUP_MAIN]"
            f".Table[{table}].EditField[{column}]").encode("latin1")
    path_block = b"\x9a" + bytes([len(path)]) + path
    value_block = b"\x81\xba" + encode_1c_length(len(value.encode())) + value.encode() + b"\x20\x20\xa1"
    return b"H" * 21 + path_block + value_block + b"TAIL"


def test_retarget_element_segment_table_keeps_leaf():
    """Card 90 / 86e: a table is a MID-path Table[<name>] segment (the column is the leaf). Re-targeting the
    segment swaps the table box and keeps the column EditField leaf + path validity."""
    from qa_mcp.protocol.element_ref import extract_element_paths, retarget_element_segment
    frame = _cell_frame("PF_TABLE_ITEMS", "PF_TABLE_TEXT", "CELLAA")
    out, n = retarget_element_segment(frame, "PF_TABLE_ITEMS", "OTHER_TBL", kind="Table")
    assert n == 1
    assert any(p.endswith("Table[OTHER_TBL].EditField[PF_TABLE_TEXT]") for p in extract_element_paths(out))
    assert b"Table[PF_TABLE_ITEMS]" not in out
    assert b"EditField[PF_TABLE_TEXT]" in out  # column leaf untouched


def test_derive_table_cell_write_commit_partner_locates_block():
    """Card 90 / 86e: a table-cell write template = the contiguous Table[..].EditField[column] SET block (the
    write block, stopping before the next non-cell frame) + a focus-change synthesized from the commit partner
    — exactly the card-86c commit-partner derive, since a cell SET is a plain string SET."""
    from qa_mcp.protocol.native_write import derive_table_cell_write
    aa, cmt = "CELLAA", "C90CMT"
    aa_seq = encode_1c_length(len(aa.encode())) + aa.encode()
    cmt_seq = encode_1c_length(len(cmt.encode())) + cmt.encode()
    frames = [
        b"setup_0_connect_open_xxxx",                                         # 0 setup
        b"setup_1_addrow_no_editfield",                                       # 1 add-row #1 (no EditField)
        b"hdr Table[PF_TABLE_ITEMS].EditField[PF_TABLE_TEXT] activate",       # 2 cell activate
        b"hdr Table[PF_TABLE_ITEMS].EditField[PF_TABLE_TEXT] " + aa_seq,      # 3 cell SET (CELLAA)
        b"addrow_2_no_editfield",                                             # 4 add-row #2 (no EditField)
        b"hdr Table[PF_TABLE_ITEMS].EditField[PF_TABLE_TEXT] second_cell",    # 5 second cell edit
        b"hdr EditField[PF_EDIT_STRING] activate",                           # 6 partner activate (focus-change)
        b"hdr EditField[PF_EDIT_STRING] " + cmt_seq,                          # 7 partner SET
        b"control_tail_nofields",                                            # 8 tail
    ]
    t = derive_table_cell_write(_write_capture(frames), "PF_TABLE_TEXT", aa,
                                commit_partner_field="PF_EDIT_STRING", commit_partner_value=cmt)
    assert t.field == "PF_TABLE_TEXT"
    assert t.write_block == (2, 3)        # cell activate + SET only (stops before add-row #2)
    assert t.commit_block == (6, 6)       # partner activate = synthesized focus-change
    assert t.setup_end == 1               # before the cell activate


def test_set_table_cell_frame_retargets_value_keeps_table_segment():
    """Card 90 / 86e: writing a cell reuses build_write_frame — the value (fixed-width) + offset-19 counter are
    re-targeted while the Table[<table>] segment and column leaf are preserved (same-column write)."""
    frame = _cell_frame("PF_TABLE_ITEMS", "PF_TABLE_TEXT", "CELLAA")
    out = build_write_frame(frame, "CELLAA", "HELLO9", base_field="PF_TABLE_TEXT",
                            target_field="PF_TABLE_TEXT", seq=4)
    assert b"HELLO9" in out and b"CELLAA" not in out
    assert b"Table[PF_TABLE_ITEMS].EditField[PF_TABLE_TEXT]" in out
    assert out[19:21] == (4).to_bytes(2, "little")
    assert len(out) == len(frame)         # same-length value keeps frame size


def test_set_table_cell_frame_retargets_column_leaf_keeps_table():
    """Card 90 / 86e: targeting a different COLUMN swaps the EditField leaf only (the Table[<table>] segment is
    preserved), via build_write_frame's element-leaf retarget."""
    frame = _cell_frame("PF_TABLE_ITEMS", "PF_TABLE_TEXT", "CELLAA")
    out = build_write_frame(frame, "CELLAA", "WORLD9", base_field="PF_TABLE_TEXT",
                            target_field="PF_TABLE_NUMBER", seq=1)
    assert b"EditField[PF_TABLE_NUMBER]" in out
    assert b"EditField[PF_TABLE_TEXT]" not in out
    assert b"Table[PF_TABLE_ITEMS]" in out  # table segment preserved, only the column leaf swapped
    assert b"WORLD9" in out


def test_derive_open_list_locates_nav_block():
    """Card 90 §7 Step 4: an open-list template = the contiguous run of frames carrying the e1cib/list nav link
    (UTF-16LE); ``setup_end`` is everything before it (connect + open form)."""
    from qa_mcp.protocol.native_write import derive_open_list
    link = "e1cib/list/Справочник.Товары"
    nav = link.encode("utf-16le")
    frames = [
        b"setup_0_connect_xxxx",            # 0 setup
        b"setup_1_openform_xxxx",           # 1 setup
        b"HDR nav " + nav + b" command",    # 2 open-list command (carries the nav link)
        b"control_tail_nofields",           # 3 tail
    ]
    t = derive_open_list(_write_capture(frames), link)
    assert t.base_link == link
    assert t.setup_end == 1
    assert t.open_list_block == (2, 2)


def test_rowselect_search_value_retarget_fixed_width():
    """Card 90 follow-up #1: a native row-select carries its search value as a length-prefixed fixed-width
    string (`… 9a<len>VALUE <pad>`); re-targeting the value (same length here) selects a different row while
    keeping the frame size — exactly the fixed-width `retarget_value` used for cell SETs."""
    val = "PF_ROW_002_TEXT"  # 15
    frame = b"H" * 8 + b"\xeb\x53" + encode_1c_length(len(val)) + val.encode() + b"\x20\x20\x20" + b"TAIL"
    out = retarget_value(frame, "PF_ROW_002_TEXT", "PF_ROW_003_TEXT")
    assert b"PF_ROW_003_TEXT" in out and b"PF_ROW_002_TEXT" not in out
    assert len(out) == len(frame)  # same-length row value keeps the frame size


def test_read_table_cell_value_grid_readback():
    """Card 90 follow-up #3: a committed table cell echoes via `EditField[<col>] <counter> e0 41 81 81 ba
    <len><value>`; the middle counter byte varies (here \\x82), which read_field_value_near misses but
    read_table_cell_value parses by anchoring on the value-SET tag."""
    blob = (b"...PF_TABLE_ITEMS].EditField[PF_TABLE_TEXT]\x81\x82\x81\xe0\x41\x81\x81\xba"
            + encode_1c_length(6) + b"R2WROT \xa1\xa3rest")
    assert read_table_cell_value(blob, "PF_TABLE_TEXT") == "R2WROT"
    assert read_field_value_near(blob, "PF_TABLE_TEXT") is None  # the old reader misses the \x82 counter byte
    assert read_table_cell_value(b"no cell here", "PF_TABLE_TEXT") is None


def test_derive_command_click_locates_last_run():
    """Card 90 follow-up #2: a command-click template = the LAST contiguous Button[base] run (the click —
    `…Button[NAME] 88 81 81 e1`); the earlier Button run is the form-open render and stays in the setup."""
    from qa_mcp.protocol.native_write import derive_command_click
    p = "SecondaryFrame[s].ManagedForm[f].Group[PF_COMMAND_BAR_MAIN].Button[PF_ADD_ROW]".encode("latin1")
    frames = [
        b"setup_0_xxxx",
        b"HDR" + p + b" render-a",                 # 1 RENDER run (form open)
        b"HDR" + p + b" render-b",                 # 2 RENDER run
        b"middle_no_button_xxxx",                  # 3 gap
        b"HDR" + p + b" \x88\x81\x81\xe1 click",   # 4 CLICK run
        b"HDR" + p + b" click-dup",                # 5 CLICK run
        b"control_tail_nobutton",                  # 6 tail
    ]
    t = derive_command_click(_write_capture(frames), "PF_ADD_ROW")
    assert t.base_button == "PF_ADD_ROW"
    assert t.click_block == (4, 5)   # the LAST run (the click), not the render (1,2)
    assert t.setup_end == 3


def test_click_command_retargets_button_leaf_keeps_command_tag():
    """Card 90 follow-up #2: re-targeting the click to another button swaps the `Button` leaf and keeps the
    `88 81 81 e1` command-execute marker (the Button twin of the checkbox EditField retarget)."""
    from qa_mcp.protocol.element_ref import retarget_element_leaf
    p = "SecondaryFrame[s].ManagedForm[f].Group[PF_COMMAND_BAR_MAIN].Button[PF_ADD_ROW]".encode("latin1")
    frame = b"H" * 21 + b"\x9a" + bytes([len(p)]) + p + b"\x88\x81\x81\xe1" + b"TAIL"
    out, n = retarget_element_leaf(frame, "PF_ADD_ROW", "PF_RESET_STATE", kind="Button")
    assert n == 1
    assert b"Button[PF_RESET_STATE]" in out and b"Button[PF_ADD_ROW]" not in out
    assert b"\x88\x81\x81\xe1" in out  # command-execute tag preserved


def test_rowops_derive_first_click_carries_form_open_setup():
    """Card 97 #1: the combined connect+open+rowops capture clicks PF_COPY_ROW FIRST, so
    derive_command_click('PF_COPY_ROW') yields a setup that spans the whole form-open render (everything before
    the first click) — the clean replay base that click_command retargets to any row-op command. The later
    clicks (MOVE/DELETE) are AFTER the COPY block and are not in COPY's setup."""
    from qa_mcp.protocol.native_write import derive_command_click
    bar = "SecondaryFrame[s].ManagedForm[f].Group[PF_COMMAND_BAR_MAIN]"
    def render(btn):  # a form-open descriptor frame for one button
        return f"HDR {bar}.Button[{btn}] render".encode("latin1")
    def click(btn):   # a genuine command click for one button (88 82 81 20 20 20 tail)
        return f"HDR {bar}.Button[{btn}] ".encode("latin1") + b"\x88\x82\x81\x20\x20\x20"
    frames = [
        b"setup_handshake_0", b"setup_open_form_1",
        render("PF_COPY_ROW"), render("PF_MOVE_ROW_DOWN"),   # 2,3 form-open render run
        render("PF_MOVE_ROW_UP"), render("PF_DELETE_ROW"),   # 4,5 form-open render run
        click("PF_COPY_ROW"),                                # 6 first genuine click
        click("PF_MOVE_ROW_DOWN"),                           # 7
        click("PF_MOVE_ROW_UP"),                             # 8
        click("PF_DELETE_ROW"),                              # 9 last genuine click
    ]
    t = derive_command_click(_write_capture(frames), "PF_COPY_ROW")
    assert t.base_button == "PF_COPY_ROW"
    assert t.click_block == (6, 6)   # the COPY click, not the render at index 2
    assert t.setup_end == 5          # setup spans the full form-open render (0..5)


def test_rowops_retarget_copy_to_longer_command_is_length_aware():
    """Card 97 #1: all four row-op commands share the `…Group[PF_COMMAND_BAR_MAIN].Button[NAME]` invoke, so one
    genuine PF_COPY_ROW click retargets to any of them. The names differ in length (PF_COPY_ROW=11 →
    PF_MOVE_ROW_DOWN=15), so the element-path length prefix must be recomputed and the command tail preserved."""
    from qa_mcp.protocol.element_ref import retarget_element_leaf
    p = "SecondaryFrame[s].ManagedForm[f].Group[PF_COMMAND_BAR_MAIN].Button[PF_COPY_ROW]".encode("latin1")
    frame = b"H" * 21 + b"\x9a" + bytes([len(p)]) + p + b"\x88\x82\x81\x20\x20\x20" + b"TAIL"
    for target in ("PF_DELETE_ROW", "PF_MOVE_ROW_UP", "PF_MOVE_ROW_DOWN"):
        out, n = retarget_element_leaf(frame, "PF_COPY_ROW", target, kind="Button")
        assert n == 1
        assert f"Button[{target}]".encode("latin1") in out and b"Button[PF_COPY_ROW]" not in out
        assert b"\x88\x82\x81\x20\x20\x20" in out  # command invoke tail preserved
        # length prefix recomputed: the path-length byte equals the new path length
        new_p = out[out.index(b"SecondaryFrame") - 1]
        assert new_p == len(f"SecondaryFrame[s].ManagedForm[f].Group[PF_COMMAND_BAR_MAIN].Button[{target}]")


def test_derive_table_command_locates_table_level_invoke():
    """Card 97 #1 multi-select: the genuine "select all rows" step is a TABLE-level command addressed at the
    `Table[<table>]` leaf (NOT a Button). derive_table_command finds the LAST `Table[<table>]` run (the invoke,
    `88 82 81 20 20 20`) past the form-open render, with the setup spanning the form-open — so
    `click_command(template, None)` replays it with no leaf retarget."""
    from qa_mcp.protocol.native_write import derive_table_command
    tbl = "SecondaryFrame[s].ManagedForm[f].Table[PF_TABLE_ITEMS]"
    frames = [
        b"setup_handshake_0", b"setup_open_form_1",
        f"HDR {tbl} render".encode("latin1"),                          # 2 form-open render run
        b"middle_no_table_xxxxxxxx",                                   # 3 gap
        f"HDR {tbl} ".encode("latin1") + b"\x88\x82\x81\x20\x20\x20",  # 4 the select-all invoke (last run)
    ]
    t = derive_table_command(_write_capture(frames), "PF_TABLE_ITEMS")
    assert t.base_button == "Table[PF_TABLE_ITEMS]"
    assert t.click_block == (4, 4)   # the invoke, not the render at index 2
    assert t.setup_end == 3          # setup spans the form-open render


def test_native_write_session_stores_setup_retargets():
    """Card 90 follow-up #1: NativeWriteSession carries setup-frame value retargets (the row-select value swap
    applied while replaying the form-open setup)."""
    from qa_mcp.protocol.native_write import NativeWriteSession
    val = "X"
    frames = [b"setup0", b"hdr EditField[F] " + encode_1c_length(1) + b"X", b"hdr EditField[O] focus"]
    t = derive_write_template(_write_capture(frames), "F", val, "DEF")
    s = NativeWriteSession(t, setup_retargets=[("PF_ROW_002_TEXT", "PF_ROW_003_TEXT")])
    assert s._setup_retargets == [("PF_ROW_002_TEXT", "PF_ROW_003_TEXT")]
    assert NativeWriteSession(t)._setup_retargets == []


def test_retarget_nav_link_repoints_catalog_same_length():
    """Card 90 §7 Step 4: re-pointing the open-list nav link swaps the catalog (same-length here), keeping the
    length-prefixed UTF-16LE framing."""
    from qa_mcp.protocol.navigation import retarget_nav_link
    old = "e1cib/list/Справочник.Товары"
    new = "e1cib/list/Справочник.Склады"   # same length (…Товары / …Склады = 6 chars each)
    frame = b"H" * 8 + bytes([len(old)]) + old.encode("utf-16le") + b"TAIL"
    out, n = retarget_nav_link(frame, old, new)
    assert n >= 1
    assert new.encode("utf-16le") in out
    assert old.encode("utf-16le") not in out


def _utf16_field_frame(field: str, value: str | None = None) -> bytes:
    """A synthetic frame whose element path leaf is UTF-16LE (as the wire encodes a non-ASCII field name)."""
    path = ("EditField[" + field + "]").encode("utf-16-le")
    body = b""
    if value is not None:
        body = b"\x81\xba" + encode_1c_length(len(value.encode())) + value.encode() + b"\x20\xa1"
    return b"H" * 21 + path + body + b"T"


def test_editfields_in_handles_ascii_and_utf16_cyrillic_paths():
    """Card 98 (2nd-config gate): element paths are 1-byte ASCII for ASCII field names but UTF-16LE for
    non-ASCII (Cyrillic) names. editfields_in must decode BOTH, else the write deriver finds nothing on a
    real (Russian-named) config."""
    from qa_mcp.protocol.native_write import editfields_in
    ascii_frame = b"x" * 8 + b"EditField[PF_EDIT_STRING]" + b"y"
    utf16_frame = b"x" * 8 + "EditField[НаименованиеПолное]".encode("utf-16-le") + b"y"
    assert editfields_in(ascii_frame) == {"PF_EDIT_STRING"}
    assert editfields_in(utf16_frame) == {"НаименованиеПолное"}
    assert editfields_in(ascii_frame + utf16_frame) == {"PF_EDIT_STRING", "НаименованиеПолное"}


def test_read_field_value_near_utf16_cyrillic_anchor():
    """read_field_value_near reads a value addressed by a UTF-16LE EditField leaf (Cyrillic field name)."""
    field = "Наименование"  # Наименование
    leaf = ("EditField[" + field + "]").encode("utf-16-le")
    blob = b"H" * 8 + leaf + b"\x88\x82\x81\xe0\x41\x81\x81\xba" + encode_1c_length(len(b"QADEMO2026")) + b"QADEMO2026" + b"\x20\xa1"
    assert read_field_value_near(blob, field) == "QADEMO2026"


def test_derive_write_template_handles_utf16_cyrillic_field():
    """Card 98 (2nd-config gate): derive a write template for a Cyrillic-named field (UTF-16LE element path)
    — the SET, activate prefix, focus-change (a DIFFERENT Cyrillic field) and read-back are all located."""
    name = "Наименование"  # Наименование
    other = name + "ОсновнойВалюты"  # НаименованиеОсновнойВалюты
    frames = [
        b"setup-prefix",                       # 0
        _utf16_field_frame(name),              # 1 activate
        _utf16_field_frame(name, "QADEMO2026"),  # 2 SET (value)
        _utf16_field_frame(other),             # 3 focus-change (different field)
        _utf16_field_frame(name),              # 4 read-back
    ]
    t = derive_write_template(_write_capture(frames), name, "QADEMO2026", default_value="")
    assert t.field == name
    assert t.write_block == (1, 3)
    assert t.stop_after == 3
    assert 4 in t.read_frames


def _search_set_frame(value: str) -> bytes:
    """A synthetic dynlist search-string SET frame: the UTF-16 ``b7`` value buffer
    (``e0 41 81 81 b7 <char-count><utf-16le value><space pad>``) — the same buffer a reference-name SET uses."""
    val_block = bytes.fromhex("e0418181b7") + encode_1c_length(len(value)) + value.encode("utf-16-le") + b"\x20\x20\x20"
    return b"HDR" + val_block + b"TAIL"


def test_derive_search_list_locates_first_search_block():
    """Card 97 change 4: a decode capture types TWO different search strings (for the byte-diff); the derive
    must set stop_after to the LAST frame of the FIRST search's SET block so the replay applies ONE search."""
    from qa_mcp.protocol.native_write import derive_search_list
    frames = [
        b"setup0", b"setup1", b"setup2",        # 0-2 handshake/open
        b"table-activate-1",                     # 3 dynlist activate (before first search)
        _search_set_frame("Молоко"),             # 4 first search SET (888281)
        _search_set_frame("Молоко"),             # 5 first search SET dup (818181)
        b"table-activate-2",                     # 6 dynlist re-activate (before second search)
        _search_set_frame("Творог"),             # 7 second search SET
        _search_set_frame("Творог"),             # 8 second search SET dup
    ]
    t = derive_search_list(_write_capture(frames), "ДенамическийСписокИерархияСтрокаПоиска", "Молоко")
    assert t.stop_after == 5  # last frame of the FIRST contiguous Молоко run (not the Творог frames)
    assert t.captured_value == "Молоко"
    assert t.search_field == "ДенамическийСписокИерархияСтрокаПоиска"


def test_search_set_buffer_retargets_utf16_fixed_width():
    """Card 97 change 4: the search value re-targets via the UTF-16 ``b7`` fixed-width retarget (shared with the
    reference-field SET) — the new string lands, the old is gone, the frame size is preserved."""
    from qa_mcp.protocol.native_write import retarget_ref_value
    frame = _search_set_frame("Молоко")
    out = retarget_ref_value(frame, "Молоко", "Сыр")  # shorter -> trailing padding grows
    assert "Молоко".encode("utf-16-le") not in out
    assert "Сыр".encode("utf-16-le") in out
    assert len(out) == len(frame)  # fixed width


def test_derive_search_list_requires_value_present():
    """Card 97 change 4: derive_search_list raises if the captured search value is absent (UTF-16 b7 buffer)."""
    from qa_mcp.protocol.native_write import derive_search_list
    try:
        derive_search_list(_write_capture([b"no search value here at all"]), "SF", "Молоко")
        assert False, "expected ValueError when the captured search value is absent"
    except ValueError:
        pass


def test_retarget_element_leaf_any_ascii_and_utf16_same_length():
    """Card 97 change 4 (view-mode): retarget a Button leaf whether the element path is ASCII (latin1, the
    fixture `PF_*`) or UTF-16LE (Cyrillic dynlist commands); the UTF-16 branch requires the same char length."""
    from qa_mcp.protocol.element_ref import retarget_element_leaf_any
    # ASCII path (1-byte length prefix)
    apath = b"SecondaryFrame[S].Group[G].Button[PF_ADD_ROW]"
    aframe = b"\x9a" + bytes([len(apath)]) + apath + b"TAIL"
    out, n = retarget_element_leaf_any(aframe, "PF_ADD_ROW", "PF_DELETE_ROW", kind="Button")
    assert n == 1 and b"Button[PF_DELETE_ROW]" in out
    # UTF-16LE path, same char length: Список(6) -> Дерево(6) keeps the frame size (no char-count change)
    u16 = "Button[ДенамическийСписокИерархияСписок]".encode("utf-16-le")
    uframe = b"HDR" + u16 + b"TAIL"
    out2, n2 = retarget_element_leaf_any(
        uframe, "ДенамическийСписокИерархияСписок", "ДенамическийСписокИерархияДерево", kind="Button")
    assert n2 == 1 and len(out2) == len(uframe)
    assert "Button[ДенамическийСписокИерархияДерево]".encode("utf-16-le") in out2
    assert "Button[ДенамическийСписокИерархияСписок]".encode("utf-16-le") not in out2


def test_retarget_element_leaf_any_utf16_different_length_raises():
    """Card 97 change 4: a UTF-16 leaf retarget that changes the char count is rejected (resizing the path's
    char-count length prefix is a documented refinement)."""
    from qa_mcp.protocol.element_ref import retarget_element_leaf_any
    uframe = b"HDR" + "Button[ДенамическийСписокИерархияСписок]".encode("utf-16-le") + b"TAIL"
    try:
        retarget_element_leaf_any(
            uframe, "ДенамическийСписокИерархияСписок", "ДенамическийСписокИерархияИерархическийСписок", kind="Button")
        assert False, "expected ValueError for a different-length UTF-16 leaf retarget"
    except ValueError:
        pass


def test_find_element_command_locates_utf16_button_last_run():
    """Card 97 change 4: _find_element_command finds a Cyrillic (UTF-16LE) Button command — the LAST contiguous
    run of frames addressing the leaf (the earlier render run is skipped)."""
    from qa_mcp.protocol.native_write import _find_element_command
    leaf = "Button[ДенамическийСписокИерархияСписок]"
    u16 = leaf.encode("utf-16-le")
    mgr = [
        b"setup-0",
        b"render " + u16 + b" (early form-open run)",  # 1 earlier run
        b"between-frame-no-leaf",                        # 2 breaks the run
        b"click " + u16 + b" 88 82 81 20 20 20",        # 3 the invoke
        b"click " + u16 + b" 81 81 81 20 20 20",        # 4 the invoke dup
    ]
    assert _find_element_command(mgr, leaf) == (3, 4)


def test_set_list_view_rejects_unknown_mode():
    """Card 97 change 4: set_list_view validates the mode before any I/O."""
    from pathlib import Path
    from qa_mcp.protocol.native_write import set_list_view
    try:
        set_list_view(Path("/nonexistent-capture"), "НеизвестныйРежим")
        assert False, "expected ValueError for an unknown view mode"
    except ValueError:
        pass


def test_retarget_cell_address_resize_variable_length():
    """Card 97 change 3: the «перейти к ячейке» navigate carries the address as \\xfa<len><utf-8> + a fixed
    3-space suffix; the retarget swaps the length-prefixed address and lets the FRAME RESIZE by the length delta
    (the navigate frame tolerates resize — proven live), so an ARBITRARY-length address works (no padding budget)."""
    from qa_mcp.protocol.native_write import retarget_cell_address
    nav = b"HDR EditField[PF_REPORT] " + bytes([0xfa, 4]) + b"R1C1\x20\x20\x20TAIL"
    # same length -> frame unchanged size
    out = retarget_cell_address(nav, "R1C1", "R2C2")
    assert bytes([0xfa, 4]) + b"R2C2" in out and len(out) == len(nav)
    # LONGER (6 chars) -> frame GROWS by 2, trailing structural spaces preserved
    out6 = retarget_cell_address(nav, "R1C1", "R12C12")
    assert bytes([0xfa, 6]) + b"R12C12" + b"\x20\x20\x20TAIL" in out6
    assert len(out6) == len(nav) + 2 and bytes([0xfa, 4]) + b"R1C1" not in out6
    # even longer (8 chars) -> grows by 4 (no budget cap)
    out8 = retarget_cell_address(nav, "R1C1", "R100C100")
    assert bytes([0xfa, 8]) + b"R100C100" + b"\x20\x20\x20TAIL" in out8 and len(out8) == len(nav) + 4
    # no-ops
    assert retarget_cell_address(nav, "R1C1", "R1C1") == nav
    assert retarget_cell_address(b"no address here", "R1C1", "R2C2") == b"no address here"


def test_derive_read_spreadsheet_cell_validates_navigate_address():
    """Card 97 change 3: derive_read_spreadsheet_cell requires the navigate command (the \\xfa<len><address>) to
    be present, and records the captured cell value parsed from the client response."""
    from qa_mcp.protocol.native_write import derive_read_spreadsheet_cell
    nav = b"hdr EditField[PF_REPORT] 88 82 81 " + bytes([0xfa, 4]) + b"R1C1"
    val = b"hdr EditField[PF_REPORT]\x81\x81\x81\xe1\x9a\x0bPF_RPT_R1C1\x20"
    cap = _write_capture([b"setup", nav])
    # add a client_to_manager frame carrying the value (the read response)
    import base64, json as _json
    with (cap / "traffic.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(_json.dumps({"event": "chunk", "direction": "client_to_manager", "chunk_no": 9,
                              "byte_count": len(val), "payload_b64": base64.b64encode(val).decode()}) + "\n")
    t = derive_read_spreadsheet_cell(cap, "PF_REPORT", "R1C1")
    assert t.captured_address == "R1C1"
    assert t.captured_value == "PF_RPT_R1C1"
    try:
        derive_read_spreadsheet_cell(_write_capture([b"no navigate command here"]), "PF_REPORT", "R1C1")
        assert False, "expected ValueError when the navigate command is absent"
    except ValueError:
        pass


def test_derive_advanced_search_validates_utf16_pattern():
    """Card 97 change 4: derive_advanced_search requires the captured Pattern value to be present as a UTF-16
    `b7` buffer (the «Расширенный поиск» dialog Pattern field rides the same buffer as a ref/search value)."""
    from qa_mcp.protocol.native_write import derive_advanced_search, encode_1c_length
    val = "Молоко"
    pattern_frame = b"...Field[Pattern]" + bytes.fromhex("e0418181b7") + encode_1c_length(len(val)) + val.encode("utf-16-le") + b"\x20\x20\x20"
    t = derive_advanced_search(_write_capture([b"setup", pattern_frame, b"Button[Find] 88 82 81"]), captured_value=val)
    assert t.captured_value == val
    assert t.search_command == "ДенамическийСписокИерархияНайти"
    try:
        derive_advanced_search(_write_capture([b"no pattern value here"]), captured_value=val)
        assert False, "expected ValueError when the captured Pattern value is absent"
    except ValueError:
        pass

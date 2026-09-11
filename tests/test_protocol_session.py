from __future__ import annotations

import socket
from pathlib import Path

from qa_mcp.protocol import AcceptanceStatus, InitialUiContext, TAIL_MARKER, TestClientSession
from qa_mcp.protocol.evidence import get_readonly_operation_descriptor
from qa_mcp.protocol.native_mutation import _read_available as mutation_read_available
from qa_mcp.protocol.responses import extract_edit_field_value
from qa_mcp.protocol.session import read_available


class FakeSocket:
    def __init__(self, responses: list[bytes]) -> None:
        self.responses = list(responses)
        self.sent: list[bytes] = []
        self.closed = False
        self.timeouts: list[float] = []

    def setsockopt(self, *_args: object) -> None:
        return None

    def settimeout(self, timeout: float) -> None:
        self.timeouts.append(timeout)

    def recv(self, _size: int) -> bytes:
        if not self.responses:
            raise socket.timeout()
        return self.responses.pop(0)

    def sendall(self, payload: bytes) -> None:
        self.sent.append(payload)

    def close(self) -> None:
        self.closed = True


class EventSocket:
    def __init__(self, events: list[bytes | type[Exception]]) -> None:
        self.events = list(events)
        self.timeouts: list[float] = []

    def settimeout(self, timeout: float) -> None:
        self.timeouts.append(timeout)

    def recv(self, _size: int) -> bytes:
        if not self.events:
            raise socket.timeout()
        event = self.events.pop(0)
        if event is socket.timeout:
            raise socket.timeout()
        return event


def test_session_send_read_and_cleanup_uses_owned_socket() -> None:
    fake = FakeSocket([b"response-a", b"response-b"])
    session = TestClientSession(read_timeout_sec=0.01, idle_timeout_sec=0.01)
    session._socket = fake  # package tests avoid opening real sockets

    response = session.send_and_read(b"request")
    session.close()

    assert fake.sent == [b"request"]
    assert response == b"response-aresponse-b"
    assert fake.closed is True
    assert session._socket is None


def test_read_available_waits_for_tail_after_idle_timeout() -> None:
    value_blob = b"\x00EditField[PF_EDIT_STRING]\x81\x81\x81\xfa\x02OK\x20\xa1"
    sock = EventSocket([value_blob[:20], socket.timeout, value_blob[20:] + TAIL_MARKER])

    response = read_available(sock, first_timeout_sec=0.1, idle_timeout_sec=0.01)

    assert response == value_blob + TAIL_MARKER
    assert extract_edit_field_value(response, "PF_EDIT_STRING") == "OK"
    assert len(sock.timeouts) >= 3


def test_read_available_tail_less_buffer_uses_hard_deadline() -> None:
    sock = EventSocket([b"partial", socket.timeout])

    response = read_available(sock, first_timeout_sec=0.001, idle_timeout_sec=0.001)

    assert response == b"partial"


def test_native_mutation_read_available_uses_same_tail_behavior() -> None:
    payload = b"mutation-response" + TAIL_MARKER
    sock = EventSocket([b"mutation-", socket.timeout, b"response" + TAIL_MARKER])

    assert mutation_read_available(sock, first_timeout=0.1, idle_timeout=0.01) == payload


def test_initial_context_result_includes_evidence_status(tmp_path: Path) -> None:
    descriptor = get_readonly_operation_descriptor("active-window-context", Path.cwd())
    context = InitialUiContext(
        status="ok",
        capture_dir=tmp_path / "capture",
        templates_path=tmp_path / "templates.json",
        output_dir=tmp_path / "out",
        descriptor=descriptor,
        ack_guid="11111111-1111-1111-1111-111111111111",
        frame4_sequence=4,
        sent_byte_count=10,
        received_byte_count=20,
        frames=[{"send_index": 8, "semantic_guess": "main_frame_with_home_page"}],
    )

    result = context.to_result()

    assert result["case_id"] == "active-window-context"
    assert result["evidence_status"] == AcceptanceStatus.ACCEPTED.value
    assert result["descriptor"]["accepted_normalized_hash"]
    assert result["sent_byte_count"] == 10


def test_form_element_descriptor_remains_unresolved() -> None:
    descriptor = get_readonly_operation_descriptor("form-element-details", Path.cwd())

    assert descriptor.acceptance_status == AcceptanceStatus.INCOMPLETE_HASH
    assert descriptor.accepted_normalized_hash is None
    assert descriptor.unresolved_reason == "accepted_probe_without_reviewed_request_hash"

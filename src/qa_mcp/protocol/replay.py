"""Shared TestClient replay session primitives."""

from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Callable

from .bootstrap_synth import SYNTH_TEMPLATE_VERSION, resolve_synth_platform_version
from .native_mutation import GuidRebinder
from .transport import connect_testclient, read_protocol_available


DEFAULT_SEND_TIMEOUT_SEC = 10.0
SEND_TIMEOUT_REASON = "send_timeout"


class ProtocolSendTimeout(Exception):
    """Raised when an outbound TestClient frame cannot be sent within the send deadline."""


def send_all(sock: socket.socket, payload: bytes, *, timeout_sec: float = DEFAULT_SEND_TIMEOUT_SEC) -> None:
    sock.settimeout(timeout_sec)
    try:
        sock.sendall(payload)
    except socket.timeout as exc:
        raise ProtocolSendTimeout(SEND_TIMEOUT_REASON) from exc


def frame_seq(frame: bytes) -> int:
    return int.from_bytes(frame[19:21], "little") if len(frame) >= 21 else 0


@dataclass(frozen=True)
class ReplayOp:
    """Description of a contiguous replay operation within a manager stream."""

    lo: int
    hi: int

    @property
    def indices(self) -> range:
        return range(self.lo, self.hi + 1)


class ReplaySession:
    """Open a TestClient socket and replay manager frames with live GUID rebinding."""

    def __init__(
        self,
        manager_chunks: list[bytes],
        client_chunks: list[bytes],
        *,
        host: str = "127.0.0.1",
        port: int = 15381,
        read_timeout_sec: float = 0.6,
        idle_timeout_sec: float = 0.15,
        connect_timeout_sec: float = 10.0,
        send_timeout_sec: float = DEFAULT_SEND_TIMEOUT_SEC,
        connect: Callable[..., socket.socket] | None = None,
    ) -> None:
        self.manager_chunks = manager_chunks
        self.client_chunks = client_chunks
        self.host = host
        self.port = port
        self.read_timeout_sec = read_timeout_sec
        self.idle_timeout_sec = idle_timeout_sec
        self.connect_timeout_sec = connect_timeout_sec
        self.send_timeout_sec = send_timeout_sec
        self.connect = connect or connect_testclient
        self.sock: socket.socket | None = None
        self.rebinder: GuidRebinder | None = None
        self.next_seq = 0
        live_version = resolve_synth_platform_version()
        self._captured_platform_version = SYNTH_TEMPLATE_VERSION.encode("ascii")
        self._live_platform_version = (
            live_version.encode("ascii")
            if live_version and live_version != SYNTH_TEMPLATE_VERSION
            else None
        )

    def __enter__(self) -> "ReplaySession":
        sock = self.connect((self.host, self.port), timeout=self.connect_timeout_sec)
        self.sock = sock
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.rebinder = GuidRebinder.from_client_chunks([{"payload": chunk} for chunk in self.client_chunks])
            self.observe_response(self.receive())
            return self
        except Exception:
            sock.close()
            self.sock = None
            self.rebinder = None
            self.next_seq = 0
            raise

    def __exit__(self, *_exc: object) -> None:
        if self.sock is not None:
            close = getattr(self.sock, "close", None)
            if close is not None:
                close()
            self.sock = None
        self.rebinder = None

    def apply(self, frame: bytes) -> bytes:
        if self.rebinder is None:
            raise RuntimeError("ReplaySession is not open")
        payload = frame
        if self._live_platform_version is not None:
            payload = payload.replace(self._captured_platform_version, self._live_platform_version)
        return self.rebinder.apply(payload)

    def observe_response(self, response: bytes) -> None:
        if self.rebinder is None:
            raise RuntimeError("ReplaySession is not open")
        self.rebinder.observe_response(response)

    def receive(self) -> bytes:
        if self.sock is None:
            raise RuntimeError("ReplaySession is not open")
        return read_protocol_available(self.sock, self.read_timeout_sec, self.idle_timeout_sec)

    def send(self, wire: bytes) -> None:
        if self.sock is None:
            raise RuntimeError("ReplaySession is not open")
        send_all(self.sock, wire, timeout_sec=self.send_timeout_sec)

    def exchange(self, wire: bytes) -> bytes:
        self.send(wire)
        response = self.receive()
        self.observe_response(response)
        return response

    def replay_setup(
        self,
        setup_end: int,
        *,
        frame_fn: Callable[[int, bytes], bytes] | None = None,
    ) -> int:
        last_seq = 0
        for index in range(0, setup_end + 1):
            frame = self.manager_chunks[index]
            if frame_fn is not None:
                frame = frame_fn(index, frame)
            wire = self.apply(frame)
            self.exchange(wire)
            last_seq = max(last_seq, frame_seq(wire))
        self.next_seq = last_seq + 1
        return self.next_seq

    def replay_indices(
        self,
        indices: range | list[int] | tuple[int, ...],
        *,
        frame_fn: Callable[[int, bytes, int], bytes] | None = None,
    ) -> list[tuple[int, bytes]]:
        responses: list[tuple[int, bytes]] = []
        for index in indices:
            wire = self.apply(self.manager_chunks[index])
            if frame_fn is not None:
                wire = frame_fn(index, wire, self.next_seq)
            response = self.exchange(wire)
            responses.append((index, response))
        return responses

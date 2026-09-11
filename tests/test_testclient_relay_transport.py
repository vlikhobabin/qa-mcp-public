from __future__ import annotations

import socket
import threading
from collections.abc import Callable
from pathlib import Path

import pytest

from qa_mcp.config import Settings, activate_application_settings
from qa_mcp.protocol import foreground, native_mutation, native_write, native_xtest
from qa_mcp.protocol import lifecycle
from qa_mcp.protocol.replay import ReplaySession
from qa_mcp.protocol.session import TestClientSession
from qa_mcp.protocol.transport import (
    RELAY_ENDPOINT_ENV,
    RELAY_TOKEN_ENV,
    RELAY_PREFACE,
    RelayAuthenticationError,
    RelayConfigurationError,
    connect_testclient,
    relay_listener_reachable,
)


def _server(handler: Callable[[socket.socket], None]) -> tuple[socket.socket, int, threading.Thread]:
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]

    def run() -> None:
        try:
            connection, _ = listener.accept()
            with connection:
                handler(connection)
        finally:
            listener.close()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return listener, port, thread


def test_relay_connector_authenticates_only_the_exact_endpoint() -> None:
    observed: list[bytes] = []

    def relay(connection: socket.socket) -> None:
        observed.append(connection.recv(1024))
        connection.sendall(b"OK\n")
        observed.append(connection.recv(16))
        connection.sendall(b"reply")

    _, port, thread = _server(relay)
    env = {
        RELAY_ENDPOINT_ENV: f"127.0.0.1:{port}",
        RELAY_TOKEN_ENV: "relay-secret",
    }
    with connect_testclient(("127.0.0.1", port), timeout=2, env=env) as connection:
        connection.sendall(b"payload")
        assert connection.recv(16) == b"reply"
    thread.join(timeout=2)

    assert observed == [b"QA-MCP-TESTCLIENT-RELAY/1 relay-secret\n", b"payload"]


def test_direct_connector_sends_no_preface_when_relay_is_absent_or_different() -> None:
    observed: list[bytes] = []

    def direct(connection: socket.socket) -> None:
        observed.append(connection.recv(16))
        connection.sendall(b"direct")

    _, port, thread = _server(direct)
    env = {
        RELAY_ENDPOINT_ENV: "127.0.0.1:65530",
        RELAY_TOKEN_ENV: "relay-secret",
    }
    with connect_testclient(("127.0.0.1", port), timeout=2, env=env) as connection:
        connection.sendall(b"payload")
        assert connection.recv(16) == b"direct"
    thread.join(timeout=2)

    assert observed == [b"payload"]


def test_relay_listener_probe_sends_no_preface_or_target_payload() -> None:
    observed: list[bytes] = []

    def relay(connection: socket.socket) -> None:
        observed.append(connection.recv(16))

    _, port, thread = _server(relay)
    env = {
        RELAY_ENDPOINT_ENV: f"127.0.0.1:{port}",
        RELAY_TOKEN_ENV: "relay-secret",
    }

    assert relay_listener_reachable(("127.0.0.1", port), timeout=2, env=env) is True
    thread.join(timeout=2)

    assert observed == [b""]


@pytest.mark.parametrize(
    "env",
    [
        {RELAY_ENDPOINT_ENV: "127.0.0.1:15382"},
        {RELAY_TOKEN_ENV: "relay-secret"},
    ],
)
def test_partial_relay_configuration_fails_closed_without_secret(env: dict[str, str]) -> None:
    with pytest.raises(RelayConfigurationError) as error:
        connect_testclient(("127.0.0.1", 15382), timeout=0.1, env=env)

    assert "relay-secret" not in str(error.value)


class _FakeRelaySocket:
    def __init__(self, reply: bytes = b"OK\n") -> None:
        self.reply = bytearray(reply)
        self.sent: list[bytes] = []
        self.closed = False
        self.socket_options: list[tuple[object, ...]] = []

    def __enter__(self) -> "_FakeRelaySocket":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def sendall(self, payload: bytes) -> None:
        self.sent.append(payload)

    def recv(self, amount: int) -> bytes:
        if not self.reply:
            return b""
        chunk = bytes(self.reply[:amount])
        del self.reply[:amount]
        return chunk

    def close(self) -> None:
        self.closed = True

    def setsockopt(self, *args: object) -> None:
        self.socket_options.append(args)

    def settimeout(self, _timeout: float) -> None:
        return None


def test_active_application_relay_is_authoritative_over_env_and_keeps_direct_absence(monkeypatch) -> None:
    """The shared connector sees factory scope even when a legacy env is supplied."""

    calls: list[tuple[tuple[str, int], float | None]] = []
    sockets: list[_FakeRelaySocket] = []

    def create(address: tuple[str, int], timeout: float | None = None, **_kwargs: object) -> _FakeRelaySocket:
        calls.append((address, timeout))
        fake = _FakeRelaySocket()
        sockets.append(fake)
        return fake

    monkeypatch.setattr("qa_mcp.protocol.transport.socket.create_connection", create)
    process_relay = {RELAY_ENDPOINT_ENV: "process.example:15382", RELAY_TOKEN_ENV: "process-token"}
    scoped = Settings(
        manager_templates="manager.json",
        value_read_templates="value.json",
        testclient_relay_endpoint="factory.example:15383",
        testclient_relay_token="factory-token",
    )

    with activate_application_settings(scoped):
        connect_testclient(("factory.example", 15383), timeout=1.25, env=process_relay).close()
        connect_testclient(("direct.example", 15384), timeout=2.5, env=process_relay).close()
    with activate_application_settings(Settings(manager_templates="manager.json", value_read_templates="value.json")):
        connect_testclient(("process.example", 15382), timeout=3.0, env=process_relay).close()

    assert calls == [
        (("factory.example", 15383), 1.25),
        (("direct.example", 15384), 2.5),
        (("process.example", 15382), 3.0),
    ]
    assert [sock.sent for sock in sockets] == [
        [f"{RELAY_PREFACE} factory-token\n".encode()],
        [],
        [],
    ]


@pytest.mark.parametrize(
    "endpoint, token",
    [
        ("factory.example:15382", ""),
        ("", "factory-token"),
        ("factory.example:not-a-port", "factory-token"),
        ("factory.example:15382", "line\nbreak"),
    ],
)
def test_invalid_scoped_relay_fails_before_socket_creation(
    monkeypatch, endpoint: str, token: str,
) -> None:
    calls: list[object] = []
    monkeypatch.setattr(
        "qa_mcp.protocol.transport.socket.create_connection",
        lambda *_args, **_kwargs: calls.append(object()),
    )
    settings = Settings(
        manager_templates="manager.json",
        value_read_templates="value.json",
        testclient_relay_endpoint=endpoint,
        testclient_relay_token=token,
    )

    with activate_application_settings(settings), pytest.raises(RelayConfigurationError) as error:
        connect_testclient(("factory.example", 15382), env={RELAY_ENDPOINT_ENV: "process:1", RELAY_TOKEN_ENV: "x"})

    assert calls == []
    if token:
        assert token not in str(error.value)


def test_authentication_refusal_closes_socket_without_peer_or_token_diagnostics(monkeypatch) -> None:
    fake = _FakeRelaySocket(b"NO factory-token hostile-peer-prose\n")
    monkeypatch.setattr("qa_mcp.protocol.transport.socket.create_connection", lambda *_args, **_kwargs: fake)
    settings = Settings(
        manager_templates="manager.json",
        value_read_templates="value.json",
        testclient_relay_endpoint="factory.example:15382",
        testclient_relay_token="factory-token",
    )

    with activate_application_settings(settings), pytest.raises(RelayAuthenticationError) as error:
        connect_testclient(("factory.example", 15382))

    assert fake.closed is True
    assert fake.sent == [f"{RELAY_PREFACE} factory-token\n".encode()]
    assert "factory-token" not in str(error.value)
    assert "hostile-peer-prose" not in str(error.value)


def test_lifecycle_readiness_uses_scoped_listener_only_probe(monkeypatch) -> None:
    calls: list[tuple[tuple[str, int], float | None]] = []
    fake = _FakeRelaySocket()

    def create(address: tuple[str, int], timeout: float | None = None, **_kwargs: object) -> _FakeRelaySocket:
        calls.append((address, timeout))
        return fake

    monkeypatch.setattr("qa_mcp.protocol.transport.socket.create_connection", create)
    settings = Settings(
        manager_templates="manager.json",
        value_read_templates="value.json",
        testclient_relay_endpoint="factory.example:15382",
        testclient_relay_token="factory-token",
    )

    with activate_application_settings(settings):
        assert lifecycle.port_is_listening("factory.example", 15382, timeout_sec=0.25) is True
        assert lifecycle.port_is_listening("direct.example", 15383, timeout_sec=0.25) is True

    assert calls == [(("factory.example", 15382), 0.25), (("direct.example", 15383), 0.25)]
    assert fake.sent == []
    assert fake.closed is True


def test_shared_native_consumers_use_the_active_relay_at_fake_socket_boundary(monkeypatch, tmp_path: Path) -> None:
    """Exercise every shared connector family without a TestClient or mutation."""

    calls: list[tuple[tuple[str, int], float | None]] = []
    sockets: list[_FakeRelaySocket] = []

    def create(address: tuple[str, int], timeout: float | None = None, **_kwargs: object) -> _FakeRelaySocket:
        calls.append((address, timeout))
        fake = _FakeRelaySocket()
        sockets.append(fake)
        return fake

    monkeypatch.setattr("qa_mcp.protocol.transport.socket.create_connection", create)
    monkeypatch.setattr(foreground, "resolve_capture_dir", lambda *_args: tmp_path)
    monkeypatch.setattr(foreground, "_read_chunks", lambda *_args: [])
    monkeypatch.setattr(foreground, "_normalize_data_ref_link", lambda value: value)
    monkeypatch.setattr(native_write, "_read_chunks", lambda *_args: [])
    monkeypatch.setattr(native_xtest, "_read_chunks", lambda *_args: [])
    monkeypatch.setattr(native_xtest, "resolve_capture_dir", lambda *_args: tmp_path)
    settings = Settings(
        manager_templates="manager.json",
        value_read_templates="value.json",
        testclient_relay_endpoint="factory.example:15382",
        testclient_relay_token="factory-token",
    )

    class Display:
        def type_text(self, *_args: object, **_kwargs: object) -> None:
            return None

        def send_keys(self, *_args: object, **_kwargs: object) -> None:
            return None

    with activate_application_settings(settings):
        session = TestClientSession(host="factory.example", port=15382, connect_timeout_sec=1.0)
        session.connect()
        session.close()
        with ReplaySession([], [], host="factory.example", port=15382, connect_timeout_sec=2.0):
            pass
        foreground_socket = foreground.foreground_form_by_link(
            "safe-link", host="factory.example", port=15382, connect_timeout_sec=3.0,
        )
        assert foreground_socket is not None
        foreground_socket.close()
        with native_write._open_replay_session(
            tmp_path, host="factory.example", port=15382,
            read_timeout_sec=0.1, idle_timeout_sec=0.1, connect_timeout_sec=4.0,
        ):
            pass
        native_mutation.run_replay_with_renderers(
            host="factory.example", port=15382, manager_chunks=[], client_chunks=[], renderers={},
            connect_timeout_sec=5.0, read_timeout_sec=0.1, idle_timeout_sec=0.1,
        )
        native_xtest.write_form_value_xtest(
            tmp_path, "value", "field", host="factory.example", port=15382,
            settle_sec=0, display_backend=Display(),
        )

    assert [address for address, _timeout in calls] == [("factory.example", 15382)] * 6
    assert [timeout for _address, timeout in calls] == [1.0, 2.0, 3.0, 4.0, 5.0, 15.0]
    assert all(sock.sent == [f"{RELAY_PREFACE} factory-token\n".encode()] for sock in sockets)
    assert all(sock.closed for sock in sockets)

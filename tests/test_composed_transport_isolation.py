"""Factory-bound transport isolation regressions (all external boundaries are fake)."""

from __future__ import annotations

import asyncio
import os
import threading
from pathlib import Path
from typing import Any

import pytest

from qa_mcp import mcp_server
from qa_mcp.config import Settings, active_application_settings
from qa_mcp.core import bind_application_context, current_application_context
from qa_mcp.protocol import foreground, native_mutation, native_write, native_xtest
from qa_mcp.protocol import transport
from qa_mcp.protocol.replay import ReplaySession
from qa_mcp.protocol.session import TestClientSession


class _Socket:
    def __init__(self, reply: bytes = b"OK\n") -> None:
        self.reply = bytearray(reply)
        self.sent: list[bytes] = []
        self.closed = False

    def __enter__(self) -> "_Socket":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def sendall(self, payload: bytes) -> None:
        self.sent.append(payload)

    def recv(self, count: int) -> bytes:
        result = bytes(self.reply[:count])
        del self.reply[:count]
        return result

    def close(self) -> None:
        self.closed = True

    def setsockopt(self, *_args: object) -> None:
        pass

    def settimeout(self, _timeout: float) -> None:
        pass


class _Display:
    def type_text(self, *_args: object, **_kwargs: object) -> None:
        pass

    def send_keys(self, *_args: object, **_kwargs: object) -> None:
        pass


@pytest.fixture
def fake_native_boundaries(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[list[tuple[tuple[str, int], float | None]], list[_Socket]]:
    """Keep the real protocol consumers while stopping at sockets/captures/display."""

    calls: list[tuple[tuple[str, int], float | None]] = []
    sockets: list[_Socket] = []

    def create(address: tuple[str, int], timeout: float | None = None, **_kwargs: object) -> _Socket:
        sock = _Socket()
        settings = active_application_settings()
        sock.owner = settings.manager_templates if settings is not None else "unbound"
        calls.append((address, timeout))
        sockets.append(sock)
        return sock

    monkeypatch.setattr(transport.socket, "create_connection", create)
    monkeypatch.setattr(foreground, "resolve_capture_dir", lambda *_args: tmp_path)
    monkeypatch.setattr(foreground, "_read_chunks", lambda *_args: [])
    monkeypatch.setattr(foreground, "_normalize_data_ref_link", lambda value: value)
    monkeypatch.setattr(native_write, "_read_chunks", lambda *_args: [])
    monkeypatch.setattr(native_xtest, "_read_chunks", lambda *_args: [])
    monkeypatch.setattr(native_xtest, "resolve_capture_dir", lambda *_args: tmp_path)
    return calls, sockets


def _settings(name: str, endpoint: str = "", token: str = "") -> Settings:
    return Settings(
        manager_templates=f"{name}-manager.json",
        value_read_templates=f"{name}-value.json",
        remote_client=True,
        testclient_relay_endpoint=endpoint,
        testclient_relay_token=token,
    )


def _attachment(name: str, host: str, port: int) -> Any:
    return mcp_server._AttachedTestClientContext(  # noqa: SLF001 - actual attachment listener seam
        host=host,
        port=port,
        attached_at=1.0,
        status={"host_agent": {"ok": True, "alive": True, "listening": True}, "owner": name},
    )


def test_real_factories_isolate_every_native_consumer_and_bound_absence(
    monkeypatch: pytest.MonkeyPatch,
    fake_native_boundaries: tuple[list[tuple[tuple[str, int], float | None]], list[_Socket]],
    tmp_path: Path,
) -> None:
    """C1/C3: factory Settings own every shared native connector, never process relay state."""

    calls, sockets = fake_native_boundaries
    monkeypatch.setenv(transport.RELAY_ENDPOINT_ENV, "process.invalid:15499")
    monkeypatch.setenv(transport.RELAY_TOKEN_ENV, "process-token")
    before_environment = dict(os.environ)
    attachments: dict[str, Any] = {}

    def native_family(family: str, host: str, port: int) -> dict[str, object]:
        context = current_application_context()
        settings = active_application_settings()
        assert settings is context.settings
        assert context.attachment is attachments[settings.manager_templates]
        if family == "session":
            session = TestClientSession(host=host, port=port, connect_timeout_sec=1.0)
            session.connect()
            session.close()
        elif family == "replay":
            with ReplaySession([], [], host=host, port=port, connect_timeout_sec=2.0):
                pass
        elif family == "foreground":
            sock = foreground.foreground_form_by_link("safe-link", host=host, port=port, connect_timeout_sec=3.0)
            assert sock is not None
            sock.close()
        elif family == "native_write":
            with native_write._open_replay_session(  # noqa: SLF001 - shared native-write consumer
                tmp_path, host=host, port=port, read_timeout_sec=0.1, idle_timeout_sec=0.1, connect_timeout_sec=4.0,
            ):
                pass
        elif family == "native_mutation":
            native_mutation.run_replay_with_renderers(
                host=host, port=port, manager_chunks=[], client_chunks=[], renderers={}, connect_timeout_sec=5.0,
                read_timeout_sec=0.1, idle_timeout_sec=0.1,
            )
        elif family == "native_xtest":
            native_xtest.write_form_value_xtest(
                tmp_path, "value", "field", host=host, port=port, settle_sec=0, display_backend=_Display(),
            )
        elif family == "attachment_listener":
            assert mcp_server._attached_endpoint_is_listening(context.attachment) is True  # noqa: SLF001 - actual attachment path
        else:
            raise AssertionError(f"unknown family {family}")
        return {"factory": settings.manager_templates, "family": family}

    def low_level_mapping(host: str, port: int) -> None:
        # A factory-dispatched legacy mapping cannot override its active Settings.
        transport.connect_testclient(
            (host, port), timeout=6.0,
            env={transport.RELAY_ENDPOINT_ENV: "mapping.invalid:15498", transport.RELAY_TOKEN_ENV: "mapping-token"},
        ).close()

    def relay_readiness(host: str, port: int) -> dict[str, bool]:
        context = current_application_context()
        assert active_application_settings() is context.settings
        assert context.attachment is attachments[context.settings.manager_templates]
        return {"ready": transport.relay_listener_reachable((host, port), timeout=0.75)}

    async def interleaved_session(host: str, port: int) -> dict[str, str]:
        await asyncio.sleep(0)
        context = current_application_context()
        settings = active_application_settings()
        assert settings is context.settings
        assert context.attachment is attachments[settings.manager_templates]
        session = TestClientSession(host=host, port=port, connect_timeout_sec=9.0)
        session.connect()
        session.close()
        return {"endpoint": settings.testclient_relay_endpoint}

    factories = {
        "a": mcp_server.create_mcp_server(
            settings=_settings("a", "a.example:15382", "a-token"),
            extra_tools={
                "native_family": native_family, "low_level_mapping": low_level_mapping, "relay_readiness": relay_readiness,
                "interleaved_session": interleaved_session,
            },
        ),
        "b": mcp_server.create_mcp_server(
            settings=_settings("b", "b.example:15383", "b-token"),
            extra_tools={
                "native_family": native_family, "low_level_mapping": low_level_mapping, "relay_readiness": relay_readiness,
                "interleaved_session": interleaved_session,
            },
        ),
        "absent": mcp_server.create_mcp_server(
            settings=_settings("absent"),
            extra_tools={
                "native_family": native_family, "low_level_mapping": low_level_mapping, "relay_readiness": relay_readiness,
                "interleaved_session": interleaved_session,
            },
        ),
    }
    addresses = {"a": ("a.example", 15382), "b": ("b.example", 15383), "absent": ("direct.example", 15384)}
    for name, server in factories.items():
        context = mcp_server.application_context(server)
        context.attachment = _attachment(name, *addresses[name])
        attachments[context.settings.manager_templates] = context.attachment

    def assert_batch(start: int, family: str, expected: list[tuple[Any, ...]]) -> None:
        # Each batch is a consumer invocation per owner, never an aggregate auth count.
        actual = [
            (sock.owner, address, timeout, tuple(sock.sent), sock.closed)
            for (address, timeout), sock in zip(calls[start:], sockets[start:], strict=True)
        ]
        assert sorted(actual) == sorted(expected), (family, actual, expected)

    def observation(name: str, address: tuple[str, int], timeout: float, *, auth: bool) -> tuple[Any, ...]:
        preface = (f"{transport.RELAY_PREFACE} {name}-token\n".encode(),) if auth else ()
        return (f"{name}-manager.json", address, timeout, preface, True)

    async def invoke_matrix() -> None:
        timeouts = {
            "session": 1.0, "replay": 2.0, "foreground": 3.0, "native_write": 4.0,
            "native_mutation": 5.0, "native_xtest": 15.0, "attachment_listener": 0.5,
        }
        for family, timeout in timeouts.items():
            start = len(calls)
            results = await asyncio.gather(*(
                factories[name].call_tool("native_family", {"family": family, "host": host, "port": port})
                for name, (host, port) in addresses.items()
            ))
            assert [result.structured_content["factory"] for result in results] == [
                "a-manager.json", "b-manager.json", "absent-manager.json",
            ]
            assert_batch(start, family, [
                observation(name, address, timeout, auth=name != "absent" and family != "attachment_listener")
                for name, address in addresses.items()
            ])

    asyncio.run(invoke_matrix())

    async def interleave() -> list[dict[str, str]]:
        results = await asyncio.gather(
            factories["a"].call_tool("interleaved_session", {"host": "a.example", "port": 15382}),
            factories["b"].call_tool("interleaved_session", {"host": "b.example", "port": 15383}),
        )
        return [result.structured_content for result in results]

    start = len(calls)
    assert asyncio.run(interleave()) == [{"endpoint": "a.example:15382"}, {"endpoint": "b.example:15383"}]
    assert_batch(start, "interleaved_session", [
        observation(name, addresses[name], 9.0, auth=True) for name in ("a", "b")
    ])
    for name, address, ready in (
        ("a", addresses["a"], True), ("b", addresses["b"], True),
        ("a", ("not-the-relay.example", 15388), False), ("absent", addresses["absent"], False),
    ):
        start = len(calls)
        assert asyncio.run(factories[name].call_tool(
            "relay_readiness", {"host": address[0], "port": address[1]},
        )).structured_content == {"ready": ready}
        assert_batch(start, "relay_readiness", [observation(name, address, 0.75, auth=False)] if ready else [])

    for name, address, auth in (
        ("a", addresses["a"], True), ("b", addresses["b"], True),
        ("a", ("other-direct.example", 15385), False),
        ("absent", ("absent-direct.example", 15386), False),
    ):
        start = len(calls)
        asyncio.run(factories[name].call_tool("low_level_mapping", {"host": address[0], "port": address[1]}))
        assert_batch(start, "low_level_mapping", [observation(name, address, 6.0, auth=auth)])
    assert dict(os.environ) == before_environment


@pytest.mark.parametrize(
    ("endpoint", "token"),
    [
        ("partial.example:15382", ""),
        ("", "partial-token"),
        ("bad.example:not-a-port", "bad-token"),
        ("unsafe.example:15382", "line\nbreak"),
    ],
)
def test_factory_scoped_invalid_relay_never_falls_back_or_opens_socket(
    monkeypatch: pytest.MonkeyPatch, endpoint: str, token: str,
) -> None:
    """C2: invalid Settings fail in real factory dispatch before the fake socket boundary."""

    monkeypatch.setenv(transport.RELAY_ENDPOINT_ENV, "process.invalid:15499")
    monkeypatch.setenv(transport.RELAY_TOKEN_ENV, "process-token")
    opened: list[object] = []
    monkeypatch.setattr(transport.socket, "create_connection", lambda *_args, **_kwargs: opened.append(object()))

    def actual_session() -> None:
        TestClientSession(host="partial.example", port=15382).connect()

    server = mcp_server.create_mcp_server(
        settings=_settings("invalid", endpoint, token), extra_tools={"actual_session": actual_session},
    )
    with pytest.raises(Exception) as error:
        asyncio.run(server.call_tool("actual_session", {}))

    assert opened == []
    assert "process-token" not in str(error.value)
    if token:
        assert token not in str(error.value)


def test_factory_refusal_closes_before_protocol_and_hides_peer_or_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """C2: real factory dispatch retains bounded refusal cleanup at the shared connector."""

    monkeypatch.setenv(transport.RELAY_ENDPOINT_ENV, "process.invalid:15499")
    monkeypatch.setenv(transport.RELAY_TOKEN_ENV, "process-token")
    refused = _Socket(b"NO factory-token hostile-peer-prose\n")
    monkeypatch.setattr(transport.socket, "create_connection", lambda *_args, **_kwargs: refused)

    def actual_session() -> None:
        TestClientSession(host="factory.example", port=15382).connect()

    server = mcp_server.create_mcp_server(
        settings=_settings("refusal", "factory.example:15382", "factory-token"),
        extra_tools={"actual_session": actual_session},
    )
    with pytest.raises(Exception) as error:
        asyncio.run(server.call_tool("actual_session", {}))

    assert refused.closed is True
    assert refused.sent == [f"{transport.RELAY_PREFACE} factory-token\n".encode()]
    assert "factory-token" not in str(error.value)
    assert "hostile-peer-prose" not in str(error.value)


def test_nested_factory_failure_restores_a_native_transport_attachment_and_worker_scope(
    monkeypatch: pytest.MonkeyPatch,
    fake_native_boundaries: tuple[list[tuple[tuple[str, int], float | None]], list[_Socket]],
) -> None:
    """C4: B connects then fails; A reconnects immediately and a bound sync worker stays A."""

    calls, sockets = fake_native_boundaries
    monkeypatch.setenv(transport.RELAY_ENDPOINT_ENV, "process.invalid:15499")
    monkeypatch.setenv(transport.RELAY_TOKEN_ENV, "process-token")
    before_environment = dict(os.environ)
    main_thread = threading.get_ident()
    caller = current_application_context()
    caller_settings = active_application_settings()

    def connect_for_active() -> tuple[int, str, Any]:
        context = current_application_context()
        settings = active_application_settings()
        assert settings is context.settings
        endpoint = settings.testclient_relay_endpoint
        host, raw_port = endpoint.rsplit(":", 1)
        session = TestClientSession(host=host, port=int(raw_port), connect_timeout_sec=7.0)
        session.connect()
        session.close()
        return threading.get_ident(), endpoint, context.attachment

    async def fail_after_native_b() -> None:
        _thread, endpoint, attachment = connect_for_active()
        assert endpoint == "b.example:15383"
        assert attachment is b_attachment
        await asyncio.sleep(0)
        raise RuntimeError("B after native connection")

    b = mcp_server.create_mcp_server(
        settings=_settings("b", "b.example:15383", "b-token"), extra_tools={"fail_after_native_b": fail_after_native_b},
    )
    b_context = mcp_server.application_context(b)
    b_attachment = _attachment("b", "b.example", 15383)
    b_context.attachment = b_attachment

    a = mcp_server.create_mcp_server(
        settings=_settings("a", "a.example:15382", "a-token"), extra_tools={},
    )
    a_context = mcp_server.application_context(a)
    a_attachment = _attachment("a", "a.example", 15382)
    a_context.attachment = a_attachment
    bound_worker = bind_application_context(connect_for_active, a_context)

    async def outer_a() -> dict[str, object]:
        assert current_application_context() is a_context
        assert active_application_settings() is a_context.settings
        with pytest.raises(Exception, match="B after native connection"):
            await b.call_tool("fail_after_native_b", {})
        assert current_application_context() is a_context
        assert active_application_settings() is a_context.settings
        assert a_context.attachment is a_attachment and b_context.attachment is b_attachment
        resumed = connect_for_active()
        worker = await asyncio.to_thread(bound_worker)
        return {"resumed": resumed, "worker": worker}

    result = asyncio.run(bind_application_context(outer_a, a_context)())
    assert result["resumed"][1:] == ("a.example:15382", a_attachment)
    assert result["worker"][0] != main_thread
    assert result["worker"][1:] == ("a.example:15382", a_attachment)
    assert calls == [
        (("b.example", 15383), 7.0), (("a.example", 15382), 7.0), (("a.example", 15382), 7.0),
    ]
    assert [sock.sent for sock in sockets] == [
        [f"{transport.RELAY_PREFACE} b-token\n".encode()],
        [f"{transport.RELAY_PREFACE} a-token\n".encode()],
        [f"{transport.RELAY_PREFACE} a-token\n".encode()],
    ]
    assert all(sock.closed for sock in sockets)
    assert a_context.attachment is a_attachment and b_context.attachment is b_attachment
    assert current_application_context() is caller
    assert active_application_settings() is caller_settings
    assert dict(os.environ) == before_environment

    # Unbound explicit legacy mapping remains a separate, compatible adapter.
    legacy = {transport.RELAY_ENDPOINT_ENV: "legacy.example:15387", transport.RELAY_TOKEN_ENV: "legacy-token"}
    transport.connect_testclient(("legacy.example", 15387), timeout=8.0, env=legacy).close()
    assert calls[-1] == (("legacy.example", 15387), 8.0)
    assert sockets[-1].sent == [f"{transport.RELAY_PREFACE} legacy-token\n".encode()]
    transport.connect_testclient(("process.invalid", 15499), timeout=9.0).close()
    assert calls[-1] == (("process.invalid", 15499), 9.0)
    assert sockets[-1].sent == [f"{transport.RELAY_PREFACE} process-token\n".encode()]


@pytest.mark.parametrize("endpoint", [
    "https://relay.example:15382", "relay.example/path:15382", "user@relay.example:15382",
    "bad host:15382", "bad\\host:15382", "[not-ip]:15382", "[2001:db8::zz]:15382",
    "bad..host:15382", "-bad.host:15382", "bad.host?secret:15382", "bad#host:15382",
    "bad\x7fhost:15382",
])
@pytest.mark.parametrize("destination", ["configured", "different-direct"])
@pytest.mark.parametrize("consumer", ["session", "listener"])
def test_factory_malformed_relay_host_fails_before_any_destination(
    monkeypatch: pytest.MonkeyPatch, endpoint: str, destination: str, consumer: str,
) -> None:
    """F1/C2: malformed relay settings cannot allow even a different direct route."""

    monkeypatch.setenv(transport.RELAY_ENDPOINT_ENV, "process.example:15499")
    monkeypatch.setenv(transport.RELAY_TOKEN_ENV, "process-token")
    before_environment = dict(os.environ)
    opened: list[tuple[Any, ...]] = []

    def create(*args: Any, **kwargs: Any) -> _Socket:
        opened.append((args, kwargs))
        return _Socket()

    monkeypatch.setattr(transport.socket, "create_connection", create)
    host = endpoint.rsplit(":", 1)[0]
    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]
    address = (host, 15382) if destination == "configured" else ("direct.example", 15400)

    def probe() -> None:
        if consumer == "session":
            session = TestClientSession(host=address[0], port=address[1])
            session.connect()
            session.close()
        else:
            transport.relay_listener_reachable(address, timeout=0.25)

    server = mcp_server.create_mcp_server(
        settings=_settings("malformed-host", endpoint, "synthetic-secret-token"),
        extra_tools={"invalid_host_probe": probe},
    )
    with pytest.raises(Exception, match="TestClient relay endpoint has an invalid host") as error:
        asyncio.run(server.call_tool("invalid_host_probe", {}))
    assert opened == []
    assert len(str(error.value)) < 256
    assert "synthetic-secret-token" not in str(error.value)
    assert "process-token" not in str(error.value)
    assert endpoint not in str(error.value)
    assert dict(os.environ) == before_environment


@pytest.mark.parametrize("endpoint, address", [
    ("relay.example:15382", ("relay.example", 15382)),
    ("localhost:15382", ("localhost", 15382)),
    ("127.0.0.1:15382", ("127.0.0.1", 15382)),
    ("[::1]:15382", ("::1", 15382)),
    ("[fe80::1%eth0]:15382", ("fe80::1%eth0", 15382)),
    ("2001:db8::1:15382", ("2001:db8::1", 15382)),
    ("test_client:15382", ("test_client", 15382)),
    ("münchen.example:15382", ("münchen.example", 15382)),
    ("relay.example.:15382", ("relay.example.", 15382)),
])
def test_factory_supported_relay_host_syntax_preserves_exact_endpoint(
    fake_native_boundaries: tuple[list[tuple[tuple[str, int], float | None]], list[_Socket]],
    endpoint: str, address: tuple[str, int],
) -> None:
    """F1/C3: local syntax validation preserves the supported host/IP spelling."""

    calls, sockets = fake_native_boundaries

    def probe() -> None:
        session = TestClientSession(host=address[0], port=address[1], connect_timeout_sec=0.25)
        session.connect()
        session.close()

    server = mcp_server.create_mcp_server(
        settings=_settings("valid-host", endpoint, "valid-token"), extra_tools={"valid_host_probe": probe},
    )
    asyncio.run(server.call_tool("valid_host_probe", {}))
    assert calls == [(address, 0.25)]
    assert len(sockets) == 1 and sockets[0].closed
    assert sockets[0].sent == [f"{transport.RELAY_PREFACE} valid-token\n".encode()]

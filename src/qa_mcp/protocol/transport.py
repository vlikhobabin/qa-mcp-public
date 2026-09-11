"""Shared socket connect/receive helpers for the native TestClient protocol."""

from __future__ import annotations

import ipaddress
import re
import socket
import time
from collections.abc import Mapping

from ..config import (
    TESTCLIENT_RELAY_ENDPOINT_ENV,
    TESTCLIENT_RELAY_TOKEN_ENV,
    active_application_settings,
)
from .frames import TAIL_MARKER


RELAY_ENDPOINT_ENV = TESTCLIENT_RELAY_ENDPOINT_ENV
RELAY_TOKEN_ENV = TESTCLIENT_RELAY_TOKEN_ENV
RELAY_PREFACE = "QA-MCP-TESTCLIENT-RELAY/1"
RELAY_MAX_REPLY = 64


class RelayConfigurationError(ValueError):
    """Relay runtime settings are incomplete or malformed."""


class RelayAuthenticationError(ConnectionError):
    """The configured relay refused its bounded authentication preface."""


def _validate_relay_host(host: str, *, bracketed: bool) -> None:
    """Validate host syntax locally without resolving or normalizing the endpoint."""

    try:
        if not host or any(char.isspace() or ord(char) < 32 or ord(char) == 127
                           or char in "/\\?#@[]" for char in host):
            raise ValueError
        if bracketed or ":" in host:
            ipaddress.IPv6Address(host)
        else:
            # Preserve ordinary DNS/container names, IDNA and a trailing DNS dot.
            ascii_host = host.encode("idna").decode("ascii").removesuffix(".")
            if len(ascii_host) > 253 or any(
                not re.fullmatch(r"[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?", label)
                for label in ascii_host.split(".")
            ):
                raise ValueError
    except ValueError:
        raise RelayConfigurationError("TestClient relay endpoint has an invalid host") from None


def _parse_endpoint(value: str) -> tuple[str, int]:
    endpoint = value.strip()
    if endpoint.startswith("["):
        close = endpoint.find("]")
        if close < 0 or close + 1 >= len(endpoint) or endpoint[close + 1] != ":":
            raise RelayConfigurationError("TestClient relay endpoint must be host:port")
        host, raw_port = endpoint[1:close], endpoint[close + 2 :]
    else:
        try:
            host, raw_port = endpoint.rsplit(":", 1)
        except ValueError as exc:
            raise RelayConfigurationError("TestClient relay endpoint must be host:port") from exc
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise RelayConfigurationError("TestClient relay endpoint has an invalid port") from exc
    if not host or not 1 <= port <= 65535:
        raise RelayConfigurationError("TestClient relay endpoint must contain a valid host and port")
    _validate_relay_host(host, bracketed=endpoint.startswith("["))
    return host, port


def _relay_token(value: str) -> str:
    """Return a relay token only when it is safe to put in the ASCII preface."""

    token = value.strip()
    if not token or not token.isascii() or any(char.isspace() or ord(char) < 32 for char in token):
        raise RelayConfigurationError("TestClient relay token is invalid")
    return token


def relay_configuration(env: Mapping[str, str] | None = None) -> tuple[tuple[str, int], str] | None:
    """Resolve relay settings, preferring the active composed application.

    The active Settings binding deliberately distinguishes an application that
    configured no relay from an unbound low-level call.  A low-level mapping is
    therefore a legacy adapter only; it cannot override a composed call.
    """

    settings = active_application_settings()
    if settings is not None:
        endpoint = settings.testclient_relay_endpoint.strip()
        token = settings.testclient_relay_token.strip()
    else:
        import os

        values = os.environ if env is None else env
        endpoint = values.get(RELAY_ENDPOINT_ENV, "").strip()
        token = values.get(RELAY_TOKEN_ENV, "").strip()
    if bool(endpoint) != bool(token):
        raise RelayConfigurationError("TestClient relay endpoint and token must be configured together")
    if not endpoint:
        return None
    return _parse_endpoint(endpoint), _relay_token(token)


def _read_relay_reply(sock: socket.socket) -> bytes:
    reply = bytearray()
    while len(reply) <= RELAY_MAX_REPLY:
        chunk = sock.recv(1)
        if not chunk:
            break
        reply.extend(chunk)
        if chunk == b"\n":
            break
    return bytes(reply)


def connect_testclient(
    address: tuple[str, int],
    timeout: float | None = None,
    source_address: tuple[str, int] | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> socket.socket:
    """Connect directly, or authenticate the exact configured host-agent relay."""

    relay = relay_configuration(env)
    sock = socket.create_connection(address, timeout=timeout, source_address=source_address)
    if relay is None or address != relay[0]:
        return sock
    try:
        sock.sendall(f"{RELAY_PREFACE} {relay[1]}\n".encode("ascii"))
        reply = _read_relay_reply(sock)
        if reply != b"OK\n":
            # Relay replies are untrusted and may echo credentials.  Keep the
            # public error locally controlled while retaining the socket cleanup.
            raise RelayAuthenticationError("TestClient relay authentication failed")
        return sock
    except Exception:
        sock.close()
        raise


def relay_listener_reachable(
    address: tuple[str, int],
    timeout: float | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> bool:
    """Probe only the configured relay listener without opening its target.

    A normal authenticated relay connection consumes the Windows TestClient's
    single-manager accept state even when the caller only wants a readiness
    check.  Connecting and closing before the auth preface proves the container
    route while the host-agent launch result remains the target-readiness proof.
    Direct TestClient endpoints are intentionally not accepted here.
    """

    relay = relay_configuration(env)
    if relay is None or address != relay[0]:
        return False
    try:
        with socket.create_connection(address, timeout=timeout):
            return True
    except OSError:
        return False


def read_protocol_available(
    sock: socket.socket,
    first_timeout_sec: float,
    idle_timeout_sec: float,
    *,
    tail_marker: bytes = TAIL_MARKER,
) -> bytes:
    """Drain one protocol response from ``sock``.

    The TestClient protocol terminates normal frames with ``TAIL_MARKER``. Older
    callers treated the first idle gap as the response boundary, which split
    slow responses. This helper keeps reading until the tail is seen or a hard
    monotonic deadline expires, using the idle timeout only as the per-recv wait
    once data has started arriving.
    """

    buffer = bytearray()
    deadline = time.monotonic() + max(0.0, first_timeout_sec)

    while True:
        if tail_marker and tail_marker in buffer:
            break

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break

        timeout = min(idle_timeout_sec, remaining) if buffer else remaining
        if timeout <= 0:
            break

        sock.settimeout(timeout)
        try:
            payload = sock.recv(65536)
        except socket.timeout:
            continue
        if not payload:
            break
        buffer.extend(payload)

    return bytes(buffer)

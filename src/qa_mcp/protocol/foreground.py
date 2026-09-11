"""Protocol-owned foreground/open replay helpers."""

from __future__ import annotations

import socket
import time
from pathlib import Path
from typing import Any, Callable

from . import resolve_capture_dir
from .bootstrap_synth import SYNTH_TEMPLATE_VERSION, resolve_synth_platform_version
from .frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT
from .introspection import _normalize_data_ref_link, _repo_root
from .native_mutation import GuidRebinder, _read_available
from .native_write import _read_chunks, retarget_list_read_frame
from .transport import connect_testclient

_FOREGROUND_CAPTURE = "listform-read"
_FOREGROUND_CAPTURE_NAV = "e1cib/list/Справочник.Товары"


def foreground_form_by_link(
    open_link: str,
    *,
    host: str,
    port: int,
    read_timeout_sec: float = 6.0,
    idle_timeout_sec: float = 1.5,
    connect_timeout_sec: float = 10.0,
    max_total_sec: float = 30.0,
    allow_partial: bool = False,
    repo_root: Path | None = None,
) -> Any:
    """Open a form by nav link to the foreground and return the held manager socket."""
    nav_link = _normalize_data_ref_link(open_link)
    cap = resolve_capture_dir(_FOREGROUND_CAPTURE, repo_root or _repo_root())
    mgr = _read_chunks(cap, MANAGER_TO_CLIENT)
    cli = _read_chunks(cap, CLIENT_TO_MANAGER)

    live_ver = resolve_synth_platform_version()
    ver_old = SYNTH_TEMPLATE_VERSION.encode("ascii")
    ver_new = live_ver.encode("ascii") if live_ver and live_ver != SYNTH_TEMPLATE_VERSION else None
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    sock = connect_testclient((host, port), timeout=connect_timeout_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    started = time.monotonic()

    def read_bounded() -> bytes:
        remaining = max_total_sec - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError(f"foreground replay timed out for {nav_link!r}")
        return _read_available(sock, min(read_timeout_sec, remaining), min(idle_timeout_sec, remaining))

    try:
        rebinder.observe_response(read_bounded())
    except TimeoutError:
        sock.close()
        return None
    for frame in mgr:
        retargeted = retarget_list_read_frame(
            frame,
            old_nav=_FOREGROUND_CAPTURE_NAV,
            new_nav=nav_link,
            old_col_block=b"",
            new_col_block=b"",
        )
        if ver_new is not None:
            retargeted = retargeted.replace(ver_old, ver_new)
        wire = rebinder.apply(retargeted)
        try:
            sock.sendall(wire)
        except OSError:
            sock.close()
            return None
        try:
            rebinder.observe_response(read_bounded())
        except TimeoutError:
            if allow_partial:
                return sock
            sock.close()
            return None
    return sock


def open_bare_create_form_for_write(
    open_link: str,
    *,
    host: str,
    port: int,
    foreground_form_by_link: Callable[..., Any] = foreground_form_by_link,
) -> tuple[Any | None, dict[str, Any]]:
    """Open a bare create form through foreground replay and return resource metadata."""
    nav_link = _normalize_data_ref_link(open_link)
    meta: dict[str, Any] = {
        "foreground_method": "create_listreplay",
        "normalized_open_link": nav_link,
        "partial_foreground_replay": True,
    }
    try:
        resource = foreground_form_by_link(
            nav_link,
            host=host,
            port=port,
            read_timeout_sec=2.0,
            idle_timeout_sec=0.6,
            max_total_sec=20.0,
            allow_partial=True,
        )
        if resource is None:
            return None, {**meta, "reason": "create foreground replay did not render"}
        return resource, meta
    except Exception as exc:  # noqa: BLE001 - tool result must fail closed
        return None, {
            **meta,
            "error": "create-foreground-failed",
            "reason": f"{type(exc).__name__}: {exc}",
        }

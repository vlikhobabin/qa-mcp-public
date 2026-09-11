"""Card 98 #2 — OS-level window enumeration on the TestClient display.

vanessa-mcp exposes ``get_window_list_os`` (the OS window manager's window list). The capture-free
equivalent enumerates the visible top-level X11 windows on the client's Xvfb display via ``xdotool`` — the
same OS tool the XTEST write hybrid (``native_xtest``) already depends on, so no new dependency. The command
shapes are pure (``_search_argv`` / ``_name_argv`` / ``_geometry_argv``) and the output parsing
(``parse_geometry``) is offline-testable; only ``list_windows`` shells out.

This is the OS-level list (what a window manager sees). The protocol-level "windows known to the test client"
list (vanessa ``get_window_list_testclient``) is a separate, decode-heavy concern (the SecondaryFrame set in
the manager stream) — a follow-up; ``open_card`` / ``close_window`` / ``activate_window`` already address
individual windows by their SecondaryFrame ref.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any, Callable

Runner = Callable[[list[str]], str]


def _xdotool() -> str:
    return shutil.which("xdotool") or "xdotool"


def _search_argv() -> list[str]:
    """xdotool argv that lists the visible top-level windows' ids (one per line). ``--name ""`` matches every
    named window; ``--onlyvisible`` drops unmapped/hidden ones."""
    return [_xdotool(), "search", "--onlyvisible", "--name", ""]


def _name_argv(window_id: str) -> list[str]:
    return [_xdotool(), "getwindowname", str(window_id)]


def _geometry_argv(window_id: str) -> list[str]:
    return [_xdotool(), "getwindowgeometry", "--shell", str(window_id)]


def parse_geometry(shell_output: str) -> dict[str, int]:
    """Parse ``xdotool getwindowgeometry --shell`` output (``KEY=VALUE`` lines: WINDOW/X/Y/WIDTH/HEIGHT/SCREEN)
    into ``{x, y, width, height}``. Missing/non-integer values are skipped (best-effort)."""
    vals: dict[str, int] = {}
    keymap = {"X": "x", "Y": "y", "WIDTH": "width", "HEIGHT": "height"}
    for line in shell_output.splitlines():
        line = line.strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        out_key = keymap.get(key.strip().upper())
        if out_key is None:
            continue
        try:
            vals[out_key] = int(value.strip())
        except ValueError:
            continue
    return vals


def _default_runner(display: str) -> Runner:
    env = {**os.environ, "DISPLAY": display}

    def run(argv: list[str]) -> str:
        proc = subprocess.run(argv, env=env, capture_output=True, timeout=15.0)  # noqa: S603
        return proc.stdout.decode("utf-8", "replace")

    return run


def list_windows(display: str, *, runner: Runner | None = None, geometry: bool = True) -> list[dict[str, Any]]:
    """Enumerate visible top-level X11 windows on ``display`` (OS-level — vanessa ``get_window_list_os`` parity,
    card 98 #2). Returns ``[{id, title, geometry?}]`` in xdotool stacking order. ``runner`` (argv -> stdout) is
    injectable for offline tests; the default shells out to ``xdotool`` with ``DISPLAY=display``. Requires
    xdotool on PATH (raises otherwise) unless a ``runner`` is injected."""
    if runner is None and shutil.which("xdotool") is None:
        raise RuntimeError("xdotool not found on PATH — get_window_list needs it to enumerate OS windows")
    run = runner or _default_runner(display)
    ids = [line.strip() for line in run(_search_argv()).splitlines() if line.strip()]
    windows: list[dict[str, Any]] = []
    for wid in ids:
        entry: dict[str, Any] = {"id": wid, "title": run(_name_argv(wid)).strip()}
        if geometry:
            geo = parse_geometry(run(_geometry_argv(wid)))
            if geo:
                entry["geometry"] = geo
        windows.append(entry)
    return windows

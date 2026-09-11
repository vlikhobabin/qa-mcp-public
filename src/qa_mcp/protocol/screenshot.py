"""OS-level screenshots of the TestClient display (card 85).

v1 captures the client's X display on Linux via ``scrot`` (fallback ImageMagick ``import``); an optional
window title (``xdotool``) targets a single window. Vanessa's own tool is ``get_window_screenshot_os`` — so
OS-level capture is the PARITY mechanism, not a compromise. The display is the one owned by the lifecycle
(`launch_test_client(display=…)` → its `status()["display"]`).

Windows (pywin32 ``PrintWindow``) is a deferred backend — `WindowsGdiBackend` raises NotImplementedError so
the platform dispatch is in place without an unverified implementation on the Linux delivery contour.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

# A runner runs argv (with an env) and returns something with .returncode/.stdout/.stderr — injectable for tests.
Runner = Callable[..., "subprocess.CompletedProcess[bytes]"]

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class ScreenshotError(RuntimeError):
    """Raised when every capture attempt for a display/window fails."""


def _default_runner(argv: list[str], *, env: dict[str, str] | None = None, timeout: float = 30.0):
    return subprocess.run(argv, env=env, capture_output=True, timeout=timeout)  # noqa: S603


def _display_env(display: str) -> dict[str, str]:
    # full environment (PATH etc.) with DISPLAY overridden — a DISPLAY-only env would break PATH lookup
    return {**os.environ, "DISPLAY": display}


@dataclass
class LinuxX11Backend:
    """Capture an X display with the binaries already present in the lab (scrot / ImageMagick import)."""

    name: str = "linux-x11"
    runner: Runner = _default_runner

    def _find_window(self, display: str, title: str) -> str | None:
        """Best-effort: resolve a window-title substring to an X window id via xdotool (works without a WM).
        Returns the LAST match (usually the top-level window) or None."""
        xdotool = shutil.which("xdotool")
        if not xdotool:
            return None
        try:
            res = self.runner([xdotool, "search", "--name", title], env=_display_env(display))
        except (FileNotFoundError, subprocess.SubprocessError):
            return None
        if getattr(res, "returncode", 1) != 0:
            return None
        ids = [tok for tok in (res.stdout or b"").decode(errors="replace").split() if tok.strip()]
        return ids[-1] if ids else None

    def _attempts(self, display: str, out_path: Path, window_id: str | None) -> list[list[str]]:
        """Ordered argv attempts: a window id -> `import -window <id>`; otherwise scrot (root) then import."""
        scrot, import_bin = shutil.which("scrot"), shutil.which("import")
        out = str(out_path)
        attempts: list[list[str]] = []
        if window_id and import_bin:
            attempts.append([import_bin, "-window", window_id, out])
        if scrot:
            attempts.append([scrot, "-o", out])
        if import_bin:
            attempts.append([import_bin, "-window", "root", out])
        return attempts

    def capture(self, display: str, out_path: str | os.PathLike[str], *, window: str | None = None) -> dict[str, Any]:
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            out.unlink()  # avoid a stale file masquerading as a fresh capture
        window_id = self._find_window(display, window) if window else None
        attempts = self._attempts(display, out, window_id)
        if not attempts:
            raise ScreenshotError("no capture tool available (need scrot or ImageMagick `import`)")
        last_err: str | None = None
        for argv in attempts:
            try:
                res = self.runner(argv, env=_display_env(display))
            except (FileNotFoundError, subprocess.SubprocessError) as exc:
                last_err = f"{argv[0]}: {exc}"
                continue
            if getattr(res, "returncode", 1) == 0 and out.exists() and out.stat().st_size > 0:
                return {
                    "path": str(out),
                    "display": display,
                    "window": window,
                    "matched_window_id": window_id,
                    "size_bytes": out.stat().st_size,
                    "backend": self.name,
                    "tool": Path(argv[0]).name,
                }
            stderr = (getattr(res, "stderr", b"") or b"").decode(errors="replace").strip()
            last_err = stderr[:300] or f"{Path(argv[0]).name} rc={getattr(res, 'returncode', None)}"
        raise ScreenshotError(f"all capture attempts failed for display {display}: {last_err}")


@dataclass
class WindowsGdiBackend:
    """Deferred (card 85 scope): pywin32 PrintWindow(hwnd, PW_RENDERFULLCONTENT). Stubbed so the dispatch
    exists; not implemented because Windows is not the active delivery/verification contour."""

    name: str = "windows-gdi"

    def capture(self, display: str, out_path: str | os.PathLike[str], *, window: str | None = None) -> dict[str, Any]:
        raise NotImplementedError(
            "Windows screenshot backend (pywin32 PrintWindow) is deferred — card 85 v1 is Linux X11 only"
        )


def get_backend(platform: str | None = None, *, runner: Runner | None = None):
    """Return the screenshot backend for ``platform`` (default: this host's). Linux -> X11; else -> Windows stub."""
    plat = platform if platform is not None else sys.platform
    if plat.startswith("linux"):
        return LinuxX11Backend(runner=runner or _default_runner)
    return WindowsGdiBackend()


def capture_screenshot(
    display: str,
    out_path: str | os.PathLike[str],
    *,
    window: str | None = None,
    platform: str | None = None,
    runner: Runner | None = None,
) -> dict[str, Any]:
    """Capture a PNG of ``display`` (optionally a single window by title substring) into ``out_path``.
    Returns capture metadata (path / display / tool / size_bytes / matched_window_id)."""
    return get_backend(platform, runner=runner).capture(display, out_path, window=window)

"""Card 85: OS-level screenshot backend — hermetic backend tests with fake tools."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol.screenshot import (  # noqa: E402
    PNG_MAGIC,
    LinuxX11Backend,
    ScreenshotError,
    WindowsGdiBackend,
    capture_screenshot,
    get_backend,
)


@pytest.fixture(autouse=True)
def available_fake_tools(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: f"/fake/bin/{name}" if name in {"scrot", "import", "xdotool"} else None)


class FakeRunner:
    """Stand-in for subprocess.run: xdotool returns canned ids; capture tools (scrot/import) write a fake PNG
    to their last argv element, unless their basename is in ``fail_tools`` (then rc=1, no file)."""

    def __init__(self, *, xdotool_ids: str = "", fail_tools: tuple[str, ...] = ()) -> None:
        self.calls: list[list[str]] = []
        self.xdotool_ids = xdotool_ids
        self.fail_tools = set(fail_tools)

    def __call__(self, argv, *, env=None, timeout=30.0):
        self.calls.append(argv)
        tool = Path(argv[0]).name
        if tool == "xdotool":
            return SimpleNamespace(returncode=0 if self.xdotool_ids else 1,
                                   stdout=self.xdotool_ids.encode(), stderr=b"")
        out = argv[-1]
        if tool in self.fail_tools:
            return SimpleNamespace(returncode=1, stdout=b"", stderr=b"simulated failure")
        Path(out).write_bytes(PNG_MAGIC + b"fake-image-bytes")
        return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

    def tools(self) -> list[str]:
        return [Path(c[0]).name for c in self.calls]


def test_capture_uses_scrot_for_whole_display(tmp_path) -> None:
    runner = FakeRunner()
    out = tmp_path / "shot.png"
    result = capture_screenshot(":99", out, platform="linux", runner=runner)
    assert result["tool"] == "scrot"
    assert result["display"] == ":99"
    assert result["matched_window_id"] is None
    assert result["size_bytes"] > 0 and out.exists()
    assert "scrot" in runner.tools()


def test_capture_falls_back_to_import_when_scrot_fails(tmp_path) -> None:
    runner = FakeRunner(fail_tools=("scrot",))
    result = capture_screenshot(":99", tmp_path / "shot.png", platform="linux", runner=runner)
    assert result["tool"] == "import"
    # scrot was tried first, then import
    assert runner.tools() == ["scrot", "import"]


def test_capture_window_uses_xdotool_then_import(tmp_path) -> None:
    runner = FakeRunner(xdotool_ids="111 222")
    result = capture_screenshot(":99", tmp_path / "w.png", window="Документ", platform="linux", runner=runner)
    assert result["matched_window_id"] == "222"  # last match = top-level
    assert result["tool"] == "import"
    import_call = next(c for c in runner.calls if Path(c[0]).name == "import")
    assert "-window" in import_call and "222" in import_call


def test_capture_raises_when_all_attempts_fail(tmp_path) -> None:
    runner = FakeRunner(fail_tools=("scrot", "import"))
    with pytest.raises(ScreenshotError):
        capture_screenshot(":99", tmp_path / "x.png", platform="linux", runner=runner)


def test_get_backend_dispatch() -> None:
    assert isinstance(get_backend("linux"), LinuxX11Backend)
    assert isinstance(get_backend("win32"), WindowsGdiBackend)
    assert isinstance(get_backend("darwin"), WindowsGdiBackend)  # non-linux -> stub


def test_windows_backend_is_deferred_stub(tmp_path) -> None:
    with pytest.raises(NotImplementedError):
        WindowsGdiBackend().capture(":0", tmp_path / "x.png")

"""Real local display integration; does not launch 1C."""
import shutil
import pytest
from qa_mcp.protocol import lifecycle
from qa_mcp.protocol.screenshot import PNG_MAGIC, capture_screenshot


@pytest.mark.skipif(not (shutil.which("Xvfb") and shutil.which("scrot")), reason="need Xvfb + scrot")
def test_real_capture_against_owned_xvfb(tmp_path) -> None:
    """End-to-end capture path with a REAL Xvfb (no 1C): own a display, screenshot it, assert a real PNG."""
    display = lifecycle.pick_free_display(start=120)
    xvfb_pid = lifecycle._start_xvfb(display, "640x480x24", out_dir=None)
    try:
        out = tmp_path / "real.png"
        result = capture_screenshot(display, out)  # real backend, real scrot
        assert out.exists()
        data = out.read_bytes()
        assert data.startswith(PNG_MAGIC)
        assert result["size_bytes"] == len(data) > 100
        assert result["display"] == display
    finally:
        lifecycle._terminate_group(xvfb_pid, kill_after_sec=3.0)

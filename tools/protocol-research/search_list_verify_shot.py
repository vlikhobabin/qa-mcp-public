#!/usr/bin/env python3
"""Card 97 change 4 — live-verify the dynamic-list SEARCH STRING capture-free, by screenshot (no Vanessa).

Each run boots a FRESH native /TESTCLIENT (clean session = empty search box), replays the genuine
connect+open+search setup from the card97-ch4 capture, and SETs the dynlist search string (re-targeted). The
fixture form stays rendered after the connection closes, so the screenshot shows the dynlist
(ДенамическийСписокИерархия, now with a visible command bar) filtered by the search:
  baseline   -> the FULL Товары list (setup only, no search frame sent)
  'Молоко'   -> the search box shows 'Молоко', the list narrows to matches (or empty)
  '<value>'  -> any re-targeted UTF-16 string (bounded by the captured 'Молоко' length)

    .venv/bin/python tools/protocol-research/search_list_verify_shot.py [value1 value2 ...]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import derive_search_list, search_list  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card97-ch4-search-20260619"


def _shot(label: str, value: str | None, out: Path, *, baseline: bool = False) -> None:
    """Boot a fresh client, replay (setup-only for baseline, else setup+search), screenshot."""
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    try:
        t = derive_search_list(CAP)
        if baseline:
            t.stop_after = 15  # replay ONLY the handshake+open frames -> the full, unfiltered list
            res = search_list(t, t.captured_value, port=15381)
        else:
            res = search_list(t, value, port=15381)
        time.sleep(1.5)
        shot = out / f"{label}.png"
        a = capture_screenshot(disp, out_path=str(shot))
        print(f"{label:14s} value={res.get('value')!r} echoed={res.get('echoed')} "
              f"display={disp} png={a.get('size_bytes')}B -> {shot.name}")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
        time.sleep(1.0)


def main(argv: list[str]) -> int:
    out = REPO / "runtime/protocol-research/search-list-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    values = argv or ["Молоко", "Творог"]
    _shot("00-baseline", None, out, baseline=True)
    for i, v in enumerate(values, 1):
        _shot(f"{i:02d}-search", v, out)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

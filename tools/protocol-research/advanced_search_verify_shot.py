#!/usr/bin/env python3
"""Card 97 change 4 — live-verify the dynlist «Расширенный поиск» (advanced-search) DIALOG filter capture-free.

Each run boots a FRESH native /TESTCLIENT and replays the genuine flow (open form → click «Расширенный поиск»
→ the UniversalListFindExtForm dialog opens → SET Pattern → click Find) with the Pattern re-targeted. The dialog
window GUID is rebound by GuidRebinder. The list filters by the dialog's default field; the screenshot shows the
result.

    .venv/bin/python tools/protocol-research/advanced_search_verify_shot.py [value1 value2 ...]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import advanced_search, derive_advanced_search  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card97-ch4-advsearch-20260619"


def main(argv: list[str]) -> int:
    out = REPO / "runtime/protocol-research/advsearch-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    values = argv or ["Молоко"]
    for i, v in enumerate(values, 1):
        r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
        pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
        try:
            t = derive_advanced_search(CAP)
            res = advanced_search(t, v, port=15381)
            time.sleep(1.5)
            shot = out / f"{i:02d}-advsearch.png"
            a = capture_screenshot(disp, out_path=str(shot))
            print(f"advanced_search({v!r}) echoed={res.get('echoed')} display={disp} "
                  f"png={a.get('size_bytes')}B -> {shot.name}")
        finally:
            stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
            time.sleep(1.0)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

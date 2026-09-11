#!/usr/bin/env python3
"""Card 96 / E3 — capture-free window CLOSE live-verify (no Vanessa).

close/activate are window-level commands (`…SecondaryFrame[<window>] 88 82 81`, the same family as the dialog
close). A faithful full-stream replay of the genuine navigation (open form → open list → drill a row → the card
opens) plus the window-level close, truncated before any subsequent close, closes only the active card. Verified
by the closed window's (live, rebound) SecondaryFrame being reported BEFORE the close but gone AFTER it.

    PYTHONPATH=src python3 tools/protocol-research/close_window_probe.py [port] [capture_dir] [window_ref]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import derive_close_window, close_window  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card96-windows3-20260618/traffic"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    ref = sys.argv[3] if len(sys.argv) > 3 else "e1cib/data/Справочник.Контрагенты"
    t = derive_close_window(cap, window_ref=ref)
    print(f"capture={cap.parent.name} window_ref={ref!r} close_frame={t.close_frame} stop_after={t.stop_after}")
    r = close_window(t, port=port)
    print(f"  close_window: accepted={r['accepted']} closed={r['closed']} "
          f"live_sf={(r['live_window_sf'] or '')[:8]} active_after={r['active_window_after']}")
    ok = bool(r["closed"])
    print("RESULT:", "PASS — capture-free close_window (card window closed)" if ok
          else ("WEAK PASS — accepted but close not confirmed by SF delta" if r["accepted"] else "INCONCLUSIVE"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

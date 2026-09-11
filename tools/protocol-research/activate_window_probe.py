#!/usr/bin/env python3
"""Card 96 / E3 — capture-free window ACTIVATE live-verify (no Vanessa).

activate/close are the SAME window-level command (`…SecondaryFrame[<window>] 88 82 81`); on a BURIED window it
brings it to front (activate), on the active window it closes it. A faithful full-stream replay of the genuine
navigation (open form → open list → drill a row → the target is buried) plus that command on the target brings
it forward. Verified by the target becoming the ACTIVE (last-reported) window — the inverse of close.

    PYTHONPATH=src python3 tools/protocol-research/activate_window_probe.py [port] [capture_dir] [window_ref]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import derive_activate_window, activate_window  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card96-activate-20260618/traffic"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    ref = sys.argv[3] if len(sys.argv) > 3 else "e1cib/app/Обработка.ФикстураПротоколаTestClient"
    t = derive_activate_window(cap, window_ref=ref)
    print(f"capture={cap.parent.name} window_ref={ref!r} activate_frame={t.activate_frame}")
    r = activate_window(t, port=port)
    print(f"  activate_window: accepted={r['accepted']} activated={r['activated']} "
          f"live_sf={(r['live_window_sf'] or '')[:8]} target_in_activate_resp={r['target_in_activate_resp']}")
    ok = bool(r["activated"])
    print("RESULT:", "PASS — capture-free activate_window (target window brought to front)" if ok
          else ("WEAK PASS — accepted but activation not confirmed" if r["accepted"] else "INCONCLUSIVE"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Card 96 / E1 — capture-free dialog ANSWER live-verify (no Vanessa).

Decode (evidence genuine-card96-dialogs): a ПоказатьВопрос/ПоказатьПредупреждение dialog opens a NEW top-level
window (a fresh SecondaryFrame GUID); the genuine answer is a WINDOW-LEVEL command on the dialog SF
(`…SecondaryFrame[<dlg>] 88 82 81` = the window's default action = ОК), NOT a Button activate. A faithful
full-stream replay answers it: GuidRebinder learns the LIVE dialog GUID from the live open response and rebinds
the captured one in the close command (same first-appearance rebinding as the form window). Commit is confirmed
by the result_marker (PF_V4_WARNING_ACK) in the post-answer read-sweep.

    PYTHONPATH=src python3 tools/protocol-research/answer_dialog_probe.py [port] [capture_dir] [result_marker]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import answer_dialog, derive_answer_dialog  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card96-dialog-warn-20260618/traffic"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    marker = sys.argv[3] if len(sys.argv) > 3 else "PF_V4_WARNING_ACK"
    t = derive_answer_dialog(cap, result_marker=marker)
    print(f"capture={cap.name} dialog_sf={t.dialog_sf} close_frame=mgr[{t.close_frame}] marker={marker!r}")
    r = answer_dialog(t, port=port)
    print(f"  answer: committed={r['committed']} (marker {marker} in the post-answer read-back)")
    ok = bool(r["committed"])
    print("RESULT:", "PASS — capture-free dialog answer committed" if ok else "INCONCLUSIVE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

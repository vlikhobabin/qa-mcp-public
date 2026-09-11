#!/usr/bin/env python3
"""Card 96 / E2 — capture-free CHOOSE-FROM-LIST live-verify (no Vanessa).

Decode (evidence genuine-card96-choicelist): clicking the command that raises ПоказатьВыборИзСписка opens a
popup that REUSES the form window (no new SecondaryFrame), and the pick is the choose tag
`e0 4b 53 <0x9a><len><value>` addressed at the ManagedForm — the same `e0 4b 53` family as a radio set_choice,
but at the form. The pick result surfaces as a user message `Сообщить("PF_CHOICE=" + value)`, so the commit is
confirmed by the `PF_CHOICE=<value>` ASCII marker on the wire (also the first user-message read decode, E5).

This probe opens a fresh connection, replays the form-open setup, clicks the choice-list command, and picks
``value`` (re-targeted from the captured PF_CHOICE_B), then checks the marker.

    # choice list (defaults):
    PYTHONPATH=src python3 tools/protocol-research/choose_from_list_probe.py [port] [capture_dir] [value]
    # popup menu (the wire twin):
    PYTHONPATH=src python3 tools/protocol-research/choose_from_list_probe.py 15381 \
        runtime/protocol-research/captures/genuine-card96-menu-20260618/traffic \
        PF_MENU_2 PF_SHOW_CHOICE_MENU PF_MENU_1 'PF_MENU='
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import choose_from_list, derive_choose_from_list  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card96-choicelist-20260618/traffic"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    value = sys.argv[3] if len(sys.argv) > 3 else "PF_CHOICE_A"
    base_command = sys.argv[4] if len(sys.argv) > 4 else "PF_SHOW_CHOICE_LIST"
    captured_value = sys.argv[5] if len(sys.argv) > 5 else "PF_CHOICE_B"
    message_prefix = sys.argv[6] if len(sys.argv) > 6 else "PF_CHOICE="
    t = derive_choose_from_list(cap, base_command, captured_value)
    print(f"capture={cap.name} setup_end={t.setup_end} choose_block={t.choose_block} captured={t.captured_value!r}")
    r = choose_from_list(t, value, message_prefix=message_prefix, port=port)
    print(f"  pick {value!r}: accepted={r['accepted']} committed={r['committed']} message={r['message']!r}")
    ok = bool(r["committed"])
    print("RESULT:", f"PASS — capture-free pick committed ({value})" if ok else "INCONCLUSIVE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Card 96 / E5 — capture-free user-message READ live-verify (no Vanessa).

The "messages to user" panel (`Сообщить` text) is reported by the client as the envelope
`cb 53 9a <byte-len> <UTF-8>`. A faithful full-stream replay of a genuine flow that raises a message (e.g. the
choose-from-list/menu callbacks) lets `extract_user_messages` decode it — the capture-free assertion read for
«нет сообщений пользователю» / reading `Сообщить` output.

    PYTHONPATH=src python3 tools/protocol-research/read_user_messages_probe.py [port] [capture_dir] [expected]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import derive_read_user_messages, read_user_messages  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card96-choicelist-20260618/traffic"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    expected = sys.argv[3] if len(sys.argv) > 3 else "PF_CHOICE=PF_CHOICE_B"
    t = derive_read_user_messages(cap, expected=expected)
    print(f"capture={cap.parent.name} expected={expected!r}")
    r = read_user_messages(t, port=port)
    print(f"  read_user_messages: count={r['count']} messages={r['messages']} expected_found={r['expected_found']}")
    ok = bool(r["expected_found"])
    print("RESULT:", "PASS — capture-free read_user_messages (Сообщить text read back)" if ok
          else ("WEAK — messages read but expected not among them" if r["count"] else "INCONCLUSIVE — no messages"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Card 98 change-1 — live-verify read_form_descriptor(open_link=…): open ANY form by nav-link and introspect it
with NO per-form capture (navigate → resolve SecondaryFrame.ManagedForm → live-enumerate + value-read).

    .venv/bin/python tools/protocol-research/read_form_descriptor_openlink_verify.py [nav_link]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, read_form_descriptor, stop_test_client  # noqa: E402

LINK = sys.argv[1] if len(sys.argv) > 1 else "e1cib/list/Справочник.Контрагенты"


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} open_link={LINK}")
    try:
        d = read_form_descriptor(port=15381, open_link=LINK, gherkin=False)
        print(f"\nopened form: {d.get('opened')!r}")
        print(f"enumerated: {d.get('element_count')} elements; {d.get('field_count')} field VALUES read")
        print("elements:", json.dumps(d.get("elements", [])[:10], ensure_ascii=False)[:500])
        print("field values:", json.dumps(d.get("fields", {}), ensure_ascii=False)[:500])
        print("\nPASS — form opened + resolved + introspected" if d.get("opened") else "FAIL — form not opened/resolved")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

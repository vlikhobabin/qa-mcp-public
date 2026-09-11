#!/usr/bin/env python3
"""Card 98 change-5 (THE gate) — config-agnostic open on a SECOND, FOREIGN config (demo_1_0_41_3 = a real
1C:БСП base, NO suite fixture). Proves the productized read_form_descriptor(open_link=…) introspects a form on a
config it has never captured: bootstrap (config-portable) → bare desktop → navigate (MainFrame retargeted to the
demo's live desktop) → resolve → descriptor. If this returns the demo form's element tree, the "100% replacement
on ANY config" claim's open-surface is closed.

    .venv/bin/python tools/protocol-research/config_agnostic_2nd_config_probe.py [nav_link]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, read_form_descriptor, stop_test_client  # noqa: E402

IB = "/opt/1c-dev/demo_1_0_41_3"
PORT = 15382
LINK = sys.argv[1] if len(sys.argv) > 1 else "e1cib/list/Справочник.Валюты"


def main() -> int:
    r = launch_test_client(
        infobase_path=IB, port=PORT, user="Администратор", kind="thick",
        display="auto", manage_apache=False, wait_sec=150.0,
    )
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched demo БСП pid={pid} listening={r.get('listening')} port={PORT} open_link={LINK}")
    rc = 1
    try:
        d = read_form_descriptor(port=PORT, open_link=LINK, gherkin=False)
        print(f"\nopened form: {d.get('opened')!r}")
        print(f"enumerated: {d.get('element_count')} elements; {d.get('field_count')} field VALUES read")
        print("elements:", json.dumps(d.get("elements", [])[:14], ensure_ascii=False)[:700])
        if d.get("opened") and d.get("element_count"):
            print("\nPASS — a DEMO (2nd-config) form opened + introspected with NO fixture, NO per-form capture")
            rc = 0
        else:
            print("\nFAIL — demo form not opened/introspected")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=False)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

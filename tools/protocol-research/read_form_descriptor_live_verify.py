#!/usr/bin/env python3
"""Card 98 change-1 generalization — live-verify read_form_descriptor(enumerate_live=True): introspect the form
with the field list enumerated LIVE (splice-replay of the descriptor query), NO per-form capture field list.
Compares to the capture-based path (enumerate_live=False) and the Vanessa oracle.

    .venv/bin/python tools/protocol-research/read_form_descriptor_live_verify.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, read_form_descriptor, stop_test_client  # noqa: E402

ORACLE = REPO / "runtime/protocol-research/captures/tm-v1-ro-batchQ3/mcp_manager_fixture_optional_form_analysis_gherkin.json"


def load_oracle() -> dict[str, str]:
    text = json.loads(ORACLE.read_text(encoding="utf-8-sig"))["result"]["content"][0]["text"]
    return {m.group(1): m.group(2)
            for m in re.finditer(r"элемент формы с именем '([^']+)' стал равен \"([^\"]*)\"", text)}


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    try:
        oracle = load_oracle()
        live = read_form_descriptor(port=15381, enumerate_live=True, gherkin=False)
        cap = read_form_descriptor(port=15381, enumerate_live=False, gherkin=False)
        print(f"\nLIVE  enumeration: {live['field_count']} fields decoded / {live['queried']} queried")
        print(f"CAPTURE enumeration: {cap['field_count']} fields decoded / {cap['queried']} queried")
        g = live["fields"]
        common = set(g) & set(oracle)
        match = [k for k in common if g[k] == oracle[k]]
        print(f"\noracle {len(oracle)}; LIVE∩oracle {len(common)}; VALUE-MATCH {len(match)}/{len(common)}")
        mism = [(k, g[k], oracle[k]) for k in sorted(common) if g[k] != oracle[k]]
        print("mismatches:", mism if mism else "none")
        print("LIVE got, NOT in capture path:", sorted(set(g) - set(cap["fields"]))[:12])
        for k in ("PF_EDIT_STRING", "PF_EDIT_NUMBER", "PF_CHECKBOX_TRUE", "Контрагент"):
            print(f"  {k:28} -> {g.get(k)!r}")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

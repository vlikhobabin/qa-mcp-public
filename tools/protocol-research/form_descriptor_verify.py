#!/usr/bin/env python3
"""Card 98 #1 — live-verify read_form_descriptor (the get_form_analysis equivalent) capture-free against a fresh
native /TESTCLIENT, comparing the decoded name->value descriptor to the genuine Vanessa form-analysis oracle.

    .venv/bin/python tools/protocol-research/form_descriptor_verify.py
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
        desc = read_form_descriptor(port=15381)
        got = desc["fields"]
        oracle = load_oracle()
        print(f"\ndescriptor: {desc['field_count']} fields decoded / {desc['queried']} queried")
        common = set(got) & set(oracle)
        match = [k for k in common if got[k] == oracle[k]]
        print(f"oracle {len(oracle)} fields; common {len(common)}; VALUE-MATCH {len(match)}/{len(common)}")
        print("oracle NOT in descriptor:", sorted(set(oracle) - set(got)))
        mism = [(k, got[k], oracle[k]) for k in sorted(common) if got[k] != oracle[k]]
        print("mismatches:", mism if mism else "none")
        print("\nsample fields:")
        for k in ("PF_FIXTURE_VERSION", "PF_LAST_ACTION", "PF_EDIT_STRING", "PF_EDIT_NUMBER", "PF_EDIT_DATE",
                  "PF_CHECKBOX_TRUE", "PF_CHECKBOX_FALSE"):
            print(f"  {k:22s} -> {got.get(k)!r}")
        print("\nCyrillic fields (card 98 #1 — UTF-16 0x97 query path):")
        for k in ("Контрагент", "ПолеСоСпискомВыбораСтрока"):
            print(f"  {k:26s} -> {got.get(k)!r}  (decoded={k in got}, oracle={oracle.get(k)!r})")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

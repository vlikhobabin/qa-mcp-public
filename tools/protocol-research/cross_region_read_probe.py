#!/usr/bin/env python3
"""Card 97 #2-read (cross-region value read) — live-verify reading a PF_GROUP_MAIN status marker capture-free
against a fresh native /TESTCLIENT (no Vanessa). The card-79 value-read query carries the FULL element path
``Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[PF_EDIT_STRING]``; a leaf-only retarget keeps the
``PF_GROUP_EDITS`` container, so a marker directly under PF_GROUP_MAIN returns the 0x88 no-value stub. This probe
passes the marker's real groups (``["PF_GROUP_MAIN"]``) so ``_read_field_value`` retargets the WHOLE path.

Proves: (a) the cross-region full-path read returns the marker value; (b) the OLD leaf-only read of the same
marker still returns None (the stub) — i.e. the group container was the blocker; (c) the editable-region read
(PF_EDIT_STRING) is unchanged.

    .venv/bin/python tools/protocol-research/cross_region_read_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import (  # noqa: E402
    _read_field_value, launch_test_client, stop_test_client,
)

CAP = "tm-v1-ro-batchQ3"
TPL = "runtime/protocol-research/templates/tm-v1-open-plus-valueread/manager_frame_templates.json"

# PF_GROUP_MAIN status markers (groups=["PF_GROUP_MAIN"], one level above the editable PF_GROUP_EDITS region).
MARKERS = ["PF_FIXTURE_VERSION", "PF_LAST_ACTION", "PF_SELECTED_ROW_MARKER"]


def read(field: str, groups: list[str] | None) -> str | None:
    return _read_field_value(field, host="127.0.0.1", port=15381, capture_dir=CAP, manager_templates=TPL, groups=groups)


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    try:
        print("\n-- control: editable-region read (groups=None, leaf-only) --")
        print(f"  PF_EDIT_STRING (groups=None)      -> {read('PF_EDIT_STRING', None)!r}")

        print("\n-- control: cross-region marker via OLD leaf-only path (expect None / 0x88 stub) --")
        for m in MARKERS:
            print(f"  {m:24s} (groups=None)  -> {read(m, None)!r}")

        print("\n-- FIX: cross-region marker via full-path retarget (groups=['PF_GROUP_MAIN']) --")
        for m in MARKERS:
            print(f"  {m:24s} (PF_GROUP_MAIN) -> {read(m, ['PF_GROUP_MAIN'])!r}")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

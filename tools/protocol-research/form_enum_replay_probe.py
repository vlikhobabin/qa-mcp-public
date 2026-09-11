#!/usr/bin/env python3
"""Card 98 change-1 generalization — can we replay the form-analysis re-render (capture frame 40, which
enumerates 45 elements) on a live session to get the element tree WITHOUT a per-form field list? Open the form,
then send the captured enumeration frame GUID-rebound (captured SecondaryFrame/ManagedForm -> the live session's)
via run_action, and count the element names in the response.

    .venv/bin/python tools/protocol-research/form_enum_replay_probe.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import _repo_root, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = "tm-v1-ro-batchQ3"
TPL = "runtime/protocol-research/templates/tm-v1-open-plus-valueread/manager_frame_templates.json"
GUID = rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"


class _GuidSwap:
    def __init__(self, mapping: dict[bytes, bytes]) -> None:
        self.mapping = {k: v for k, v in mapping.items() if k and v and k != v}

    def apply(self, payload: bytes) -> bytes:
        for cap, live in self.mapping.items():
            payload = payload.replace(cap, live)
        return payload


def _names(blob: bytes) -> set[str]:
    return {m.group(1).decode() for m in re.finditer(rb"EditField\[([A-Za-z0-9_]+)\]", blob)}


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    try:
        repo = _repo_root()
        bootstrap = CaptureBootstrap.load(resolve_capture_dir(CAP, repo))
        templates = ProtocolTemplates.load((repo / TPL).resolve())
        out_dir = repo / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
        with TestClientSession(host="127.0.0.1", port=15381) as session:
            handle = session.open_and_bootstrap(bootstrap=bootstrap, templates=templates,
                                                 output_dir=out_dir, synthesized=synthesize_bootstrap())
            handle.run_segment(list(range(11, 18)), query_id="form-element-details")
            live_sf = (handle.state.secondary_frame_guid or "").encode()
            live_mf = (handle.state.managed_form_guid or "").encode()
            print(f"live SF={live_sf!r} MF={live_mf!r}")
            for fi in (40, 41, 39, 38):
                f = bootstrap.captured_frame(fi)
                cap_sf = re.search(rb"SecondaryFrame\[(" + GUID + rb")\]", f)
                cap_mf = re.search(rb"ManagedForm\[(" + GUID + rb")\]", f)
                mapping = {}
                if cap_sf and live_sf:
                    mapping[cap_sf.group(1)] = live_sf
                if cap_mf and live_mf:
                    mapping[cap_mf.group(1)] = live_mf
                before = len(handle.state.received_stream)
                try:
                    res = handle.run_action(_GuidSwap(mapping).apply(f), query_id="action")
                except Exception as e:
                    print(f"  frame {fi}: ERROR {type(e).__name__}: {e}")
                    continue
                resp = bytes(handle.state.received_stream[before:])
                print(f"  frame {fi}: accepted={res['accepted']} recv={res['recv_bytes']} element_names={len(_names(resp))}")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

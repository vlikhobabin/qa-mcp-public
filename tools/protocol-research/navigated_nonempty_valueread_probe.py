#!/usr/bin/env python3
"""Card 98 change-5 follow-up — NON-EMPTY navigated RECORD value-read. The demo Валюты create form's fields are
empty, so to prove the navigated value-read returns a real VALUE (not just resolves an empty field), type a value
into the rendered form (xtest), Tab to commit the object attribute, then navigated-value-read every field and
look for the typed value. If a field reads back the typed text, the navigated value-read is verified end-to-end
on a real 2nd-config RECORD form.

    .venv/bin/python tools/protocol-research/navigated_nonempty_valueread_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.native_xtest import xtest_key, xtest_type  # noqa: E402
from qa_mcp.protocol.responses import extract_descriptor_fields, extract_form_field_values  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

IB = "/opt/1c-dev/demo_1_0_41_3"
PORT = 15382
LINK = "e1cib/data/Справочник.Валюты"
VALUE = "НавигЗначение777"


def main() -> int:
    r = srv.launch_test_client(infobase_path=IB, port=PORT, user="Администратор", kind="thick",
                               display="auto", manage_apache=False, wait_sec=150.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={display}")
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    rc = 1
    try:
        with TestClientSession(host="127.0.0.1", port=PORT) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            resolved = srv._open_form_by_link(h, LINK)
            print(f"resolved: {resolved}")
            if not resolved:
                return 1
            _, sf, mf = resolved
            h.state.secondary_frame_guid, h.state.managed_form_guid = sf, mf
            srv.capture_screenshot(display, out_path=str(out / "01_after_nav.png"))
            # type a value into the focused field of the rendered create form, then Tab to commit the attribute
            xtest_type(display, VALUE)
            xtest_key(display, "Tab")
            srv.capture_screenshot(display, out_path=str(out / "02_after_type.png"))
            print(f"typed {VALUE!r} + Tab; screenshots in {out}")

            blob = srv._live_descriptor_blob(h, (sf, mf))
            specs = extract_descriptor_fields(blob)
            print(f"fields: {[n for n, _ in specs]}")
            found = {}
            for name, groups in specs:
                def rw(_i, payload, _n=name, _g=tuple(groups)):
                    return srv._retarget_read_to_groups(payload, srv._VALUE_READ_CAPTURED_FIELD, _n, list(_g),
                                                        form_ref=(sf, mf))
                before = len(h.state.received_stream)
                try:
                    h.run_segment(srv._VALUE_READ_FRAMES, query_id="form-value-read", frame_rewriter=rw)
                except Exception as e:  # noqa: BLE001
                    print(f"  {name}: EXCEPTION {type(e).__name__}: {e}")
                    continue
                vals = extract_form_field_values(bytes(h.state.received_stream[before:]))
                if vals:
                    found.update(vals)
                print(f"  {name}: {vals}")
            print(f"\nALL read values: {found}")
            if VALUE in found.values():
                print(f"PASS — navigated RECORD value-read returned the typed value {VALUE!r} (non-empty, capture-free, 2nd config)")
                rc = 0
            else:
                print("FAIL — typed value not read back (focus/commit/value-read gap)")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=False)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

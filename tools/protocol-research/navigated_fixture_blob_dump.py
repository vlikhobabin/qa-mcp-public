#!/usr/bin/env python3
"""Diagnostic — DUMP the navigated fixture descriptor blob: what are the 5 elements, and are the EditFields
present-but-unparsed or genuinely absent? Open the fixture by nav-link, resolve, descriptor-query, then print
the blob size + every ASCII and UTF-16LE printable run + all `<Kind>[name]` matches (both encodings).

    .venv/bin/python tools/protocol-research/navigated_fixture_blob_dump.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.native_write import splice_descriptor_query  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

LINK = sys.argv[1] if len(sys.argv) > 1 else "e1cib/data/Обработка.ФикстураПротоколаTestClient"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 15381
IB = sys.argv[3] if len(sys.argv) > 3 else None  # e.g. /opt/1c-dev/demo_1_0_41_3
MANAGE_APACHE = PORT == 15381


def ascii_runs(b: bytes, n=4):
    return re.findall(rb"[\x20-\x7e]{%d,}" % n, b)


def utf16_runs(b: bytes, n=3):
    out = []
    for m in re.finditer((rb"(?:[\x20-\x7e\x00-\x04][\x04\x00]){%d,}" % n), b):
        try:
            s = m.group(0).decode("utf-16-le", "ignore").strip()
            if s:
                out.append(s)
        except Exception:
            pass
    return out


def main() -> int:
    r = srv.launch_test_client(port=PORT, infobase_path=IB, user=("Администратор" if IB else None),
                               kind=("thick" if IB else None), manage_apache=MANAGE_APACHE,
                               display="auto", wait_sec=150.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} port={PORT} link={LINK}")
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    try:
        with TestClientSession(host="127.0.0.1", port=PORT) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            resolved = srv._open_form_by_link(h, LINK)
            print(f"resolved: {resolved}")
            if not resolved:
                return 1
            _, sf, mf = resolved
            before = len(h.state.received_stream)
            h.run_action(splice_descriptor_query(srv._splice_header_no_form(h), sf, mf), query_id="descriptor")
            blob = bytes(h.state.received_stream[before:])
            (out / "fixture_navlink_descriptor.bin").parent.mkdir(parents=True, exist_ok=True)
            (out / "fixture_navlink_descriptor.bin").write_bytes(blob)
            print(f"descriptor {len(blob)}B saved {out/'fixture_navlink_descriptor.bin'}")
            kinds = re.findall(rb"([A-Za-z]+)\[([A-Za-z0-9_]+)\]", blob)
            print(f"ASCII <Kind>[name] ({len(kinds)}): {[(k.decode(), n.decode()) for k, n in kinds][:30]}")
            print(f"PF_ in blob? {b'PF_' in blob} ; EditField in blob? {b'EditField' in blob} ; InputField? {b'InputField' in blob}")
            print(f"ASCII runs ({len(ascii_runs(blob))}): {[x.decode('latin1') for x in ascii_runs(blob)][:40]}")
            u16 = utf16_runs(blob)
            print(f"UTF-16 runs ({len(u16)}): {u16[:40]}")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=MANAGE_APACHE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

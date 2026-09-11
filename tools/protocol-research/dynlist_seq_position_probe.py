#!/usr/bin/env python3
"""Card 98 — DYNLIST read with INCREMENTING sequence counters. Genuine position+read frames each carry a unique
+1 sequence (offset 19-20); the splice reused ONE (frame 218's), so the client deduped the same-sequence
table-ACTION (positioning) → no current row. Fix: bump the sequence per command. Open the Товары list, position to
first row (the `88 82 81 20 20 20` pairs, retargeted + sequenced), read «Наименование».

    .venv/bin/python tools/protocol-research/dynlist_seq_position_probe.py [port] [link] [table] [column]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.element_ref import encode_element_path_block  # noqa: E402
from qa_mcp.protocol.native_write import _seq_of, _set_seq, splice_table_cell_read  # noqa: E402
from qa_mcp.protocol.responses import extract_table_cell_value  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
LINK = sys.argv[2] if len(sys.argv) > 2 else "e1cib/list/Справочник.Товары"
TABLE = sys.argv[3] if len(sys.argv) > 3 else "Список"
COLUMN = sys.argv[4] if len(sys.argv) > 4 else "Наименование"
MANAGE = PORT == 15381
NONCE1 = bytes.fromhex("754ee15d6fb6f64f9a9c819ed06cd42bd5a719411d3b48724fb9e909d74b25b8f0")
NONCE2 = bytes.fromhex("3e312772a733f14a928d66945ecff123d51bdd3f72b47be443a9f3456621c73aa8")
TAIL = b"\x66\x53\xb2\xa6"


def main() -> int:
    r = srv.launch_test_client(port=PORT, infobase_path=None, manage_apache=MANAGE, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} link={LINK} table={TABLE} column={COLUMN}")
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
            h.state.secondary_frame_guid, h.state.managed_form_guid = sf, mf
            groups = srv._table_groups(srv._live_descriptor_blob(h, (sf, mf)), TABLE)
            print(f"groups={groups}")
            path = encode_element_path_block(".".join(
                [f"SecondaryFrame[{sf}]", f"ManagedForm[{mf}]"] + [f"Group[{g}]" for g in groups] + [f"Table[{TABLE}]"]))

            base = _seq_of(srv._splice_header_no_form(h))
            seq = base + 1
            print(f"base seq (frame218) = {base}; sequencing actions from {seq}")

            def send_action(opcode: bytes, nonce: bytes):
                nonlocal seq
                hdr = srv._splice_header_no_form(h)
                cmd = _set_seq(hdr + nonce + path + opcode + TAIL, seq)
                h.run_action(cmd, query_id=f"pos-{seq}")
                seq += 1

            # «перехожу к первой строке» — the two table-command pairs, each frame uniquely sequenced
            send_action(b"\x88\x82\x81\x20\x20\x20", NONCE1)
            send_action(b"\x81\x81\x81\x20\x20\x20", NONCE1)
            send_action(b"\x88\x82\x81\xe1\x20\x20\x20", NONCE2)
            send_action(b"\x81\x81\x81\xe1\x20\x20\x20", NONCE2)

            # read with the next sequence
            read_cmd = _set_seq(splice_table_cell_read(srv._splice_header_no_form(h), sf, mf, groups, TABLE, COLUMN), seq)
            before = len(h.state.received_stream)
            h.run_action(read_cmd, query_id=f"read-{seq}")
            resp = bytes(h.state.received_stream[before:])
            value = extract_table_cell_value(resp)
            env = b"\xe0\x4b\x53" in resp
            print(f"read: value={value!r} (e0-4b-53 envelope={env})")
            print("\nPASS — dynlist current-row read works with incrementing sequences" if value
                  else "\nFAIL — still no value")
            return 0 if value else 1
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=MANAGE)


if __name__ == "__main__":
    raise SystemExit(main())

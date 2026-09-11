#!/usr/bin/env python3
"""Card 98 — DYNLIST read via an INTERACTION-ready open. After the navigate, the genuine flow does activate [27]
+ render/data queries [29]/[31] (the [31] query references the table "Список" — it loads the dynlist data) BEFORE
positioning. Replay activate + render queries (retargeted to the live S.F) + position + read, all sequence-bumped.

    .venv/bin/python tools/protocol-research/dynlist_interaction_open_probe.py [port] [link] [table] [column]
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
# genuine bodies after cb2395 (genuine-card98-listform-read)
ACT27 = bytes.fromhex("554d850d068aee499e292f8d0e7a9f0ed580b15a0e8d542748a01554838e799d4f81888181e04b55202020206653b2a6")
RENDER29 = bytes.fromhex("0a102bc90b462c40b5aeb6e2329a7234d50b3e4c2b74dd774d97e508fcca43ce189a345365636f6e646172794672616d655b61346231626135312d383466312d343333322d623962382d3664613761663934643565615d888181e1828284818181812020206653b2a6")
RENDER31 = bytes.fromhex("0a102bc90b462c40b5aeb6e2329a7234d5117db013edacc44f8055a5015d05b5fa9a665365636f6e646172794672616d655b61346231626135312d383466312d343333322d623962382d3664613761663934643565615d2e4d616e61676564466f726d5b33613465333031392d333231612d346338352d386638312d6166393361346164366236365d888181e182828682970641043f04380441043e043a048181812020206653b2a6")
GS = b"a4b1ba51-84f1-4332-b9b8-6da7af94d5ea"
GF = b"3a4e3019-321a-4c85-8f81-af93a4ad6b66"
NONCE1 = bytes.fromhex("754ee15d6fb6f64f9a9c819ed06cd42bd5a719411d3b48724fb9e909d74b25b8f0")
NONCE2 = bytes.fromhex("3e312772a733f14a928d66945ecff123d51bdd3f72b47be443a9f3456621c73aa8")
TAIL = b"\x66\x53\xb2\xa6"


def main() -> int:
    r = srv.launch_test_client(port=PORT, infobase_path=None, manage_apache=MANAGE, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} link={LINK}")
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
            sfb, mfb = sf.encode(), mf.encode()
            path = encode_element_path_block(".".join(
                [f"SecondaryFrame[{sf}]", f"ManagedForm[{mf}]"] + [f"Group[{g}]" for g in groups] + [f"Table[{TABLE}]"]))

            seq = _seq_of(srv._splice_header_no_form(h)) + 1

            def send(bodybytes, qid):
                nonlocal seq
                cmd = _set_seq(srv._splice_header_no_form(h) + bodybytes, seq)
                h.run_action(cmd, query_id=f"{qid}-{seq}")
                seq += 1

            # INTERACTION-ready open: activate + render/data queries (retargeted to live S.F)
            send(ACT27, "activate")
            send(RENDER29.replace(GS, sfb), "render29")
            send(RENDER31.replace(GS, sfb).replace(GF, mfb), "render31")
            # position to first row
            send(NONCE1 + path + b"\x88\x82\x81\x20\x20\x20" + TAIL, "pos1a")
            send(NONCE1 + path + b"\x81\x81\x81\x20\x20\x20" + TAIL, "pos1b")
            send(NONCE2 + path + b"\x88\x82\x81\xe1\x20\x20\x20" + TAIL, "pos2a")
            send(NONCE2 + path + b"\x81\x81\x81\xe1\x20\x20\x20" + TAIL, "pos2b")
            # read
            before = len(h.state.received_stream)
            h.run_action(_set_seq(splice_table_cell_read(srv._splice_header_no_form(h), sf, mf, groups, TABLE, COLUMN), seq),
                         query_id=f"read-{seq}")
            value = extract_table_cell_value(bytes(h.state.received_stream[before:]))
            print(f"read: value={value!r}")
            print("\nPASS — dynlist read via interaction-ready open" if value else "\nFAIL — still no value")
            return 0 if value else 1
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=MANAGE)


if __name__ == "__main__":
    raise SystemExit(main())

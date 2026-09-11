#!/usr/bin/env python3
"""Card 98 change-1 — feasibility: open a DIFFERENT form on the held session (splice the nav-link navigate
command) then descriptor-query it, proving introspection of ANY form with no per-form capture. Stage 1: open
fixture + descriptor-query (live MainFrame GUID). Stage 2: splice navigate (MainFrame→live, nav-link→target).
Stage 3: descriptor-query the navigated form.

    .venv/bin/python tools/protocol-research/open_any_form_probe.py [e1cib/list/Справочник.Контрагенты]
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
from qa_mcp.protocol.native_write import splice_descriptor_query, splice_window_list_queries  # noqa: E402
from qa_mcp.protocol.responses import extract_descriptor_fields, extract_testclient_windows  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

OPEN_FRAMES = list(range(11, 18))
SPLIT = b"\xcb\x23\x95"
TARGET = sys.argv[1] if len(sys.argv) > 1 else "e1cib/list/Справочник.Контрагенты"
# navigate command body (genuine-card90-openlist frame 14, after cb2395): <nonce> 9a 2f MainFrame[<guid>] <op> f7 <cc> <navlink utf16> <pad><tail>
NAV_BODY_HEX = ("e3490553e2c8d04b881be98d27b886d1d5ed8b4c6ff37b244c8fb26d223bc724aa"
                "9a2f4d61696e4672616d655b36636137356535302d363261332d343834322d623663642d6234323966373539316566325d"
                "888281f71c650031006300690062002f006c006900730074002f0021043f044004300432043e0447043d0438043a042e0022043e043204300440044b042020206653b2a6")
GENUINE_MAINFRAME = "6ca75e50-62a3-4842-b6cd-b429f7591ef2"
GENUINE_NAVLINK = "e1cib/list/Справочник.Товары"
PATH_RE = re.compile(rb"SecondaryFrame\[([0-9a-f-]{36})\]\.ManagedForm\[([0-9a-f-]{36})\]")


def live_header(handle):
    sent0 = len(handle.state.sent_stream)
    handle.run_segment([218], query_id="form-value-read")
    rendered = bytes(handle.state.sent_stream[sent0:])
    return rendered[: rendered.rfind(SPLIT) + len(SPLIT)], rendered


def main() -> int:
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} target={TARGET}")
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            h.run_segment(OPEN_FRAMES, query_id="form-element-details")
            header, rendered = live_header(h)
            m = PATH_RE.search(rendered)
            s0, f0 = m.group(1).decode(), m.group(2).decode()
            # stage 1: descriptor-query the fixture → live MainFrame GUID
            before = len(h.state.received_stream)
            h.run_action(splice_descriptor_query(rendered, s0, f0), query_id="form-descriptor")
            d0 = bytes(h.state.received_stream[before:])
            mf = re.search(rb"MainFrame\[([0-9a-f-]{36})\]", d0)
            live_mainframe = mf.group(1).decode() if mf else GENUINE_MAINFRAME
            print(f"stage1: fixture descriptor {len(d0)}B, {len(extract_descriptor_fields(d0))} fields; live MainFrame={live_mainframe}")

            # stage 2: navigate to TARGET (retarget MainFrame→live, nav-link→target)
            nav_body = bytes.fromhex(NAV_BODY_HEX)
            nav_body = nav_body.replace(GENUINE_MAINFRAME.encode(), live_mainframe.encode())
            nav_body = nav_body.replace(GENUINE_NAVLINK.encode("utf-16-le"), TARGET.encode("utf-16-le"))
            # the nav-link char-count prefix (f7 <cc>) must match the retargeted length
            cc = len(TARGET)
            nav_body = re.sub(rb"\xf7.", b"\xf7" + bytes([cc]), nav_body, count=1)
            # frame 15 body (the 2nd navigate frame; opcode 81 81 81 vs frame14's 88 82 81)
            navstart = len(h.state.received_stream)
            before = len(h.state.received_stream)
            h.run_action(header + bytes(nav_body), query_id="navigate")
            r2 = re.sub(rb"\x88\x82\x81\xf7", b"\x81\x81\x81\xf7", bytes(nav_body), count=1)
            h.run_action(header + r2, query_id="navigate2")
            navresp = bytes(h.state.received_stream[before:])
            print(f"stage2: navigate resp={len(navresp)}B")
            full = bytes(h.state.received_stream[navstart:])
            obs_mf = sorted(set(re.findall(rb"ManagedForm\[([0-9a-f-]{36})\]", full)))
            print(f"   ManagedForm GUIDs in full post-nav stream: {[g.decode() for g in obs_mf]}")
            srv.capture_screenshot(r["display"], out_path=str(out / "after_nav.png"))
            print(f"   screenshot: {out / 'after_nav.png'}")

            # stage 3: window-list to see what's open + the new form's SecondaryFrame
            header3, rendered3 = live_header(h)
            before = len(h.state.received_stream)
            for q in splice_window_list_queries(rendered3):
                h.run_action(q, query_id="window-list")
            wl = bytes(h.state.received_stream[before:])
            wins = extract_testclient_windows(wl)
            print(f"stage3: windows now open: {[(w['kind'], w['caption']) for w in wins]}")
            # the navigated form = the SecondaryFrame whose caption matches the target catalog
            target_name = TARGET.rsplit(".", 1)[-1] if "." in TARGET else TARGET
            new = next((w for w in wins if w["kind"] == "SecondaryFrame" and target_name in w["caption"]), None)
            print(f"   navigated form: {new}")
            mf_in_nav = sorted(set(x.decode() for x in re.findall(rb"ManagedForm\[([0-9a-f-]{36})\]", navresp + wl)))
            print(f"   ManagedForm GUIDs seen in nav/wl: {mf_in_nav}")
            # stage 4: RESOLVE the navigated form's S.F (the resolve query: input S-only -> response gives S.F)
            if new:
                from qa_mcp.protocol.native_write import WINDOW_LIST_HEADER_MARKER
                RESOLVE_PRE = bytes.fromhex("0a102bc90b462c40b5aeb6e2329a7234d561c48a217a04ac4eb41f7524b252e4c59a34")
                RESOLVE_POST = bytes.fromhex("888181e1818181818181812020206653b2a6")
                header4, rendered4 = live_header(h)
                hdr = rendered4[: rendered4.rfind(WINDOW_LIST_HEADER_MARKER) + 3]
                s_path = f"SecondaryFrame[{new['guid']}]".encode("latin1")
                before = len(h.state.received_stream)
                h.run_action(hdr + RESOLVE_PRE + s_path + RESOLVE_POST, query_id="resolve-form")
                rr = bytes(h.state.received_stream[before:])
                m2 = re.search(rb"SecondaryFrame\[([0-9a-f-]{36})\]\.ManagedForm\[([0-9a-f-]{36})\]", rr)
                print(f"stage4 RESOLVE: {len(rr)}B; resolved S.F = {bool(m2)}")
                if m2:
                    new_f = m2.group(2).decode()
                    print(f"   navigated form F = {new_f}")
                    # stage 5: descriptor-query the navigated form with its real S.F
                    header5, rendered5 = live_header(h)
                    before = len(h.state.received_stream)
                    h.run_action(splice_descriptor_query(rendered5, new["guid"], new_f), query_id="form-descriptor")
                    dN = bytes(h.state.received_stream[before:])
                    fields = extract_descriptor_fields(dN)
                    from collections import Counter
                    kinds = Counter(k.decode() for k in re.findall(rb"([A-Za-z]+)\[[A-Za-z0-9_]+\]", dN))
                    print(f"stage5 DESCRIPTOR of {new['caption']}: {len(dN)}B, {len(fields)} EditFields")
                    print(f"   ASCII element kinds: {dict(kinds.most_common(6))}")
                    print(f"   sample EditFields: {[n for n,_ in fields[:8]]}")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

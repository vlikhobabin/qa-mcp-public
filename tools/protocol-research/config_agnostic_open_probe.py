#!/usr/bin/env python3
"""Card 98 change-5 (THE gate) — CONFIG-AGNOSTIC open: introspect ANY form with NO fixture open at all.

The open-any-form wrapper (open_any_form_probe.py) bootstraps by opening the FIXTURE (frames 11-17) so a
value-read frame can render a live splice header (the header carries the form's managed_form_guid). That ties
introspection to a config that HAS the fixture. This probe removes that tie:

  1. bootstrap (frames 1-10) ONLY — NO fixture open (frames 11-17 skipped).
  2. build the splice header WITHOUT a form — render value-read frame 218 with PLACEHOLDER form GUIDs and slice
     to the `cb 23 95` marker. The header's only live fields (ack_guid @2, sequence @19) come from bootstrap;
     the form GUIDs (managed_form @151, secondary_frame @101) are AFTER the marker, so the splice discards them.
     (Offline-proven byte-identical to the fixture-rendered header[0:51].)
  3. window-list → the live desktop MainFrame GUID (config-agnostic source for the navigate) + prove NO fixture
     SecondaryFrame is open.
  4. navigate to the TARGET nav-link (MainFrame retargeted to the live desktop, nav-link retargeted).
  5. window-list → the navigated form's SecondaryFrame (by caption).
  6. resolve (S → S.F) → descriptor (full element tree).

If this works, introspection is lifted onto ANY real config (no fixture needed) — closes the change-5 gate.

    .venv/bin/python tools/protocol-research/config_agnostic_open_probe.py [e1cib/list/Справочник.Контрагенты]
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    NAVIGATE_BODY,
    NAVIGATE_GENUINE_LINK,
    WINDOW_LIST_HEADER_MARKER,
    splice_descriptor_query,
    splice_resolve_form_query,
    splice_window_list_queries,
)
from qa_mcp.protocol.responses import (  # noqa: E402
    extract_descriptor_elements,
    extract_descriptor_fields,
    extract_testclient_windows,
)
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

TARGET = sys.argv[1] if len(sys.argv) > 1 else "e1cib/list/Справочник.Контрагенты"
GENUINE_MAINFRAME = "6ca75e50-62a3-4842-b6cd-b429f7591ef2"
PLACEHOLDER_GUID = "00000000-0000-0000-0000-000000000000"


def splice_header_no_form(handle) -> bytes:
    """Build the value-read splice header WITHOUT a form open: render frame 218 with placeholder form GUIDs,
    slice to + incl. the cb-23-95 marker. ack_guid + sequence (the header's only dynamic fields) are live."""
    rendered = handle.templates.render(
        218, handle.state.ack_guid, handle.state.frame4_sequence,
        managed_form_guid=PLACEHOLDER_GUID, secondary_frame_guid=PLACEHOLDER_GUID,
    ).payload
    j = rendered.rfind(WINDOW_LIST_HEADER_MARKER)
    return rendered[: j + len(WINDOW_LIST_HEADER_MARKER)]


def window_list(handle) -> list[dict]:
    header = splice_header_no_form(handle)
    before = len(handle.state.received_stream)
    for q in splice_window_list_queries(header):
        handle.run_action(q, query_id="window-list")
    return extract_testclient_windows(bytes(handle.state.received_stream[before:]))


def navigate(handle, nav_link: str, main_frame: str) -> None:
    """Build the 2-frame navigate, MainFrame source retargeted to the live desktop GUID."""
    header = splice_header_no_form(handle)
    body = NAVIGATE_BODY.replace(GENUINE_MAINFRAME.encode("latin1"), main_frame.encode("latin1"))
    body = body.replace(NAVIGATE_GENUINE_LINK.encode("utf-16-le"), nav_link.encode("utf-16-le"))
    body = re.sub(rb"\xf7.", b"\xf7" + bytes([len(nav_link)]), body, count=1)
    body2 = body.replace(b"\x88\x82\x81\xf7", b"\x81\x81\x81\xf7", 1)
    handle.run_action(header + body, query_id="navigate")
    handle.run_action(header + body2, query_id="navigate2")


def main() -> int:
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} target={TARGET}")
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    rc = 1
    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            # 1. bootstrap ONLY — NO fixture open (open_and_bootstrap runs frames 1..10; we DON'T run 11-17)
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            print(f"step1 bootstrap: ack_guid={h.state.ack_guid} seq={h.state.frame4_sequence} (NO fixture open)")

            # 2+3. window-list on the bare desktop → live MainFrame, prove no fixture SecondaryFrame
            wins0 = window_list(h)
            print(f"step3 windows (bare desktop): {[(w['kind'], w['caption']) for w in wins0]}")
            mains = [w for w in wins0 if w["kind"] == "MainFrame"]
            if not mains:
                print("FAIL — no MainFrame in the bare-desktop window list (cannot source the navigate)")
                return 1
            live_mainframe = mains[0]["guid"]
            print(f"   live desktop MainFrame = {live_mainframe} (genuine hardcoded = {GENUINE_MAINFRAME})")

            # 4. navigate to TARGET, MainFrame retargeted to the live desktop
            navstart = len(h.state.received_stream)
            navigate(h, TARGET, live_mainframe)
            srv.capture_screenshot(r["display"], out_path=str(out / "after_nav.png"))
            print(f"step4 navigate sent; screenshot {out / 'after_nav.png'}")

            # 5. window-list → the navigated form's SecondaryFrame (by caption)
            wins1 = window_list(h)
            print(f"step5 windows after navigate: {[(w['kind'], w['caption']) for w in wins1]}")
            target_name = TARGET.rsplit(".", 1)[-1] if "." in TARGET else TARGET
            new = next((w for w in wins1 if w["kind"] == "SecondaryFrame" and target_name in w["caption"]), None)
            if new is None:
                print(f"FAIL — navigated form '{target_name}' not found in the window list (navigate did not open it)")
                return 1
            print(f"   navigated form window: {new}")

            # 6. resolve (S → S.F) → descriptor (element tree)
            header = splice_header_no_form(h)
            before = len(h.state.received_stream)
            h.run_action(splice_resolve_form_query(header, new["guid"]), query_id="resolve-form")
            rr = bytes(h.state.received_stream[before:])
            m = re.search(new["guid"].encode("latin1") + rb"\]\.ManagedForm\[([0-9a-f-]{36})\]", rr)
            if m is None:
                print(f"FAIL — resolve did not return the form's ManagedForm F ({len(rr)}B)")
                return 1
            new_f = m.group(1).decode()
            print(f"step6 resolve: F = {new_f}")
            header = splice_header_no_form(h)
            before = len(h.state.received_stream)
            h.run_action(splice_descriptor_query(header, new["guid"], new_f), query_id="form-descriptor")
            dN = bytes(h.state.received_stream[before:])
            elements = extract_descriptor_elements(dN)
            fields = extract_descriptor_fields(dN)
            kinds = Counter(e["kind"] for e in elements)
            print(f"step6 DESCRIPTOR of {new['caption']!r}: {len(dN)}B, {len(elements)} elements, {len(fields)} EditFields")
            print(f"   element kinds: {dict(kinds.most_common(8))}")
            print(f"   sample elements: {[(e['kind'], e['name']) for e in elements[:10]]}")
            if elements:
                print("\nPASS — form opened + introspected with NO fixture open (config-agnostic)")
                rc = 0
            else:
                print("\nFAIL — descriptor returned no elements")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

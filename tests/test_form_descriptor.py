"""Card 98 #1 — read_form_descriptor: capture field-enumeration (offline, against the real capture) + the
Gherkin state formatting. The live sweep needs a /TESTCLIENT, so it is verified by the probe
tools/protocol-research/form_descriptor_verify.py (live: 41 fields, value-matched vs the Vanessa oracle)."""
import dataclasses
import types

import pytest

import qa_mcp.mcp_server as srv
from qa_mcp.protocol import CaptureBootstrap, resolve_capture_dir


@pytest.fixture(autouse=True)
def clear_attached_testclient_context():
    srv._clear_attached_testclient_context()
    yield
    srv._clear_attached_testclient_context()


@pytest.fixture(autouse=True)
def _neutralize_list_refresh(monkeypatch):
    # Card 125 Change 5 — dynlist reads now force an «Обновить»/F5 refresh (display backend) and poll-until-stable
    # before reporting. Unit tests must NOT spawn a real xdotool keystroke or sleep between poll reads: stub the
    # refresh to a delivered no-op and zero the poll settle. Tests that assert the refresh/poll behavior itself
    # override _force_list_refresh / drive _ensure_list_fresh directly.
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("f5", None), raising=False)
    monkeypatch.setattr(srv, "LIST_POLL_SETTLE_SEC", 0.0, raising=False)


def _stub_list_table(monkeypatch, table="Список", available=None):
    def resolve(**kwargs):
        requested = kwargs.get("requested_table")
        selected = requested or table
        return selected, {
            "source": "test",
            "available_tables": available or [selected],
            "requested_table": requested,
        }

    monkeypatch.setattr(srv, "_resolve_list_table_for_read", resolve)


def test_enumerate_capture_fields_from_real_capture():
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", srv._repo_root()))
    specs = dict(srv._enumerate_capture_fields(bootstrap))
    # the genuine form-analysis sweep queries the 41 ASCII-named form fields
    assert len(specs) >= 40
    # each field carries its enclosing Group chain (used for the cross-region full-path read)
    assert specs["PF_EDIT_STRING"] == ["PF_GROUP_MAIN", "PF_GROUP_EDITS"]
    assert specs["PF_LAST_ACTION"] == ["PF_GROUP_MAIN"]          # one level up — a cross-region field
    assert "PF_CHECKBOX_TRUE" in specs and "PF_EDIT_DATE" in specs


def test_enumerate_capture_fields_includes_cyrillic():
    """Card 98 #1: the sweep also enumerates Cyrillic-named fields (their query paths ride the 0x97 UTF-16
    envelope, in Group[Группа1]) — Контрагент / ПолеСоСпискомВыбораСтрока were missed by the ASCII-only regex."""
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", srv._repo_root()))
    specs = dict(srv._enumerate_capture_fields(bootstrap))
    assert specs["Контрагент"] == ["Группа1"]
    assert specs["ПолеСоСпискомВыбораСтрока"] == ["Группа1"]


def test_retarget_read_to_cyrillic_field_builds_utf16_path():
    """The per-field rewriter retargets the ASCII PF_EDIT_STRING read to a Cyrillic field via the UTF-16
    (0x97) envelope, reproducing the genuine Cyrillic value-read frame length."""
    from qa_mcp.protocol.frames import MANAGER_TO_CLIENT
    from qa_mcp.protocol.native_write import _read_chunks
    from qa_mcp.protocol.element_ref import extract_element_paths_utf16, parse_element_path

    cap = resolve_capture_dir("tm-v1-ro-batchQ3", srv._repo_root())
    mgr = _read_chunks(cap, MANAGER_TO_CLIENT)
    out = srv._retarget_read_to_groups(mgr[218], "PF_EDIT_STRING", "Контрагент", ["Группа1"])
    assert any(parse_element_path(p).name == "Контрагент" for p in extract_element_paths_utf16(out))
    assert len(out) == len(mgr[300])   # == the genuine Контрагент read frame


# --- Card 98 change-1 generalization: live field enumeration from the descriptor (no per-form capture) ---

def test_extract_descriptor_fields_ascii_and_utf16():
    """The live get_form_analysis descriptor enumerates `(Group[g].)+EditField[name]` paths — ASCII and UTF-16
    (Cyrillic). extract_descriptor_fields parses both into (name, group-chain), the live _enumerate_capture_fields."""
    from qa_mcp.protocol.responses import extract_descriptor_fields

    blob = (
        b"junk Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[PF_EDIT_STRING] 81 fa more"
        + b"Group[PF_GROUP_MAIN].EditField[PF_LAST_ACTION]xx"
        + "Group[Группа1].EditField[Контрагент]".encode("utf-16-le")
    )
    specs = dict(extract_descriptor_fields(blob))
    assert specs["PF_EDIT_STRING"] == ["PF_GROUP_MAIN", "PF_GROUP_EDITS"]
    assert specs["PF_LAST_ACTION"] == ["PF_GROUP_MAIN"]
    assert specs["Контрагент"] == ["Группа1"]                       # Cyrillic group + leaf via UTF-16


def test_extract_descriptor_fields_zero_group_record_form():
    """Card 98 change-5 — a catalog RECORD form's object-attribute fields sit DIRECTLY under ManagedForm (no
    enclosing Group, e.g. demo Валюты: `ManagedForm[F].EditField[Наименование]`). extract_descriptor_fields now
    captures them with an empty group-chain, while a dynlist COLUMN (`Table[Список].EditField[col]`) is NOT a
    form-field and stays excluded."""
    from qa_mcp.protocol.responses import extract_descriptor_fields

    F = "b1757f82-58e1-4752-a98d-d604ad8537e2"
    blob = (
        f"SecondaryFrame[s].ManagedForm[{F}].EditField[Naming]".encode("utf-16-le")  # zero-group, UTF-16
        + b"  " + f"ManagedForm[{F}].EditField[PF_CODE]".encode("latin1")            # zero-group, ASCII
        + b"  " + f"ManagedForm[{F}].Table[Spisok].EditField[Col1]".encode("latin1")  # a COLUMN — excluded
        + b"  Group[G].EditField[InGroup]"                                           # group-nested (existing)
    )
    specs = dict(extract_descriptor_fields(blob))
    assert specs["Naming"] == [] and specs["PF_CODE"] == []          # zero-group form-fields, empty chain
    assert specs["InGroup"] == ["G"]                                 # group-nested still works
    assert "Col1" not in specs                                       # the dynlist column is not a form-field


def test_splice_descriptor_query_retargets_form_path():
    from qa_mcp.protocol.native_write import splice_descriptor_query, DESCRIPTOR_QUERY_PREPATH

    rendered = b"HDR" + bytes(20) + b"\xcb\x23\x95" + b"valueread-body" + b"\x66\x53\xb2\xa6"
    s, f = "11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222"
    q = splice_descriptor_query(rendered, s, f)
    header = rendered[: rendered.rfind(b"\xcb\x23\x95") + 3]
    assert q.startswith(header + DESCRIPTOR_QUERY_PREPATH)         # live header + descriptor nonce
    assert f"SecondaryFrame[{s}].ManagedForm[{f}]".encode() in q   # form path retargeted to live GUIDs
    assert q.endswith(b"\x66\x53\xb2\xa6")                         # frame tail preserved


def test_read_form_descriptor_enumerate_live_arg(monkeypatch):
    captured = {}
    monkeypatch.setattr(srv, "_read_form_descriptor",
                        lambda **k: captured.update(k) or {"fields": {}, "field_count": 0, "queried": 0})
    srv.read_form_descriptor(enumerate_live=True, gherkin=False)
    assert captured["enumerate_live"] is True


_FACAP = srv._repo_root() / "runtime/protocol-research/captures/genuine-card98-formanalysis-20260620"


def test_extract_descriptor_fields_on_genuine_capture():
    import pytest
    if not (_FACAP / "traffic.jsonl").exists():
        pytest.skip("genuine form-analysis capture not present")
    from qa_mcp.protocol.frames import CLIENT_TO_MANAGER
    from qa_mcp.protocol.native_write import _read_chunks
    from qa_mcp.protocol.responses import extract_descriptor_fields

    desc = b"".join(_read_chunks(_FACAP, CLIENT_TO_MANAGER)[44:47])
    specs = dict(extract_descriptor_fields(desc))
    assert len(specs) >= 46                                        # the full live field list (incl. Cyrillic)
    assert specs["PF_EDIT_STRING"] == ["PF_GROUP_MAIN", "PF_GROUP_EDITS"]
    assert "Контрагент" in specs and "ПолеСоСпискомВыбораСтрока" in specs


# --- Card 98 change-1: open-any-form wrapper (navigate + resolve F + full element tree) ---

def test_extract_descriptor_elements_full_tree():
    """extract_descriptor_elements enumerates EVERY element kind (the ui_read_tree surface), ASCII + UTF-16."""
    from qa_mcp.protocol.responses import extract_descriptor_elements

    blob = (
        b"x Group[PF_GROUP_MAIN]. Table[PF_TABLE].EditField[PF_COL] Button[PF_ADD] y"
        + "Table[Список]".encode("utf-16-le") + b"  " + "Button[ФормаСоздать]".encode("utf-16-le")
    )
    els = extract_descriptor_elements(blob)
    pairs = {(e["kind"], e["name"]) for e in els}
    assert ("Group", "PF_GROUP_MAIN") in pairs
    assert ("Table", "PF_TABLE") in pairs and ("EditField", "PF_COL") in pairs
    assert ("Button", "PF_ADD") in pairs
    assert ("Table", "Список") in pairs and ("Button", "ФормаСоздать") in pairs   # Cyrillic via UTF-16


def test_splice_navigate_two_frames_retargets_link():
    from qa_mcp.protocol.native_write import splice_navigate, NAVIGATE_GENUINE_LINK

    rendered = b"HDR" + bytes(20) + b"\xcb\x23\x95" + b"vr" + b"\x66\x53\xb2\xa6"
    frames = splice_navigate(rendered, "e1cib/list/Справочник.Контрагенты")
    assert len(frames) == 2                                              # the genuine navigate is a 2-frame request
    for fr in frames:
        assert "e1cib/list/Справочник.Контрагенты".encode("utf-16-le") in fr
        assert NAVIGATE_GENUINE_LINK.encode("utf-16-le") not in fr      # genuine link fully retargeted
        assert fr.endswith(b"\x66\x53\xb2\xa6")
    assert b"\x88\x82\x81\xf7" in frames[0] and b"\x81\x81\x81\xf7" in frames[1]  # the two opcode variants


def test_splice_header_no_form_is_byte_identical_to_fixture_render():
    """Card 98 change-5 — _splice_header_no_form builds the value-read splice header (up to cb-23-95) WITHOUT a
    form open: its only live fields are ack_guid @2 + sequence @19 (both from bootstrap); the form GUIDs sit
    AFTER the marker, so a placeholder render of frame 218 yields a header BYTE-IDENTICAL to a real-GUID render —
    no fixture needed to graft a session-live splice header."""
    from pathlib import Path
    from types import SimpleNamespace
    from qa_mcp.protocol.templates import ProtocolTemplates

    tpl = ProtocolTemplates.load((srv._repo_root() / srv.VALUE_READ_TEMPLATES).resolve())
    ack, seq = "a1d6981e-f0c8-be46-8a71-4a259a654dbb", 27000
    handle = SimpleNamespace(templates=tpl, state=SimpleNamespace(ack_guid=ack, frame4_sequence=seq))
    header = srv._splice_header_no_form(handle)
    assert header.endswith(b"\xcb\x23\x95") and len(header) == 51
    # a render with REAL form GUIDs yields the same header[0:51] (the form GUIDs are after the marker)
    real = tpl.render(218, ack, seq, managed_form_guid="fa3103a3-9357-4522-aa41-9c9385a61d01",
                      secondary_frame_guid="12345678-1234-1234-1234-123456789abc").payload
    assert header == real[: real.rfind(b"\xcb\x23\x95") + 3]


def test_splice_navigate_main_frame_retarget():
    """Card 98 change-5 — splice_navigate(main_frame=…) retargets the desktop MainFrame source GUID so a
    config-agnostic open navigates from the LIVE desktop (the default keeps the genuine GUID for vanessa_client)."""
    from qa_mcp.protocol.native_write import splice_navigate, NAVIGATE_GENUINE_MAINFRAME

    rendered = b"HDR" + bytes(20) + b"\xcb\x23\x95" + b"vr" + b"\x66\x53\xb2\xa6"
    live_mf = "deadbeef-0000-1111-2222-333344445555"
    frames = splice_navigate(rendered, "e1cib/list/Справочник.Контрагенты", main_frame=live_mf)
    for fr in frames:
        assert live_mf.encode("latin1") in fr                               # retargeted to the live desktop
        assert NAVIGATE_GENUINE_MAINFRAME.encode("latin1") not in fr        # genuine MainFrame fully replaced
    # default (no main_frame) keeps the genuine GUID — vanessa_client's desktop GUID is deterministic
    default = splice_navigate(rendered, "e1cib/list/Справочник.Контрагенты")
    assert NAVIGATE_GENUINE_MAINFRAME.encode("latin1") in default[0]


def test_splice_table_cell_read_matches_genuine_shape():
    """Card 98 — splice_table_cell_read builds the decoded table-cell read command: <header> <nonce> <Table path
    block> 88 81 81 e0 4b 55 eb 53 <column block> <pad> <tail>. ASCII (fixture) + Cyrillic (dynlist) both encode
    via the 0x9a/0x97 envelope. Asserted against the genuine genuine-card98-tableread structure."""
    from qa_mcp.protocol.native_write import (
        splice_table_cell_read, TABLE_READ_NONCE, TABLE_READ_SUFFIX, TABLE_READ_TAIL,
    )

    rendered = b"HDR" + bytes(20) + b"\xcb\x23\x95" + b"vr" + b"\x66\x53\xb2\xa6"
    s, f = "8e999279-8c89-476f-8fc4-3aad53a42666", "5be66bd6-6634-4efd-b1c8-a17b42b91692"
    cmd = splice_table_cell_read(rendered, s, f, ["PF_GROUP_MAIN"], "PF_TABLE_ITEMS", "PF_TABLE_TEXT")
    assert TABLE_READ_NONCE in cmd and TABLE_READ_SUFFIX in cmd and cmd.endswith(TABLE_READ_TAIL)
    # ASCII path + column ride the 0x9a string envelope
    assert b"\x9a" + bytes([len(f"SecondaryFrame[{s}].ManagedForm[{f}].Group[PF_GROUP_MAIN].Table[PF_TABLE_ITEMS]")])\
        + f"SecondaryFrame[{s}].ManagedForm[{f}].Group[PF_GROUP_MAIN].Table[PF_TABLE_ITEMS]".encode("latin1") in cmd
    assert b"\x9a\x0dPF_TABLE_TEXT" in cmd                                # column name block (0x9a, len 13)
    # a Cyrillic dynlist column rides the 0x97 UTF-16 envelope
    cyr = splice_table_cell_read(rendered, s, f, [], "Список", "Наименование")
    assert b"\x97\x0c" + "Наименование".encode("utf-16-le") in cyr        # 12 chars UTF-16
    assert "Table[Список]".encode("utf-16-le") in cyr


def test_table_groups_discovery_ascii_and_utf16():
    """_table_groups finds the Group chain enclosing Table[T] — ASCII (fixture PF_GROUP_MAIN.Table[PF_TABLE_ITEMS])
    and UTF-16 (a dynlist Table[Список] directly under ManagedForm → no groups)."""
    ascii_blob = b"x Group[PF_GROUP_MAIN].Table[PF_TABLE_ITEMS] y"
    assert srv._table_groups(ascii_blob, "PF_TABLE_ITEMS") == ["PF_GROUP_MAIN"]
    u16 = b"junk" + "ManagedForm[x].Table[Список]".encode("utf-16-le") + b"more"
    assert srv._table_groups(u16, "Список") == []                   # dynlist Table directly under ManagedForm


def test_read_table_cell_tool_shape(monkeypatch):
    monkeypatch.setattr(srv, "_read_table_cell",
                        lambda **k: {"table": k["table"], "column": k["column"], "value": "PF_ROW_001_TEXT",
                                     "groups": ["PF_GROUP_MAIN"], "opened": None})
    r = srv.read_table_cell("PF_TABLE_ITEMS", "PF_TABLE_TEXT")
    assert r["value"] == "PF_ROW_001_TEXT" and r["table"] == "PF_TABLE_ITEMS"


def test_read_list_column_tool_shape(monkeypatch):
    # read_list_column now drives the FAITHFUL FULL-REPLAY path (derive + read_list_column_replay), not the splice
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_column_replay",
                        lambda t, open_link=None, column=None, **k: {
                            "nav_link": open_link, "column": column, "value": "EUR", "captured_value": t.captured_value})
    r = srv.read_list_column("Наименование", "e1cib/list/Справочник.Валюты")
    assert r["table"] == "Список" and r["column"] == "Наименование"   # dynlist convenience defaults table=Список
    assert r["value"] == "EUR" and r["nav_link"] == "e1cib/list/Справочник.Валюты"


def test_resolve_list_table_uses_single_descriptor_table(monkeypatch):
    monkeypatch.setattr(
        srv,
        "_read_form_descriptor",
        lambda **k: {
            "opened": "Валюты",
            "elements": [{"kind": "Table", "name": "Валюты"}],
            "element_count": 1,
        },
    )

    table, meta = srv._resolve_list_table_for_read(
        host="127.0.0.1", port=15381, open_link="e1cib/list/Справочник.Валюты")

    assert table == "Валюты"
    assert meta["available_tables"] == ["Валюты"]


def test_resolve_list_table_rejects_wrong_explicit_table(monkeypatch):
    monkeypatch.setattr(
        srv,
        "_read_form_descriptor",
        lambda **k: {
            "opened": "Валюты",
            "elements": [{"kind": "Table", "name": "Валюты"}],
            "element_count": 1,
        },
    )

    table, diagnostic = srv._resolve_list_table_for_read(
        host="127.0.0.1", port=15381, open_link="e1cib/list/Справочник.Валюты", requested_table="Список")

    assert table is None
    assert diagnostic["error"] == "list-table-not-found"
    assert diagnostic["requested_table"] == "Список"
    assert diagnostic["available_tables"] == ["Валюты"]
    assert "genuinely empty" not in diagnostic["reason"]


def test_resolve_list_table_reports_ambiguous_descriptor(monkeypatch):
    monkeypatch.setattr(
        srv,
        "_read_form_descriptor",
        lambda **k: {
            "opened": "Документ",
            "elements": [{"kind": "Table", "name": "Товары"}, {"kind": "Table", "name": "Услуги"}],
            "element_count": 2,
        },
    )

    table, diagnostic = srv._resolve_list_table_for_read(
        host="127.0.0.1", port=15381, open_link="e1cib/list/Документ.Заказ")

    assert table is None
    assert diagnostic["error"] == "list-table-ambiguous"
    assert diagnostic["available_tables"] == ["Товары", "Услуги"]


def test_resolve_list_table_retries_empty_descriptor_then_succeeds(monkeypatch):
    # Cold-client first-read hardening: an empty descriptor (opened=None, 0 elements) is a form
    # that has not rendered yet (heavy config warming up), so the resolver retries and self-heals.
    monkeypatch.setattr(srv, "_SETTINGS", dataclasses.replace(
        srv._SETTINGS, descriptor_warmup_attempts=3, descriptor_warmup_delay_sec=0.0))
    calls = {"n": 0}

    def fake_descriptor(**_k):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"opened": None, "elements": [], "element_count": 0}
        return {"opened": "Валюты", "elements": [{"kind": "Table", "name": "Валюты"}], "element_count": 1}

    monkeypatch.setattr(srv, "_read_form_descriptor", fake_descriptor)

    table, meta = srv._resolve_list_table_for_read(
        host="127.0.0.1", port=15381, open_link="e1cib/list/Справочник.Валюты")

    assert table == "Валюты"
    assert calls["n"] == 2  # retried once past the cold read, then succeeded
    assert meta.get("descriptor_warmup_retries") == 1


def test_resolve_list_table_reports_warming_up_after_retries(monkeypatch):
    monkeypatch.setattr(srv, "_SETTINGS", dataclasses.replace(
        srv._SETTINGS, descriptor_warmup_attempts=2, descriptor_warmup_delay_sec=0.0))
    calls = {"n": 0}

    def always_empty(**_k):
        calls["n"] += 1
        return {"opened": None, "elements": [], "element_count": 0}

    monkeypatch.setattr(srv, "_read_form_descriptor", always_empty)

    table, diagnostic = srv._resolve_list_table_for_read(
        host="127.0.0.1", port=15381, open_link="e1cib/list/Справочник.Валюты")

    assert table is None
    assert calls["n"] == 2  # exhausted the bounded warm-up attempts (no infinite retry)
    assert diagnostic["error"] == "list-table-unresolved"
    assert diagnostic.get("descriptor_empty") is True
    assert diagnostic.get("warmup_attempts") == 2
    assert "warming up" in diagnostic["reason"]


def test_read_list_grid_uses_resolved_descriptor_table(monkeypatch):
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch, table="Валюты")
    captured = {}
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))

    def fake_grid(t, open_link=None, columns=None, max_rows=25, table=None, **k):
        captured["table"] = table
        return {
            "table": table,
            "nav_link": open_link,
            "row_count": 1,
            "rows": [{"НаименованиеПолное": "Доллар США", "Код": "840"}],
        }

    monkeypatch.setattr(nw, "read_list_grid_replay", fake_grid)
    r = srv.read_list_grid(
        "e1cib/list/Справочник.Валюты",
        ["НаименованиеПолное", "Код"],
        max_rows=10,
    )

    assert captured["table"] == "Валюты"
    assert r["table"] == "Валюты"
    assert r["rows"][0]["Код"] == "840"
    assert "reason" not in r


def test_read_list_column_diagnostic_skips_wrong_table_replay(monkeypatch):
    import qa_mcp.protocol.native_write as nw

    monkeypatch.setattr(
        srv,
        "_resolve_list_table_for_read",
        lambda **k: (None, {
            "ok": False,
            "error": "list-table-not-found",
            "phase": "list_read",
            "open_link": k["open_link"],
            "requested_table": k["requested_table"],
            "available_tables": ["Валюты"],
            "reason": "requested table is not present; the list was not read",
        }),
    )
    monkeypatch.setattr(nw, "read_list_column_replay",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("replay should not run")))

    r = srv.read_list_column("Код", "e1cib/list/Справочник.Валюты", table="Список")

    assert r["ok"] is False
    assert r["error"] == "list-table-not-found"
    assert r["available_tables"] == ["Валюты"]


def test_read_list_row_tool_shape(monkeypatch):
    # read_list_row reads several columns of the current row in one cold session (multi-read engine)
    import qa_mcp.protocol.native_write as nw

    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_row_replay",
                        lambda t, open_link=None, columns=None, **k: {
                            "nav_link": open_link,
                            "row": {c: {"Код": "000000001", "Наименование": "Обувь"}[c] for c in columns}})
    r = srv.read_list_row("e1cib/list/Справочник.Товары", ["Код", "Наименование"])
    assert r["table"] == "Список" and r["nav_link"] == "e1cib/list/Справочник.Товары"
    assert r["row"] == {"Код": "000000001", "Наименование": "Обувь"}


def test_read_list_grid_tool_shape(monkeypatch):
    # read_list_grid iterates rows via the genuine next-row block (decoded action GUID d267315b…)
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    assert nw.NEXT_ROW_ACTION_GUID == "d267315b-1d90-0041-8c4e-c1ff077822d5"
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, **k: {
                            "nav_link": open_link, "row_count": 3,
                            "rows": [{"Наименование": v} for v in ("Обувь", "Продукты", "Услуги")]})
    r = srv.read_list_grid("e1cib/list/Справочник.Товары", ["Наименование"], max_rows=10)
    assert r["table"] == "Список" and r["row_count"] == 3
    assert [row["Наименование"] for row in r["rows"]] == ["Обувь", "Продукты", "Услуги"]


def test_read_list_grid_flat_selects_flat_capture(monkeypatch):
    # read_list_grid(flat=True) reads the flat «Список» view (nested items); flat selects the genuine flat capture
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    seen = {}
    monkeypatch.setattr(srv, "resolve_capture_dir", lambda name, root=None: seen.__setitem__("cap", name) or name)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Bosch1234"))
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, **k: {
                            "nav_link": open_link, "row_count": 1, "rows": [{"Наименование": "Bosch1234"}]})
    srv.read_list_grid("e1cib/list/Справочник.Товары", ["Наименование"], flat=True)
    assert seen["cap"] == "nextrow-flat"   # flat → the view-switch capture
    srv.read_list_grid("e1cib/list/Справочник.Товары", ["Наименование"])
    assert seen["cap"] == "nextrow"         # default → current view


def test_read_list_grid_poll_recovers_transient_zero(monkeypatch):
    # Card 125 Change 5 — a transient 0-rows read (async / not-yet-loaded dynamic list) is NOT accepted: the
    # engine forces a refresh, sweeps to a clean cold state and re-reads (poll-until-stable), recovering the rows.
    # The result flags clean_state_swept, records the refresh method + poll outcome, and carries no diagnostic.
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    calls = {"n": 0}

    def fake_replay(t, open_link=None, columns=None, max_rows=25, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"nav_link": open_link, "row_count": 0, "rows": []}          # not-yet-loaded → empty
        return {"nav_link": open_link, "row_count": 2,
                "rows": [{"Наименование": "EUR"}, {"Наименование": "USD"}]}       # after refresh+sweep → rows

    monkeypatch.setattr(nw, "read_list_grid_replay", fake_replay)
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: True)           # a display backend is reachable
    r = srv.read_list_grid("e1cib/list/Справочник.Валюты", ["Наименование"])
    assert calls["n"] == 2                            # read, reset, re-read (no re-read on the happy path)
    assert r["row_count"] == 2 and r["clean_state_swept"] is True
    assert r["list_refresh"]["method"] == "f5" and r["list_refresh"]["poll_outcome"] == "nonzero"
    assert "reason" not in r                          # recovered → no diagnostic


def test_read_list_grid_zero_without_backend_surfaces_reason(monkeypatch):
    # Card 125 Change 5 — when no display backend is reachable (refresh AND sweep both unavailable), a 0 cannot be
    # improved: the read does NOT burn extra cold reads and carries an honest "could-not-refresh" diagnostic
    # rather than a silent empty.
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    calls = {"n": 0}

    def fake_replay(t, open_link=None, columns=None, max_rows=25, **k):
        calls["n"] += 1
        return {"nav_link": open_link, "row_count": 0, "rows": []}

    monkeypatch.setattr(nw, "read_list_grid_replay", fake_replay)
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)          # no backend → no sweep
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("none", "no display backend"))  # no refresh
    r = srv.read_list_grid("e1cib/list/Справочник.Валюты", ["Наименование"])
    assert calls["n"] == 1                            # no re-read when nothing can change the list state
    assert r["row_count"] == 0 and "clean_state_swept" not in r
    assert r["list_refresh"]["method"] == "none"
    assert "reason" in r and "could not be force-refreshed" in r["reason"]
    assert r["ok"] is False
    assert r["error"] == "list-read-uncertain-zero"
    assert r["data_confidence"] == "unknown"
    assert r["underlying_error"]["error"] == "window-discovery-unconfirmed"


def test_read_list_grid_foreground_denied_refresh_is_actionable(monkeypatch):
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    refresh_error = {
        "ok": False,
        "error": "foreground-denied",
        "detail": "SetForegroundWindow denied",
        "status": 409,
        "tool": "force_list_refresh",
        "mode": "remote-client",
    }
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("none", refresh_error))
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, **k: {
                            "nav_link": open_link, "row_count": 0, "rows": []})

    r = srv.read_list_grid("e1cib/list/Справочник.Валюты", ["Наименование"])

    assert r["list_refresh"]["method"] == "none"
    assert r["list_refresh"]["error"]["error"] == "foreground-denied"
    assert "foreground-denied" in r["reason"]
    assert "no display backend was reachable" not in r["reason"]
    assert r["ok"] is False
    assert r["data_confidence"] == "unknown"
    assert r["underlying_error"]["error"] == "foreground-denied"


def test_read_list_grid_unreachable_refresh_keeps_install_guidance(monkeypatch):
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    refresh_error = {
        "ok": False,
        "error": "host-agent-unreachable",
        "detail": "Windows host display agent is unreachable from the container.",
        "install_command": "powershell -ExecutionPolicy Bypass -File .\\host-agent\\install-windows-host-agent.ps1",
        "tool": "force_list_refresh",
        "mode": "remote-client",
    }
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("none", refresh_error))
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, **k: {
                            "nav_link": open_link, "row_count": 0, "rows": []})

    r = srv.read_list_grid("e1cib/list/Справочник.Валюты", ["Наименование"])

    assert r["list_refresh"]["error"]["error"] == "host-agent-unreachable"
    assert "install-windows-host-agent.ps1" in r["list_refresh"]["note"]
    assert "host-agent-unreachable" in r["reason"]
    assert r["ok"] is False
    assert r["underlying_error"]["error"] == "host-agent-unreachable"


def test_read_list_grid_sweep_failure_remains_structured(monkeypatch):
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    sweep_error = {
        "ok": False,
        "error": "foreground-denied",
        "detail": "Escape sweep foreground denied",
        "status": 409,
        "tool": "cold_state_sweep",
        "mode": "remote-client",
    }
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("f5", None))

    def fake_sweep(*args, **kwargs):
        if kwargs.get("return_error"):
            return False, sweep_error
        return False

    monkeypatch.setattr(srv, "_cold_state_sweep", fake_sweep)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, **k: {
                            "nav_link": open_link, "row_count": 0, "rows": []})

    r = srv.read_list_grid("e1cib/list/Справочник.Валюты", ["Наименование"])

    assert r["list_refresh"]["sweep_error"]["error"] == "foreground-denied"
    assert "clean-state sweep failed" in r["reason"]
    assert "Escape sweep foreground denied" in r["reason"]
    assert r["ok"] is False
    assert r["underlying_error"]["error"] == "foreground-denied"


def test_read_list_grid_remote_uncertain_zero_attaches_window_diagnostic(monkeypatch):
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch, table="Валюты")
    refresh_error = {
        "ok": False,
        "error": "window-not-found",
        "detail": "target window not found",
        "status": 422,
        "tool": "force_list_refresh",
        "mode": "remote-client",
    }
    remote_diag = {
        "mode": "remote-client",
        "target_window": "class:V8TopLevelFrame",
        "windows": [{"hwnd": "0x42", "class": "V8TopLevelFrameSDI", "title": "Бухгалтерия", "pid": 1234}],
        "visible_cells": {"ok": True, "cells": ["Российский рубль Наименование валюты"]},
    }
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("none", refresh_error))
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    monkeypatch.setattr(srv, "_remote_client_list_diagnostic", lambda tool: remote_diag)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, table=None, **k: {
                            "nav_link": open_link, "row_count": 0, "rows": []})

    r = srv.read_list_grid("e1cib/list/Справочник.Валюты", ["Наименование"])

    assert r["ok"] is False
    assert r["data_confidence"] == "unknown"
    assert r["underlying_error"]["error"] == "window-not-found"
    assert r["remote_window_diagnostic"]["windows"][0]["class"] == "V8TopLevelFrameSDI"
    assert "Российский рубль" in r["remote_window_diagnostic"]["visible_cells"]["cells"][0]


# --- Card 125 Change 5: dynlist refresh-and-poll engine (_ensure_list_fresh) -----------------------------------

def _counted_reader(counts):
    # A fake read_once returning the scripted row counts in order; records how many reads happened.
    state = {"i": 0, "reads": 0}

    def read_once():
        c = counts[min(state["i"], len(counts) - 1)]
        state["i"] += 1
        state["reads"] += 1
        return {"row_count": c}

    return read_once, state


def test_ensure_list_fresh_returns_rows_on_first_nonzero_read(monkeypatch):
    # A current list (rows present on the first post-refresh read) returns immediately — no extra cold reads.
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    read_once, state = _counted_reader([5])
    out, meta = srv._ensure_list_fresh(read_once=read_once, count_of=lambda o: o["row_count"],
                                       refresh=True, poll_attempts=4, settle_sec=0)
    assert out["row_count"] == 5
    assert state["reads"] == 1 and meta["poll_outcome"] == "nonzero"
    assert meta["refresh"] is True and meta["refresh_method"] == "f5"


def test_ensure_list_fresh_stabilizes_on_equal_zero_counts(monkeypatch):
    # Two equal successive reads (0, 0) => the list is stably empty; the poll stops (does not run out the budget).
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    read_once, state = _counted_reader([0, 0, 0, 0])
    out, meta = srv._ensure_list_fresh(read_once=read_once, count_of=lambda o: o["row_count"],
                                       refresh=True, poll_attempts=6, settle_sec=0)
    assert out["row_count"] == 0
    assert state["reads"] == 2 and meta["poll_outcome"] == "stable"


def test_ensure_list_fresh_wait_for_rows_polls_through_transient_zeros(monkeypatch):
    # wait_for_rows overrides the stable-empty early stop: it keeps polling through not-yet-loaded 0s until the
    # expected minimum appears, and records that it was met.
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    read_once, state = _counted_reader([0, 0, 3])
    out, meta = srv._ensure_list_fresh(read_once=read_once, count_of=lambda o: o["row_count"],
                                       refresh=True, wait_for_rows=2, poll_attempts=6, settle_sec=0)
    assert out["row_count"] == 3 and state["reads"] == 3
    assert meta["poll_outcome"] == "wait_for_rows_met"
    assert meta["wait_for_rows"] == 2 and meta["wait_for_rows_met"] is True


def test_ensure_list_fresh_wait_for_rows_unmet_within_budget(monkeypatch):
    # If the expected minimum never appears within the poll budget, wait_for_rows_met is False (not a bare 0).
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    read_once, state = _counted_reader([0, 0, 0])
    out, meta = srv._ensure_list_fresh(read_once=read_once, count_of=lambda o: o["row_count"],
                                       refresh=True, wait_for_rows=2, poll_attempts=3, settle_sec=0)
    assert out["row_count"] == 0 and state["reads"] == 3
    assert meta["poll_outcome"] == "timeout" and meta["wait_for_rows_met"] is False


def test_ensure_list_fresh_optout_does_not_refresh_and_records_it(monkeypatch):
    # refresh=False must NOT force a refresh, and the meta records "no refresh applied" so an absence assertion is
    # explicit rather than silently refreshed.
    called = {"refresh": 0}
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: called.__setitem__("refresh", called["refresh"] + 1) or ("f5", None))
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    read_once, state = _counted_reader([0])
    out, meta = srv._ensure_list_fresh(read_once=read_once, count_of=lambda o: o["row_count"],
                                       refresh=False, poll_attempts=4, settle_sec=0)
    assert called["refresh"] == 0                      # opt-out never touched the display backend
    assert state["reads"] == 1                         # nothing could change the empty state → no re-read
    assert meta["refresh"] is False and meta["refresh_method"] == "none"
    assert "opt-out" in meta["refresh_note"]


def test_read_list_grid_empty_after_refresh_is_unambiguous(monkeypatch):
    # Card 125 Change 5, empty-vs-not-loaded disambiguation: with a display backend, a genuinely empty list reports
    # "empty (refreshed)" — the legacy "EITHER empty OR cold-boundary" ambiguity is gone on the refreshed path.
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, **k: {
                            "nav_link": open_link, "row_count": 0, "rows": []})
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: True)           # backend reachable → can requery
    r = srv.read_list_grid("e1cib/list/Справочник.ПустойСписок", ["Наименование"])
    assert r["row_count"] == 0
    assert r["ok"] is True
    assert r["data_confidence"] == "confirmed"
    assert r["list_refresh"]["method"] == "f5" and r["list_refresh"]["poll_outcome"] == "stable"
    assert "empty (refreshed)" in r["reason"] and "cold-client boundary" not in r["reason"]


def test_read_list_grid_zero_without_descriptor_sweep_is_cautious(monkeypatch):
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch, table="Валюты")
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, table=None, **k: {
                            "nav_link": open_link, "row_count": 0, "rows": []})
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("f5", None))
    r = srv.read_list_grid("e1cib/list/Справочник.Валюты", ["Наименование"])
    assert r["table"] == "Валюты"
    assert "descriptor-open form state was not confirmed clean" in r["reason"]
    assert "genuinely empty" not in r["reason"]
    assert r["ok"] is False
    assert r["underlying_error"]["error"] == "window-discovery-unconfirmed"


def test_read_list_grid_wait_for_rows_met_surfaced(monkeypatch):
    # read_list_grid(wait_for_rows=N) blocks through transient 0s and surfaces wait_for_rows_met on the result.
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    seq = iter([0, 0, 2])
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, **k: (lambda c: {
                            "nav_link": open_link, "row_count": c,
                            "rows": [{"Наименование": f"r{i}"} for i in range(c)]})(next(seq)))
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: True)
    r = srv.read_list_grid("e1cib/list/Справочник.Договоры", ["Наименование"], wait_for_rows=2)
    assert r["row_count"] == 2
    assert r["list_refresh"]["wait_for_rows"] == 2 and r["list_refresh"]["wait_for_rows_met"] is True


def test_read_list_grid_refresh_optout_records_no_refresh(monkeypatch):
    # refresh=False opts out: the grid read does not force a refresh and marks refresh=False so an absence
    # assertion is not masked by an implicit refresh.
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_grid_replay",
                        lambda t, open_link=None, columns=None, max_rows=25, **k: {
                            "nav_link": open_link, "row_count": 0, "rows": []})
    called = {"refresh": 0}
    monkeypatch.setattr(srv, "_force_list_refresh",
                        lambda *a, **k: called.__setitem__("refresh", called["refresh"] + 1) or ("f5", None))
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    r = srv.read_list_grid("e1cib/list/Справочник.Валюты", ["Наименование"], refresh=False)
    assert called["refresh"] == 0                      # opt-out never forced a refresh
    assert r["list_refresh"]["refresh"] is False and r["list_refresh"]["method"] == "none"
    assert "reason" in r and "opt-out" in r["reason"]
    assert r["ok"] is False
    assert r["data_confidence"] == "unknown"


def test_read_list_column_uncertain_none_value_fails_loud(monkeypatch):
    import qa_mcp.protocol.native_write as nw

    _stub_list_table(monkeypatch, table="Валюты")
    refresh_error = {
        "ok": False,
        "error": "window-not-found",
        "detail": "target window not found",
        "tool": "force_list_refresh",
        "mode": "remote-client",
    }
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("none", refresh_error))
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_column_replay",
                        lambda t, open_link=None, column=None, table=None, **k: {
                            "column": column, "nav_link": open_link, "value": None, "captured_value": "Обувь"})

    r = srv.read_list_column("Наименование", "e1cib/list/Справочник.Валюты")

    assert r["ok"] is False
    assert r["data_confidence"] == "unknown"
    assert r["underlying_error"]["error"] == "window-not-found"


def test_read_list_row_all_none_after_refresh_error_fails_loud(monkeypatch):
    import qa_mcp.protocol.native_write as nw

    refresh_error = {
        "ok": False,
        "error": "window-not-found",
        "detail": "target window not found",
        "tool": "force_list_refresh",
        "mode": "remote-client",
    }
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("none", refresh_error))
    monkeypatch.setattr(srv, "_cold_state_sweep", lambda *a, **k: False)
    monkeypatch.setattr(nw, "derive_read_list_column",
                        lambda cap, **k: nw.ReadListColumnTemplate(cap, "e1cib/list/Справочник.Товары",
                                                                   "Наименование", "Обувь"))
    monkeypatch.setattr(nw, "read_list_row_replay",
                        lambda t, open_link=None, columns=None, **k: {
                            "nav_link": open_link, "row": {c: None for c in columns}})

    r = srv.read_list_row("e1cib/list/Справочник.Валюты", ["Наименование", "Код"])

    assert r["ok"] is False
    assert r["data_confidence"] == "unknown"
    assert r["underlying_error"]["error"] == "window-not-found"


def test_search_list_forces_refresh_and_records_it(monkeypatch):
    # Card 125 Change 5: search_list forces a refresh (the enumerated primitive) before filtering, so the filter
    # runs against a current list; the refresh method is recorded. It is refresh-only (a filter has no row count).
    monkeypatch.setattr(srv, "derive_search_list", lambda *a, **k: object())
    monkeypatch.setattr(srv, "native_search_list",
                        lambda t, value, host=None, port=None: {"search_field": "SF", "value": value, "echoed": True})
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: ("f5", None))
    r = srv.search_list("Молоко")
    assert r["echoed"] is True and r["list_refresh"]["refresh"] is True and r["list_refresh"]["method"] == "f5"
    # opt-out path records that no refresh was applied
    monkeypatch.setattr(srv, "_force_list_refresh", lambda *a, **k: (_ for _ in ()).throw(AssertionError("refreshed")))
    r2 = srv.search_list("Молоко", refresh=False)
    assert r2["list_refresh"]["refresh"] is False and r2["list_refresh"]["method"] == "none"


def test_read_list_row_where_uses_byvalue_replay(monkeypatch):
    # read_list_row(where={col: value}) positions the dynlist to the WHERE row via the by-value replay
    import qa_mcp.protocol.native_write as nw

    monkeypatch.setattr(srv, "resolve_capture_dir", lambda name, root=None: name)
    captured = {}

    def fake_byval(cap, where_value, where_column="Наименование", open_link=None, columns=None, **k):
        captured.update(cap=cap, where_value=where_value, where_column=where_column, columns=columns)
        vals = {"Наименование": "Молоко", "Код": "000000026"}
        return {"nav_link": open_link, "where": {where_column: where_value}, "row": {c: vals[c] for c in columns}}

    monkeypatch.setattr(nw, "read_list_row_by_value_replay", fake_byval)
    r = srv.read_list_row("e1cib/list/Справочник.Товары", ["Наименование", "Код"], where={"Наименование": "Молоко"})
    assert captured["cap"] == "rowbyvalue"
    assert captured["where_value"] == "Молоко" and captured["where_column"] == "Наименование"
    assert r["where"] == {"Наименование": "Молоко"} and r["row"]["Код"] == "000000026"


def test_read_list_row_where_rejects_multikey():
    result = srv.read_list_row("e1cib/list/Справочник.Товары", ["Код"], where={"Наименование": "A", "Код": "1"})
    assert result["ok"] is False
    assert result["error"] == "invalid-arguments"
    assert result["tool"] == "read_list_row"


def test_row_select_from_read_frame_shape():
    """Card 98 — row_select_from_read_frame reuses a table-read frame's header+nonce+path prefix and appends the
    go-to-row-by-value suffix: 88 81 81 e1 81 81 82 … c0 4b 53 <search col> eb 53 <search value> <pad> <tail>.
    (Byte-shape only — the suffix is decoded from a FORM table; live on a dynlist it does NOT reposition, so it is
    NOT wired into the tools, kept for a genuine dynlist row-select capture.)"""
    from qa_mcp.protocol.element_ref import encode_element_path_block
    from qa_mcp.protocol.native_write import (
        row_select_from_read_frame, ROW_SELECT_OPCODE, ROW_SELECT_SEP_COLUMN, ROW_SELECT_SEP_VALUE, ROW_SELECT_TAIL,
    )

    # a minimal table-read frame: <prefix> 88 81 81 e0 4b 55 eb 53 <col> <pad> <tail>
    prefix = b"HDR" + bytes(20) + b"\xcb\x23\x95" + b"NONCE" + b"\x97\x0c" + "Список".encode("utf-16le") + b"PATH"
    read_frame = prefix + bytes.fromhex("888181e04b55") + b"\xeb\x53" + encode_element_path_block("Наименование") \
        + b"\x20\x20\x20\x20" + bytes.fromhex("6653b2a6")
    sel = row_select_from_read_frame(read_frame, "Наименование", "Молоко")
    assert sel.startswith(prefix)                       # reuses the live header+nonce+path prefix
    assert ROW_SELECT_OPCODE in sel and sel.endswith(ROW_SELECT_TAIL)
    assert ROW_SELECT_SEP_COLUMN + encode_element_path_block("Наименование") in sel   # search column
    assert ROW_SELECT_SEP_VALUE + encode_element_path_block("Молоко") in sel          # search value
    assert bytes.fromhex("888181e04b55") not in sel     # the read action was replaced, not kept


def test_derive_read_list_column_from_capture():
    """Card 98 — derive_read_list_column reads the genuine list-form capture: nav-link + column present, and the
    captured value the genuine read returned («Обувь», the first Товары row) is recovered for verbatim reference."""
    from qa_mcp.protocol.bootstrap import resolve_capture_dir
    from qa_mcp.protocol.native_write import derive_read_list_column

    cap = resolve_capture_dir("listform-read")
    t = derive_read_list_column(cap)
    assert t.nav_link == "e1cib/list/Справочник.Товары" and t.column == "Наименование"
    assert t.table == "Список"
    assert t.captured_value == "Обувь"


def test_rowbyvalue_capture_shape():
    """Card 98 — the genuine dynlist go-to-row-by-value capture (rowbyvalue) carries the markers
    read_list_row_by_value_replay's defaults assume: a table-read frame, the WHERE column «Наименование»
    (c0 4b 53 <block>) + the match value «Сапоги» (eb 53 <block>) on one go-to-row frame, and the read column
    «Код» (eb 53 <block>) on the read frame. Guards the capture + the function's retarget anchors."""
    from qa_mcp.protocol.bootstrap import resolve_capture_dir
    from qa_mcp.protocol.element_ref import encode_element_path_block
    from qa_mcp.protocol.frames import MANAGER_TO_CLIENT
    from qa_mcp.protocol.native_write import _read_chunks

    mgr = _read_chunks(resolve_capture_dir("rowbyvalue"), MANAGER_TO_CLIENT)
    reads = [i for i, b in enumerate(mgr) if b"\x88\x81\x81\xe0\x4b\x55\xeb\x53" in b]
    assert reads, "no table-read frame in the rowbyvalue capture"
    where_col = b"\xc0\x4b\x53" + encode_element_path_block("Наименование")
    match_val = b"\xeb\x53" + encode_element_path_block("Сапоги")
    read_col = b"\xeb\x53" + encode_element_path_block("Код")
    assert any(where_col in b and match_val in b for b in mgr), "go-to-row frame (WHERE column + match value) absent"
    assert any(read_col in b for b in mgr), "read column «Код» (eb 53 <block>) absent"


def test_retarget_list_read_frame():
    """Card 98 — retarget_list_read_frame swaps the nav-link (UTF-16 + f7 char-count) on a navigate frame and the
    read column block (eb 53 <block>) on the read frame, and is a no-op elsewhere."""
    from qa_mcp.protocol.element_ref import encode_element_path_block
    from qa_mcp.protocol.native_write import retarget_list_read_frame

    old_nav, new_nav = "e1cib/list/Справочник.Товары", "e1cib/list/Справочник.Контрагенты"
    old_cb = b"\xeb\x53" + encode_element_path_block("Наименование")
    new_cb = b"\xeb\x53" + encode_element_path_block("Код")
    # navigate frame: f7 <char-count=0x1c> <nav-link utf-16>
    nav_frame = b"PRE\xf7" + bytes([len(old_nav)]) + old_nav.encode("utf-16le") + b"POST"
    out = retarget_list_read_frame(nav_frame, old_nav=old_nav, new_nav=new_nav, old_col_block=old_cb, new_col_block=new_cb)
    assert new_nav.encode("utf-16le") in out and old_nav.encode("utf-16le") not in out
    assert b"\xf7" + bytes([len(new_nav)]) + new_nav.encode("utf-16le") in out   # char-count fixed
    # read frame: column block swapped
    read_frame = b"X" + old_cb + b"\x20\x20\x20\x20TAIL"
    out2 = retarget_list_read_frame(read_frame, old_nav=old_nav, new_nav=new_nav, old_col_block=old_cb, new_col_block=new_cb)
    assert new_cb in out2 and old_cb not in out2
    # unrelated frame: untouched
    other = b"\x00\x01\x02nothing-here\x03"
    assert retarget_list_read_frame(other, old_nav=old_nav, new_nav=new_nav, old_col_block=old_cb, new_col_block=new_cb) == other
    # verbatim (no retarget): identical
    assert retarget_list_read_frame(read_frame, old_nav=old_nav, new_nav=old_nav, old_col_block=old_cb, new_col_block=old_cb) == read_frame


def test_retarget_list_read_frame_retargets_cyrillic_table_segment():
    from qa_mcp.protocol.element_ref import encode_element_path_block
    from qa_mcp.protocol.native_write import retarget_list_read_frame

    old_path = "SecondaryFrame[11111111-1111-1111-1111-111111111111].ManagedForm[22222222-2222-2222-2222-222222222222].Table[Список]"
    frame = b"HDR" + encode_element_path_block(old_path) + b"\x88\x81\x81\xe0\x4b\x55"
    out = retarget_list_read_frame(
        frame,
        old_nav="e1cib/list/Справочник.Товары",
        new_nav="e1cib/list/Справочник.Валюты",
        old_col_block=b"",
        new_col_block=b"",
        old_table="Список",
        new_table="Валюты",
    )

    assert "Table[Валюты]".encode("utf-16-le") in out
    assert "Table[Список]".encode("utf-16-le") not in out


def test_retarget_list_read_frame_to_data_link():
    """Card 101 — the fixture-free foreground replay retargets the genuine cold list-open nav-link to the TARGET,
    including a DOCUMENT data-link (different prefix AND length): the f7 char-count is recomputed for the new link."""
    from qa_mcp.protocol.native_write import retarget_list_read_frame

    old_nav = "e1cib/list/Справочник.Товары"
    new_nav = "e1cib/data/Документ.Заказ?ref=bbef0050ba5c887711e1fc040faf2b04"
    nav_frame = b"PRE\xf7" + bytes([len(old_nav)]) + old_nav.encode("utf-16le") + b"POST"
    out = retarget_list_read_frame(nav_frame, old_nav=old_nav, new_nav=new_nav, old_col_block=b"", new_col_block=b"")
    assert new_nav.encode("utf-16le") in out and old_nav.encode("utf-16le") not in out
    assert b"\xf7" + bytes([len(new_nav)]) + new_nav.encode("utf-16le") in out   # char-count fixed for the data-link


def test_splice_resolve_form_query():
    from qa_mcp.protocol.native_write import splice_resolve_form_query, RESOLVE_QUERY_PREPATH

    rendered = b"HDR" + bytes(20) + b"\xcb\x23\x95" + b"vr" + b"\x66\x53\xb2\xa6"
    q = splice_resolve_form_query(rendered, "0511e849-76b0-4edf-9c4d-a6a6215eb8b8")
    assert RESOLVE_QUERY_PREPATH in q
    assert b"SecondaryFrame[0511e849-76b0-4edf-9c4d-a6a6215eb8b8]" in q   # S-only (no ManagedForm)
    assert b"ManagedForm[" not in q and q.endswith(b"\x66\x53\xb2\xa6")


def test_read_form_descriptor_open_link_shape(monkeypatch):
    monkeypatch.setattr(srv, "_read_form_descriptor",
                        lambda **k: {"opened": "Контрагенты", "elements": [{"kind": "Table", "name": "Список"}],
                                     "element_count": 1})
    r = srv.read_form_descriptor(open_link="e1cib/list/Справочник.Контрагенты")
    assert r["opened"] == "Контрагенты" and r["element_count"] == 1
    assert "gherkin" not in r                                            # the open_link path returns elements, not fields


def test_open_form_by_link_polls_managed_form_inside_same_session(monkeypatch):
    from qa_mcp.protocol import introspection
    from qa_mcp.protocol import native_write
    from qa_mcp.protocol import responses

    main_guid = "11111111-1111-1111-1111-111111111111"
    secondary_guid = "22222222-2222-2222-2222-222222222222"
    managed_guid = "33333333-3333-3333-3333-333333333333"
    window_snapshots = iter([
        [{"kind": "MainFrame", "guid": main_guid, "caption": "desktop"}],
        [{"kind": "MainFrame", "guid": main_guid, "caption": "desktop"}],
        [
            {"kind": "MainFrame", "guid": main_guid, "caption": "desktop"},
            {"kind": "SecondaryFrame", "guid": secondary_guid, "caption": "Валюты"},
        ],
    ])

    class FakeHandle:
        state = types.SimpleNamespace(received_stream=bytearray())

        def run_action(self, payload, *, query_id):
            if query_id == "resolve-form":
                self.state.received_stream.extend(
                    f"{secondary_guid}].ManagedForm[{managed_guid}]".encode("ascii")
                )
            else:
                self.state.received_stream.extend(b"response")

    monkeypatch.setattr(introspection, "_splice_header_no_form", lambda *_args, **_kwargs: b"header")
    monkeypatch.setattr(native_write, "splice_window_list_queries", lambda _header: [b"windows"])
    monkeypatch.setattr(native_write, "splice_navigate", lambda *_args, **_kwargs: [b"navigate"])
    monkeypatch.setattr(native_write, "splice_resolve_form_query", lambda *_args, **_kwargs: b"resolve")
    monkeypatch.setattr(responses, "extract_testclient_windows", lambda _blob: next(window_snapshots))
    monkeypatch.setattr(
        introspection.Settings,
        "from_env",
        lambda: types.SimpleNamespace(descriptor_warmup_attempts=2, descriptor_warmup_delay_sec=0.0),
    )

    opened = introspection._open_form_by_link(
        FakeHandle(),
        "e1cib/list/Справочник.Валюты",
    )

    assert opened == ("Валюты", secondary_guid, managed_guid)


def test_read_form_descriptor_uses_attached_endpoint_by_default(monkeypatch):
    captured = {}
    srv._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15444, "listening": True}
    )
    monkeypatch.setattr(srv.client_lifecycle, "port_is_listening", lambda host, port: True)
    monkeypatch.setattr(
        srv,
        "_read_form_descriptor",
        lambda **k: captured.update(k) or {
            "opened": "Контрагенты",
            "elements": [{"kind": "Table", "name": "Список"}],
            "element_count": 1,
            "fields": {},
        },
    )

    r = srv.read_form_descriptor(open_link="e1cib/list/Справочник.Контрагенты", gherkin=False)

    assert captured["host"] == "attached-host"
    assert captured["port"] == 15444
    assert r["attached_endpoint"]["host"] == "attached-host"
    assert r["element_count"] == 1


def test_read_form_descriptor_attached_endpoint_reaches_extracted_helper(monkeypatch):
    captured = {}
    srv._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "extracted-host", "port": 15447, "listening": True}
    )
    monkeypatch.setattr(srv.client_lifecycle, "port_is_listening", lambda host, port: True)
    monkeypatch.setattr(
        srv.protocol_introspection,
        "_read_form_descriptor",
        lambda **k: captured.update(k) or {"fields": {"PF_A": "1"}, "field_count": 1, "queried": 1},
    )

    r = srv.read_form_descriptor(gherkin=False)

    assert captured["host"] == "extracted-host"
    assert captured["port"] == 15447
    assert r["attached_endpoint"]["host"] == "extracted-host"


def test_read_form_descriptor_explicit_host_port_override_attached_endpoint(monkeypatch):
    captured = {}
    srv._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15444, "listening": True}
    )
    monkeypatch.setattr(srv.client_lifecycle, "port_is_listening", lambda host, port: True)
    monkeypatch.setattr(
        srv,
        "_read_form_descriptor",
        lambda **k: captured.update(k) or {"fields": {"PF_A": "1"}, "field_count": 1, "queried": 1},
    )

    r = srv.read_form_descriptor(host="127.0.0.2", port=15555, gherkin=False)

    assert captured["host"] == "127.0.0.2"
    assert captured["port"] == 15555
    assert "attached_endpoint" not in r


def test_read_form_descriptor_attached_empty_result_is_diagnostic(monkeypatch):
    srv._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15444, "listening": True}
    )
    monkeypatch.setattr(srv.client_lifecycle, "port_is_listening", lambda host, port: True)
    monkeypatch.setattr(
        srv,
        "_read_form_descriptor",
        lambda **_k: {"opened": None, "elements": [], "element_count": 0, "fields": {}, "field_count": 0},
    )

    r = srv.read_form_descriptor(open_link="e1cib/list/Справочник.Контрагенты", gherkin=False)

    assert r["ok"] is False
    assert r["error"] == "attached-descriptor-empty"
    assert r["phase"] == "descriptor"
    assert r["attached_endpoint"]["host"] == "attached-host"


def test_read_form_descriptor_formats_gherkin(monkeypatch):
    monkeypatch.setattr(srv, "_read_form_descriptor",
                        lambda **k: {"fields": {"PF_A": "1", "PF_B": "Да"}, "field_count": 2, "queried": 2})
    r = srv.read_form_descriptor()
    assert r["field_count"] == 2 and r["queried"] == 2
    assert "элемент формы с именем 'PF_A' стал равен \"1\"" in r["gherkin"]
    assert "элемент формы с именем 'PF_B' стал равен \"Да\"" in r["gherkin"]


def test_read_form_descriptor_gherkin_optional(monkeypatch):
    monkeypatch.setattr(srv, "_read_form_descriptor", lambda **k: {"fields": {"PF_A": "1"}, "field_count": 1, "queried": 1})
    assert "gherkin" not in srv.read_form_descriptor(gherkin=False)

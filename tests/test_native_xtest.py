"""Offline tests for qa_mcp.protocol.native_xtest (card 98 — XTEST hybrid command construction)."""
from qa_mcp.protocol.native_xtest import xdotool_argv


def test_xdotool_argv_type_unicode():
    argv = xdotool_argv("type", "--delay", "60", "ТестРубль")  # Cyrillic value passes through verbatim
    assert argv[0].endswith("xdotool")
    assert argv[1:] == ["type", "--delay", "60", "ТестРубль"]


def test_xdotool_argv_key_chords():
    assert xdotool_argv("key", "Tab")[1:] == ["key", "Tab"]
    assert xdotool_argv("key", "ctrl+s")[1:] == ["key", "ctrl+s"]
    assert xdotool_argv("key", "Return")[1:] == ["key", "Return"]


def test_send_keys_sequence(monkeypatch):
    # card 96 change 4 — send_keys delivers a chord sequence in order via xdotool 'key', accepts str or list
    import qa_mcp.protocol.native_xtest as nx

    sent = []
    monkeypatch.setattr(nx, "_run_xdotool", lambda display, action, *rest: sent.append((display, action, rest)))
    r = nx.send_keys(["Down", "Down", "Return"], display=":7", settle_sec=0)
    assert r == {"keys": ["Down", "Down", "Return"], "display": ":7", "sent": 3}
    assert sent == [(":7", "key", ("Down",)), (":7", "key", ("Down",)), (":7", "key", ("Return",))]
    sent.clear()
    nx.send_keys("Escape", display=":7", settle_sec=0)   # a single chord as a bare string
    assert sent == [(":7", "key", ("Escape",))]


def test_write_form_value_xtest_uses_send_keys(monkeypatch):
    # write_form_value_xtest routes its Tab/Ctrl+S through the shared send_keys primitive (card 96 change 4)
    import inspect
    import qa_mcp.protocol.native_xtest as nx

    src = inspect.getsource(nx.write_form_value_xtest)
    assert "send_keys(" in src and "Tab" in src and "ctrl+s" in src


def test_write_form_value_xtest_importable_and_signature():
    from qa_mcp.protocol.native_xtest import write_form_value_xtest
    import inspect
    sig = inspect.signature(write_form_value_xtest)
    # field is addressed by name; blur commits; save is optional; display targets the client's Xvfb
    for p in ("capture", "value", "field", "host", "port", "display", "blur", "save"):
        assert p in sig.parameters, p


# --- Card 97 #2 DATE grid cell: calendar-picker geometry (the date->click math, pure) ----------------------
from qa_mcp.protocol.native_xtest import calendar_day_cell, calendar_month_cell


def test_calendar_month_cell_two_columns():
    # months 1-6 are the left column, 7-12 the right; default origin = Jan cell
    assert calendar_month_cell(1) == (932, 444)         # Янв
    assert calendar_month_cell(6) == (932, 444 + 5 * 30)  # Июн (left col, last row)
    assert calendar_month_cell(7) == (932 + 53, 444)    # Июл (right col, first row)
    assert calendar_month_cell(8) == (985, 474)         # Авг — the live-verified click


def test_calendar_month_cell_rejects_out_of_range():
    import pytest
    with pytest.raises(ValueError):
        calendar_month_cell(0)
    with pytest.raises(ValueError):
        calendar_month_cell(13)


def test_calendar_day_cell_august_2026_15th():
    # Aug 1 2026 is a Saturday (weekday 5), so day 15 -> index 5+14=19 -> row 2, col 5 -> the live-verified click
    assert calendar_day_cell(2026, 8, 15) == (1037 + 5 * 35, 474 + 2 * 30) == (1212, 534)


def test_calendar_day_cell_first_of_month():
    # Jan 1 2026 is a Thursday (weekday 3): day 1 -> index 3 -> row 0, col 3
    assert calendar_day_cell(2026, 1, 1) == (1037 + 3 * 35, 474)


def test_calendar_day_cell_custom_geometry():
    # geometry is parameterized for other resolutions/layouts
    assert calendar_day_cell(2026, 8, 15, origin=(100, 200), step=(40, 25)) == (100 + 5 * 40, 200 + 2 * 25)


def test_parse_subimage_match():
    # card 99 #2 — parse ImageMagick `compare -subimage-search` output (abs (normalized) @ x,y)
    from qa_mcp.protocol.native_xtest import parse_subimage_match

    assert parse_subimage_match("1234.5 (0.0188) @ 932,370") == (0.0188, 932, 370)
    assert parse_subimage_match("noise 0 (0) @ 1240,361 [0]") == (0.0, 1240, 361)
    assert parse_subimage_match("no match here") is None
    assert parse_subimage_match("") is None


def test_imagemagick_compare_argv():
    from qa_mcp.protocol.native_xtest import imagemagick_compare_argv

    argv = imagemagick_compare_argv("haystack.png", "needle.png")
    assert argv[0].endswith("compare")
    assert argv[1:] == ["-metric", "RMSE", "-subimage-search", "haystack.png", "needle.png", "null:"]


def test_locate_calendar_button_with_injected_runner():
    # card 99 #2 — a confident match returns the glyph CENTER (top-left + half the 18x18 template)
    from qa_mcp.protocol.native_xtest import locate_calendar_button

    found = locate_calendar_button("shot.png", runner=lambda argv: "0 (0.01) @ 1240,361")
    assert found == (1240 + 9, 361 + 9)  # (1249, 370)
    # a low-confidence match (score over threshold) is rejected — no guessed coordinates
    assert locate_calendar_button("shot.png", max_score=0.18,
                                  runner=lambda argv: "9999 (0.7) @ 10,10") is None
    # no match line at all
    assert locate_calendar_button("shot.png", runner=lambda argv: "") is None


def test_imagemagick_label_argv():
    # card 100 — render a column-header TITLE to a needle PNG for subimage-search localization
    from qa_mcp.protocol.native_xtest import imagemagick_label_argv

    argv = imagemagick_label_argv("Дата", "/tmp/n.png", font="Liberation-Sans", pointsize=13)
    assert argv[0].endswith("convert")
    assert argv[1:] == ["-background", "white", "-fill", "black", "-font", "Liberation-Sans",
                        "-pointsize", "13", "label:Дата", "/tmp/n.png"]


def test_locate_text_with_injected_runner():
    # card 100 — localize on-screen text by rendering+subimage-search; returns the matched box center.
    # With an injected runner the needle PNG is not rendered, so _png_dimensions falls back to 18x18.
    from qa_mcp.protocol.native_xtest import locate_text

    found = locate_text("shot.png", "Дата", out_png="/tmp/none.png",
                        runner=lambda argv: "9368 (0.14) @ 1079,435")
    assert found == (1079 + 9, 435 + 9)
    # over-threshold match is rejected (no guessed coordinate)
    assert locate_text("shot.png", "Дата", out_png="/tmp/none.png", max_score=0.2,
                       runner=lambda argv: "9999 (0.7) @ 10,10") is None
    assert locate_text("shot.png", "Дата", out_png="/tmp/none.png", runner=lambda argv: "") is None


def test_locate_text_short_label_fallback():
    # card 125 — a short label whose needle lands just over the strict 0.2 threshold (e.g. «Владелец» at 0.21,
    # measured against a real create-form screenshot) is located via the point-size fallback, while a genuine
    # miss and long labels stay strict. Injected runner returns the same output for every point size.
    from qa_mcp.protocol.native_xtest import locate_text

    just_over = lambda argv: "999 (0.21) @ 252,351"  # correct position, RMSE just over the strict 0.2

    diag: dict = {}
    found = locate_text("shot.png", "Владелец", out_png="/tmp/none.png", runner=just_over, diag=diag)
    assert found == (252 + 9, 351 + 9)          # relaxed short-label fallback accepts 0.21 (<= 0.28)
    assert diag["path"] == "fallback"

    # a long label does NOT get the relaxed fallback — it stays strict and rejects 0.21
    assert locate_text("shot.png", "Наименование разменной валюты", out_png="/tmp/none.png",
                       runner=just_over) is None

    # a genuine miss (0.5) is rejected even for a short label
    miss: dict = {}
    assert locate_text("shot.png", "Код", out_png="/tmp/none.png",
                       runner=lambda argv: "999 (0.5) @ 10,10", diag=miss) is None
    assert miss["path"] == "miss"

    # a clean primary match still takes the fast strict path (no fallback sweep)
    ok: dict = {}
    assert locate_text("shot.png", "Код", out_png="/tmp/none.png",
                       runner=lambda argv: "999 (0.12) @ 40,50", diag=ok) == (40 + 9, 50 + 9)
    assert ok["path"] == "primary"


def test_locate_text_records_box_in_diag():
    # card 125 — locate_text records the matched needle box (center + width -> right edge) in diag so a
    # caller can derive the input column from the rightmost label edge.
    from qa_mcp.protocol.native_xtest import locate_text

    diag: dict = {}
    # injected runner: needle not rendered, so _png_dimensions falls back to 18x18 -> center = x+9, y+9, w=18
    assert locate_text("shot.png", "Код", out_png="/tmp/n.png",
                       runner=lambda argv: "9 (0.10) @ 100,200", diag=diag) == (109, 209)
    assert diag["box"]["cx"] == 109 and diag["box"]["w"] == 18
    assert diag["box"]["right"] == 109 + 9 and diag["box"]["left"] == 109 - 9


def test_input_column_x_from_rightmost_label_edge():
    # card 125 — the input column aligns to the RIGHTMOST label edge + gap, so a short and a long label
    # click into the same column; empty -> fall back to label-center + input_offset.
    from qa_mcp.protocol.native_xtest import input_column_x

    assert input_column_x([275, 520, 300], gap=24) == 520 + 24     # rightmost edge + gap
    assert input_column_x([None, 275], gap=10) == 275 + 10
    assert input_column_x([], fallback_center=266, fallback_offset=170) == 266 + 170
    assert input_column_x([], fallback_offset=170) == 170


def test_table_cell_from_header_geometry():
    # card 100 — the first data-row cell sits one grid row (≈28 px) below the localized column header center
    from qa_mcp.protocol.native_xtest import table_cell_from_header

    assert table_cell_from_header((1094, 443)) == (1094, 471)
    assert table_cell_from_header((1094, 443), row_offset=40) == (1094, 483)


def test_calendar_origins_from_localized_button_reproduce_fixture():
    # card 99 #2 — button center + fixed deltas reproduce the old hardcoded popup origins (the generalization)
    from qa_mcp.protocol.native_xtest import CALENDAR_DAY_DELTA, CALENDAR_MONTH_DELTA

    bx, by = 1249, 370
    assert (bx + CALENDAR_MONTH_DELTA[0], by + CALENDAR_MONTH_DELTA[1]) == (932, 444)
    assert (bx + CALENDAR_DAY_DELTA[0], by + CALENDAR_DAY_DELTA[1]) == (1037, 474)


def test_calendar_year_row_geometry():
    # card 99 #2 year-nav — year-dropdown row offsets relative to the localized button center
    from qa_mcp.protocol.native_xtest import (
        CALENDAR_YEAR_BOX_DELTA, CALENDAR_YEAR_ROW_PITCH, calendar_year_row,
    )

    btn = (1249, 370)
    box = calendar_year_row(btn, 0)                       # row 0 = current year (the year box)
    assert box == (1249 + CALENDAR_YEAR_BOX_DELTA[0], 370 + CALENDAR_YEAR_BOX_DELTA[1])
    # row k is k pitches below the box; row 2 reproduces the measured 2028 click (current 2026 + 2)
    assert calendar_year_row(btn, 2) == (box[0], box[1] + 2 * CALENDAR_YEAR_ROW_PITCH)
    assert calendar_year_row(btn, 2)[1] - box[1] == 50    # pitch 25 * 2

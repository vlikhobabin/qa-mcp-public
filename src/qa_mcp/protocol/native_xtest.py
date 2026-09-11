"""Card 98 — XTEST hybrid write: protocol open+focus-BY-NAME + OS-level keystrokes (xdotool / XTEST) into the
1C client's X display.

Why a hybrid: the pure protocol replay sets a field's edit-text (SET echo) but does NOT commit an OBJECT
attribute (`Объект.*` on catalog/document forms — the bulk of business data entry); the commit needs the field
to be genuinely "user-edited", which a programmatic SetEditText does not establish, and 1C exposes no
accessible elements (so AT-SPI is no shortcut). But the 1C client's X11 window IS OS-accessible, so real
keystrokes can be injected — exactly what Vanessa's VanessaExt component does (OS input on the display),
reproduced here WITHOUT the Vanessa runtime.

`write_form_value_xtest` holds ONE manager connection: it replays the capture's open+focus prefix (protocol,
addresses the field by name), then injects the value via `xdotool type` (Unicode/Cyrillic-aware) into the
focused client window on the X display, blurs (Tab) to commit, optionally saves (Ctrl+S), and reads the value
back by replaying the capture's read sequence. Proven end-to-end (committed + DB-persisted, incl. Cyrillic) on
demo_1_0_41_3 / Справочник.Валюты.Наименование — see evidence/card98-xtest-hybrid-2026-06-18/.
"""
from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from .bootstrap import resolve_capture_dir
from .frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT
from .native_mutation import GuidRebinder, _read_available
from .native_write import _read_chunks, read_field_value_near
from .transport import connect_testclient


def xdotool_argv(action: str, *rest: str) -> list[str]:
    """Build an xdotool argv. Pure (no I/O) so the command shape is unit-testable offline."""
    exe = shutil.which("xdotool") or "xdotool"
    return [exe, action, *rest]


def _run_xdotool(display: str, action: str, *rest: str) -> None:
    if shutil.which("xdotool") is None:
        raise RuntimeError("xdotool not found on PATH — the XTEST hybrid needs it to inject OS keystrokes")
    env = {**os.environ, "DISPLAY": display}
    subprocess.run(xdotool_argv(action, *rest), env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def xtest_type(display: str, text: str, delay_ms: int = 60) -> None:
    """Type ``text`` into the focused window on ``display`` (Unicode/Cyrillic-aware via xdotool keysym remap)."""
    _run_xdotool(display, "type", "--delay", str(delay_ms), text)


def xtest_key(display: str, key: str) -> None:
    """Send a key chord (e.g. 'Tab', 'ctrl+s', 'Return') to the focused window on ``display``."""
    _run_xdotool(display, "key", key)


def xtest_type_unicode(display: str, text: str, delay_ms: int = 20) -> None:
    """Type ``text`` via per-character ``xdotool key U<codepoint>`` — reliable for Cyrillic/Unicode where plain
    ``xdotool type`` drops non-ASCII (e.g. into a GTK file-chooser location entry; card 109). xdotool remaps an
    unused keycode for each codepoint, so every char is delivered."""
    keys = [f"U{ord(c):04X}" for c in text]
    if keys:
        _run_xdotool(display, "key", "--delay", str(delay_ms), *keys)


def xtest_click(display: str, x: int, y: int, *, button: int = 1) -> None:
    """Move the pointer to screen (x, y) on ``display`` and click ``button`` (XTEST via xdotool). The mouse
    escape hatch for controls 1C only drives by mouse — notably the date calendar picker (card 97/99)."""
    _run_xdotool(display, "mousemove", str(int(x)), str(int(y)))
    _run_xdotool(display, "click", str(button))


def send_keys(
    keys: "str | list[str]",
    *,
    display: str = ":89",
    settle_sec: float = 0.15,
) -> dict[str, Any]:
    """Send raw OS keystrokes to the focused 1C client window on ``display`` via XTEST (xdotool) — card 96
    change 4 (keyboard). 1C keyboard input is OS-LEVEL: Vanessa injects keys with the VanessaExt external
    component INSIDE the client, and the typed key is in NO manager->client protocol frame (the card-98
    write-commit root-cause), so there is no key-press command to replay — raw keys are delivered exactly as
    Vanessa delivers them, via XTEST into the client window. The underlying primitive (``xtest_key``) is the same
    one DB-verified in ``write_form_value_xtest`` (Tab commits an object attribute; Ctrl+S = Записать saves to
    the DB), which now routes its Tab/Ctrl+S through this function.

    ``keys`` is one chord ('Return') or a sequence (['Down', 'Down', 'Return']); each is an xdotool key spec
    (Return / Escape / Tab / Up / Down / Left / Right / ctrl+s / alt+F4 / …) sent in order with ``settle_sec``
    between chords. The keys go to the FOCUSED window (the launched client is the lone app window after
    matchbox). High-level keyboard INTENTS are already covered capture-free by protocol tools — confirm/cancel
    dialogs (`answer_dialog`), field commit (Tab here or the focus-change), row navigation (`select_table_row` /
    `read_list_grid`), save (`click_command` «Записать») — so ``send_keys`` is the raw-key escape hatch for
    controls that need genuine OS keys (masked editors, custom shortcuts). Returns {keys, display, sent}."""
    seq = [keys] if isinstance(keys, str) else list(keys)
    for chord in seq:
        xtest_key(display, chord)
        if settle_sec:
            time.sleep(settle_sec)
    return {"keys": seq, "display": display, "sent": len(seq)}


# --- Card 97 #2 DATE grid cell: pure-MOUSE calendar-picker geometry ----------------------------------------
# A 1C DATE grid cell rejects synthetic keystrokes (its masked editor doesn't receive XTEST `type`/`key` —
# proven, while a plain string field does), but it IS settable by MOUSE: protocol-activate the cell → click its
# calendar dropdown button → the calendar popup opens (a 2-column month list + a Monday-first 6-week day grid)
# → click the month then the day. These pure helpers turn a target date into the month/day click coordinates,
# given the popup's grid geometry (origin + step), so the date->clicks math is unit-testable offline. Defaults
# match the fixture under matchbox-maximized 1280x1024 (live-verified: Авг + 15 set "15.08.2026"). The popup
# origin is layout/resolution-specific — pass measured origins for another setup.

def calendar_month_cell(
    month: int, *, origin: tuple[int, int] = (932, 444), col_step: int = 53, row_step: int = 30
) -> tuple[int, int]:
    """Screen (x, y) of ``month`` (1..12) in the calendar's 2-column month list (months 1-6 left, 7-12 right;
    each column lists 6 months top-to-bottom). ``origin`` is the Jan (month 1) cell center."""
    if not 1 <= month <= 12:
        raise ValueError(f"month must be 1..12, got {month}")
    col = 0 if month <= 6 else 1
    row = (month - 1) % 6
    return origin[0] + col * col_step, origin[1] + row * row_step


def calendar_day_cell(
    year: int, month: int, day: int, *, origin: tuple[int, int] = (1037, 474), step: tuple[int, int] = (35, 30)
) -> tuple[int, int]:
    """Screen (x, y) of ``day`` in the calendar's Monday-first 6-week day grid. The grid lays the month into a
    7-col x 6-row matrix starting at the Monday of the week containing day 1 (leading days are the prev month),
    so the cell index = weekday(year,month,1) + (day-1), row = index//7, col = index%7. ``origin`` is the
    top-left day cell center; ``step`` is (col_width, row_height)."""
    import calendar as _cal
    first_weekday = _cal.weekday(year, month, 1)  # Mon=0 .. Sun=6
    index = first_weekday + (day - 1)
    row, col = divmod(index, 7)
    return origin[0] + col * step[0], origin[1] + row * step[1]


# --- Card 99 #2: locate the date cell's calendar dropdown button ON SCREEN (no hardcoded coords) --------------
# The ONLY layout-specific input the date picker needs is the calendar dropdown button's screen position — the
# popup's month-list and day-grid origins are then FIXED offsets from that button (the popup opens at a constant
# place relative to it). So localizing the button generalizes the whole pick. The button is a distinctive ~16x16
# calendar glyph that appears in the ACTIVE date cell after protocol-activation; ImageMagick's `compare
# -subimage-search` finds it (no extra Python imaging deps — the screenshot path already shells out to
# import/scrot). Popup deltas measured from the live fixture (button center (1249,370): month list origin
# (932,444), day grid origin (1037,474)) — relative to the button so they travel with it.
CALENDAR_BUTTON_TEMPLATE = Path(__file__).resolve().parent / "assets" / "calendar_button.png"
CALENDAR_MONTH_DELTA = (-317, 74)   # month-list (Jan) origin relative to the calendar-button center
CALENDAR_DAY_DELTA = (-212, 104)    # day-grid top-left origin relative to the calendar-button center
# Card 99 #2 year-nav: the calendar's ‹/› arrows step the MONTH (not the year — measured); the YEAR is changed
# via the «<year> ▼» dropdown at the popup's top-left. Clicking it opens a list with the CURRENT year at the top
# (row 0) and current+1/+2/+3 below (then a ▼ scroll); clicking row k selects current+k. Deltas relative to the
# button center (year box = current/row-0); up to CALENDAR_YEAR_MAX_STEP rows are directly clickable per open
# (chain opens for larger forward offsets).
CALENDAR_YEAR_BOX_DELTA = (-284, 48)   # year dropdown box (current year / row 0) relative to the button center
CALENDAR_YEAR_ROW_PITCH = 25           # vertical pitch between year rows in the open dropdown
CALENDAR_YEAR_MAX_STEP = 3             # rows below the current year that are visible without scrolling


def calendar_year_row(button_xy: "tuple[int, int]", offset: int) -> "tuple[int, int]":
    """Screen (x, y) of the year-dropdown row ``offset`` rows below the current year (row 0 = current year), given
    the localized calendar-button center. ``offset`` 0..CALENDAR_YEAR_MAX_STEP is directly clickable after opening
    the dropdown (open it by clicking ``offset=0``, the year box)."""
    bx, by = button_xy
    return bx + CALENDAR_YEAR_BOX_DELTA[0], by + CALENDAR_YEAR_BOX_DELTA[1] + CALENDAR_YEAR_ROW_PITCH * offset

_SUBIMAGE_MATCH_RE = re.compile(r"\(([0-9.eE+-]+)\)\s*@\s*(\d+),(\d+)")


def imagemagick_compare_argv(haystack_png: str, needle_png: str) -> list[str]:
    """Build the ImageMagick ``compare -subimage-search`` argv (pure, unit-testable). RMSE metric; ``null:``
    discards the diff/heatmap output (only the stderr score+offset is wanted)."""
    exe = shutil.which("compare") or "compare"
    return [exe, "-metric", "RMSE", "-subimage-search", haystack_png, needle_png, "null:"]


def parse_subimage_match(text: str) -> "tuple[float, int, int] | None":
    """Parse ImageMagick ``compare -subimage-search`` output into ``(normalized_score, x, y)`` — the best-match
    top-left and its normalized RMSE in [0,1] (0 = exact). Pure, unit-testable. Returns None if no match line."""
    m = _SUBIMAGE_MATCH_RE.search(text or "")
    if not m:
        return None
    return float(m.group(1)), int(m.group(2)), int(m.group(3))


def locate_calendar_button(
    screenshot_png: "str | Path",
    *,
    template_png: "str | Path" = CALENDAR_BUTTON_TEMPLATE,
    max_score: float = 0.18,
    runner: "Callable[[list[str]], str] | None" = None,
) -> "tuple[int, int] | None":
    """Find the calendar dropdown button in ``screenshot_png`` by template-matching the shipped glyph
    (``compare -subimage-search``) and return its CENTER screen (x, y) — or None when no confident match
    (normalized RMSE > ``max_score``: button not visible / cell not activated / off-screen). Card 99 #2; this is
    the one layout-specific measurement a general date-cell set needs. ``runner`` (argv -> combined output) is
    injectable for tests; the default runs ImageMagick and reads its stderr."""
    haystack, needle = str(screenshot_png), str(template_png)

    def _default_runner(argv: list[str]) -> str:
        proc = subprocess.run(argv, capture_output=True, text=True)  # compare exits non-zero on any diff
        return (proc.stderr or "") + (proc.stdout or "")

    run = runner or _default_runner
    parsed = parse_subimage_match(run(imagemagick_compare_argv(haystack, needle)))
    if parsed is None:
        return None
    score, x, y = parsed
    if score > max_score:
        return None
    try:
        with open(needle, "rb") as fh:
            sig = fh.read(33)
        w = int.from_bytes(sig[16:20], "big") if sig[:8] == b"\x89PNG\r\n\x1a\n" else 18
        h = int.from_bytes(sig[20:24], "big") if sig[:8] == b"\x89PNG\r\n\x1a\n" else 18
    except OSError:
        w = h = 18
    return x + w // 2, y + h // 2


def xtest_double_click(display: str, x: int, y: int, *, button: int = 1, gap_ms: int = 120) -> None:
    """Double-click at screen (x, y) on ``display`` — move once, then two clicks within the double-click interval
    (XTEST via xdotool ``click --repeat 2``). Card 100: double-clicking a grid cell enters its inline editor (the
    config-agnostic activation that opens a date cell's calendar button — no protocol write_block / no capture)."""
    _run_xdotool(display, "mousemove", str(int(x)), str(int(y)))
    _run_xdotool(display, "click", "--repeat", "2", "--delay", str(gap_ms), str(button))


def _png_dimensions(path: "str | Path") -> "tuple[int, int]":
    """(width, height) of a PNG from its IHDR (no imaging deps); (18, 18) fallback for a non-PNG/short file."""
    try:
        with open(path, "rb") as fh:
            sig = fh.read(24)
        if sig[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(sig[16:20], "big"), int.from_bytes(sig[20:24], "big")
    except OSError:
        pass
    return 18, 18


def imagemagick_label_argv(text: str, out_png: str, *, font: str = "Liberation-Sans", pointsize: int = 13,
                           background: str = "white", fill: str = "black") -> list[str]:
    """Build the ImageMagick ``convert label:`` argv that renders ``text`` to ``out_png`` (pure, unit-testable).
    Card 100: renders a column-header TITLE as a search needle to localize it on screen (the form descriptor has
    no pixel bounds). ``Liberation-Sans`` @ 13 matches the 1C Taxi table-header font on the Linux contour (the
    table header wins the global subimage-search over a colon-suffixed form-field label)."""
    exe = shutil.which("convert") or "convert"
    return [exe, "-background", background, "-fill", fill, "-font", font, "-pointsize", str(pointsize),
            f"label:{text}", out_png]


def locate_text(
    screenshot_png: "str | Path",
    text: str,
    *,
    out_png: "str | Path | None" = None,
    font: str = "Liberation-Sans",
    pointsize: int = 13,
    max_score: float = 0.2,
    fallback_pointsizes: "tuple[int, ...]" = (12, 14),
    fallback_max_score: float = 0.28,
    short_label_chars: int = 14,
    runner: "Callable[[list[str]], str] | None" = None,
    diag: "dict[str, Any] | None" = None,
) -> "tuple[int, int] | None":
    """Localize on-screen ``text`` by rendering it as a needle (``convert label:``) and subimage-searching it in
    ``screenshot_png`` (``compare -subimage-search``); return the matched box CENTER (x, y), or None when no
    confident match. Card 100 — config-agnostic localization of a table column header by its on-screen title (no
    pixel bounds in the descriptor).

    Card 125 — short/single-word/reference labels (e.g. «Владелец») render a narrow needle whose normalized RMSE
    lands just over the tight ``max_score`` (0.2), so the default single-pointsize search rejects a match that is
    at the CORRECT position. When the primary search misses and the label is short (``len(text) <=
    short_label_chars``), retry across ``fallback_pointsizes`` and accept the lowest-RMSE candidate up to the
    relaxed ``fallback_max_score``. The chosen knob (`path`/`pointsize`/`score`) is recorded in ``diag`` when a
    dict is passed. Longer labels keep the strict single-pointsize path unchanged.

    ``runner`` (argv -> combined output) is injectable for tests; the default shells ImageMagick."""
    def _default_runner(argv: list[str]) -> str:
        proc = subprocess.run(argv, capture_output=True, text=True)
        return (proc.stderr or "") + (proc.stdout or "")

    run = runner or _default_runner

    def _search(pt: int) -> "tuple[float, int, int, int] | None":
        """Render (real runs only) + subimage-search at ``pt``; return (score, center_x, center_y, needle_width)."""
        needle = str(out_png) if (out_png is not None and pt == pointsize) else str(
            Path(tempfile.gettempdir()) / f"qa_needle_{abs(hash((text, font, pt)))}.png")
        if runner is None:  # real run: render the needle first (tests inject the compare output directly)
            subprocess.run(imagemagick_label_argv(text, needle, font=font, pointsize=pt),
                           check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        parsed = parse_subimage_match(run(imagemagick_compare_argv(str(screenshot_png), needle)))
        if parsed is None:
            return None
        score, x, y = parsed
        w, h = _png_dimensions(needle)
        return score, x + w // 2, y + h // 2, w

    def _accept(match: "tuple[float, int, int, int]", pt: int, path: str) -> "tuple[int, int]":
        # card 125: record the matched box (center + width -> right edge) so a caller can derive the input column.
        score, cx, cy, w = match
        if diag is not None:
            diag.update({"path": path, "pointsize": pt, "score": score,
                         "box": {"cx": cx, "cy": cy, "w": w, "left": cx - w // 2, "right": cx + w // 2}})
        return cx, cy

    primary = _search(pointsize)
    if primary is not None and primary[0] <= max_score:
        return _accept(primary, pointsize, "primary")

    # Short-label fallback: sweep point sizes, take the lowest-RMSE candidate under the relaxed threshold.
    if len(text) <= short_label_chars:
        candidates: list[tuple[tuple[float, int, int, int], int]] = []
        if primary is not None:
            candidates.append((primary, pointsize))
        for pt in fallback_pointsizes:
            got = _search(pt)
            if got is not None:
                candidates.append((got, pt))
        if candidates:
            best, best_pt = min(candidates, key=lambda c: c[0][0])
            if best[0] <= fallback_max_score:
                return _accept(best, best_pt, "fallback")

    if diag is not None:
        diag.update({"path": "miss", "score": primary[0] if primary else None})
    return None


def input_column_x(label_right_edges: "list[int | None]", *, gap: int = 24,
                   fallback_center: "int | None" = None, fallback_offset: int = 170) -> int:
    """Derive the X of a single-column form's INPUT column from the located labels' right edges.

    card 125: managed-form inputs are right-aligned to the LONGEST label, so a short label's own
    right-edge would under-reach the column and its value lands in a neighbour. Using the RIGHTMOST label
    edge + ``gap`` makes a short label («Код») and a long label («Наименование разменной валюты») both
    click into the same input column. With no located labels, fall back to the legacy
    ``fallback_center + fallback_offset`` (label-center + input_offset)."""
    edges = [e for e in label_right_edges if e is not None]
    if edges:
        return max(edges) + gap
    if fallback_center is not None:
        return fallback_center + fallback_offset
    return fallback_offset


def table_cell_from_header(header_center: "tuple[int, int]", *, row_offset: int = 28) -> "tuple[int, int]":
    """Screen (x, y) of the FIRST data-row cell directly below a localized column-header center — the header x
    (the column) with y stepped down by ``row_offset`` (one Taxi grid row ≈ 28 px). Card 100: the click point that
    activates a tabular date cell's inline editor, derived from the column header with no hardcoded coordinates."""
    hx, hy = header_center
    return hx, hy + row_offset


def write_form_value_xtest(
    capture: str | Path,
    value: str,
    field: str,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    display: str = ":89",
    setup_stop: int = 17,
    read_start: int = 25,
    read_frame: int = 28,
    blur: bool = True,
    save: bool = False,
    type_delay_ms: int = 60,
    settle_sec: float = 1.0,
    repo_root: Path | None = None,
    display_backend: Any | None = None,
) -> dict[str, Any]:
    """Write ``value`` into a form field via the protocol+XTEST hybrid and verify by read-back.

    Holds ONE manager connection: replay the capture's open+focus prefix ``[0..setup_stop]`` (opens the form +
    focuses ``field`` BY NAME) → ``xdotool type`` the value into the focused client window on ``display`` →
    ``Tab`` (blur, commits the object attribute) → optional ``Ctrl+S`` (Записать, saves to DB) → replay the
    capture's read sequence ``[read_start..read_frame]`` and check the value is read back.

    The defaults match the shipped demo capture `demo-write` (Справочник.Валюты.Наименование);
    ``field`` is the capture's focused field (used for the read-back). Returns a result dict; ``committed`` is
    True when the value (UTF-8 or UTF-16LE) appears in the read-back stream.
    """
    cap = resolve_capture_dir(capture, repo_root) if not Path(capture).exists() else Path(capture)
    mgr = _read_chunks(cap, MANAGER_TO_CLIENT)
    cli = _read_chunks(cap, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    vb, v16 = value.encode("utf-8"), value.encode("utf-16-le")
    diverged: int | None = None
    consec_empty = 0
    read_resp = b""

    with connect_testclient((host, port), timeout=15.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        # PROTOCOL: open the form + focus the field by name
        for i in range(0, min(setup_stop, len(mgr) - 1) + 1):
            wire = rebinder.apply(mgr[i])
            try:
                sock.sendall(wire)
            except OSError:
                diverged = i
                break
            resp = _read_available(sock, 0.6, 0.15)
            rebinder.observe_response(resp)
            if not resp and len(wire) > 16:
                consec_empty += 1
                if consec_empty >= 8:
                    diverged = i
                    break
            elif resp:
                consec_empty = 0
        # OS INPUT: type into the focused client window on the X display
        if diverged is None:
            time.sleep(settle_sec)
            if display_backend is None:
                xtest_type(display, value, type_delay_ms)
            else:
                display_backend.type_text(value, display=display, delay_ms=type_delay_ms, unicode=False)
            keys = (["Tab"] if blur else []) + (["ctrl+s"] if save else [])
            if keys:
                if display_backend is None:
                    send_keys(keys, display=display)  # the shared card-96 keyboard primitive
                else:
                    display_backend.send_keys(keys, display=display)
            time.sleep(settle_sec)
            # READ-BACK: replay the capture's read sequence (in order — the read needs its setup frames)
            for rf in range(read_start, min(read_frame, len(mgr) - 1) + 1):
                try:
                    sock.sendall(rebinder.apply(mgr[rf]))
                except OSError:
                    break
                read_resp += _read_available(sock, 0.9, 0.2)

    committed = (vb in read_resp) or (v16 in read_resp)
    return {
        "field": field,
        "value": value,
        "committed": committed,
        "value_in_readback": committed,
        "readback_value": read_field_value_near(read_resp, field),
        "diverged_at": diverged,
        "blurred": blur,
        "saved": save,
        "display": display,
    }

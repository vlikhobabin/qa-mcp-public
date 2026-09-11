## Context

Card 97 shipped the hard part of date-cell entry capture-free and live-verified
(`10.01.2026` → `15.08.2026`, committed): protocol-activate the cell by replaying
`set_table_cell`'s write_block (activate+SET, WITHOUT the commit) so the inline
date editor + calendar dropdown appear, then mouse-drive dropdown → month → day →
`Return`. The date→click geometry (`calendar_month_cell` / `calendar_day_cell`)
is productized and unit-tested. Keystrokes are ruled out (1C's masked date editor
ignores synthetic XTEST keys; protocol text-SET is rejected) — mouse only.

The ONLY gap to a general tool is on-screen LOCALIZATION: the calendar dropdown
button coords and the calendar popup origin are layout/scroll/resolution
specific, and the probe HARDCODES them for the fixture. This localization is the
single new capability, and it is SHARED with any future generic click-by-coords /
cell-by-coords tool — so it is built once here.

## Goals / Non-Goals

**Goals:**

- A general `set_table_date_cell(table, column, date, …)` MCP tool.
- One reusable on-screen localization capability (descriptor bounds and/or
  template-match) that yields the calendar-button + popup coordinates.
- Live verification on the fixture date column with localized (not hardcoded)
  coordinates; ideally a 2nd form as a generality check.

**Non-Goals:**

- Re-deriving the activate/calendar mechanism or date→click math (done, reused).
- Keystroke-based date entry (ruled out).
- A fully general click-by-coords tool surface — this change builds the
  localization primitive it would share, not the whole tool.
- Vanessa, EDT or meta involvement.

## Decisions

- **Localization route — try descriptor bounds first, template-match as fallback.**
  Investigate whether the form descriptor carries decodable pixel BOUNDS for the
  target column/cell (extend `extract_descriptor_*` in `responses.py`). If bounds
  are present and reliable, compute the calendar-button click point from them. If
  not decodable, fall back to screenshot template-matching the calendar dropdown
  button icon (a recognizable, layout-stable glyph) to find its on-screen origin.
- **Reuse the shipped mechanism unchanged.** Once the cell/button origin is
  known, drive the existing activate → calendar-open → `calendar_month_cell` /
  `calendar_day_cell` → `Return` sequence (`native_xtest.py`). No change to the
  date math.
- **Explicit blocked result, never guessed coords.** If neither route localizes
  the cell with confidence, return `blocked`/`unsupported` with a reason; do not
  click hardcoded or guessed coordinates.
- **Fixture-scoped mutation.** Exercise only on the fixture `PF_TABLE_DATE`
  column; recovery is re-opening the form. Read back the set value
  (`read_table_cell`) to confirm.
- **Runtime preflight.** Needs an X display (XTEST mouse), matchbox for stable
  layout/focus, and apache stopped for the native client per the lab recipe.

## Risks / Trade-offs

- [Risk] The descriptor may NOT carry pixel bounds (1C descriptors are logical,
  not pixel layouts). Mitigation: template-matching is the primary fallback and
  is self-contained; treat descriptor-bounds as a bonus if decodable.
- [Risk] Template-matching is sensitive to theme/DPI/scroll. Mitigation: match a
  stable calendar-button glyph, score the match, and return `blocked` below a
  confidence threshold rather than mis-clicking.
- [Risk] Layout/scroll changes between activate and click. Mitigation: localize
  AFTER activation (the inline editor + dropdown are visible) and click promptly;
  re-localize if the read-back fails.
- [Risk] Generality unproven on a single form. Mitigation: aim for a 2nd form;
  if only the fixture is available, record residual risk explicitly.
- [Risk] This is the look-ahead change (medium-high effort, new capability). It
  is fine to land change 1 first and treat change 2 as deferred until date-grid
  entry / click-by-coords is actually needed.

## Migration Plan

- Decide the localization route (probe whether descriptor bounds decode; build
  template-match otherwise).
- Wrap the localization + the shipped activate/calendar/click sequence into
  `set_table_date_cell`.
- Live-verify on the fixture date column with localized coordinates; capture
  evidence and (ideally) repeat on a 2nd form.
- Add the localization unit test; sync the spec.

## Open Questions

- Do qa-mcp form descriptors carry any decodable pixel bounds, or is on-screen
  geometry only obtainable from a screenshot?
- Is a single recognizable calendar-button glyph reliable across the fixture
  theme + a 2nd form, or does the template need per-theme variants?
- Is a 2nd date-grid form available in the lab to prove generality, or is the
  fixture the only date column?

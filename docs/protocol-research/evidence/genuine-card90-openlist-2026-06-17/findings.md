# Card 90 — open_list: capture + capture-free replay + native verify (2026-06-17)

## Summary

Opening a LIST window is now DONE end-to-end, capture-free — the LAST card-90 element type. A list is opened by
a top-level **navigation-link** command `e1cib/list/<metadata-path>` (`<0xf7><char-count:1><utf-16le link>`,
decoded card 86d). No fixture change was needed: the fixture's embedded dynamic list `ДенамическийСписокИерархия`
is based on `Catalog.Товары`, so navigating to `e1cib/list/Справочник.Товары` opens that catalog's list. The
nav-link decode + `render_open_list_command` already existed but were "not yet live-verified" (the lab captures
had no open-list flow); this closes that gap with a genuine fixture capture + a live capture-free replay.

## Capture (genuine, via Vanessa)

`tools/protocol-research/qa-card90-capture-openlist.feature` (connect + open fixture form + «Я перехожу по
навигационной ссылке "e1cib/list/Справочник.Товары"»). The scenario succeeded and the **Товары** list window
opened (active-window caption = "Товары", nav-link = `e1cib/list/Справочник.Товары`). Traffic:
`runtime/protocol-research/captures/genuine-card90-openlist-20260617/traffic-selfcontained/traffic.jsonl`
(36 chunks — connect + open form + the 2-frame open-list command; client TPort 48001 / manager 42466). The
open-list command is at manager frames (14,15).

## Capture-free replay (no Vanessa) — ✅ LIVE-VERIFIED by screenshot

`tools/protocol-research/set_open_list_shot.py`: launch the TestClient on an owned display, replay the genuine
setup (connect + open fixture form) with live GUID rebinding, then send the genuine nav-link open command. A
separate **"Товары"** list window opened (tab "Товары", rows Обувь/Продукты/Услуги/Электротовары) on a fresh
native client. Screenshots: `runtime/protocol-research/openlist-shot/20260617-12{2726,3132}/`. The list window
persists after the replay connection closes, so the realistic flow `launch_test_client → open_list →
capture_screenshot` works.

## Productization

- `native_write._find_open_list` / `OpenListTemplate` / `derive_open_list(capture_dir, base_link)` — locate the
  contiguous nav-link command frames (on the real capture: setup_end=13, open_list_block=(14,15)).
- `native_write.open_list(template, target_catalog=None, …)` — replay setup + the nav-link command, optionally
  re-targeting the catalog via `navigation.retarget_nav_link` (variable-length).
- MCP tool **`open_list(catalog, base_link, …)`** — the **15th** qa-mcp tool.
- Unit tests: 2 new (offline) in `tests/test_native_write.py`; full suite **218 passed**.

⚠ READ-BACK: an open-list has no value read-back (it opens a window) — verify visually (capture_screenshot),
like page-switch. Re-targeting the catalog is best-effort (the frame's internal length fields beyond the
nav-link char-count are not fully decoded); the base `Справочник.Товары` is the live-proven path. The MainFrame
GUID is carried in the replayed command and rebound by `GuidRebinder` from the live setup responses (no separate
MainFrame-GUID plumbing needed for the full-replay path).

## Card 90 status

DONE — all element types: checkbox + choice + table-cell + page-field + **open_list**. The capture-free epic now
covers read / input+commit / navigate (page-switch) / checkbox / choice / table-cell / page-field / open_list.

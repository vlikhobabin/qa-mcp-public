# Card 96 / E3 — open_card (drill into a list row → record card): productized + live-verified capture-free

**Date:** 2026-06-18. **Card:** 96 (interaction breadth), change 3 (object navigation). **Status:** `open_card`
DONE (MCP tool #23, 230 tests, live-verified, no Vanessa). `close_window` / `activate_window` follow.

## Decode

Capture `genuine-card96-opencard-20260618` (open fixture form → open the Контрагенты list via the nav link
`e1cib/list/Справочник.Контрагенты` → «Изменить» (`ФормаИзменить`) the active row → the record card opens). The
flow involves THREE windows — the fixture form, the catalog LIST (`Справочник.Контрагенты.Форма.ФормаСписка`),
and the record CARD (`Справочник.Контрагенты.ФормаГруппы`, the active row was the "Покупатели" group) — each a
distinct top-level `SecondaryFrame`. So **drilling into a list row opens a NEW window** (the record form), the
same new-window shape as a dialog (answer_dialog). The card window's per-open SecondaryFrame GUID is learnable
from its open response, so a faithful full-stream replay reproduces it with `GuidRebinder`.

## Productize

`src/qa_mcp/protocol/native_write.py`: `OpenCardTemplate`, `derive_open_card(capture_dir, result_marker)`
(validates multiple windows + the card marker present as UTF-16), `open_card(template, …)` — a faithful
full-stream replay (open form → open list → «Изменить» → card opens); `GuidRebinder` rebinds the form / list /
card window GUIDs as they appear (first-appearance, same as the dialog window — no special new-window handling).
Opening is confirmed by ``result_marker`` (a card-specific UTF-16 string, default the card form id
"ФормаГруппы") reading back. MCP tool `open_card(result_marker)` (the **23rd**). Unit test
`test_derive_open_card_validates_windows_and_marker`.

## Live proof (no Vanessa)

`tools/protocol-research/{open_card_probe.py,run_open_card_test.sh}`, fresh native client: replay → `opened=true`
(the card marker "ФормаГруппы" reads back). PASS. The full-stream-replay + GuidRebinder new-window machinery from
answer_dialog transferred directly — confirming it generalizes to any new-window navigation (dialogs, cards).

## Notes

- Opens the captured ACTIVE row's card (here the "Покупатели" group card). To open a SPECIFIC row's card,
  precede with a row-select (compose with the shipped `select_table_row` row-match retarget) — a documented
  refinement.
## close_window — PRODUCTIZED + live-verified capture-free (2026-06-18); the "descriptor-less" blocker was a FALSE ALARM

**Update 2026-06-18 (session 2).** The blocker below is RESOLVED — the cold-cache re-capture was NOT needed.

- **The blocker was untested and wrong.** Handoff point 3 asked: does a descriptor-less windows capture replay
  against a warm-cached client (which shares the on-disk `~/.1cv8` form cache)? Tested directly
  (`tools/protocol-research/{windows_explore_probe.py,run_windows_explore_test.sh}`, replaying the existing
  `genuine-card96-windows3-20260618` capture against a fresh native TestClient on the SAME infobase): the session
  **ESTABLISHED cleanly through all three window-close frames** (mgr[20,26,29]), zero divergence, the client
  responding (110-byte replies to the 150-byte close commands). The replay client reads its form descriptors from
  the shared on-disk cache, so a descriptor-less capture replays as-is. **No cache-clear, no re-capture needed.**
- **close_window productized from windows3.** `native_write.py`: `_window_sf_for_ref` / `_find_window_close` /
  `_next_sf_close_after`, `CloseWindowTemplate`, `derive_close_window(capture_dir, window_ref)`,
  `close_window(template, …)`. The card window is identified by the SecondaryFrame co-occurring with its record
  data ref (`e1cib/data/Справочник.Контрагенты`); the close is the `88 82 81` command on that SF (mgr[26] in
  windows3 — the 150-byte window-level close, distinct from the 213-byte `88 82 81` Изменить-execute on the list
  SF that OPENS the card). The full stream is replayed (GuidRebinder rebinds list/card window GUIDs) **truncated
  one frame before the next window-close** (mgr[29] closes the fixture) so ONLY the card closes.
- **MCP tool #24** `close_window(window_ref)`. Unit test `test_derive_close_window_locates_close_and_truncates_before_next`. 231 tests.
- **Live proof (no Vanessa):** `tools/protocol-research/{close_window_probe.py,run_close_window_test.sh}` →
  `accepted=True closed=True active_window_after=e1cib/app/`. The closed card's (live, rebound) SecondaryFrame is
  reported by the client BEFORE the close and gone AFTER it, and the fixture form behind it becomes active. PASS.
- **activate_window — PRODUCTIZED + live-verified (2026-06-18, MCP tool #25).** Captured two clean flows via
  the genuine Vanessa manager (warm; no cache-clear — descriptor-less replay is proven): `genuine-card96-
  windows4-20260618` (open→list→card→**close** card→**activate** fixture) and `genuine-card96-activate-20260618`
  (open→list→card→**activate** the buried fixture, NOTHING closed — the unambiguous activate). Capture recipe
  [[genuine-action-capture-recipe]]: auto-allow at manager BOOT only (it would XTEST-contaminate the window
  ops); steps confirmed via search_for_steps_by_keywords — «И я закрываю текущее окно» (`ЯЗакрываюТекущееОкно`),
  «И я активизирую окно "Заголовок"» (`ЯАктивизируюОкно`, UI.Окна).

  **⭐ Decode (the key insight): close and activate are the SAME window-level command.** A byte-diff of the
  card-CLOSE (windows4 mgr[26]) and the fixture-ACTIVATE (activate mgr[25]) shows them STRUCTURALLY IDENTICAL —
  `…SecondaryFrame[<window>] 88 82 81 20 20 20 …`, differing only in the offset-19 sequence counter and the
  embedded window GUIDs. So `88 82 81` is a **generic window-level command whose effect is contextual on
  z-order**: applied to the ACTIVE/topmost window it closes it; applied to a BACKGROUND window it brings it to
  front (activate). The earlier "activate = `e0 4b`" note was wrong — the `e0 4b` frames are auto-activation on
  window OPEN, not the «активизирую окно» step.

  - **Code** `native_write.py`: `ActivateWindowTemplate`, `derive_activate_window(capture_dir, window_ref)` (reuses
    `_window_sf_for_ref` + `_find_window_close` — same finder as close), `activate_window(template, …)` — faithful
    full-stream replay; GuidRebinder rebinds the window GUIDs. **Verification is the INVERSE of close_window:** the
    target becomes the ACTIVE (last-reported) window — its (live, rebound) SecondaryFrame is the one in the final
    window-bearing client response (`activated`), whereas for close the target's SF is gone and a DIFFERENT window
    is active. MCP tool `activate_window(window_ref)` (the **25th**). Unit test
    `test_derive_activate_window_locates_command_on_target_sf`. 232 tests.
  - **Live proof (no Vanessa):** `tools/protocol-research/{activate_window_probe.py,run_activate_window_test.sh}`
    → `accepted=True activated=True target_in_activate_resp=True` (the buried fixture form raised to front, its
    live SF is the final active window). PASS.

⇒ **Card 96 change-3 (object navigation) is DONE:** open_card (#23) · close_window (#24) · activate_window (#25),
all capture-free + live-verified, no Vanessa.

---
### (historical) close_window + activate_window — decoded + Vanessa-verified; productization once blocked on multi-connection capture

The other two E3 navigation commands are DECODED and proven via the genuine manager, but their capture-free
productization is blocked by a capture-tooling limitation (not a protocol unknown).

- **Vanessa steps (resolved):** close = «И я закрываю текущее окно» / «И я закрываю окно "Заголовок"»;
  activate = «И я активизирую окно "Заголовок"». Both PROVEN on the genuine manager: opening the Контрагенты
  list + a record card (5 windows: card, list, fixture form, app, home), then `закрываю текущее окно` closes
  the active card (window count 5→4, the card gone) and `активизирую окно "QA MCP Protocol Fixture V1"` makes
  the fixture form active. ⚠ title match is a SUBSTRING — «Контрагенты» is ambiguous (it is inside «Покупатели
  (Контрагенты)»); use an unambiguous title.
- **Decode:** close/activate are **window-level commands** — `…SecondaryFrame[<window>] 88 82 81` (the same
  `88 82 81` family as the dialog-close in answer_dialog, applied to ANY window) plus `e0 4b` activate-with-
  action frames. So the productization is the SAME full-stream-replay + GuidRebinder new-window machinery as
  answer_dialog / open_card, verified by `accepted` (a window command has no value read-back, like open_list /
  switch_page).
- **Blocker — investigated 2026-06-18 (the "multi-connection" framing was partly WRONG):**
  1. The extra TCP connections in the windows pcap to port **1081** are NOT 1C — `127.0.0.1:1081` is a local
     forward PROXY and those connections are the AGENT's own API traffic (`CONNECT chatgpt.com:443`,
     `CONNECT api.openai.com:443`). The real 1C manager↔client link is a SINGLE connection (client TPort ↔ one
     manager ephemeral port). So pcap_to_traffic's single-connection model is correct; merging connections is
     NOT the fix.
  2. The REAL problem: the windows captures are INCOMPLETE — the single 1C connection has the handshake + the
     list-open + the window commands + the form/card CAPTIONS, but is MISSING the form-field descriptor frames
     (`EditField[PF_*]`) and the card form id (`ФормаГруппы`) — ~31 manager chunks vs ~79 for the clean
     open_card capture. A descriptor-less stream cannot establish the replay session.
  3. **Likely cause — client-side form-descriptor caching.** open_card was the FIRST time the fixture form +
     the catalog card were opened this session → the full descriptors were sent on the wire + captured. Every
     subsequent capture (the windows attempts) reuses the cached compiled forms (`~/.1cv8/1C/1cv8/<ib-guid>/`),
     so the descriptor frames are NOT re-sent → the capture is incomplete. (A replay client shares that cache,
     so a descriptor-less capture MIGHT still replay — untested.)
  ⇒ **NEXT (concrete):** capture the close/activate flow from a COLD client (clear the `~/.1cv8/.../<ib-guid>/`
  form cache so the descriptors re-send), as ONE clean single-shot flow (open form → list → card → close →
  activate) — like the open_card capture got — then productize `close_window` / `activate_window` via the
  existing full-replay + GuidRebinder window machinery (the decode is done: window-level `88 82 81` + `e0 4b`).
  Alternatively, test whether the shared client cache lets a descriptor-less windows capture replay as-is.
  Captures: `genuine-card96-windows{,2,3}-20260618` (all incomplete — descriptor-cached).

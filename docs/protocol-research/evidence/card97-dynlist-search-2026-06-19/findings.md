# Card 97 change 4 — dynamic-list SEARCH-STRING: capture → decode → productize

**Date:** 2026-06-19. **Scope:** the first dynamic-list operation of card 97 change 4 — filter a dynamic list
by a **search string** (the incremental search box), capture-free, no Vanessa. Target:
`ДенамическийСписокИерархия` (Catalog.Товары) on the embedded fixture form.

## Fixture prerequisite (deploy) — the dynlist command bar was HIDDEN

The fixture dynlist EXISTS (`ДенамическийСписокИерархия`, with a `searchStringAddition`
`ДенамическийСписокИерархияСтрокаПоиска`), but its command bar was `commandBarLocation=None` → the search box
is not rendered, so the genuine Vanessa search step failed with **«Невидимый пользователю элемент управления не
может выполнять интерактивные действия»**. One-line fixture edit (dynlist `commandBarLocation` `None`→`Top`)
surfaces the whole command bar (search string + view-status + the «Ещё» menu = view-mode / filter / advanced
search), unlocking ALL of change 4. Deployed via `deploy_fixture.sh` (`TAG=card97-ch4`):
gen `5569447fe9…` → **`08d5aabf7575…`**. Backup: `Form.form.bak-card97-ch4-dynlist`.

## Capture (genuine Vanessa manager)

Feature `qa-card97-ch4-dynlist-search.feature` (connect+open+two DIFFERENT searches for the byte-diff):
```
И в таблице "ДенамическийСписокИерархия" в дополнение формы с именем 'ДенамическийСписокИерархияСтрокаПоиска' я ввожу текст 'Молоко'
И в таблице "ДенамическийСписокИерархия" в дополнение формы с именем 'ДенамическийСписокИерархияСтрокаПоиска' я ввожу текст 'Творог'
```
Result: **Success**. tcpdump (lo, portrange 48000-48400) → client TPort **48001**, dominant manager port
**59110** → `pcap_to_traffic.py cap.pcap 48001 <out> 59110` → `traffic.jsonl` (24 manager→client chunks).
Capture: `runtime/protocol-research/captures/genuine-card97-ch4-search-20260619/`.

## Decode (KEY) — the search SET is the UTF-16 `b7` value buffer, addressed at the SearchStringAddition

Per-search manager→client sequence (mgr ordinals):
- `#16` — `Table[ДенамическийСписокИерархия]` activate (focus the dynlist before the search).
- `#17` — search SET, tag `88 82 81`, value buffer.
- `#18` — search SET duplicate, tag `81 81 81` (the same SET-pair duplication as a plain field, card 86c).
- `#19–21` — the SECOND search (`Творог`), identical structure (the diff: only the value bytes change).

The value buffer:
```
…<element path …ДенамическийСписокИерархияСтрокаПоиска]>  [88 82 81 | 81 81 81]  e0 41 81 81 b7  <char-count:1>  <UTF-16LE value>  20 20 20  <nonce>
```
- The value rides the **UTF-16 `b7` buffer** (`e0 41 81 81 b7 <char-count><utf-16le><ASCII-space pad>`) — the
  **same buffer a CatalogRef name SET uses** (card 96 / E2 `retarget_ref_value`), NOT the plain-string UTF-8
  `ba` buffer. char-count = 6 for both "Молоко"/"Творог"; 3 trailing spaces of padding.
- The element path leaf is `…СтрокаПоиска]` (the `SearchStringAddition` element), encoded **UTF-16LE** on the
  wire (Cyrillic name — the card-98 UTF-16 path situation).

⇒ a dynlist search is structurally a **reference-name SET addressed at the search-string addition**. It reuses
the existing `set_reference_field` full-replay machinery wholesale.

Decoder: `tools/protocol-research/card97_dynlist_search_decode.py`.

## Productize

- `protocol/native_write.py`: `SearchListTemplate` + `derive_search_list(capture_dir, search_field, captured_value)`
  (locates the FIRST search's SET block → `stop_after`, so a two-search decode capture replays as ONE search) +
  `search_list(template, value, …)` — replays setup→activate→SET through `stop_after`, re-targeting the UTF-16
  search string via `retarget_ref_value` (fixed-width; bounded by the captured length ≈ 6+1 chars for "Молоко").
- MCP tool `search_list(value, search_field=…, captured_value="Молоко", capture="genuine-card97-ch4-search-20260619")`
  — the **34th** tool.
- Unit tests (3): derive locates the first search block (`stop_after`), the UTF-16 search value retargets
  fixed-width, derive raises when the value is absent. Suite **254 passed** (was 251).

## Live-verify ✅ (no Vanessa, screenshot-proven)

Probe: `tools/protocol-research/search_list_verify_shot.py` (boots a fresh native /TESTCLIENT per shot →
baseline / search 'Молоко' / search 'Творог' → screenshot). Result
(`runtime/protocol-research/search-list-shot/20260619-073504/`):
- `00-baseline` — `echoed=False` (no search frame sent); form opens at the top (the dynlist is below the fold).
- `01-search 'Молоко'` — `echoed=True`; the dynlist command bar is visible, the **search box shows "Молоко"**,
  and the Товары list is filtered to the **single matching row** `000000026 | Молоко | Mol34 | Животноводство…`.
- `02-search 'Творог'` — `echoed=True`; the **search box shows "Творог"** and the list narrows to **0 rows**
  (no Товары item matches).

The "Молоко"→1-row vs "Творог"→0-row contrast (both showing the exact RE-TARGETED value in the box) is the
definitive proof: the capture-free search SET applies, with the value swapped. (The search activates/focuses
the dynlist, which scrolls the form to it — why the search shots show the list and the baseline shows the top.)

## Honest boundaries

- **Value length** is bounded by the captured "Молоко" (6 chars) + padding — fixed-width retarget, same as
  `set_reference_field`. A longer search needs a capture with a longer value (documented refinement).
- **Read-back:** a list-filter has no clean value read-back (the visible rows narrow) — verified by screenshot;
  `echoed` reports the search value echoed in the client responses.
- **Generalization to other dynlists:** the search addition is targeted by the captured fixture name; another
  config's dynlist search would re-target the `…СтрокаПоиска]` leaf (refinement — the buffer/mechanism is
  config-independent).

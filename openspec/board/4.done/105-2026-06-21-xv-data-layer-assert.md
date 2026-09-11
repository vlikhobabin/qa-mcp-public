# 105. E-XV — data-layer cross-verification (OData / query / DCS) fused with UI

## Status
4.done

## Order Index
105

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-21 project review: Vanessa asserts only through the UI. qa-mcp can assert what the UI did AGAINST the
  data layer in the same scenario — a genuine "beyond Vanessa" capability. Substrate is ALREADY in the profile:
  `live-mcp` (standard OData + the custom HTTP-service 1C-query/DCS, Apache `127.0.0.1:8316`), and the
  `read_record` vs OData cross-check is already used ad-hoc in card 99/100 verification.
- Parent epic: card 102. Capability: extends `qa-mcp-protocol-lab` (read/assert surface) with a data-layer
  assertion that delegates to `live-mcp`.

## Summary
A first-class assertion that a UI action persisted to the database: after a UI write + save, query the data
layer (OData / 1C query / DCS via `live-mcp`) and assert the stored value — positive (match) and negative
(mismatch surfaces a clear diff). Exposed as both an MCP tool and a Gherkin step so it composes into authored
scenarios. This closes the loop the protocol cannot: `write_form_value_xtest` → save → **assert in the DB**.

## Acceptance
- An MCP tool (e.g. `assert_data`) asserts a stored value via `live-mcp` (OData read / 1C query) and returns a
  clear pass/fail with the actual vs expected.
- A Gherkin phrasing (e.g. «Значение в базе ... равно ...») maps to it (no-drift test).
- Live end-to-end on a real config: UI write + save → data-layer assert passes; a deliberately wrong expectation
  fails with a readable diff.

## Change Set (waves — living plan, lightweight: card-as-plan, no full OpenSpec ff)
1. ✅ `data-assert-tool` — DONE 2026-06-21. **Design decision (better than the stub):** instead of delegating to
   `live-mcp` (a separate MCP server qa-mcp can't call in-process — and a Gherkin step couldn't either), qa-mcp
   got its OWN thin read-only OData client `src/qa_mcp/data/odata.py` (`ODataClient`, injectable `fetcher` for
   offline tests, `$filter`/`$select`/`$top`, basic auth, env config `QA_MCP_ODATA_URL/USER/PASSWORD`) +
   `assert_data_value` (equals/contains/regex, no-record case) + MCP tool `assert_data` (#54). Self-contained,
   no cross-MCP runtime dependency; same standard-OData endpoint `live-mcp` uses (Apache `127.0.0.1:8316`).
2. ✅ `data-assert-step` — DONE 2026-06-21. Gherkin «В базе 'EntitySet' где "<OData-filter>" поле 'Поле' равно
   'Значение'» → `assert_data` kind (double-quoted filter so it can carry single-quoted OData literals);
   no-drift + mapping tests.
3. ✅ `ui-to-db-roundtrip-verify` (LIVE) — DONE 2026-06-21. BOTH halves live-verified: the data-layer (assert)
   read path AND the full UI→DB roundtrip (UI write + save → assert in the DB).
   - **Done (live, read-only, no Xvfb):** the whole read path proven end-to-end against the live `vanessa_client`
     infobase (Apache OData `127.0.0.1:8316`, `Администратор:`): `ODataClient` + `assert_data_value` (ok/bad),
     Gherkin → transpile → `ScenarioRunner.run()` (sessionless — opens NO TestClient), by-key (guid) fetch,
     Cyrillic filter-value round-trip, and the MCP `assert_data` tool surface. Evidence:
     `evidence/card105-data-layer-live-2026-06-21/findings.md`.
   - **Two real bugs the live run caught** (offline fakes could not — they inject the fetcher): (1) a Cyrillic
     entity-set path raised `UnicodeEncodeError` before send → now `quote`-encoded; (2) `$filter` spaces went out
     as `+`, which 1C OData rejects with HTTP 500 «Operation not allowed in clause "ГДЕ"» → now `%20` via
     `quote_via=quote`. Both pinned by offline regressions in `tests/test_odata.py`.
   - **DONE (live UI→DB roundtrip) 2026-06-21** (boot session): the full flagship loop, end-to-end on
     `vanessa_client` — booted the client (Xvfb `:105` + matchbox, manage_apache), `write_form_value_xtest`
     wrote `Справочник.Валюты.Наименование="QAROUNDTRIP2026"` + saved (`committed/value_in_readback/saved`=true),
     teardown restarted Apache, then `assert_data` over OData confirmed **ok=true, actual="QAROUNDTRIP2026",
     record_count=1**. The UI write PERSISTED to the DB, confirmed at the data layer — the loop Vanessa cannot do.
     Evidence: `evidence/card105-ui-to-db-roundtrip-live-2026-06-21/`. (The write created a new lab currency
     record; our read-only OData client does not delete it.)

## Verify
- Offline — `pytest` 390 green (`tests/test_odata.py`: URL/filter/select/auth build, by-key wrap, match modes,
  assert match/mismatch/missing, + the two live-bug regressions `test_url_is_ascii_safe_for_cyrillic_entity_set`
  and `test_filter_spaces_encode_as_percent20_not_plus`; + a Gherkin `assert_data` mapping test).
- LIVE (read-only, no Xvfb) — data-layer assert proven end-to-end vs the real `vanessa_client` infobase through
  all layers (ODataClient → assert_data_value → ScenarioRunner.run → MCP tool); two URL-encoding bugs found and
  fixed. Evidence: `evidence/card105-data-layer-live-2026-06-21/findings.md`.
- LIVE (UI→DB roundtrip, flagship) — booted `vanessa_client` (Xvfb + matchbox, manage_apache),
  `write_form_value_xtest` wrote+saved `Валюты.Наименование="QAROUNDTRIP2026"`, teardown restarted Apache, then
  `assert_data` over OData confirmed it persisted (ok=true, record_count=1). Evidence
  `evidence/card105-ui-to-db-roundtrip-live-2026-06-21/`.

## Archive
- card complete (offline + both live halves); kept as the living record (lightweight card-as-plan, no OpenSpec ff).

## Result
Data-layer cross-verification COMPLETE — offline + LIVE: self-contained read-only OData client + `assert_data`
core + MCP tool (#54) + Gherkin step (unit-tested), the data-layer read path live-verified, AND the full flagship
UI→DB roundtrip proven on `vanessa_client` (UI write+save → assert in the DB) — the "beyond Vanessa" loop the UI
cannot self-check. Card → 4.done.

## Next
- closed. The `assert_data` step also features in card 104's live report demo (a passing data-layer testcase).

## Related
- Parent: card 102. Substrate: `live-mcp` (`query_odata` / `execute_1c_query` / `read_record`), already proven in
  card 99/100 verification vs OData. Code: `src/qa_mcp/mcp_server.py`, `src/qa_mcp/scenario/gherkin.py`.
- Lab: [[lab-infobase-access]], [[ibsrv-odata-vs-httpservice]]. Memory: [[surpass-vanessa-native-superset-goal]].

## Log
- 2026-06-21 card created (E-XV track — substrate ready). Thin backlog stub; change set outlined, not yet
  ff-processed.
- 2026-06-21 DONE (offline) in-session, lightweight card-as-plan: shipped a SELF-CONTAINED read-only OData client
  (`src/qa_mcp/data/odata.py`) instead of delegating to `live-mcp` (cross-MCP call isn't possible in-process / from
  a Gherkin step); `assert_data_value` + MCP `assert_data` (#54) + Gherkin step `assert_data`. `tests/test_odata.py`
  (6) + a mapping test. 369 tests green. Card → 3.inprogress; only the live read-only roundtrip (change 3) remains.
- 2026-06-21 LIVE (read-only) data-layer half verified vs the real `vanessa_client` infobase (no Xvfb): all four
  layers green end-to-end (ODataClient/assert_data_value, Gherkin→transpile→ScenarioRunner.run sessionless,
  by-key guid, Cyrillic filter, MCP `assert_data`). The live run caught + fixed TWO real bugs (Cyrillic path →
  UnicodeEncodeError; `$filter` `+` → HTTP 500 «ГДЕ»), both pinned by offline regressions. 390 tests. Evidence:
  `evidence/card105-data-layer-live-2026-06-21/`. Remaining: the UI-write half of the roundtrip (TestClient boot).
- 2026-06-21 LIVE UI→DB ROUNDTRIP done (boot session) — the flagship loop end-to-end: booted vanessa_client
  (Xvfb+matchbox, manage_apache), `write_form_value_xtest` wrote+saved `Валюты.Наименование="QAROUNDTRIP2026"`,
  teardown restarted apache, `assert_data` over OData confirmed it persisted (ok=true, record_count=1). The
  "beyond Vanessa" UI-action→DB-assert loop is proven. Evidence `evidence/card105-ui-to-db-roundtrip-live-2026-06-21/`.
  **Card 105 fully verified (offline + both live halves) — ready to close.**
- 2026-06-21 published the OData fixes + live-verified data-layer half on `main` in `f647a4a` (scoped `$opsx-pub`,
  co-published with card 103). Card stays in 3.inprogress for the UI-write half of the roundtrip (TestClient boot).
- 2026-06-21 CLOSED → 4.done. Both live halves were already verified (the flagship UI→DB roundtrip published in
  `9885ec4`); this just moves the card to 4.done now that the boot session + follow-ups confirm it fully verified.
  The `assert_data` step is also exercised live in card 104's report demo. All 3 changes ✅.

## Why

The card 125 live re-run's independent list read (`read_list_grid` on a freshly-created auto-generated `ФормаСписка`)
returned a false `0 rows` — even as the FIRST read after a fresh `launch_test_client`, so not the cold-client boundary —
while both just-created records were visibly present in a screenshot of that same list. 1C dynamic lists are async and
eventually-consistent: a just-created record is not shown until the list query re-runs (the user-level fix is F5 / the
«Обновить» command). The current dynlist read replays a next-row capture with no forced refresh and no retry, so a single
early / mis-bound snapshot reports `0` and the primitive can only emit an ambiguous "EITHER empty OR cold-boundary".

## What Changes

- Add a shared `_ensure_list_fresh(open_link)` helper that (1) issues an explicit list refresh — a protocol replay of the
  list's «Обновить»/F5 command when reachable, `send_keys(["F5"])` into the focused list window as the fallback — and
  (2) polls the row read until the count is stable (two equal successive reads) or non-zero, up to a bounded timeout.
- Wire that helper into the dynlist read primitives: `read_list_grid`, `read_list_row`, `read_list_column`, `search_list`.
- Default `refresh=True`, with an opt-out for the rare test that asserts "row absent WITHOUT a refresh".
- Add a `wait_for_rows` / `expected_min_rows` option so a verification read can assert "≥N rows within T" instead of a
  single snapshot.
- Rework the `0 rows` diagnostic: after a forced refresh + settle, report `0` as "empty (refreshed)" and drop the
  cold-boundary guess for the post-refresh path, so `0` unambiguously means a genuinely empty list.

This change touches **protocol tools and Python manager code** (the dynlist read primitives and a new shared helper) plus
their **offline tests**. It needs **only offline capture-backed tests** for acceptance; a live TestClient run against a
freshly-created catalog list is an optional confirmation, not required by the gate (the repro is already retained).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: dynamic-list read primitives must force a list refresh and poll-until-stable before reporting
  row results, so a `0`-row result only ever denotes a genuinely empty list (not a stale or not-yet-loaded dynamic list).

## Impact

- `src/qa_mcp/mcp_server.py` — `read_list_grid` / `read_list_row` / `read_list_column` / `search_list` gain the shared
  refresh + poll-until-stable path and the `refresh` / `wait_for_rows` options.
- A new shared helper (e.g. `_ensure_list_fresh`) in the dynlist read module / protocol layer.
- Offline tests under `tests/` for the refresh + poll-until-stable loop and the empty-vs-not-loaded disambiguation.
- No new live-write surface; reads stay read-only. No metadata/BSL/source changes. No breaking API change (new optional
  parameters only; the default `refresh=True` changes read behavior to be currency-correct).

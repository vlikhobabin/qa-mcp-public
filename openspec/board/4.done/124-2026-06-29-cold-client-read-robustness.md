# 124. Harden the cold-client boundary — cold-replay reads must be robust to a dirty TestClient session

## Status
4.done

## Order Index
124

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-29 first public-delivery e2e (v0.1.0 GHCR image driven on the historical-user Windows demo base
  `demo_1_0_41_3`, memory [[qa-mcp-public-delivery-prep]]). `read_list_grid` returned **0 rows** for the
  «Валюты» list — but a screenshot (host-agent `/screenshot`) proved the list has **3 real rows**
  (EUR/USD/Рубли). Debugging showed the row-extraction code is CORRECT; the 0 came from violating the
  **cold-client boundary**.

## Summary
The cold-replay read tools — `read_list_grid` (capture `nextrow`/`nextrow-flat`), `read_list_column`,
`read_list_row` (`rowbyvalue`) — do a **cold full-replay** (fresh socket, replay the genuine capture from
frame 0: setup → open the list → position to the first row → read). This assumes a **clean desktop** (no
stale form tabs). When the TestClient session is already **dirty** — e.g. a prior `read_form_descriptor`,
`open_list`, or a chained read left form tabs open — the cold-replay's open/first-row-read lands on the
wrong instance and the first read returns empty, so the loop breaks immediately and the tool **silently
returns `row_count: 0`** as if the catalog were empty. This is a UX sharp edge: a 0 that means "you violated
the cold boundary" is indistinguishable from a genuine "empty list".

The constraint is documented ("one grid read per fresh `launch_test_client` — the cold-client boundary") but
it is (a) easy to violate in a real agent session that mixes reads, and (b) fails **silently + wrong** rather
than recovering or signalling.

## Evidence / repro (live, reproducible)
- **DIRTY → wrong:** `read_form_descriptor(e1cib/list/Справочник.Валюты)` (opens a Валюты tab), then
  `read_list_grid(...Валюты, ["Код","Наименование"])` → `row_count: 0`.
- **FRESH → correct:** restart the TestClient, then `read_list_grid(...Валюты)` as the FIRST read →
  `row_count: 3` rows `EUR/USD/Рубли` (000000003/2/1) — both via the compiled v0.1.0 container AND via an
  instrumented dev-source `read_list_grid_replay` on loopback. Matches the screenshot.
- Root cause confirmed at the code level: `read_list_grid_replay` (`protocol/native_write.py`) cold-replays
  through the first read then loops `extract_table_cell_value`; on a dirty session the first `extract_*`
  returns `None` → `break` at the "all None / row repeats" guard → 0 rows.
- **Spike (2026-06-29) — the naive fix does NOT work:** dirty (`read_form_descriptor` Валюты) → grid `0` →
  `close_window` (no args, returned `null`) → grid **still `0`**. So a bare `close_window` before the read is
  NOT the sweep. Likely mechanism: opening an **already-open** list **dedups to the existing tab** (1C
  activates it instead of opening fresh), so the cold-replay's open lands on a form instance it did not
  create and its first-row read targets the wrong GUIDs → empty. The fix must RELIABLY clear the target list
  (or all forms) from the desktop before the cold-replay — or make the cold-replay detect + handle the
  already-open case.

## Proposed Change Set (for `$opsx-ff`; ordered)
1. **`cold-state-sweep-before-replay`** — before a cold-replay read, RELIABLY clear the target list (or all
   open forms) from the desktop so the cold-replay opens a FRESH instance it owns. Candidate mechanisms (the
   spike showed bare `close_window` is insufficient): (a) the clean-state «Escape sweep» used before the 8.5
   XTEST writes — but that is XTEST/display, so in model-B it needs the host agent (`send_keys` Escape); (b) a
   protocol-level close-ALL-forms before the replay; (c) make the cold-replay itself **close the target list
   if already open** (handle the 1C "activate existing tab" dedup) before re-opening. Pick the one that works
   over the thin/model-B protocol surface (no display) and verify on the live dirty→read repro. Capability:
   cold-replay read robustness.
2. **`distinguish-empty-from-dirty`** — after the sweep, if a read still yields 0 rows, surface a structured
   result that distinguishes **genuinely empty** (the sweep succeeded + the list opened + 0 rows) from a
   **cold-boundary / open failure** (a clear `reason`/diagnostic), instead of a bare `row_count: 0`. Optional
   single auto-retry after the sweep. Capability: diagnostic-safe read outcome.

(Build 1 first — the sweep is the actual robustness fix and reuses proven machinery. Build 2 makes the
remaining 0-rows honest.)

## Acceptance
- `read_list_grid` / `read_list_column` / `read_list_row` return the **correct rows regardless of prior
  session state** (a preceding `read_form_descriptor` / `open_list` / chained read no longer forces 0 rows) —
  verified live on the demo «Валюты» (3 rows) after first dirtying the session.
- A genuinely empty list still returns 0, but a cold-boundary/open failure returns a **clear diagnostic**
  (not a silent 0 indistinguishable from empty).
- Offline `pytest` stays green; the live-regression harness covers the dirty-then-read case.

## Verify
- not started (live repro available: historical-user `.201` demo base; dirty the session with `read_form_descriptor`
  then `read_list_grid` → expect non-zero after the fix).

## Archive
- not started

## Related
- `src/qa_mcp/protocol/native_write.py` (`read_list_grid_replay`, `derive_read_list_column`,
  `read_list_row`/`rowbyvalue`); `src/qa_mcp/mcp_server.py` (`read_list_grid`/`read_list_column`/
  `read_list_row` tools); the 8.5 clean-state Escape sweep (memory [[qa-mcp-8-5-platform-support]]).
- Bundled captures: `_bundled/8.3/captures/{nextrow,nextrow-flat,rowbyvalue}`.
- Predecessor: the productize/harden epic (card 111) — this is a Track-B/D hardening follow-on.

## Result
- **✅ IMPLEMENTED + LIVE-VALIDATED 2026-06-29 (direct fix, no OpenSpec artifacts — per request).**
  `src/qa_mcp/mcp_server.py`: added `_cold_state_sweep()` (best-effort bounded Escape sweep via the display
  backend — local X11 in model A / host agent in model B; never raises) and wired **retry-on-zero** into
  `read_list_grid`, `read_list_column`, and `read_list_row` (both the where-path and the first-row path): on an
  empty result the read sweeps the accumulated tabs to the start page and **retries ONCE** (no overhead on the
  happy path — sweep only fires on a 0), and surfaces `clean_state_swept: true` + a `reason` that distinguishes
  a genuinely-empty list from a cold-boundary-with-no-display.
- **Live-validated on the historical-user demo «Валюты»:** dirty the session (`read_form_descriptor` opens a tab) →
  `read_list_grid` first replay = `0` → auto-sweep (host-agent Escape ×8) → retry = **3 rows EUR/USD/Рубли**,
  `clean_state_swept: true`. With NO display backend reachable, the read returns `0` + the clear diagnostic
  (also validated). Offline `pytest` **546 passed** (no regression).
- **Both card change-goals met:** (1) cold-replay reads recover regardless of prior session state when a display
  backend is available; (2) the otherwise-silent 0 now carries a `reason`. The sweep reuses the proven
  clean-working-area Escape machinery; it needs `QA_MCP_HOST_AGENT_WINDOW` set to the config's main window
  title (the runbook already instructs this) — a wrong/missing title → no sweep + the diagnostic fires.

## Next
- **Follow-up (not blocking):** an OFFLINE unit test for the retry-on-zero path (fake backend that returns 0
  then rows; assert sweep called + `clean_state_swept`), and a live-regression harness case for dirty-then-read.
- Consider a host-agent heuristic to focus the 1C TestClient window without an exact `QA_MCP_HOST_AGENT_WINDOW`
  (so the sweep works even when the window title is unset) — a small robustness add.

## Log
- 2026-06-29 created from the v0.1.0 e2e finding. The «0 rows on a populated list» turned out to be a
  cold-client-boundary violation in the test procedure, NOT a row-extraction bug — but the silent-wrong-0
  behaviour is a real UX sharp edge worth hardening. Live repro + root cause recorded above.
- 2026-06-29 spike: confirmed dirty→0 and that a bare `close_window` does NOT recover it (still 0). Refined
  the sweep design (Escape-via-host-agent / protocol close-all / cold-replay handles already-open dedup) —
  the implementation must pick the mechanism that works over the thin model-B protocol surface.
- 2026-06-29 IMPLEMENTED (direct, no OpenSpec artifacts per request) + LIVE-VALIDATED: the **Escape sweep via
  the display backend + retry-on-zero** wins. dirty→`read_list_grid`=0→auto-sweep→retry=3 rows EUR/USD/Рубли
  (`clean_state_swept:true`); no-backend→0+diagnostic; offline 546 green. Card → `4.done`. See Result.
- 2026-06-29 FOLLOW-UPS CLOSED + shipped in **v0.1.1**: offline unit tests (retry-on-zero recover +
  diagnostic, 548 green); **host-agent heuristic** (focus the 1C window by class `V8TopLevelFrame*` when
  `QA_MCP_HOST_AGENT_WINDOW` is unset — live-validated on historical-user: no-window → recovery → 3 rows; agent →
  `0.1.0-card124`); CORE live-regression check `ui.list_grid_after_dirty`. **Live-regression GREEN 6/6** in
  the lab `vanessa_client` — the new check passed via the DIAGNOSTIC branch (`row_count=0,
  clean_state_swept=None, has_reason=True`): a headless model-A CORE run has no display the sweep can reach,
  so the read correctly degrades to `0 + reason` (not a silent 0); the RECOVERY branch is validated on
  historical-user (model-B). Released `v0.1.1` (GHCR image + dist `.exe`), all workflow steps green.
- 2026-06-29 RESIDUAL CLOSED (`f87703b`): the regression harness now boots the UI phase on an OWNED display
  (`display="auto"`), exports `DISPLAY` to the check process, and starts matchbox for ALL UI runs (not just
  `--include-write`). **Re-ran the live-regression → `ui.list_grid_after_dirty` now RECOVERS in the lab:
  `row_count=5, clean_state_swept=True, has_reason=False`** (was `0/None/True`). GREEN 6/6; offline 548; the
  owned display is torn down with the client (no leak). Both fix branches — recovery (lab + historical-user) AND the
  no-display diagnostic — are now live-validated.

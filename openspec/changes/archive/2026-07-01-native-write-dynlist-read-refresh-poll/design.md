## Context

The dynlist read primitives (`read_list_grid`, `read_list_row`, `read_list_column`, `search_list`) open a list by
nav-link and replay a genuine "next-row" capture to walk the dynamic list. They take a single cold snapshot of the
list's current query result. 1C dynamic lists are async and eventually-consistent: a just-created record is not present
in the list's result until the list query re-runs (the interactive fix is F5 / the «Обновить» command). During the
card 125 live re-run, `read_list_grid` on a freshly-created auto-generated `ФормаСписка` returned `0 rows` as the FIRST
read after a fresh launch (so not the cold-client boundary) while both records were on screen — the read fired against a
not-yet-refreshed list. The primitive's own diagnostic can only say "EITHER empty OR cold-boundary", i.e. it cannot
distinguish empty from not-yet-loaded.

## Goals / Non-Goals

**Goals:**
- A dynlist read never reports a false `0` for records that are present-after-refresh.
- `0 rows` unambiguously means a genuinely empty list.
- One shared refresh-and-poll policy applied uniformly across all four dynlist read primitives.
- An opt-in way to assert "≥N rows within a timeout" for verification reads.

**Non-Goals:**
- Changing how individual rows/cells are decoded once the list is current (out of scope; reuse existing value-read).
- Server-side list requery internals; this operates only through the UI/protocol refresh a user would trigger.
- Making non-list reads (form value-read, `read_record`) refresh — this change is dynlist-only.

## Decisions

- **Shared `_ensure_list_fresh(open_link, ...)` helper.** One helper, called by all four primitives, so the policy is
  uniform and testable in isolation. Alternative (inline per primitive) rejected: four copies drift and are the reason
  the gap existed.
- **Refresh strategy: protocol «Обновить» command preferred, `F5` keystroke fallback.** Prefer replaying the list
  form's standard «Обновить»/refresh command (deterministic, no OS-key/focus/display dependency), captured like the
  other form-command replays. When that command replay is not reachable for a given list, fall back to
  `send_keys(["F5"])` into the focused list window (matches exactly what a user does; requires the Xvfb `display` +
  focus). Alternative (F5-only) rejected as display/focus-fragile; alternative (server requery) rejected as out of the
  protocol/UI boundary.
- **Poll-until-stable, not fixed sleep.** After the refresh, re-read the row count until two successive reads agree or a
  non-zero count appears, bounded by a timeout. A fixed sleep either wastes time or races; stable-poll self-tunes to the
  async load. `wait_for_rows`/`expected_min_rows` layers an explicit lower-bound assertion on top.
- **`refresh=True` by default, explicit opt-out.** Currency-correct reads should be the default; the rare "assert row
  absent WITHOUT refresh" test opts out. The read result records the refresh method and poll outcome as evidence.
- **Diagnostic rework.** On the refreshed path, drop the "EITHER empty OR cold-boundary" guess: a post-refresh `0` is
  reported as "empty (refreshed)". The cold-client-boundary wording remains only for the opt-out/no-refresh path.

## Risks / Trade-offs

- [Forced refresh masks a genuine "not shown without refresh" test] → Mitigation: `refresh=False` opt-out that records
  "no refresh applied" so absence assertions are explicit, not silently refreshed.
- [F5 fallback needs a focused list window + Xvfb display] → Mitigation: prefer the protocol «Обновить» replay; when
  only F5 is possible and no display is available, record a bounded diagnostic instead of a silent no-op.
- [Poll timeout too short on a slow/large list] → Mitigation: bounded, caller-tunable timeout; `wait_for_rows` returns a
  clear "expected minimum not met within T" outcome rather than a bare `0`.
- [Refresh adds latency to every list read] → Trade-off accepted: a currency-correct read is worth the one refresh +
  short poll; callers that need the old snapshot behavior use the opt-out.

## Capture Sources And Replay Strategy

- Reuse the existing genuine next-row capture(s) already backing `read_list_grid` for the row walk after the list is
  current; add (or reuse, if already captured) a genuine «Обновить»/refresh command replay for the refresh step, scoped
  to the list command bar («Еще» → Обновить / F5), following the same first-appearance GUID-rebinding replay machinery
  as the other form-command replays.
- The `F5` fallback is an OS-level keystroke (`send_keys`), not a protocol frame, consistent with the existing Tab /
  Ctrl+S OS-key handling.
- Safety/runtime: reads stay read-only; the refresh only re-runs the list query. No new mutation surface. No raw
  captures, screenshots, credentials or infobase data are committed; live confirmation evidence (if produced) lands
  under an ignored `.artifacts/` root.

## Migration Plan

- Additive, no breaking API: new optional parameters (`refresh`, `wait_for_rows`/`expected_min_rows`) with
  `refresh=True` default. Rollback = revert the change; primitives return to the single-snapshot behavior.

## Open Questions

- Whether every list form reliably exposes a replayable «Обновить» command, or whether some auto-generated list forms
  require the F5 fallback — to be resolved during implementation from real capture attempts; the fallback covers the gap
  regardless.

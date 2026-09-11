## 1. Shared refresh-and-poll helper

- [x] 1.1 Add `_ensure_list_fresh(open_link, ...)` in the dynlist read module: force a list refresh, then poll the row
      read until stable (two equal successive reads) or non-zero, up to a bounded, caller-tunable timeout.
- [x] 1.2 Refresh strategy: prefer a protocol replay of the list's «Обновить»/F5 command (capture/reuse a genuine
      refresh command, GUID-rebound like other form-command replays); fall back to `send_keys(["F5"])` into the focused
      list window when the protocol command is not reachable. (No genuine «Обновить» capture exists yet — the F5 keystroke
      fallback via the display backend is the delivered path; `_force_list_refresh` keeps the protocol-replay slot for a
      future capture. Documented in `design.md` Open Questions.)
- [x] 1.3 Record the refresh method used (protocol «Обновить» vs `F5` fallback) and the poll outcome (stable count vs
      timeout) as fields on the read result for evidence (`list_refresh` block via `_list_refresh_summary`).

## 2. Wire into the dynlist read primitives

- [x] 2.1 Route `read_list_grid`, `read_list_row`, `read_list_column`, `search_list` through the shared refresh path
      (`_ensure_list_fresh` for the row-reading trio; `search_list` is refresh-only — a filter reports no row count).
- [x] 2.2 Add a `refresh` parameter defaulting to `True`, with an explicit opt-out; the opt-out path records
      "no refresh applied" so an absence assertion is not masked.
- [x] 2.3 Add `wait_for_rows` / `expected_min_rows`: block until ≥N rows or the bounded timeout; return whether the
      expected minimum was met (`read_list_grid(wait_for_rows=N)` → `list_refresh.wait_for_rows_met`).
- [x] 2.4 Rework the `0 rows` diagnostic (`_list_zero_reason`): on the refreshed path report `0` as "empty (refreshed)";
      keep the cold-boundary/opt-out wording only for the no-refresh / no-backend path.

## 3. Offline tests

- [x] 3.1 Test the refresh + poll-until-stable loop (stabilizes on equal counts; returns rows once the list is current).
- [x] 3.2 Test empty-vs-not-loaded disambiguation (post-refresh `0` = empty; no cold-boundary ambiguity on that path).
- [x] 3.3 Test `wait_for_rows=N` blocks until ≥N rows or timeout, and reports which occurred.
- [x] 3.4 Test the `refresh=False` opt-out reads without refresh and records "no refresh applied".

## 4. Verification and evidence

- [x] 4.1 `uv run pytest tests/ -q` — green (588 passed; includes `test_form_descriptor.py` dynlist-read tests +
      `test_clean_tool_surface.py` R&D-scrub gate).
- [x] 4.2 `uv run python -m compileall src/qa_mcp` — passes.
- [ ] 4.3 Optional live confirmation on the Linux TestClient contour (demo10413) — DEFERRED (optional; not required by the
      acceptance gate). The offline capture-backed tests are authoritative per `proposal.md`; the false-`0` repro is
      already retained (card 125 log, 2026-07-01). No live TestClient was driven in this delivery session.
- [x] 4.4 `openspec validate native-write-dynlist-read-refresh-poll --strict` and
      `git diff --check -- openspec/changes/native-write-dynlist-read-refresh-poll openspec/board`.

## Verification Matrix

Card scope: qa-mcp Python-manager code that drives 1C QA/TestClient dynamic-list reads. Reads stay read-only; the only
runtime action is the list's own «Обновить» refresh. Target infobase for the optional live check: demo10413
(`env_file=/opt/ai-dev-suite-for-1c/demo10413/.ai/qa-demo10413.env`), Linux TestClient contour.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | residual_risk | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Python manager / protocol tools | `_ensure_list_fresh` + `_force_list_refresh` + `_list_zero_reason` / `_list_refresh_summary` + 4 dynlist read primitives | refresh + poll-until-stable, `refresh`/`wait_for_rows` params, reworked diagnostic | offline pytest for refresh/poll/opt-out/wait_for_rows/empty-vs-not-loaded + compileall (588 passed) | `tests/test_form_descriptor.py`, `src/qa_mcp/mcp_server.py` | provided | qa-mcp | none for offline scope | — |
| QA/TestClient UI (dynamic list) | dynlist read currency on a freshly-created catalog list | live create → dynlist read returns persisted row (no false `0`) | bounded run summary + list screenshot | deferred (optional) | N/A | qa-mcp | F5 fallback needs Xvfb+focus and the protocol «Обновить» replay is not yet captured → best-effort refresh with a recorded diagnostic, never a silent no-op | optional live confirm deferred (task 4.3); offline capture-backed gate is authoritative per proposal; the false-`0` repro is already retained |
| OpenSpec workflow | change artifacts + `qa-mcp-protocol-lab` spec deltas | proposal/design/specs/tasks + strict validate | `openspec validate --strict` rc0; `git diff --check` clean | `openspec/changes/native-write-dynlist-read-refresh-poll/` | provided | qa-mcp | none | — |
| Runtime apply / metadata / BSL | n/a | n/a | n/a | n/a | N/A | qa-mcp | read-only «Обновить»/F5 refresh only; no runtime apply, metadata, BSL, source or import surface is touched, so there is no residual runtime-mutation risk | no metadata/BSL/source/import change; read-only list refresh only |

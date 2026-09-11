# 74. Native scenario runner + MCP (orchestrate .feature without Vanessa)

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-13: the last big piece toward full Vanessa-manager replacement. Builds on the now
  capture-free bootstrap (cards 62 + 73) and the 134/160 accepted protocol members.

## Summary
Today scenarios run through Vanessa Automation (it parses `.feature` and executes steps). Goal:
execute scenarios through the in-repo Python TestManager with **no Vanessa in the loop** — a
native runner that drives a `TestClientSession` (synthesized bootstrap) through an ordered list
of steps, each mapped to an accepted manager operation, with assertions and a result report;
then a native MCP surface that exposes it (replacing vanessa-mcp's run/step tools).

## Architecture (phased)
- **Phase 1 — runner spine (this card's first slice):** a `qa_mcp.scenario` package — a Scenario/
  Step model + a ScenarioRunner that bootstraps once (synthesized) and executes read-only steps
  (active-window / form-summary / element-details) with `assert_contains` checks → a ScenarioResult.
  Offline-tested with a fake session; one live read-only proof (no Vanessa). Reuses the proven
  live reads in `session.py`.
- **Phase 2 — single-session multi-op: ✅ capability DONE (2026-06-13).** `TestClientSession.
  open_and_bootstrap()` runs the handshake/initial-UI (frames 1..10) ONCE and returns a
  `SessionHandle`; `handle.run_segment(frame_indices, query_id)` sends an operation segment on the
  same open socket, continuing the sequence/managed-form state. The shared per-frame loop was
  extracted into `_process_frame` (`exchange_template_frames` unchanged in behavior; 117 tests
  pass). Live proof: bootstrap ONCE → segment [11] (active-window, ok) → segment [12..17]
  (form-summary, ok) on one socket, no re-bootstrap. Evidence phase2_single_session_proof.json.
  NOTE: the linear template makes segments order-dependent (capture order); independent
  re-issuable operations are Phase 3. **Phase 2 FULLY DONE 2026-06-13:** `SessionHandle` gained a
  frame cursor + typed `active_window()` / `form_summary()` ops; `ScenarioRunner.run_single_session()`
  bootstraps once and dispatches steps to the handle (offline tests + live proof
  `native-single-session-smoke` passed: bootstrap once → active-window + form-summary on one socket
  through the runner, no Vanessa). Evidence phase2_runner_single_session_proof.json. 119 tests.
- **Phase 3 — action steps:** map navigation/mutation steps to the parametric synthesizers
  (`navigation.render_*`, `mutation.render_write_frame`, `run_replay_with_renderers` + GuidRebinder)
  via an api_member → executor registry; handle the captured-write-template constraint.
  - **Step 1 DONE (2026-06-13): the bridge.** `qa_mcp.scenario.actions` — `ACTION_REGISTRY`
    (open_list / form_command / select_row / open_card → the navigation synthesizers) +
    `render_action(kind, template_body, params, guid_map, sequence)` (explicit per-kind param
    allowlist so forwarding `**kw` can't leak bad kwargs). Step model gained ACTION_STEP_KINDS +
    `params`. Offline tests (7): retarget row value, open_card identity, missing-required raises,
    unexpected-param filtered, unknown-kind raises. This is the missing api_member→executor layer.
  - **Step 2 (2026-06-13): live-replay wiring — code done + offline-proven; live proof gated on a
    data-safety decision.** `qa_mcp.scenario.replay.build_action_renderers(manager_chunks, steps)`
    locates each action step's command-frame ordinal (by its captured `marker`) and builds a
    `(captured, rebinder) -> render_action(...)` renderer; tool `native_action_scenario.py` feeds
    them to `run_replay_with_renderers` (live, with GUID rebinding). 10 offline tests (incl. the
    live retarget: Средний→Малый via a renderer + fake rebinder; missing-marker reported; ordinal
    lookup). The only captured flow with all 3 nav markers (open-list/select-row/open-card,
    ord 8/15/19) is `mut-warehouse-donotuse-20260610` — a MUTATION capture; replaying it live
    re-applies the warehouse НеИспользовать toggle (revertible via COM, but a data change). Per the
    project data-safety rules, the live action proof needs a USER decision: (a) a navigation-only
    capture (no write frames), or (b) accept the revertible mutation replay, or (c) skip the write
    ordinals. Bridge + tool are committed; live proof pending that choice. 129 tests pass.
  - **Live action EXECUTED (2026-06-13, user chose accept-the-revertible-mutation):**
    `native_action_proof.ps1` COM-snapshotted `Склады["Средний"].НеИспользовать` (=False) → booted
    a fresh TestClient → drove the warehouse action scenario via the registry +
    `run_replay_with_renderers` → the flag flipped to **True** (mutation APPLIED — the action ran
    end-to-end through the Python manager, no Vanessa) → COM-restored to False (independently
    verified). The action path has a proven real live effect. Caveat: the full-capture replay is
    slow (hundreds of frames × idle timeouts) and was interrupted before clean completion → no
    zero-divergence report this run. Perf/robustness follow-up: thin polls (keep_every), replay via
    the proxy harness (15382) like the accepted-member probes, or skip the write for a nav-only
    clean completion. Evidence phase3_live_action_proof.md. **Phase 3 done (bridge + live effect);
    perf-clean replay is a follow-up.**
- **Phase 4 — Gherkin bridge: ✅ DONE 2026-06-13.** `qa_mcp.scenario.gherkin` —
  `parse_feature` (splits scenarios, strips ru/en keywords, skips #/@ lines) +
  a `STEP_PATTERNS` registry mapping recognized ru phrasings to Step kinds (read_active_window /
  read_form_summary / read_element / open_list / select_row / open_card) + an assertion pattern
  ("результат содержит '…'" → attaches expect_contains to the previous step) +
  `transpile_feature/transpile_scenario` → `TranspileResult(scenario, unmapped)`. Unsupported steps
  (e.g. the Vanessa-canonical "нажимаю на кнопку"/"ввожу текст" — need future click/input action
  kinds) are reported in `unmapped`, never silently dropped. `native_scenario_runner.py --feature`
  transpiles + runs a .feature directly. Offline: 6 tests incl. Gherkin→runner end-to-end (a
  read-only feature transpiled + run via run_single_session with a fake session → passed).
  135 tests pass.
- **Phase 5 — native MCP: ✅ DONE 2026-06-13.** `qa_mcp.mcp_server` (FastMCP, mcp SDK 1.27) exposes
  `transpile` (pure: .feature → scenario + unmapped), `run_scenario` (feature_text or scenario_json
  → run via ScenarioRunner against a live /TESTCLIENT, no Vanessa), `run_step` (single read step).
  `mcp` added to pyproject deps + `[project.scripts] qa-native-mcp`; launch `python -m
  qa_mcp.mcp_server` (stdio). Offline: 5 tests (tools registered; scenario_from_input feature/json/
  error; pure transpile tool). 140 tests pass. run_scenario delegates to the live-proven runner;
  a live MCP-client roundtrip is left to integration (needs an MCP client + booted TestClient).

## Status note
All 5 phases of the native runner/MCP track are delivered: read-only spine, single-session multi-op,
action steps (bridge + proven live mutation effect), Gherkin bridge, native MCP. The native stack now
runs scenarios end-to-end with NO Vanessa in the loop. Follow-ups (not blockers): perf-clean full
action replay (thin polls / proxy harness), click_button/input_text action kinds to widen Gherkin
coverage to the Vanessa-canonical steps, and a live MCP-client integration test.

## Acceptance (Phase 1 slice) — DONE 2026-06-13
- ✅ `qa_mcp.scenario` Scenario/Step model + ScenarioRunner with offline unit tests (fake session,
  4 tests: pass / failed-assert / step-error-captured / from_dict+validation).
- ✅ Live read-only scenario (active-window → form-summary → active-window) ran end-to-end through
  the Python manager with NO Vanessa → `native-readonly-smoke` passed. Evidence
  `docs/protocol-research/evidence/native-scenario-runner/phase1_readonly_proof.json`.

## Change Set
- `src/qa_mcp/scenario/` (model.py, runner.py, __init__.py)
- `src/qa_mcp/protocol/session.py` — `get_form_summary` now accepts `synthesized`
- `tools/protocol-research/native_scenario_runner.py` + `native_scenario_proof.ps1`
- `tests/test_scenario_runner.py` (4 tests)
- `docs/protocol-research/evidence/native-scenario-runner/phase1_readonly_proof.json`

## Result
- Phase 1 DONE (runner spine proven offline + live, read-only). Phases 2-5 remain (single-session
  multi-op, action steps via the parametric synthesizers + member→executor registry, Gherkin
  bridge, native MCP). Card stays in progress for the remaining phases.

## Result
DONE 2026-06-13 — all 5 phases delivered; native scenario runner + MCP run scenarios end-to-end
without Vanessa. 140 tests pass.

## Next
- **click_button/input_text + perf-clean: code DONE offline (2026-06-13).** ACTION_REGISTRY gained
  `click_button` (render_form_command identity press, located by marker) + `input_text`
  (render_select_row_command value re-target); ACTION_STEP_KINDS extended; Gherkin gained the
  Vanessa-canonical patterns ("я нажимаю на кнопку с именем '…'" → click_button; "в поле с именем
  '…' я ввожу текст '…'" → input_text) so the project's real .feature now transpile to executable
  steps. native_action_proof.ps1 passes `--keep-every-poll 8` (thin polls → faster/cleaner replay).
  143 tests. **click_button LIVE PROVEN (2026-06-13):** native_click_proof.ps1 ran the scenario
  [open_list → select_row → click_button "Изменить"] against a fresh TestClient via the registry +
  run_replay_with_renderers, bounded with `--max-ordinal 25` (stops before the warehouse write) +
  `--keep-every-poll 8` → **diverged_at_send_index=null (zero divergence), 26/26 frames responded,
  NO data mutation** (flag verified still False; no COM revert needed). The bounded replay also
  solves the earlier slow-replay hang (fast prefix). This closes #1 click + #2 perf-clean together.
  Evidence followup1_live_click_proof.json. **input_text LIVE PROVEN (2026-06-14):** self-captured
  the input flow via an action manifest (`fixture-input-string.json`: open the fixture form
  [`И я открываю основную форму обработки "ФикстураПротоколаTestClient"`] → `в поле с именем
  'PF_EDIT_STRING' я ввожу текст "PF_INPUT_PROOF"`) through `run_protocol_capture.ps1
  -Scenario demo-action-manifest`. KEY: field text-input commands encode the field/value in **UTF-8**
  (navigation/row commands use UTF-16LE) → added `find_marker_ordinal` (tries both encodings).
  native_input_proof.ps1 replayed [input_text @ PF_INPUT_PROOF] bounded `--max-ordinal 283
  --keep-every-poll 8` → **diverged_at=null (zero divergence), 281/281 frames responded**. SAFE:
  PF_EDIT_STRING is an in-memory form Attribute (not persisted) → no revert. Evidence
  followup1_live_input_proof.json. So both click_button AND input_text are proven live.
- **#3 live MCP-client integration test: ✅ DONE (2026-06-13).** `tests/test_mcp_server_live.py`
  launches `python -m qa_mcp.mcp_server` as a subprocess (PYTHONPATH=src), connects an MCP client
  over stdio, initializes, lists tools (transpile/run_scenario/run_step), and calls `transpile` →
  correct scenario returned — the MCP surface works end-to-end over the real protocol. 144 tests.
- Other follow-ups: input_text LIVE (blocked on a user text-field capture); cross-config bootstrap
  constants (defer); protocol tail (unsupported_initial partly unblocked by the new fixture).

## Log
- 2026-06-13: card opened; codebase scoped (parametric synthesizers + run_replay_with_renderers +
  GuidRebinder + synthesized bootstrap exist; missing = step model, member→executor registry,
  Gherkin parse, multi-step orchestration). Phased plan above.

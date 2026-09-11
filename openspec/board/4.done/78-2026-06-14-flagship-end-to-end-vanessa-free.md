# 78. Flagship end-to-end milestone — a real scenario run fully through qa_mcp (no Vanessa)

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-14: chosen direction toward full Vanessa replacement (after the protocol tail closed at
  145/160). Runtime is already Vanessa-free (native runner card 74 runs reads + actions against a live
  TestClient with no Vanessa process). The flagship proves replacement on a representative MULTI-STEP
  scenario and surfaces the remaining integration glue.

## Goal
Run one representative multi-step scenario **end-to-end through `qa_mcp` with zero Vanessa process**:
synthesized (capture-free) bootstrap → a chain of reads + actions in ONE session → assertions →
a `ScenarioResult` report. Demonstrate it from a Gherkin `.feature` via the native MCP/runner.

## Current state / the gap
- `ScenarioRunner.run_single_session` (synthesized bootstrap, one socket) supports **reads only**
  (`read_active_window`, `read_form_summary`). `_run_step_on_handle` rejects other kinds.
- Action steps (click/input/select/safe_ui) currently run via `native_action_scenario.py` —
  a SEPARATE path that replays a whole capture (capture's own bootstrap + retargeted action) with
  live GUID rebinding. Proven live, zero-divergence (click 26/26, input 281/281, choice 292/292), but
  it is NOT chained into the synthesized single session, and it re-uses the capture's bootstrap.
- So a single synthesized session that does reads AND actions together does not exist yet.

## Architecture note (honest framing)
"No Vanessa" is already true at RUNTIME (no Vanessa process during execution). The residual Vanessa
dependency is at AUTHORING time: action command FORMATS come from captured templates (write-from-capture;
captures were Vanessa-driven). This milestone does not remove that (that is the separate de-novo-synthesis
frontier); it proves the composed runtime replacement and the action+read single-session integration.

## Phased plan
- **Phase A — action-in-synthesized-session feasibility.** Can `SessionHandle` send a retargeted
  captured ACTION command frame as an operation segment, rebinding the captured GUIDs to the synthesized
  session's identifiers (managed_form_guid / frame4_sequence / message counter)? Spike: take a captured
  click/input command frame, rebind to a live synthesized session, send it, confirm the client accepts
  (response, no reset). NOTE: this is adjacent to card 76's session-GUID problem — if the captured action
  frame carries manager-originated session GUIDs, the same synthesis is needed. Decide: integrate into
  SessionHandle, or compose via the proven replay path.
- **Phase B — runner integration.** Extend `_run_step_on_handle` (or a new dispatch) to execute action
  steps on the handle (using Phase A). Keep the order-dependent linear-template constraint in mind.
- **Phase C — flagship scenario + report.** Author a representative `.feature` (e.g. open the fixture
  form → input PF_EDIT_STRING → click a button → read element + assert) → transpile → run via the native
  runner/MCP against a live TestClient, **no Vanessa** → `ScenarioResult` passed, with evidence.
- **Phase D — package as the replacement demo.** A one-command entry (`qa-native-mcp` / a runner script)
  + a short doc: "run this scenario with no Vanessa." Evidence under docs/.../native-scenario-runner/.

## Acceptance
- A multi-step (≥1 read + ≥1 action) scenario runs end-to-end through qa_mcp against a live TestClient
  with NO Vanessa process, status=passed, assertions evaluated, ScenarioResult + evidence saved.
- Driven from a `.feature` through the native transpiler/runner.

## Log
- 2026-06-14: card created; current state scoped (run_single_session reads-only; actions on a separate
  replay path). Phase A (action-in-synthesized-session feasibility) is the first step.
- 2026-06-14: **Phase A feasibility — POSITIVE (static analysis).** The captured input action command
  frame (`fixture-input-capture` mgr ord 282, len 287) carries exactly 2 GUIDs
  (`d848f317-…`, `4451d8b2-…`) and **both are client-learnable** (appear in the capture's client→manager
  responses), neither is a config constant nor manager-originated. So an action command can be rebound
  from the LIVE session's client responses and sent in the synthesized session — it does **NOT** hit
  card 76's manager-originated-session-GUID wall. (Consistent with action-manifest captures replaying
  clean: input 281/281, click 26/26, choice 292/292, diverged_at=null.) → Integrating actions into
  `SessionHandle` is tractable. NEXT (Phase A spike, live): in `run_single_session`, after the
  synthesized bootstrap, send the rebinding-retargeted action command frame as a segment, confirm the
  client accepts it (response, no reset); then Phase B (runner dispatch) + Phase C (flagship .feature).
- 2026-06-14: **Phase A brick 1 done** — `SessionHandle.run_action(command_payload, rebinder=...)`:
  sends a captured action command frame on the already-open synthesized socket (no re-bootstrap, no
  Vanessa), optionally applies a captured->live rebinder, reads the client response, updates session
  state, returns a summary (`accepted` = client responded). Pure plumbing, 3 offline tests, 148 total
  pass. NEXT brick: build the captured->live GUID rebinder for the synthesized session (learn live
  GUIDs from the bootstrap's client responses / map the captured action frame's 2 client-learnable
  GUIDs to the live managed-form + element GUIDs) → live spike: open_and_bootstrap a fixture session →
  run_action(captured input/click frame, rebinder) → assert accepted, no reset.
- 2026-06-14: **Phase B done (offline).** `ScenarioRunner` gained an injected
  `action_resolver(step) -> (command_payload, rebinder)`; `run_single_session` now dispatches
  action-kind steps to `handle.run_action` (mixed read+action in one bootstrapped session), surfaces
  client-rejected actions as step errors, stays decoupled from the capture corpus + testable. 3 new
  offline tests (mixed dispatch / missing-resolver error / rejection error); 151 total pass. **What
  remains is the LIVE wiring (Phase A brick 2 + Phase C):** a concrete `action_resolver` that (1)
  locates the captured action command frame (via `build_action_renderers`/`find_marker_ordinal`) and
  (2) builds a GuidRebinder for the live synthesized session, PLUS navigating the synthesized session
  to the fixture form (frames 11..N from the template) before the action. Then a flagship `.feature`
  end-to-end live, no Vanessa. The live navigation+rebinder alignment is the remaining risk to validate
  on a booted client.
- 2026-06-14: **offline scaffolding COMPLETE.** `build_single_session_action_resolver(manager_chunks,
  captured_mfg)` + `_SingleSessionActionRebinder` (render_action retarget + captured→live
  managed-form-GUID substitution); resolver signature is `(step, handle)` so it reads
  `handle.state.managed_form_guid` post-bootstrap. Diagnosis: in `fixture-input-capture` the action
  frame's GUID `4451d8b2` IS the managed_form_guid (→ live); the other `d848f317` is a non-ack session
  GUID (live behavior TBD). 153 tests pass. **NEXT = the LIVE spike** (needs a booted client): a script
  that boots a fresh TestClient → `open_and_bootstrap` (synthesized, on the tm-v1-ro-batchQ3 template
  that opens the fixture form) → `form_summary` (reach the fixture) → `run_single_session` with the
  input action step + the resolver (capture=fixture-input-capture, captured_mfg=4451d8b2…) → assert the
  client accepts the action (response, no reset). Then resolve `d848f317` if it rejects, and Phase C
  (flagship .feature E2E + ScenarioResult).
- 2026-06-14: **Phase A LIVE PROVEN.** `native_action_session_spike.py/.ps1`: in one synthesized
  (capture-free, no Vanessa) session — bootstrap → run_segment nav to the fixture form (active-window
  ok, form-summary 6 frames ok) → `handle.run_action(input command, rebinder)` with captured→live
  managed-form-GUID rebind (4451d8b2 → live 5ffee762) → **client ACCEPTED (sent 287B, recv 665B, no
  reset), status=ok.** The `d848f317` session GUID needed no rebind. Actions now integrate into the
  synthesized SessionHandle, live. Evidence `evidence/native-scenario-runner/phase-a-action-session-
  spike-2026-06-14/`. Bug fixed en route (also affected single_session_proof): uint16 sequence fields
  overflowed for large message counters (frame4_sequence=80300 > 65535) → now wrap mod field width.
  **Phase A + B DONE. NEXT = Phase C:** a flagship `.feature` (open fixture → input → read+assert) →
  transpile → `run_single_session` with `build_single_session_action_resolver` → live ScenarioResult
  passed, no Vanessa.
- 2026-06-14: **Phase C FLAGSHIP PASSED → CARD DONE.** A read+assert+action scenario ran end-to-end
  through `ScenarioRunner.run_single_session` in ONE synthesized session, NO Vanessa, **status=passed**:
  read_active_window (assertion `HomePage`=True), read_form_summary (ok), input_text PF_EDIT_STRING
  (action ACCEPTED, sent 287B/recv 665B via run_action + the resolver's captured→live mfg rebind).
  `native_scenario_runner.py --action-capture` builds the resolver; `native_flagship_proof.ps1` boots a
  fresh TestClient (no Vanessa). Evidence `evidence/native-scenario-runner/flagship-vanessa-free-2026-06-14/`.
  **Acceptance met.** Follow-up (not blocking): `.feature` input steps need a capture-aware retarget —
  the Gherkin transpiler can't know the captured value, so it can't emit a correct input retarget; reads
  + assertions DO transpile from `.feature`. The flagship was driven from a Scenario JSON.
- 2026-06-14 (ext): **`.feature`-driven flagship PASSED** — follow-up resolved. Added
  `captured_input_value` to `build_single_session_action_resolver` (input_text retargets the CAPTURED
  value, not the Gherkin field-name `old_value`) + `--action-input-value` to `native_scenario_runner.py`.
  `flagship.feature` (read active window → assert HomePage → form summary → `в поле с именем
  'PF_EDIT_STRING' я ввожу текст 'PF_INPUT_PROOF'`) transpiles with no unmapped steps and runs
  end-to-end through qa_mcp, no Vanessa, **status=passed** (assert True, input accepted). 154 tests.
  Evidence `.../flagship-vanessa-free-2026-06-14/feature_driven_scenario_result.json`. Next extension
  candidates: a 2nd action kind (click_button) in the synthesized session; an in-session navigation
  action (open a form via an action rather than relying on the template reads).
- 2026-06-14 (ext 1/2/3 DONE): broadened the flagship — all live, no Vanessa:
  • **click_button** (step1): clicking PF_SHOW_CHOICE_MENU (254B cmd @ord37) accepted. Added
    `marker_ordinals` to the resolver (pin a command frame when the button name is not unique).
  • **navigation** (step2): open_list `e1cib/list/Справочник.Склады` (@ord8 of mut-warehouse) accepted
    in the synthesized session — navigation off the template's rails works.
  • **chained actions** (step3): a single `run_single_session` scenario [read_active_window (assert
    HomePage), read_form_summary, click_button PF_SHOW_CHOICE_MENU, form_command PF_MENU_2] →
    **status=passed**, both actions accepted (254B + 213B). `native_scenario_runner.py` gained
    `--action-ordinals` (marker=ordinal). Evidence: `.../flagship-vanessa-free-2026-06-14/`
    (click_button / navigation_open_list / chained_actions result JSONs). 155 tests pass.
  The native runner now drives multi-step, multi-action (input / click / navigation), chained,
  assertion-bearing scenarios in one synthesized session with NO Vanessa.

# 103. E-FW — step-library breadth + BDD mechanics (drop-in узкое место №1)

## Status
4.done

## Order Index
103

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-21 project review: the single biggest gap to a DROP-IN replacement of Vanessa Automation (the
  framework, not just `vanessa-mcp`). Vanessa exposes hundreds of canonical Gherkin steps; qa-mcp's transpiler
  has ~11 step patterns (`src/qa_mcp/scenario/gherkin.py::STEP_PATTERNS`) over 52 MCP tools, and NO Scenario
  Outline/Examples, tags, hooks or nested scenarios. Existing Vanessa `.feature` files do not transpile when
  their steps are uncovered (the transpiler never silently drops — it lists them in `unmapped`).
- Parent epic: card 102. Capability (proposed): a new `qa-mcp-bdd-framework` (the authoring/runner layer) on top
  of the existing `qa-mcp-protocol-lab` driver.

## Summary
Raise the Gherkin authoring surface from a ~11-phrase demo to a real BDD layer so unaltered Vanessa feature
suites run on qa-mcp:
- **Vocabulary** — map the high-frequency Vanessa-canonical steps onto the existing 52 MCP tools (most map 1:1:
  input/click/select/open/read/assert/navigation/dialog/table/list). Keep the single-source `STEP_PATTERNS` +
  the no-drift unit test that pins every phrasing to a kind.
- **Data-driven** — Scenario Outline + Examples tables; step-level `<placeholders>`; variables/context carried
  between steps.
- **Selection** — tags + tag filtering (run subset).
- **Lifecycle** — Before/After hooks (feature + scenario scope).
- **Composition** — nested scenarios (call a scenario as a step), the Vanessa "выполнить сценарий" idiom.

## Acceptance
- A representative REAL Vanessa feature corpus (assembled in the lab) transpiles at an agreed coverage threshold
  and runs green where the underlying form supports it; `transpile` reports the residual `unmapped` honestly.
- A Scenario Outline with an Examples table executes once per row (live or offline shape test).
- Tag filtering runs only the selected subset; a Before/After hook fires once per its scope; a nested-scenario
  call executes the callee's steps.
- The no-drift test pins every new phrasing → kind; `search_for_steps` lists the expanded library.

## Change Set (waves — living plan, lightweight per operator request 2026-06-21: card-as-plan, no full OpenSpec ff)
1. ✅ `step-library-expansion` (Wave 1) — DONE 2026-06-21. Vocabulary +13 phrasings onto existing kinds/tools.
2. ✅ `scenario-outline-examples + datatables` (Wave 2) — DONE 2026-06-21. Step DataTables (`| … |` attached to
   the preceding step as `params["table"]`); Scenario Outline + Examples expanded into one scenario per data row
   with `<col>` substitution (incl. in table cells).
3. ✅ `tags-and-hooks` (Wave 2) — DONE 2026-06-21. `@tags` parsed (feature-level inherited) + `filter_by_tags`
   include/exclude; Background steps prepended to every scenario (the practical hook).
4. ✅ `nested-scenarios` (Wave 2) — DONE 2026-06-21 (transpile mapping `run_subscenario` for «я выполняю
   сценарий 'X'»; runner execution = Wave 3).
5. 🔄 `runner-execution-wiring + live-verify` (Wave 3) — **OFFLINE wiring DONE + ACTION execution LIVE-verified
   2026-06-21**; corpus-residual external-.epf open RESEARCHED → spun into card 109 (the only remainder).
   - **Done (offline):** `ScenarioRunner` now executes the broadened vocabulary, not just the original 4 kinds —
     the assertion family over a single **cached** live read (linear-cursor safe): assert_form_open /
     assert_window_open / wait_window (active-window read), assert_element_present / assert_table_rows
     (form-summary read); strict-equality (`expect_equals`, «стал равен»); data-layer `assert_data` (session
     INDEPENDENT — runs without a TestClient boot); `skip_step` no-op; `run_subscenario` (callee runs on the
     SAME bootstrapped handle, recursion-guarded). MCP `run_scenario` now builds the callee registry from every
     scenario in the feature. 390 tests (+15 runner/mcp/odata). Code: `scenario/runner.py`, `mcp_server.py`.
   - **Done (offline, action synthesis 2026-06-21):** the new ACTION kinds are now executable end-to-end —
     `open_main_form` / `close_window` / `close_all_windows` are in `ACTION_REGISTRY` (replay the captured
     command frame, GUID-rebound via `render_form_command`); `connect_client` is a runner-owned lifecycle
     no-op (qa-mcp owns the connection). **The production bridge is wired:** MCP `run_scenario` gained
     `action_capture` (+ `action_input_value` / `action_ordinals`) → `_build_action_resolver` loads the
     capture's manager frames + captured ManagedForm/SecondaryFrame GUIDs and builds the
     `build_single_session_action_resolver`, which the runner uses to execute action steps on the bootstrapped
     handle. Previously NO action step executed via `run_scenario` (resolver was never wired). Validated
     offline against a real 107-frame capture (resolver locates + GUID-rebinds a frame). 394 tests (+4).
   - **Live-verified (assert family) 2026-06-21:** booted a native `1cv8 /TESTCLIENT` (manage_apache) and ran
     the assert family through the real `run_scenario` path on the live БСП HomePage (config-agnostic — genuine
     Cyrillic elements, not the bundled fixture): positive `assert_element_present 'ДиаграммаПоПериодам'` →
     ok/True, negative (absent) → assert_failed/False, `assert_form_open 'HomePage'` → ok/True, `skip_step` →
     ok. The live run **found + fixed a real bug**: a `read_form_summary`-then-assert sequence returned `error`
     (the assert re-advanced the linear cursor past frame 17) → reads now route through the read cache so the
     assert reuses them; pinned by 2 offline regressions. Evidence: `evidence/card103-wave3-live-2026-06-21/`.
   - **Live-verified (ACTION execution — open_main_form) 2026-06-21:** an action step (NOT a read/assert)
     executes on the real `vanessa_client` through `run_scenario`. The runner's open kinds were wired to a
     single captured-frame replay (the `action_resolver` path) — which card 101 proved cannot open a form live
     (a live open is the multi-frame `splice_navigate` cold sequence against the LIVE desktop MainFrame, not one
     GUID-rebound frame). So `ScenarioRunner` gained a **`navigate_resolver`**: `open_main_form` / `open_list`
     now route to `_open_form_by_link(handle, nav_link)` — the config-agnostic, fixture-free, capture-free
     mechanism that opened 8/8 forms live via `read_form_descriptor` (card 106). `mcp_server._nav_link_for_step`
     derives the e1cib link (open_main_form `object_type`+name / open_list catalog); `_build_navigate_resolver`
     lazily loads its own `VALUE_READ_TEMPLATES` for the splice header (frame 218 — absent from a read
     scenario's `DEFAULT_TEMPLATES`) and passes it as `splice_templates`, so open steps work whatever templates
     the reads use. **Live run:** «Я открываю основную форму справочника 'Валюты'» + «… 'Банки'» both opened in
     ONE bootstrapped session (real per-form SecondaryFrame/ManagedForm GUIDs resolved) — two DIFFERENT objects
     ⇒ the config-agnostic "retarget to a DIFFERENT object than captured" requirement is met capture-free (no
     open-main-form capture needed). 404 tests (+8). Evidence:
     `evidence/card103-open-action-live-2026-06-21/`.
   - **Researched 2026-06-21 → card 109:** the corpus-residual external-`.epf` open
     (`я открываю внешнюю обработку … (Расширение)`) has no `e1cib`/URL link — it is `ВнешниеОбработкиМенеджер.
     Подключить(path)` (BSL), which Vanessa drives via VanessaExt. So it is OUTSIDE qa-mcp's protocol-replay model;
     the native, Vanessa-component-free path is «Главное меню → Файл → Открыть» + an OS file dialog (xtest, card-100
     class). Go/no-go = GO as a dedicated card: `openspec/board/1.backlog/109-external-data-processor-open.md`.
     Findings + live main-window screenshot: `evidence/card103-external-epf-research-2026-06-21/`.
   - **Optional deeper leg:** the capture-backed `action_resolver` path (single-frame click/select/input on an
     already-open form, GUID-rebound) stays offline-validated vs a real 107-frame capture; live-driving one needs
     an action capture whose frames
     match the freshly-opened form (a deeper follow-on now that the live open works).
6. ✅ `vanessa-corpus-transpile-gate` (Wave 4) — DONE 2026-06-21. Hermetic in-repo gate
   (`qa-vanessa-canonical-corpus.feature` must transpile 0-unmapped, 9 scenarios) + optional lab-corpus gate
   (≥95%, skips when absent) in `tests/test_corpus_gate.py`; CLI `--min` exit-code gate; residual documented in
   `docs/vanessa-mcp-parity.md`.

## Progress (measured — `tools/protocol-research/corpus_transpile_coverage.py`)
- **Baseline (Wave 0):** transpile coverage over the real lab corpus (11 features: four demo10413 contracts +
  six private third-party smokes + the in-repo sample) = **11.9% (12/101 steps)**; 24 distinct unmapped phrasings.
- **After Wave 1:** **84.2% (85/101 steps)**, 7 distinct unmapped. Code: `scenario/gherkin.py` (+13 patterns,
  broadened click/input, empty-quoted-arg support), `scenario/model.py` (new READ/ACTION/SKIP kinds +
  `expect_equals`). 356 tests green (+1). New kinds: assert_form_open / assert_window_open /
  assert_element_present / wait_window / open_main_form / close_window / close_all_windows / connect_client /
  skip_step (Vanessa-runtime setting, recognized-and-skipped) + read_form_value/`expect_equals` («стал равен»).
- **After Wave 2:** **97.8% (89/91 effective steps)** — DataTable rows now attach to their step (corpus step
  count 101→91), and the table-bearing/connect-with-params phrasings map. 4 demo10413 contracts + 6 private third-party
  smokes now transpile 100%. **The ONLY residual is `я открываю внешнюю обработку или отчет … (Расширение)`
  (2×)** — a genuine NEW mechanism (open an external .epf in the client), Wave 3 / a fresh card. 357 tests.
  Code: `scenario/gherkin.py` (parser rewrite: tags, Background, DataTables, Outline/Examples, `filter_by_tags`,
  +4 patterns), `scenario/model.py` (Scenario.tags + `assert_table_rows`/`run_subscenario`).

## Verify
- Wave 1: offline — `pytest` 356 green; `corpus_transpile_coverage.py` 11.9% → 84.2%.
- Wave 2: offline — `pytest` 357 green (added tags/Background/DataTable/Outline test); coverage 84.2% → **97.8%**
  (residual = external-epf open only). Live runner execution of the new kinds is task #4 / Wave 3.
- Wave 4: offline — `pytest` 359 green (added `test_corpus_gate.py`: hermetic in-repo gate + lab-corpus ≥95%
  gate); `corpus_transpile_coverage.py --min 0.95` exits 0 (97.8%). Residual documented in the parity note.
- Wave 3: offline — `pytest` **404 green** (runner execution + action synthesis + navigate bridge). LIVE — the
  assert family + an `open_main_form` ACTION step both verified through `run_scenario` on the real `vanessa_client`
  (evidence `evidence/card103-wave3-live-2026-06-21/` + `evidence/card103-open-action-live-2026-06-21/`).
- REMAINING: external-`.epf` open (corpus residual, genuinely-new mechanism) — candidate fresh card. Optional
  deeper leg: live-drive a capture-backed click/select/input on a freshly-opened form.

## Archive
- 2026-06-22 closed to `4.done` as part of roadmap-111 item 1 (board hygiene). Waves 1/2/4 done + Wave 3
  runner-execution wiring done and the assert family + an `open_main_form` ACTION step LIVE-verified through
  `run_scenario`. The transpile corpus is 100% (the external-`.epf` residual was spun into card 109, `4.done`).

## Result
DONE → 4.done. The drop-in узкое место №1 is closed: the Gherkin authoring surface grew from ~11 phrases to a broad
canonical step library with full BDD mechanics (Scenario Outline/Examples, `@tags`+filtering, Background,
DataTables, nested scenarios); the runner executes the broadened vocabulary; and the real Vanessa corpus transpiles
**100%** (gated by `tests/test_corpus_gate.py`). LIVE-verified on `vanessa_client` (assert family +
`open_main_form` via the `navigate_resolver`, config-agnostic/capture-free). The **only** remaining piece is an
*optional, non-blocking* deeper leg — live-driving a capture-backed single-frame click/select/input on a
freshly-opened form (GUID-rebound `action_resolver` path; today offline-validated vs a real 107-frame capture).
That optional follow-on is recorded in roadmap 111 (not a blocker for closing 103).

## Next
- Optional deeper leg (capture-backed single-frame action on a freshly-opened form, live) is tracked as a
  non-blocking follow-on in `openspec/board/3.inprogress/111-2026-06-22-epic-productize-harden-extend.md`.

## Related
- Parent: card 102. Code: `src/qa_mcp/scenario/{gherkin,runner,model,actions,replay}.py`,
  `docs/vanessa-mcp-parity.md` (the step table + authoring note).
- Reference oracle: the genuine Vanessa manager on Linux ([[vanessa-mcp-linux-genuine-manager]]) exposes
  `search_for_steps_by_keywords` / `frequently_used_steps` — use it to enumerate the canonical step set to cover.
- Memory: [[surpass-vanessa-native-superset-goal]], [[qa-mcp-capture-free-epic]].

## Log
- 2026-06-21 card created (E-FW track, drop-in узкое место №1). Thin backlog stub; change set outlined, not yet
  ff-processed.
- 2026-06-21 operator chose lightweight delivery (card-as-plan, no full OpenSpec ff — research mode). Wave 0
  (measure) + Wave 1 (vocabulary) DONE in-session: built `corpus_transpile_coverage.py`, measured baseline
  11.9%, added 13 canonical phrasings + new step kinds + `expect_equals` + empty-quoted args → **84.2%** corpus
  coverage, 356 tests green. Card kept as the living plan (waves 2-4 remain). Tasks #1-#5 track the waves.
- 2026-06-21 Wave 2 (BDD mechanics) DONE: parser rewrite — `@tags` (feature-inherited) + `filter_by_tags`,
  `Background` prepend, step `DataTables`, `Scenario Outline`+`Examples` expansion with `<col>` substitution,
  `run_subscenario` nested-call mapping. Coverage **84.2% → 97.8%** (89/91 effective steps; DataTable rows no
  longer count as steps). Sole residual = external-epf open (Wave 3 / fresh card). 357 tests green. Remaining:
  Wave 3 (runner exec wiring + live-verify) + Wave 4 (lock the gate + document residual).
- 2026-06-21 Wave 4 (gate + docs) DONE: hermetic in-repo gate fixture `qa-vanessa-canonical-corpus.feature` +
  `tests/test_corpus_gate.py` (in-repo 0-unmapped/9-scenario gate + lab-corpus ≥95% gate, skips when absent);
  `corpus_transpile_coverage.py --min` exit-code gate; breadth/coverage/BDD-mechanics/residual documented in
  `docs/vanessa-mcp-parity.md`. 359 tests green. Card → 3.inprogress (only Wave 3 remains, needs a lab boot).
- 2026-06-21 Wave 3 OFFLINE runner-execution wiring DONE: `ScenarioRunner` now executes the full broadened
  vocabulary (assert family over a cached single read, `expect_equals` strict-equality, `assert_data` data-layer
  assert that needs NO TestClient, `skip_step` no-op, `run_subscenario` nested-call on the same handle); MCP
  `run_scenario` builds the callee registry from the feature. 373 → 390 tests (+15 runner/mcp/odata, +2 of those
  are the OData live-regression pins below). The remaining new ACTION kinds route to `action_resolver` like the
  original action steps; their live synthesizers + on-lab read+assert verify stay LAB-gated (Xvfb boot).
- 2026-06-21 published the Wave-3 OFFLINE wiring on `main` in `f647a4a` (scoped `$opsx-pub`, co-published with
  card 105). Card stays in 3.inprogress for the LAB-gated remainder (live action synthesis + read+assert verify).
- 2026-06-21 Wave-3 ACTION synthesis wired OFFLINE: `ACTION_REGISTRY` +3 kinds (open_main_form / close_window /
  close_all_windows → render_form_command identity+rebind); `connect_client` runner no-op; MCP `run_scenario`
  `action_capture` → `_build_action_resolver` → `build_single_session_action_resolver` (the production bridge that
  was missing — no action step executed via run_scenario before). Validated offline vs a real 107-frame capture.
  394 tests (+4). Published `c58289a`.
- 2026-06-21 LIVE assert-family verify (boot session): booted a native TestClient (manage_apache) and proved the
  assert family on the live БСП HomePage via `run_scenario` (config-agnostic Cyrillic elements): positive/negative
  element asserts + form-open + skip all correct. Found+fixed a real read-then-assert linear-cursor bug (reads now
  route through the cache); +2 offline regressions → 396 tests. Evidence `evidence/card103-wave3-live-2026-06-21/`.
  Remaining live: ACTION execution on-client + config-agnostic open_main_form retarget + 105 UI/106 smoke.
- 2026-06-21 LIVE ACTION execution verify (the last live leg): an `open_main_form` action step EXECUTES on the
  real `vanessa_client` via `run_scenario`. Added a `navigate_resolver` to `ScenarioRunner` so open kinds route to
  the proven live `_open_form_by_link` (splice_navigate) instead of the offline-only captured-frame replay;
  `mcp_server._nav_link_for_step` + `_build_navigate_resolver` (lazily loads VALUE_READ_TEMPLATES for the splice
  header so open steps work under a read scenario's DEFAULT_TEMPLATES). Live: «… справочника 'Валюты'» + «'Банки'»
  both opened in one session (real S.F/M.F GUIDs resolved) — two DIFFERENT objects ⇒ config-agnostic retarget met
  capture-free. +8 offline tests → 404 green. Evidence `evidence/card103-open-action-live-2026-06-21/`. Sole
  remaining: external-`.epf` open (genuinely-new mechanism, candidate fresh card).
- 2026-06-22 CLOSED → `4.done` (roadmap-111 item 1, board hygiene). The external-`.epf` residual was delivered as
  card 109 (`4.done`) → corpus 100%; the only remaining piece is an *optional, non-blocking* deeper leg (live
  capture-backed single-frame action on a freshly-opened form), recorded as a follow-on in roadmap 111. Card 103
  is substantially complete and no longer the phase in flight.

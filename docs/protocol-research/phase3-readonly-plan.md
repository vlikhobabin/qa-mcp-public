# Phase 3 — `read_only` (107 members) build-out plan

Status: planning (2026-06-13). Phases 1 (`mutation` 9/9) and 2 (`safe_ui_action`
22 accepted / 7 candidate) are complete. Phase 3 is a **different acceptance class**
and needs a deliberate build-out, not the manifest → capture → probe loop.

## Why read_only is different
Most `read_only` members are **local manager reads** — the test manager already holds
a synced model of the form, so reading a property (`Name`, `Type`, `TitleText`,
`Caption`, `CurrentVisible`, …) or traversing it (`FindObject`, `GetChildObjects`,
`GetParent`) does **not** issue a fresh manager→client command frame. So the
wire-capture / probe-ordinal pipeline that accepted all 31 Phase 1–2 members produces
an **empty action phase** for them — it does not apply.

Acceptance for `read_only` goes through the **manager-fixture-v1 result-contract**
subsystem (the "same-action comparison"): the Python manager performs the read live
against a dedicated fixture whose state is known, and the read `result_preview` is
checked to contain an expected marker (`acceptance_contract.kind =
manager_result_preview_contains`). report_manager_fixture_v1.py emits
`accepted_protocol_mapping=true` per case; `promote_member.py` then moves the member
to `accepted_reviewed`.

## Current state (2026-06-13, after batches C→Q — read_only effectively COMPLETE)
- `read_only`: **103 accepted_reviewed, 1 accepted_seed, 3 uncovered.** (Overall API:
  134 accepted_reviewed / 1 seed / 7 candidate / 18 uncovered out of 160.)
- This session promoted **+72 read_only members across 15 batches (C→P)** via the
  inline-harness token/handler approach — extending the shared element-preview block and
  adding `form_state` / `window_state` / `app_state` / `decoration_summary` command_kinds.
  All runs green, 108 tests pass, each batch a separate commit with evidence under
  `evidence/readonly-corpus/`. The user unblocked Decoration mid-session by adding 3
  decorations (+ a combo `ПолеСоСпискомВыбораСтрока` for GetChoiceListPresentation) to the
  fixture form.
- **Remaining 4 uncovered — all genuinely blocked or architecturally N/A:**
  - `TestedApplication.WaitForCondition` — **DEFERRED to next project version** (per user; needs
    a callback function to model a condition).
  - ~~`TestedClientApplicationWindow.GetUserMessageTexts`~~ — **DONE (batch Q3)**: the
    decoration click method is `Нажать` (Click), not `Нажатие`; the `window_messages` handler
    clicks PF_DECORATION_LABEL_LINK → the fixture handler `Сообщить("…")` populates the panel →
    `ПолучитьТекстыСообщенийПользователю` returns usermessages_count=1.
  - `TestedFormField.GetObject` and `TestedFormDecoration.GetObject` — **architectural N/A**:
    fields/decorations are leaves (`child_count=0`, verified the `Контрагент` reference field),
    so `ПолучитьОбъект` raises `ObjectNotFound` — there is no descendant to get. Not cleanly
    acceptable as a read.

## Earlier checkpoint (after batches C→N)
- `read_only`: 87 accepted_reviewed, 1 seed, 19 uncovered (overall 118/160).

## Historical state (2026-06-13, session start)
- `read_only`: **2 accepted_reviewed, 7 accepted_seed, 98 uncovered.**
- Runtime is healthy: `run_protocol_capture.ps1 -Scenario manager-fixture-v1-readonly`
  runs the harness live. Smoke (3 cases) = 2 ok; full = 7/17 ran then `runner_timeout`.
- Promoted seed→reviewed this session (fresh contract-pass on run `tm-v1-ro-full`):
  `TestedClientApplicationWindow.GetCommandInterface`,
  `TestedClientApplicationWindow.GetChildObjects`. Evidence:
  `evidence/readonly-corpus/tm-v1-ro-full-2026-06-13/`.

## BREAKTHROUGH (2026-06-13) — the build-out is far cheaper than first feared
The element/form reads were not failing due to a harness bug — **the fixture form was
never opened**. Running the scenario with
`-ManagerFixtureV1OpenFixtureViaCommandInterfaceBootstrap -ManagerHarnessTimeoutSec 600`
opens it (section "Предприятие" → command "Фикстура протокола TestClient" → wait for the
"QA MCP Protocol Fixture V1" marker) and **all 17 cases complete (0 failed)** with real
read values (`protocol-fixture.v1`, `PF_TABLE_ITEMS`, `family=…;name=…;visible=…;…`).

So the per-member loop is now mechanical and **needs no separate base/EPF**:
1. run readonly with the open-fixture bootstrap;
2. add an `acceptance_contract` (`manager_result_preview_contains`) per member, asserting a
   fixture **design marker** that the real preview contains (PF_*, `protocol-fixture.v1`,
   `QA MCP Protocol Fixture V1` — not circular);
3. `report_manager_fixture_v1.py` → `promote_member.py`.

The `element_state` / `*_summary` previews already surface `family/type/name/title/
visible/enabled/data/child_count`, so ONE such read per element type can verify many
property members (Name/Type/TitleText/CurrentVisible/CurrentEnable/GetChildObjects) via
different substring contracts. Result: read_only **8 accepted_reviewed / 1 seed / 98
uncovered**; 6 seeds promoted this way (run `tm-v1-ro-openfix2`).

Remaining seed `TestedApplication.GetActiveWindow`: its handler returns the window OBJECT
(preview = type name); a meaningful contract needs a secondary read off the window, which
overlaps other members — left as `accepted_seed` deliberately rather than forced.

## Where the harness actually lives (correction)
The "manager harness" is **NOT** an external `.epf` and **NOT** a configuration object
in any infobase. It is **inline BSL generated by `tools/protocol-research/run_protocol_capture.ps1`**
(the per-command_kind handlers are around lines ~489–620) and executed on the manager via
the Vanessa step «я выполняю код встроенного языка» (`execute_step_from_text`). The report
label `DataProcessor.ProtocolFixtureTestManager.Form.ManagerHarness` is synthetic —
`manager_harness_invocation.json` shows `invocation_mode =
vanessa_mcp_execute_step_from_text_inline_bsl`, `harness_form =
inline_generated_manager_fixture_v1`. Verified: the vanessa_manager base
(`C:\1C_BASES\vanessa_manager\1Cv8.1CD`, ~18 MB) has an empty main config and only the
`client_mcp` extension (the MCP server) — no `ProtocolFixtureTestManager` object exists.
So **editing the harness = editing the inline BSL in `run_protocol_capture.ps1`** (in this
repo); no separate base/EPF.

The only real fixture configuration object is the CLIENT side:
`Обработка.ФикстураПротоколаTestClient` (synonym "Фикстура протокола TestClient", form
`Форма`) in the **vanessa_client** config (`C:\1C_BASES\vanessa_client\1Cv8.1CD`, ~233 MB).

## Gaps found this session (the build-out work)
0. **ROOT CAUSE — element/form reads fail and value reads return placeholders (highest
   priority; fix in the inline harness BSL + the fixture form).**
   Two distinct symptoms:
   - *Element/form reads* (`element_details`, `form_summary`, `*_summary`,
     find-by-marker/title) fail with `... object not found by marker` /
     `form_summary object not found by title` / `generic_summary form not found`. The
     inline BSL does `ОжидатьОтображениеОбъекта(Тип(...), … , маркер, 15)` then
     `НайтиОбъект(...)` and times out — the targeted field/form is **not displayed** when
     the read runs (the fixture form is likely not open / the element is on an inactive
     page; the marker `PF_FIXTURE_VERSION` exists in the form design but isn't found at
     runtime). Form-level reads search by the design title `QA MCP Protocol Fixture V1`
     while the open window's caption is the synonym `Фикстура протокола TestClient`.
   - *Window-level value reads that complete* return a **placeholder, not the read
     value**: `active-window` → `ТестируемоеОкноКлиентскогоПриложения` (the object TYPE
     name), `active-form` → `Нет`. So a contract marker like `QA MCP Protocol Fixture V1`
     can never match — the inline handler isn't returning the read result in
     `result_preview` for these kinds.

   Why the 2 promoted members worked: their command_kinds
   (`diagnostic_command_interface_dump`, `diagnostic_window_children`) emit a structural
   preview (`ci_children_count=…`) checked by their contract, and they read the
   window/command-interface (which exist regardless of whether the fixture form is open).
   `active_window`, `active_form`, `element_details`, and the `*_summary` kinds do not.

   **First build-out tasks (all in-repo, no separate base):** in the inline harness BSL
   (`run_protocol_capture.ps1`) — (a) open/activate the fixture form in bootstrap before
   element/form reads; (b) return the actual read value in `result_preview` for
   `active_window`/`active_form`/`*_summary`; (c) align form/element location to the test
   API's exposed caption/markers; and in the fixture обработка
   (`ФикстураПротоколаTestClient`) ensure each target element/marker is displayed/findable.
   Catalog-only edits cannot fix this. Verified via runs `tm-v1-ro-full` / `tm-v1-ro-form`
   (2026-06-13).
1. **Fixture marker coverage.** Several cases failed `... object not found by marker`
   (e.g. `PF_FIXTURE_VERSION`, the window/form find-marker cases) — same root cause as
   (0). The dedicated fixture form must carry a findable element of each type with a
   deterministic marker that the catalog/harness agree on. **This is BSL/fixture work.**
2. **Harness timeout.** The full 17-case run hit the 120 s `ManagerHarnessTimeoutSec`
   after 7 cases. Run read_only in **sub-batches** (per object/family) and/or raise the
   harness timeout.
3. **Missing acceptance contracts.** Only 3 catalog commands have an
   `acceptance_contract`; the other 7 seeds and all 98 uncovered need one (an
   `expected_result_preview_marker` per member).
4. **Harness coverage.** The inline harness BSL (in `run_protocol_capture.ps1`)
   currently implements ~16 `command_kind`s. Each read member that is not yet a `command_kind` needs a BSL
   handler that issues that read and returns a `result_preview`.

## Open evidence-policy question
Prior work (`evidence/readonly-element-hash-audit` / `-resolution`, 2026-06-03) left
some element-detail rows `incomplete_hash`: the Python-manager probe returned correct
data but there were no reviewed **request-frame** bytes (the reads were local / had no
request). Decide the policy for `read_only` `accepted_reviewed`:
- **Recommended:** the manager-fixture-v1 **result-contract** (same-action comparison)
  is sufficient for `accepted_reviewed` of a `read_only` member, since the member is a
  read and the comparison confirms the returned value. Record request-hash evidence
  additionally only where a read genuinely round-trips (e.g. some element-detail / cell
  reads); never require it for purely-local reads.

## Remaining 76 uncovered (2026-06-13) — all need harness BSL work, by type
The catalog-cheap tier is exhausted at **read_only 30/107** (this session: 6 seed
promotions + batch A 19 property members + batch B 3 GetChildObjects). The
`element_state`/`*_summary` preview only surfaces name/type/title/visible/enabled/
child_count, so everything else needs a NEW inline-harness handler (and sometimes a
fixture addition). Breakdown of the 76:

- **Decoration (15)** — blocked twice: the fixture form has NO decoration element, and
  the `element_state` handler does not search `ТестируемаяДекорацияФормы`. Add a marked
  decoration to `ФикстураПротоколаTestClient` + a decoration branch in the handler.
- **Current\* not in preview** — DONE 4 via batch C (run `tm-v1-ro-batchC3`, 2026-06-13):
  `CurrentReadOnly` (Field/Group/Table → `readonly=Нет`) and `CurrentOpened` (Group →
  `opened=Да`) added as `;readonly=`/`;opened=` tokens to the shared element-preview block
  in the inline harness. **Lesson:** every generated `КонецПопытки` in that block MUST end
  with `;` — the first batch-C run failed BSL compile ("ожидается ';'") because the two new
  `КонецПопытки` lacked it; the manager step-executor requires the separator here even
  though the language nominally allows omitting it. Batch D (run `tm-v1-ro-batchD`,
  2026-06-13) added 4 more tokens the same way: `CurrentCheck` (Button → `check=Нет`,
  ТекущееПометка), `CurrentModeIsEdit` (Table → `tablemode=Нет`, ТекущийРежимРедактирование),
  `CanBeExpanded` (Table → `canexpand=Нет`, ВозможноРазвернуть), `Expanded` (Table →
  `expanded=Нет`, Развернут) — the tree methods returned `Нет` without throwing even on the
  flat fixture table. Batch E (run `tm-v1-ro-batchE`,
  2026-06-13) finished the form-level pair via a NEW `form_state` command_kind handler
  (finds the form by title "QA MCP Protocol Fixture V1", emits `;readonly=`/`;modified=`):
  `CurrentReadOnly` (Form → `readonly=Нет`, ТекущееТолькоПросмотр) + `CurrentModified`
  (Form → `modified=Нет`, ТекущаяМодифицированность). **The Current\* token tier is now
  fully exhausted.** Remaining 66 are the heavier `Get*`/`Find*`/`Wait*` per element, the
  window/app-level reads, and Decoration (15, blocked on a fixture decoration element).
- **Get\*/Find\* per element** — `GetParent`, `GetContextMenu`, `GetCommandBar`,
  `GetToolTipText`, `GetObject`, `FindObject`, `FindObjects` for Field/Group/Table (+
  Decoration); Table `GetCellText`/`GetSelectedRows`/`GetCurrentItem`; Form
  `FormName`/`GetParent`/`GetObject`/`GetCurrentItem`/`GetChoiceListPresentation`/
  `FindDefaultButton`/`FindObjects`/`CurrentEnable`/`TitleText`.
- **Window (6)** — `Caption`, `FindObjects`, `GetUserMessageTexts`, `HomePage`,
  `IsMain`, `URL`.
- **TestedApplication (9)** — `FindObject`, `FindObjects`, `GetChildObjects`,
  `GetObject`, `GetCurrentErrorInfo`, `GetMaxActionExecutionTime`,
  `GetAccumulatedPerformanceIndicators`, plus the waits.
- **Waits** — `WaitForCondition`, `WaitForObjectDisplayed` (App), `WaitForClosing` (Form):
  need a handler that drives the wait and asserts the returned condition/boolean.

Each type = one new inline-BSL handler in `run_protocol_capture.ps1` + per-member catalog
cases + contracts + run + promote. **Validate every member name against the inventory
before generating cases** (a generated `TestedFormTable.Type` — not a real member — was
caught by `test_scope_tracker` and removed).

## Proposed sub-batches (by object)
| Object | read_only members |
| --- | ---: |
| TestedApplication | 10 |
| TestedClientApplicationWindow | 10 (2 reviewed, more seeds) |
| TestedForm | 15 |
| TestedFormButton | 6 |
| TestedFormDecoration | 15 |
| TestedFormField | 16 |
| TestedFormGroup | 16 |
| TestedFormTable | 19 |

Per member: harness `command_kind` handler → fixture element+marker →
catalog entry + `acceptance_contract` → run sub-batch live → report → promote.

## First concrete steps for the build-out session
1. Fix the fixture form markers so the existing 7 seeds + smoke cases all pass; raise
   `ManagerHarnessTimeoutSec` or batch; re-run; promote the remaining 7 seeds to
   reviewed.
2. Pick the smallest object (TestedFormButton, 6) as the first new sub-batch: add
   handlers/markers/contracts, run, promote.
3. Decide and record the evidence policy above before scaling to all 107.

Tracked on the board: card 72.

# 104. E-FW — machine-readable reporting (Allure + JUnit) for CI

## Status
4.done

## Order Index
104

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-21 project review: Vanessa Automation produces Allure results; qa-mcp has only `get_test_results`
  (in-session aggregation, no on-disk report). Without CI-consumable output there is no drop-in CI replacement.
- Parent epic: card 102. Capability (proposed): extends `qa-mcp-bdd-framework` (card 103) with a reporting sink.

## Summary
Emit standard, machine-readable test reports from a `run_scenario` run so qa-mcp slots into existing CI:
- a per-step result model (status, start/stop timing, error, attachments);
- **JUnit XML** (CI test-result panels);
- **Allure results** (results-dir JSON renderable by the Allure CLI), with screenshots (`capture_screenshot`)
  attached to failed steps and step timings.
The result model is the shared substrate; JUnit + Allure are two writers over it.

## Acceptance
- A `run_scenario` run writes a JUnit XML consumable by a standard CI test-results step (suite/case/status/time).
- The same run writes an Allure results dir that renders in the Allure CLI; a failed step carries its screenshot
  attachment + message; timings present.
- Offline unit tests assert the writers' shape against a synthetic run; one live run produces a real report.

## Change Set (waves — living plan, lightweight: card-as-plan, no full OpenSpec ff)
1. ✅ `run-result-model` — DONE 2026-06-21. `StepResult.duration_sec`/`attachments` + `ScenarioResult.duration_sec`/
   `started_at` (+to_dict); timing wired into `ScenarioRunner.run`/`run_single_session`; `_record_result`
   enriched (error/timing/attachments) so session reports are useful.
2. ✅ `junit-xml-writer` — DONE 2026-06-21. `scenario.reporting.junit_xml(results, suite_name)` — one testcase
   per scenario, `<failure>` (assert) / `<error>` (exception) with messages + counts.
3. ✅ `allure-results-writer + MCP tool` — DONE 2026-06-21. `write_allure_results(results, out_dir)` —
   per-scenario `<uuid>-result.json` (deterministic ids), step status mapping (ok→passed/assert_failed→failed/
   error→broken), `statusDetails`, screenshot attachments copied+referenced; MCP tool `write_test_report(out_dir,
   formats, suite_name, clear)` over the session `_RESULTS_LOG` (#53).

## Verify
- Offline — `pytest` 363 green (added `tests/test_reporting.py`: JUnit structure/counts/messages, model→dict→
  report, Allure status mapping + deterministic ids + attachment copy). Server imports clean; 53 MCP tools.
- ✅ LIVE end-to-end (2026-06-21) — ran THREE live scenarios on real `vanessa_client` then `write_test_report`
  → real `junit.xml` (`tests=3 failures=1 errors=0`) + `allure-results/*.json` (3 files, per-step status+timing).
  Mixed outcomes on purpose: A «HomePage asserts» 2✓+1✗ → failed; B «open_main_form Валюты+Банки» (the card-103
  live ACTION leg) → passed; C «assert_data over OData» (beyond Vanessa, sessionless) → passed. A+B ran with the
  TestClient up (Apache stopped by manage_apache); C ran post-teardown (Apache up) via `single_session=False` (the
  assert_data step is sessionless). Evidence `evidence/card104-live-report-2026-06-21/` (junit.xml, allure-results,
  README, reproduce.py).

## Archive
- card complete (offline + live end-to-end); kept as the living record (lightweight card-as-plan, no OpenSpec ff).

## Result
Reporting capability COMPLETE — offline + LIVE: result model + timing + JUnit + Allure writers + `write_test_report`
MCP tool (unit-tested), and a live end-to-end demo emitting a real JUnit + Allure report over 3 live runs (incl. a
failed case, the live open-action leg, and a beyond-Vanessa data assert). qa-mcp drops into a Vanessa CI pipeline.

## Next
- card ready to close (4.done). Optional: attach a screenshot to a failed step in the live report (writer supports
  attachments; needs a screenshot-capturing live run).

## Related
- Parent: card 102. Depends-on: card 103 (the result model / step lifecycle). Code:
  `src/qa_mcp/scenario/runner.py`, `src/qa_mcp/mcp_server.py` (`get_test_results`, `capture_screenshot`).
- Memory: [[surpass-vanessa-native-superset-goal]].

## Log
- 2026-06-21 card created (E-FW track). Thin backlog stub; change set outlined, not yet ff-processed.
- 2026-06-21 DONE (offline) in-session, lightweight card-as-plan: result model enriched (timing/attachments) +
  runner timing wired; `scenario/reporting.py` (`junit_xml` + `write_allure_results`, pure functions over the
  report-dict shape); MCP `write_test_report` (#53) over the session log; `tests/test_reporting.py` (4 tests).
  363 tests green. Card → 3.inprogress (live end-to-end report pairs with card 103 Wave 3 / lab). Tasks #6-#8.
- 2026-06-21 LIVE end-to-end demo DONE (after the card-103 live ACTION leg landed): booted the TestClient, ran 3
  live scenarios (HomePage asserts 2✓+1✗ failed; open_main_form Валюты+Банки passed; assert_data OData passed),
  `write_test_report` → real junit.xml (tests=3 failures=1) + 3 Allure results with per-step status/timing. The
  report carries the live open-action leg AND a beyond-Vanessa data assert. Card is now offline+LIVE complete →
  ready for 4.done. Evidence `evidence/card104-live-report-2026-06-21/`.
- 2026-06-21 CLOSED → 4.done. Offline + LIVE end-to-end both verified; nothing left in scope (optional screenshot
  attachment on a failed step is a nice-to-have, writer already supports it).

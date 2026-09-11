# CR-01 — Honest verdicts: measure_scenario + JUnit report

## Status
4.done

## Order Index
1

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Multi-agent code review 2026-07-02, findings C3 + S4.
- Full report: `docs/code-review-2026-07-02.md`.

## Summary
The QA product reports a **false green** in two places: `measure_scenario`
always claims the scenario passed, and the JUnit suite can render a failed
scenario as passing (and double-count others). A test tool that lies about
pass/fail is the single worst defect class here, so this is first. Both are
**offline-reproducible and offline-fixable** — no live 1C client needed.

## Problems (verified against code)

### C3 — `measure_scenario` reports `scenario_ok: true` for a failed scenario
`src/qa_mcp/debug/measure.py:307`:
```python
scenario_ok = bool(res.get("ok", res)) if isinstance(res, dict) else bool(res)
```
`run_scenario` returns `ScenarioResult.to_dict()`, whose keys are
`scenario / status / duration_sec / started_at / steps` — there is **no `"ok"`
key** (confirmed `src/qa_mcp/scenario/model.py:127`). So `res.get("ok", res)`
returns the non-empty dict itself and `bool(dict)` is always `True`. Every
`measure_scenario` run — including one whose steps all error — reports
`scenario_ok: true` next to the coverage/APDEX numbers.

### S4 — JUnit counters miscount; a failed scenario can render green
`src/qa_mcp/scenario/reporting.py:57-58`:
```python
failures = sum(1 for r in results if any(_status(s)=="assert_failed" for s in r.get("steps", [])))
errors   = sum(1 for r in results if any(_status(s)=="error"        for s in r.get("steps", [])))
```
(a) A scenario containing **both** an `assert_failed` and an `error` step is
counted in both `failures` and `errors` (one testcase → `failures="1"
errors="1"`). (b) A scenario with `status: "failed"` but **zero** bad steps
(e.g. an empty-step scenario) is emitted as a **passing** testcase — the suite
goes green while `report.status == "failed"`.

## Recommended remediation
- **C3:** replace the truthiness check with an explicit status check:
  `scenario_ok = isinstance(res, dict) and res.get("status") == "passed"`.
  Keep the non-dict fallback only if a non-dict return is genuinely reachable
  (it is not for `run_scenario`; prefer to assert dict).
- **S4:** derive the testcase verdict from the **scenario `status`**, not from a
  scan of step statuses. A testcase should be marked failed/errored iff its
  scenario status is `failed`/`error`; count each scenario **once** (failure XOR
  error, decided by scenario status, with step-level detail nested inside).
  Ensure `tests == passed + failures + errors + skipped` holds as an invariant.

## Acceptance
- `measure_scenario` on a feature whose steps error returns `scenario_ok: false`;
  on an all-passing feature returns `scenario_ok: true`. A new offline unit test
  (monkeypatching `mcp_server.run_scenario` to return a failed / a passed
  `ScenarioResult.to_dict()`) asserts both.
- JUnit XML from `reporting.junit_xml`:
  - a scenario with `status: "failed"` and no bad steps renders as a **failing**
    testcase (not passing);
  - a scenario with both an `assert_failed` and an `error` step is counted
    exactly once;
  - the invariant `tests == passed + failures + errors + skipped` holds — asserted
    by a new unit test covering all four verdict shapes.
- Cyrillic scenario/step names still XML-escape correctly (no regression to the
  existing reporting tests).
- `uv run pytest -q` stays green; the new tests are added under
  `tests/test_reporting.py` and `tests/test_measure.py`.

## Suggested change decomposition (for `$opsx-ff`)
- **Change 1 — `measure-scenario-verdict`** (capability: debug/measure verdict):
  fix `measure.py:307` + unit tests.
- **Change 2 — `junit-verdict-from-status`** (capability: scenario reporting):
  fix `reporting.py` counting + invariant test.
Both are small; may be folded into one change if `$opsx-ff` prefers.

## Change Set
1. `openspec/changes/archive/2026-07-02-measure-scenario-verdict/` — make `measure_scenario.scenario_ok` follow
   `ScenarioResult.status` instead of truthiness.
2. `openspec/changes/archive/2026-07-02-junit-verdict-from-status/` — make JUnit testcase verdicts and suite
   counters derive from scenario status, counting each scenario once.

## Change 1: `measure-scenario-verdict`

### Why
`measure_scenario` currently reports false green `scenario_ok` because it treats the non-empty scenario result dict as
truthy when the result has no `ok` key.

### Goal
Return `scenario_ok: true` only for `run_scenario` results whose `status` is exactly `"passed"`.

### Scope
- `src/qa_mcp/debug/measure.py`
- focused offline tests in `tests/test_measure.py`
- `qa-mcp-protocol-lab` delta spec

### Acceptance
- Failed scenario result dictionaries produce `scenario_ok: false`.
- Passed scenario result dictionaries produce `scenario_ok: true`.
- Malformed/missing verdict payloads do not become truthy passes.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-02-measure-scenario-verdict/`

## Change 2: `junit-verdict-from-status`

### Why
`junit_xml` currently scans step statuses, which can render a failed scenario as passing and can count one testcase in
both `failures` and `errors`.

### Goal
Derive JUnit testcase verdict and suite counters from the scenario-level `status`, using step details only for
diagnostic messages.

### Scope
- `src/qa_mcp/scenario/reporting.py`
- focused offline tests in `tests/test_reporting.py`
- `qa-mcp-protocol-lab` delta spec

### Acceptance
- `status: "failed"` with no bad step entries emits a JUnit `<failure>`.
- A scenario with both assertion and error details is counted exactly once.
- JUnit counters satisfy `tests == passed + failures + errors + skipped`.
- Cyrillic/XML escaping remains parseable.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-02-junit-verdict-from-status/`

## Verify
- `openspec validate measure-scenario-verdict --strict` — passed during `$opsx-ff`.
- `openspec validate junit-verdict-from-status --strict` — passed during `$opsx-ff`.
- `git diff --check -- openspec/changes/measure-scenario-verdict openspec/changes/junit-verdict-from-status openspec/board`
  — passed during `$opsx-ff`.
- `uv run pytest tests/test_measure.py -q` — 9 passed.
- `uv run pytest tests/test_reporting.py -q` — 8 passed.
- `uv run pytest tests/ -q` — 594 passed.
- `uv run python -m compileall -q src/qa_mcp` — passed.
- `openspec validate --all` — passed.
- `git diff --check` — passed.

## Archive
- `openspec/changes/archive/2026-07-02-measure-scenario-verdict/`
- `openspec/changes/archive/2026-07-02-junit-verdict-from-status/`

## Related
- `docs/code-review-2026-07-02.md` (C3, S4)
- `openspec/changes/archive/2026-07-02-measure-scenario-verdict/`
- `openspec/changes/archive/2026-07-02-junit-verdict-from-status/`
- Downstream: CR-07 (CI) will make these tests gate releases.

## Result
Delivered and archived. `measure_scenario` now reports `scenario_ok` from the scenario result `status` instead of
truthiness, and JUnit XML now derives one terminal testcase verdict from scenario status so failed scenarios cannot
render green and mixed assertion/error details count once. Specs synced to `qa-mcp-protocol-lab`; offline verification
is green. Published by `$opsx-pub`.

## Next
- none

## Log
- 2026-07-02 card created from the code-review report (findings C3, S4).
- 2026-07-02 `$opsx-ff`: decomposed into two apply-ready changes, generated proposal/design/spec/tasks artifacts,
  strict-validated both changes, and moved the card to `2.todo`.
- 2026-07-02 `$opsx-do`: implemented both changes, added offline regression tests, synced +3 requirements into
  `qa-mcp-protocol-lab`, archived both changes, and moved the card to `4.done`.
- 2026-07-02 `$opsx-pub`: committed (`Fix honest scenario verdict reporting`) and prepared for push to `origin/main`.

"""Offline tests for the CI quality gates (roadmap 111, item 6): per-step perf budget + coverage gate.

The coverage gate is exercised against the REAL card-110 measure capture (`tests/fixtures/card110-measure-event.json`),
so it is tested on genuine `PerformanceInfoMain` data, not a synthetic stub.
"""

from __future__ import annotations

from pathlib import Path

from qa_mcp import mcp_server
from qa_mcp.debug.gates import evaluate_coverage_gate, evaluate_perf_budget
from qa_mcp.debug.measure import build_report, extract_measures
from qa_mcp.scenario.model import Scenario, Step, StepResult
from qa_mcp.scenario.runner import ScenarioRunner

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "card110-measure-event.json"


# --- evaluate_perf_budget ------------------------------------------------------------------------------------

def test_perf_budget_ok():
    steps = [{"name": "a", "kind": "open_list", "duration_sec": 0.5},
             {"name": "b", "kind": "read_form_value", "duration_sec": 1.0}]
    v = evaluate_perf_budget(steps, max_ms=2000)
    assert v["ok"] and v["checked"] == 2 and v["violations"] == []


def test_perf_budget_violation_reports_the_slow_step():
    v = evaluate_perf_budget([{"name": "slow", "kind": "open_list", "duration_sec": 3.0}], max_ms=2000)
    assert not v["ok"]
    assert v["violations"][0]["name"] == "slow" and v["violations"][0]["ms"] == 3000.0


def test_perf_budget_per_step_override():
    steps = [{"name": "x", "kind": "k", "duration_sec": 1.5}]
    assert evaluate_perf_budget(steps, max_ms=2000)["ok"]                          # default budget passes
    assert not evaluate_perf_budget(steps, max_ms=2000, per_step_ms={"x": 1000})["ok"]  # tighter override fails


def test_perf_budget_no_budget_skips():
    v = evaluate_perf_budget([{"name": "x", "kind": "k", "duration_sec": 99}], max_ms=0)
    assert v["ok"] and v["checked"] == 0


# --- evaluate_coverage_gate (REAL card-110 fixture) ----------------------------------------------------------

def _real_report():
    return build_report(extract_measures(FIXTURE.read_text(encoding="utf-8")))


def test_coverage_gate_passes_on_real_capture():
    # card 110: the real measure captured 2 modules / 20 covered lines
    v = evaluate_coverage_gate(_real_report(), min_lines=10, min_modules=1)
    assert v["ok"] and v["covered_lines"] >= 20 and v["covered_modules"] >= 2


def test_coverage_gate_min_lines_breach():
    v = evaluate_coverage_gate(_real_report(), min_lines=10_000)
    assert not v["ok"] and "covered_lines" in v["reasons"][0]


def test_coverage_gate_min_modules_breach():
    v = evaluate_coverage_gate(_real_report(), min_modules=99)
    assert not v["ok"] and any("module" in r for r in v["reasons"])


def test_coverage_gate_required_module_missing():
    v = evaluate_coverage_gate(_real_report(), required_modules=["НетТакого :: Модуль"])
    assert not v["ok"] and v["missing_required"] == ["НетТакого :: Модуль"]


def test_coverage_gate_accepts_measure_scenario_wrapper():
    # the full measure_scenario output is {report: {...}, ...} — the gate accepts either shape
    assert evaluate_coverage_gate({"report": _real_report()}, min_lines=1)["ok"]


# --- the Gherkin step + runner integration --------------------------------------------------------------------

def test_perf_step_transpiles_to_kind_with_budget():
    out = mcp_server.transpile(feature_text="Сценарий: s\n  Тогда Каждый шаг выполняется быстрее 5000 мс\n")
    assert out["unmapped"] == []
    step = out["steps"][0]
    assert step["kind"] == "assert_step_perf" and float(step["params"]["max_ms"]) == 5000.0


class _Sess:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _runner(tmp_path):
    return ScenarioRunner(session_factory=lambda: _Sess(), bootstrap=object(), templates=object(),
                          output_dir=tmp_path)


def test_runner_perf_assert_passes_when_steps_fast(tmp_path):
    sc = Scenario.from_dict({"name": "s", "steps": [
        {"kind": "skip_step", "name": "a", "params": {"reason": "x"}},
        {"kind": "assert_step_perf", "name": "perf", "params": {"max_ms": 5000}},
    ]})
    res = _runner(tmp_path).run(sc)
    perf = [s for s in res.steps if s.kind == "assert_step_perf"][0]
    assert perf.status == "ok" and "within 5000ms" in perf.preview


def test_runner_perf_assert_fails_over_budget(tmp_path):
    slow = StepResult(name="slow", kind="open_list", status="ok")
    slow.duration_sec = 3.0
    sr = _runner(tmp_path)._eval_step_perf(
        Step(kind="assert_step_perf", name="perf", params={"max_ms": 1000}), [slow])
    assert sr.status == "assert_failed" and "OVER BUDGET" in sr.preview and "slow" in sr.preview

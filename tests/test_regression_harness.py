"""Offline tests for the live-regression harness core (roadmap 111, item 3).

The live wiring (boot, OData, MCP tools) cannot run offline, but the orchestration core is pure and IS tested
here, and the curated checks' Gherkin features are transpile-checked so a phrasing drift fails offline (before a
slow live boot), not on the lab.
"""

from __future__ import annotations

import itertools

import pytest

from qa_mcp import mcp_server
from qa_mcp.regression import checks as live_checks
from qa_mcp.regression.harness import Check, RegressionReport, run_check, run_checks
from qa_mcp.scenario.reporting import junit_xml


# A monotonic-ish fake clock: each call advances by 1.0 so durations are deterministic.
def fake_clock():
    counter = itertools.count()
    return lambda: float(next(counter))


def ok_check(name="c", required=True):
    return Check(name, "cat", lambda ctx: (True, {"k": "v"}), required=required)


def fail_check(name="c", required=True):
    return Check(name, "cat", lambda ctx: (False, {"why": "miss"}), required=required)


def raising_check(name="c", required=True):
    def _boom(ctx):
        raise ValueError("kaboom")
    return Check(name, "cat", _boom, required=required)


def test_run_check_passing():
    r = run_check(ok_check(), ctx=None, clock=fake_clock())
    assert r.ok and r.status == "ok" and r.error is None
    assert r.detail == {"k": "v"}
    assert r.duration_sec == 1.0  # one clock tick


def test_run_check_clean_miss_is_assert_failed():
    r = run_check(fail_check(), ctx=None, clock=fake_clock())
    assert not r.ok and r.status == "assert_failed" and r.error is None


def test_run_check_raise_is_error_not_swallowed():
    r = run_check(raising_check(), ctx=None, clock=fake_clock())
    assert not r.ok and r.status == "error"
    assert "ValueError: kaboom" in r.error


def test_non_dict_detail_is_wrapped():
    r = run_check(Check("c", "cat", lambda ctx: (True, "scalar")), ctx=None, clock=fake_clock())
    assert r.detail == {"value": "scalar"}


def test_report_aggregates_and_exit_code():
    rep = run_checks([ok_check("a"), fail_check("b"), ok_check("c")], ctx=None, clock=fake_clock())
    assert rep.total == 3 and rep.passed == 2 and rep.failed == 1
    assert rep.ok is False and rep.exit_code == 1


def test_all_pass_is_green():
    rep = run_checks([ok_check("a"), ok_check("b")], ctx=None, clock=fake_clock())
    assert rep.ok is True and rep.exit_code == 0


def test_optional_failure_does_not_break_the_run():
    rep = run_checks([ok_check("a"), fail_check("opt", required=False)], ctx=None, clock=fake_clock())
    assert rep.failed == 1 and rep.ok is True and rep.exit_code == 0


def test_required_failure_breaks_even_with_optional_pass():
    rep = run_checks([fail_check("req", required=True), ok_check("opt", required=False)], ctx=None,
                     clock=fake_clock())
    assert rep.ok is False and rep.exit_code == 1


def test_run_checks_accumulates_into_existing_report():
    rep = RegressionReport()
    run_checks([ok_check("a")], ctx=None, clock=fake_clock(), into=rep)
    run_checks([fail_check("b")], ctx=None, clock=fake_clock(), into=rep)
    assert rep.total == 2 and rep.passed == 1 and rep.failed == 1


def test_to_scenario_results_feeds_junit():
    rep = run_checks([ok_check("good"), fail_check("bad"), raising_check("boom")], ctx=None, clock=fake_clock())
    xml = junit_xml(rep.to_scenario_results(), suite_name="live-regression")
    assert 'tests="3"' in xml
    assert 'failures="1"' in xml and 'errors="1"' in xml
    assert "good" in xml and "bad" in xml and "boom" in xml


def test_render_shows_verdict():
    assert "GREEN" in run_checks([ok_check()], ctx=None, clock=fake_clock()).render()
    assert "RED" in run_checks([fail_check()], ctx=None, clock=fake_clock()).render()


# --- curated check wiring (structural, no lab) ----------------------------------------------------------------

def test_core_checks_shape():
    cs = live_checks.core_checks()
    names = [c.name for c in cs]
    assert names == ["preflight.protocol_drift", "data_layer.banki",
                     "ui.assert_family", "ui.open_two_objects", "ui.read_descriptor",
                     "ui.list_grid_after_dirty"]
    # the drift preflight + data-layer check run BEFORE the boot; the rest are UI-phase
    assert cs[0].phase == "data_pre" and cs[0].required is False  # drift preflight is informational
    assert cs[1].phase == "data_pre"
    assert all(c.phase == "ui" for c in cs[2:])


def test_optin_checks_phases():
    wr = live_checks.write_roundtrip_checks()
    assert [c.phase for c in wr] == ["ui", "data_post"]
    assert live_checks.measure_checks()[0].phase == "measure"


def test_write_by_label_check_requires_tool_commit_verification(monkeypatch):
    class FakeMcp:
        def write_form_fields_by_label(self, **_kwargs):
            return {
                "foregrounded": True,
                "all_targeted": True,
                "all_committed": False,
                "readback": {"verified": True},
            }

    monkeypatch.setattr(live_checks, "_mcp", lambda: FakeMcp())

    ok, detail = live_checks._write_by_label(live_checks.LiveContext(display=":99"))

    assert ok is False
    assert detail["all_targeted"] is True
    assert detail["all_committed"] is False
    assert detail["readback_verified"] is True


@pytest.mark.parametrize("feature", [
    live_checks._ASSERT_POS_FEATURE,
    live_checks._ASSERT_NEG_FEATURE,
    live_checks._OPEN_FEATURE,
    live_checks._MEASURE_FEATURE,
])
def test_curated_features_transpile_clean(feature):
    """Every curated check's Gherkin must transpile with no unmapped steps — a phrasing drift fails HERE,
    offline, not on a slow live boot."""
    out = mcp_server.transpile(feature_text=feature)
    assert out["unmapped"] == [], f"unmapped: {out['unmapped']}"
    assert out["steps"], "no steps transpiled"

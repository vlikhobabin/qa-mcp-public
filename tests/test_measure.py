"""Card 110 (E-XV) — debug-protocol measure: parse a REAL captured PerformanceInfoMain into a coverage(107)+
perf(108) report, the module-name resolver, and the rdbg request construction. All offline (no lab)."""
from __future__ import annotations

import json
from pathlib import Path

from qa_mcp.debug.measure import (
    DebuggerSession,
    build_report,
    extract_measures,
    make_mdo_resolver,
    measure_scenario,
    render_report,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "card110-measure-event.json"


def _measures():
    return extract_measures(FIXTURE.read_text(encoding="utf-8"))


# ---- parse + report (against the REAL live-captured payload) ----
def test_extract_measures_from_real_capture():
    measures = _measures()
    assert len(measures) == 2  # two DBGUIExtCmdInfoMeasure events
    assert all("moduleData" in m for m in measures)
    # accepts a pre-parsed dict too
    assert extract_measures(json.loads(FIXTURE.read_text(encoding="utf-8"))) == measures


def test_build_report_aggregates_coverage_and_perf():
    report = build_report(_measures())
    t = report["totals"]
    assert t["measure_events"] == 2
    assert t["modules"] == 2                 # form module + object module of Документ.Заказ
    assert t["covered_lines"] == 20          # 12 (form, unioned across both events) + 8 (object module)
    by_lines = sorted(m["covered_lines"] for m in report["modules"])
    assert by_lines == [8, 12]
    # perf: line 20 of the object module took 538 µs (freq=1e6 → ticks == µs)
    obj_mod = max(report["modules"], key=lambda m: m["covered_lines"] == 8)
    line20 = next(l for m in report["modules"] for l in m["lines"] if l["line"] == 20)
    assert line20["frequency"] == 1 and line20["us"] == 538.0
    assert t["total_us"] > 0


def test_build_report_with_resolver_names_modules():
    def resolver(oid):
        return {"object": "Документ.Заказ", "module": f"mod-{oid[:4]}"}

    report = build_report(_measures(), resolver=resolver)
    assert all(m["object"] == "Документ.Заказ" for m in report["modules"])
    text = render_report(report)
    assert "Документ.Заказ" in text and "covered" in text.lower()


def test_extract_measures_empty_response():
    assert extract_measures('{"response":{"result":[]}}') == []
    assert extract_measures('{}') == []
    assert extract_measures({}) == []


# ---- module-name resolver against a synthetic .mdo tree ----
def test_make_mdo_resolver(tmp_path):
    mdo = tmp_path / "Documents" / "Заказ" / "Заказ.mdo"
    mdo.parent.mkdir(parents=True)
    mdo.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<mdclass:Document xmlns:mdclass="http://g5.1c.ru/v8/dt/metadata/mdclass" uuid="OBJ-UUID">\n'
        '    <forms uuid="FORM-UUID">\n'
        '        <name>ФормаДокумента</name>\n'
        '    </forms>\n'
        '</mdclass:Document>\n',
        encoding="utf-8",
    )
    resolve = make_mdo_resolver(tmp_path)
    assert resolve("OBJ-UUID") == {"object": "Документ.Заказ", "module": "МодульОбъекта"}
    assert resolve("FORM-UUID") == {"object": "Документ.Заказ", "module": "Форма.ФормаДокумента"}
    assert resolve("missing") == {"object": None, "module": "missing"}
    assert resolve("") == {"object": None, "module": None}


# ---- rdbg request construction (no HTTP) ----
def test_debugger_session_request_construction(monkeypatch):
    sess = DebuggerSession(dbg_url="http://127.0.0.1:1550", alias="DefAlias", ui="UI-123")
    calls = []

    def fake_post(cmd, inner="", query="", body=None, timeout=12):
        calls.append({"cmd": cmd, "inner": inner, "query": query, "body": body})
        return {"status": 200, "body": ""}

    monkeypatch.setattr(sess, "_post", fake_post)

    sess.set_measure_mode("SEANCE-1")
    assert calls[-1]["cmd"] == "setMeasureMode"
    assert "<dr:measureModeSeanceID>SEANCE-1</dr:measureModeSeanceID>" in calls[-1]["inner"]
    assert "<dr:idOfDebuggerUI>UI-123</dr:idOfDebuggerUI>" in calls[-1]["inner"]
    assert "targetID" not in calls[-1]["inner"]            # the decoded fix: no targetID field

    sess.attach_targets(["T1", "T2"])
    assert calls[-1]["cmd"] == "attachDetachDbgTargets"
    assert "<dr:attach>true</dr:attach>" in calls[-1]["inner"]
    assert "<dr:id><id>T1</id></dr:id><dr:id><id>T2</id></dr:id>" in calls[-1]["inner"]

    sess.set_auto_attach(("ManagedClient", "ServerEmulation"))
    assert "<aa:targetType>ManagedClient</aa:targetType>" in calls[-1]["inner"]

    sess.poll_events()
    assert calls[-1]["cmd"] == "pingDebugUIParams"
    assert calls[-1]["query"] == "&dbgui=UI-123"           # ui in the query param, not the body
    assert calls[-1]["body"] == b""


def test_get_targets_parses_json(monkeypatch):
    sess = DebuggerSession()
    payload = {"response": {"id": [{"id": "T1", "targetType": "ManagedClient"},
                                   {"id": "T2", "targetType": "ServerEmulation"}]}}
    monkeypatch.setattr(sess, "_post", lambda *a, **k: {"status": 200, "body": json.dumps(payload)})
    assert [t["id"] for t in sess.get_targets()] == ["T1", "T2"]


# ---- measure_scenario scenario verdict (offline, no live 1C/debugger) ----
def _measure_with_scenario_status(monkeypatch, status):
    import qa_mcp.debug.measure as measure_module
    import qa_mcp.mcp_server as mcp_server
    import qa_mcp.protocol.lifecycle as lifecycle

    class FakeTarget:
        platform_root = "/tmp"

    class FakeHandle:
        def __init__(self):
            self.stopped = False

        def stop(self):
            self.stopped = True

    class FakePopen:
        def __init__(self, *args, **kwargs):
            self.terminated = False

        def terminate(self):
            self.terminated = True

    class FakeDebuggerSession:
        def __init__(self, *args, **kwargs):
            self.measure_modes = []

        def handshake(self):
            return [{"id": "T1"}]

        def attach_targets(self, ids):
            return {"status": 200, "ids": ids}

        def set_measure_mode(self, seance):
            self.measure_modes.append(seance)
            return {"status": 200}

        def poll_events(self):
            return {"status": 204, "body": ""}

    class FakeThread:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            return None

    monkeypatch.setattr(lifecycle, "load_env_file", lambda path: {})
    monkeypatch.setattr(lifecycle.TestClientTarget, "from_env", lambda *args, **kwargs: FakeTarget())
    monkeypatch.setattr(lifecycle, "launch_test_client", lambda *args, **kwargs: FakeHandle())
    monkeypatch.setattr(measure_module.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(measure_module.subprocess, "run", lambda *args, **kwargs: None)
    monkeypatch.setattr(measure_module, "DebuggerSession", FakeDebuggerSession)
    monkeypatch.setattr(measure_module.threading, "Thread", FakeThread)
    monkeypatch.setattr(measure_module.time, "sleep", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        mcp_server,
        "run_scenario",
        lambda **kwargs: {"scenario": "offline", "status": status, "duration_sec": 0.0, "started_at": 0.0, "steps": []},
    )
    return measure_scenario("Сценарий: offline\n", result_wait_sec=0, drain_sec=0)


def test_measure_scenario_reports_failed_scenario_status(monkeypatch):
    out = _measure_with_scenario_status(monkeypatch, "failed")
    assert out["scenario_ok"] is False
    assert {"ok", "report", "report_text", "raw_event_count"}.issubset(out)


def test_measure_scenario_reports_passed_scenario_status(monkeypatch):
    out = _measure_with_scenario_status(monkeypatch, "passed")
    assert out["scenario_ok"] is True

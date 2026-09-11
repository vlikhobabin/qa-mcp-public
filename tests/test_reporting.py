"""Card 104 (E-FW) — JUnit + Allure report writers (offline)."""
from __future__ import annotations

import json
from xml.etree import ElementTree as ET

from qa_mcp.scenario import ScenarioResult, StepResult, junit_xml, write_allure_results

# A synthetic "run": one passed, one assert-failed, one errored scenario.
RUN = [
    {"scenario": "passes", "status": "passed", "duration_sec": 0.5,
     "steps": [{"name": "read", "kind": "read_form_value", "status": "ok", "duration_sec": 0.5}]},
    {"scenario": "asserts", "status": "failed", "duration_sec": 1.0,
     "steps": [{"name": "check", "kind": "read_form_value", "status": "assert_failed",
                "error": "expected 'A' got 'B'", "duration_sec": 1.0}]},
    {"scenario": "errors", "status": "failed", "duration_sec": 0.2,
     "steps": [{"name": "open", "kind": "open_main_form", "status": "error",
                "error": "ConnectionError: refused", "duration_sec": 0.2}]},
]


def test_junit_xml_structure_counts_and_messages() -> None:
    xml = junit_xml(RUN, suite_name="qa")
    root = ET.fromstring(xml)
    assert root.tag == "testsuites"
    assert root.attrib["tests"] == "3"
    assert root.attrib["failures"] == "1"
    assert root.attrib["errors"] == "1"
    assert root.attrib["skipped"] == "0"
    cases = root.findall("./testsuite/testcase")
    assert [c.attrib["name"] for c in cases] == ["passes", "asserts", "errors"]
    # passed case has no failure/error child
    assert list(cases[0]) == []
    # assert-failed -> <failure>; errored -> <error>; messages carried
    fail = cases[1].find("failure")
    assert fail is not None and "expected 'A' got 'B'" in fail.attrib["message"]
    err = cases[2].find("error")
    assert err is not None and "ConnectionError" in err.attrib["message"]


def test_junit_from_model_to_dict() -> None:
    # the model's to_dict shape feeds the writer directly (end-to-end)
    sr = ScenarioResult(
        name="from model", status="failed", duration_sec=0.3,
        steps=[StepResult(name="s", kind="click_button", status="error", error="boom", duration_sec=0.3)],
    )
    root = ET.fromstring(junit_xml([sr.to_dict()]))
    case = root.find("./testsuite/testcase")
    assert case.attrib["name"] == "from model"
    assert case.find("error").attrib["message"] == "boom"


def test_junit_failed_scenario_without_bad_steps_is_failure() -> None:
    run = [{"scenario": "empty failure", "status": "failed", "duration_sec": 0.1, "steps": []}]
    root = ET.fromstring(junit_xml(run, suite_name="qa"))
    assert root.attrib["tests"] == "1"
    assert root.attrib["failures"] == "1"
    assert root.attrib["errors"] == "0"
    failure = root.find("./testsuite/testcase/failure")
    assert failure is not None
    assert "empty failure" in failure.attrib["message"]


def test_junit_mixed_bad_steps_count_once_as_error() -> None:
    run = [{
        "scenario": "mixed",
        "status": "failed",
        "duration_sec": 0.1,
        "steps": [
            {"name": "assert", "status": "assert_failed", "error": "expected A"},
            {"name": "open", "status": "error", "error": "boom"},
        ],
    }]
    root = ET.fromstring(junit_xml(run, suite_name="qa"))
    assert root.attrib["tests"] == "1"
    assert root.attrib["failures"] == "0"
    assert root.attrib["errors"] == "1"
    case = root.find("./testsuite/testcase")
    assert len(list(case)) == 1
    err = case.find("error")
    assert err is not None
    assert "assert: assert_failed" in err.text
    assert "open: error" in err.text


def test_junit_counter_invariant() -> None:
    run = [
        {"scenario": "passes", "status": "passed", "steps": []},
        {"scenario": "fails", "status": "failed", "steps": []},
        {"scenario": "errors", "status": "failed", "steps": [{"name": "s", "status": "error"}]},
    ]
    root = ET.fromstring(junit_xml(run, suite_name="qa"))
    tests = int(root.attrib["tests"])
    failures = int(root.attrib["failures"])
    errors = int(root.attrib["errors"])
    skipped = int(root.attrib["skipped"])
    passed = sum(1 for case in root.findall("./testsuite/testcase") if not list(case))
    assert tests == passed + failures + errors + skipped


def test_junit_cyrillic_and_xml_sensitive_text_round_trip() -> None:
    run = [{
        "scenario": "Проверка <&>",
        "status": "failed",
        "steps": [{"name": "Шаг <1>", "status": "assert_failed", "error": "ожидали \"А\" & получили <Б>"}],
    }]
    root = ET.fromstring(junit_xml(run, suite_name="qa"))
    case = root.find("./testsuite/testcase")
    assert case.attrib["name"] == "Проверка <&>"
    failure = case.find("failure")
    assert failure is not None
    assert failure.attrib["message"] == "ожидали \"А\" & получили <Б>"
    assert "Шаг <1>" in failure.text


def test_allure_results_written_with_status_mapping(tmp_path) -> None:
    out = tmp_path / "allure-results"
    paths = write_allure_results(RUN, out, suite_name="qa")
    assert len(paths) == 3
    by_name = {}
    for p in out.glob("*-result.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        by_name[data["name"]] = data
    assert by_name["passes"]["status"] == "passed"
    assert by_name["asserts"]["status"] == "failed"
    assert by_name["errors"]["status"] == "broken"  # scenario-level "failed" + an errored step
    # step status mapping + statusDetails
    assert by_name["asserts"]["steps"][0]["status"] == "failed"
    assert "expected 'A' got 'B'" in by_name["asserts"]["statusDetails"]["message"]
    # deterministic uuids: a second run reuses the same filenames
    again = write_allure_results(RUN, out, suite_name="qa")
    assert {p.name for p in again} == {p.name for p in paths}


def test_allure_attachment_copied(tmp_path) -> None:
    shot = tmp_path / "shot.png"
    shot.write_bytes(b"\x89PNG\r\n\x1a\n")  # minimal PNG header
    run = [{"scenario": "with shot", "status": "failed", "duration_sec": 0.1,
            "steps": [{"name": "open", "kind": "open_main_form", "status": "error",
                       "error": "x", "attachments": [str(shot)]}]}]
    out = tmp_path / "res"
    paths = write_allure_results(run, out)
    data = json.loads(paths[0].read_text(encoding="utf-8"))
    att = data["steps"][0]["attachments"]
    assert len(att) == 1 and att[0]["type"] == "image/png" and att[0]["name"] == "shot.png"
    # the file was copied into the results dir under the referenced source name
    assert (out / att[0]["source"]).exists()

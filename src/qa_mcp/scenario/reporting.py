"""Card 104 (E-FW) — machine-readable test reports (JUnit XML + Allure results) from scenario runs.

Pure functions over the scenario report-dict shape (``ScenarioResult.to_dict()`` / the session ``_RESULTS_LOG``
entries), so they are decoupled from the runtime and fully unit-testable offline::

    {scenario: str, status: "passed"|"failed", duration_sec?: float, started_at?: float,
     steps: [{name, kind, status: "ok"|"assert_failed"|"error", error?, duration_sec?, attachments?}]}

JUnit feeds CI test-result panels; Allure results render in the Allure CLI (the format Vanessa Automation emits),
with per-step status/timing and screenshot attachments — so qa-mcp slots into an existing Vanessa CI pipeline.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

# our per-step status -> Allure status
_ALLURE_STEP_STATUS = {"ok": "passed", "assert_failed": "failed", "error": "broken"}
_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".txt": "text/plain", ".json": "application/json", ".html": "text/html"}


def _status(step: dict[str, Any]) -> str:
    return step.get("status", "ok")


def _failed_steps(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    return [s for s in scenario.get("steps", []) if _status(s) != "ok"]


def _junit_case_kind(scenario: dict[str, Any]) -> str | None:
    """Return the single JUnit terminal kind for a scenario: ``None`` (passed), ``failure`` or ``error``."""
    status = scenario.get("status", "passed")
    if status == "passed":
        return None
    step_statuses = {_status(s) for s in _failed_steps(scenario)}
    if status == "error" or "error" in step_statuses:
        return "error"
    return "failure"


def _allure_scenario_status(scenario: dict[str, Any]) -> str:
    """Derive the Allure scenario status from its steps — Allure separates ``broken`` (an error/exception) from
    ``failed`` (an assertion). An errored step wins over an assert-failed one."""
    if scenario.get("status") == "passed":
        return "passed"
    statuses = {_status(s) for s in scenario.get("steps", [])}
    if "error" in statuses:
        return "broken"
    return "failed"


def _f(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def junit_xml(results: list[dict[str, Any]], suite_name: str = "qa-mcp") -> str:
    """Render scenario reports as a JUnit XML string — one ``<testcase>`` per scenario.

    The scenario-level ``status`` is the source of truth for pass/fail. Step details only choose diagnostics and
    whether a failed scenario is better represented as a JUnit failure or error. Each testcase is counted once.
    """
    total = len(results)
    outcomes = [_junit_case_kind(r) for r in results]
    failures = sum(1 for kind in outcomes if kind == "failure")
    errors = sum(1 for kind in outcomes if kind == "error")
    skipped = 0
    time_total = sum(_f(r.get("duration_sec")) for r in results)
    attrs = {"name": suite_name, "tests": str(total), "failures": str(failures), "errors": str(errors),
             "skipped": str(skipped), "time": f"{time_total:.6f}"}
    root = ET.Element("testsuites", attrs)
    suite = ET.SubElement(root, "testsuite", attrs)
    for r, kind in zip(results, outcomes, strict=True):
        case = ET.SubElement(suite, "testcase", {
            "name": r.get("scenario") or "scenario", "classname": suite_name,
            "time": f"{_f(r.get('duration_sec')):.6f}"})
        if kind is None:
            continue
        bad = _failed_steps(r)
        first = bad[0] if bad else {}
        message = (
            first.get("error")
            or f"scenario '{r.get('scenario') or 'scenario'}' {r.get('status', 'failed')}"
        )
        detail_lines = [
            f"{s.get('name')}: {_status(s)}" + (f" — {s.get('error')}" if s.get("error") else "")
            for s in bad
        ] or [message]
        detail_type = _status(first) if first else r.get("status", "failed")
        tag = kind
        el = ET.SubElement(case, tag, {"message": message, "type": detail_type})
        el.text = "\n".join(detail_lines)
    return ET.tostring(root, encoding="unicode")


def _stable_uuid(*parts: Any) -> str:
    return hashlib.sha1("::".join(str(p) for p in parts).encode("utf-8")).hexdigest()


def write_allure_results(
    results: list[dict[str, Any]], out_dir: str | Path, suite_name: str = "qa-mcp"
) -> list[Path]:
    """Write one Allure ``<uuid>-result.json`` per scenario into ``out_dir`` (created if needed). Existing files
    in a step's ``attachments`` are copied into ``out_dir`` and referenced. Deterministic uuids (stable across
    runs for the same suite/scenario/index). Returns the written result-file paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index, r in enumerate(results):
        uuid = _stable_uuid(suite_name, r.get("scenario"), index)
        start = int(_f(r.get("started_at")) * 1000)
        dur_ms = int(_f(r.get("duration_sec")) * 1000)
        steps_json: list[dict[str, Any]] = []
        all_attachments: list[dict[str, Any]] = []
        cursor = start
        for s in r.get("steps", []):
            s_dur = int(_f(s.get("duration_sec")) * 1000)
            step_attachments: list[dict[str, Any]] = []
            for path in s.get("attachments") or []:
                src = Path(path)
                if not src.exists():
                    continue
                dest_name = f"{_stable_uuid(uuid, src.name)}-attachment{src.suffix}"
                shutil.copyfile(src, out / dest_name)
                step_attachments.append({"name": src.name, "source": dest_name,
                                         "type": _MIME.get(src.suffix.lower(), "application/octet-stream")})
            all_attachments.extend(step_attachments)
            steps_json.append({"name": s.get("name") or s.get("kind"),
                               "status": _ALLURE_STEP_STATUS.get(_status(s), "broken"),
                               "start": cursor, "stop": cursor + s_dur,
                               "attachments": step_attachments})
            cursor += s_dur
        result: dict[str, Any] = {
            "uuid": uuid,
            "name": r.get("scenario") or "scenario",
            "fullName": f"{suite_name}: {r.get('scenario')}",
            "status": _allure_scenario_status(r),
            "start": start,
            "stop": start + dur_ms,
            "steps": steps_json,
            "attachments": all_attachments,
            "labels": [{"name": "suite", "value": suite_name},
                       {"name": "framework", "value": "qa-mcp"}],
        }
        bad = _failed_steps(r)
        if bad:
            result["statusDetails"] = {
                "message": bad[0].get("error") or f"{bad[0].get('name')} {_status(bad[0])}",
                "trace": "\n".join(f"{s.get('name')}: {_status(s)}" for s in bad),
            }
        dest = out / f"{uuid}-result.json"
        dest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(dest)
    return written

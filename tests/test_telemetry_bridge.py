from __future__ import annotations

import json
from pathlib import Path

from qa_mcp import telemetry_bridge


def test_missing_trace_context_is_noop() -> None:
    calls: list[dict] = []

    result = telemetry_bridge.emit_bridge_observation(
        subject="scenario_outcome",
        status="passed",
        env={},
        appender=lambda **kwargs: calls.append(kwargs),
    )

    assert result == {"ok": True, "emitted": False, "reason": "missing_trace_context"}
    assert calls == []


def test_context_file_supplies_trace_target(tmp_path: Path) -> None:
    context = tmp_path / "trace-context.json"
    context.write_text(
        json.dumps({"status": "active", "workspace": str(tmp_path), "trace_id": "trc_1", "turn_id": "trn_1"}),
        encoding="utf-8",
    )
    calls: list[dict] = []

    result = telemetry_bridge.emit_bridge_observation(
        subject="scenario_outcome",
        status="passed",
        duration_ms=42,
        retained_evidence_path=".artifacts/qa/scenario.json",
        env={"AI1C_MCP_PROXY_TRACE_CONTEXT_FILE": str(context)},
        appender=lambda **kwargs: calls.append(kwargs) or {"event_id": "evt_1"},
    )

    assert result["ok"] is True
    assert result["emitted"] is True
    assert calls[0]["workspace_value"] == str(tmp_path)
    assert calls[0]["trace_id"] == "trc_1"
    assert calls[0]["turn_id"] == "trn_1"
    observation = calls[0]["payload"]["qa_bridge_observation"]
    assert observation["kind"] == "qa_telemetry_bridge"
    assert observation["provider_id"] == "qa-mcp"
    assert observation["subject"] == "scenario_outcome"
    assert observation["status"] == "ok"
    assert observation["duration_ms"] == 42
    assert observation["retained_evidence_path"] == ".artifacts/qa/scenario.json"


def test_observation_is_bounded_and_sanitized(tmp_path: Path) -> None:
    calls: list[dict] = []
    raw_summary = "x" * 400

    result = telemetry_bridge.emit_bridge_observation(
        subject="screenshot",
        status="failed",
        retained_evidence_path=str(tmp_path / "shot.png"),
        error_class="DisplayBackendError",
        error_summary=raw_summary,
        extra={"raw_screenshot": "not allowed", "ui_tree": {"secret": "payload"}},
        env={"AI1C_MCP_PROXY_WORKSPACE": str(tmp_path), "AI1C_MCP_PROXY_TRACE_ID": "trc_2"},
        appender=lambda **kwargs: calls.append(kwargs) or {"event_id": "evt_2"},
    )

    assert result["emitted"] is True
    observation = calls[0]["payload"]["qa_bridge_observation"]
    assert observation["status"] == "fail"
    assert observation["error_class"] == "DisplayBackendError"
    assert len(observation["error_summary"]) <= telemetry_bridge.MAX_SUMMARY_CHARS
    assert "raw_screenshot" not in observation
    assert "ui_tree" not in observation


def test_invalid_context_file_is_bounded_noop(tmp_path: Path) -> None:
    context = tmp_path / "trace-context.json"
    context.write_text("{", encoding="utf-8")

    result = telemetry_bridge.emit_bridge_observation(
        subject="scenario_outcome",
        status="passed",
        env={"AI1C_MCP_PROXY_TRACE_CONTEXT_FILE": str(context)},
        appender=lambda **kwargs: {"unexpected": kwargs},
    )

    assert result["ok"] is True
    assert result["emitted"] is False
    assert result["reason"] == "missing_trace_context"
    assert result["diagnostic"]["error_class"] == "JSONDecodeError"

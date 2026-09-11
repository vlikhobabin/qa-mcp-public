"""qa-mcp semantic telemetry bridge for suite traces."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

QA_BRIDGE_KIND = "qa_telemetry_bridge"
PROVIDER_ID = "qa-mcp"
OWNER_PATH = str(Path(__file__).resolve().parents[2])
MAX_SUMMARY_CHARS = 280
MAX_CONTEXT_FILE_BYTES = 1024 * 1024

_ALLOWED_EXTRA_FIELDS = {
    "display",
    "format_count",
    "matched_window_id",
    "scenario_count",
    "size_bytes",
    "step_count",
    "window",
    "written_formats",
}


@dataclass(frozen=True)
class TraceContext:
    workspace: str
    trace_id: str
    turn_id: str = ""


def _text(value: Any) -> str:
    return str(value or "").strip()


def _truncate(value: Any, limit: int = MAX_SUMMARY_CHARS) -> str:
    text = _text(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _event_status(status: Any) -> str:
    normalized = _text(status).lower()
    if normalized in {"ok", "passed", "pass", "success", "verified", "provided", "cleaned", "restored", "true"}:
        return "ok"
    if normalized in {"skipped", "skip", "not_applicable", "not-applicable"}:
        return "skipped"
    if normalized in {"warn", "warning", "degraded"}:
        return "warn"
    if normalized in {"fail", "failed", "failure", "error", "assert_failed", "blocked", "false"}:
        return "fail"
    return "warn" if normalized else "ok"


def _duration_ms(value: Any) -> int | None:
    if value is None:
        return None
    try:
        duration = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    return max(duration, 0)


def _read_context_file(path_value: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if not path_value:
        return {}, None
    path = Path(path_value).expanduser()
    try:
        if not path.is_file() or path.stat().st_size > MAX_CONTEXT_FILE_BYTES:
            return {}, {"path": str(path), "error_class": "ContextFileUnavailable"}
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # bounded diagnostic only; telemetry must not break tools.
        return {}, {"path": str(path), "error_class": exc.__class__.__name__}
    if not isinstance(data, dict):
        return {}, {"path": str(path), "error_class": "ContextFileNotObject"}
    if _text(data.get("status") or "active") != "active":
        return {}, None
    return data, None


def resolve_trace_context(env: Mapping[str, str] | None = None) -> tuple[TraceContext | None, dict[str, Any] | None]:
    values = os.environ if env is None else env
    workspace = _text(values.get("AI1C_MCP_PROXY_WORKSPACE"))
    trace_id = _text(values.get("AI1C_MCP_PROXY_TRACE_ID") or values.get("AI1C_TRACE_ID"))
    turn_id = _text(values.get("AI1C_MCP_PROXY_TURN_ID") or values.get("AI1C_TURN_ID"))

    context_file = _text(values.get("AI1C_MCP_PROXY_TRACE_CONTEXT_FILE"))
    file_context, diagnostic = _read_context_file(context_file)
    workspace = _text(file_context.get("workspace")) or workspace
    trace_id = _text(file_context.get("trace_id")) or trace_id
    turn_id = _text(file_context.get("turn_id")) or turn_id

    if not workspace or not trace_id:
        return None, diagnostic
    return TraceContext(workspace=workspace, trace_id=trace_id, turn_id=turn_id), diagnostic


def build_observation(
    *,
    subject: str,
    status: Any,
    duration_ms: Any = None,
    retained_evidence_path: str | None = None,
    evidence_summary: str | None = None,
    sensitivity_class: str = "internal",
    tool_name: str | None = None,
    error_class: str | None = None,
    error_summary: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    observation: dict[str, Any] = {
        "kind": QA_BRIDGE_KIND,
        "subject": _text(subject) or "qa_outcome",
        "status": _event_status(status),
        "provider_id": PROVIDER_ID,
        "tool_name": tool_name or f"qa.testclient.bridge.{_text(subject) or 'qa_outcome'}",
        "owner_path": OWNER_PATH,
        "sensitivity_class": sensitivity_class,
    }
    duration = _duration_ms(duration_ms)
    if duration is not None:
        observation["duration_ms"] = duration
    if retained_evidence_path:
        observation["retained_evidence_path"] = _truncate(retained_evidence_path, 500)
    if evidence_summary:
        observation["evidence_summary"] = _truncate(evidence_summary)
    if error_class:
        observation["error_class"] = _truncate(error_class, 120)
    if error_summary:
        observation["error_summary"] = _truncate(error_summary)
    for key, value in (extra or {}).items():
        if key not in _ALLOWED_EXTRA_FIELDS:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            observation[key] = _truncate(value, 500) if isinstance(value, str) else value
        elif isinstance(value, list) and all(isinstance(item, (str, int, float, bool)) for item in value):
            observation[key] = value[:20]
    return observation


def _agent_core_candidates(env: Mapping[str, str]) -> list[Path]:
    candidates: list[Path] = []
    configured = _text(env.get("AI1C_AGENT_CORE_HOME"))
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.append(Path(__file__).resolve().parents[3] / "agent-core")
    candidates.append(Path("/opt/ai-dev-suite-for-1c/agent-core"))
    return candidates


def _direct_appender(env: Mapping[str, str]) -> Callable[..., dict[str, Any]] | None:
    for root in _agent_core_candidates(env):
        scripts = root / "scripts"
        module = scripts / "ai_trace_store.py"
        if not module.is_file():
            continue
        scripts_text = str(scripts)
        if scripts_text not in sys.path:
            sys.path.insert(0, scripts_text)
        try:
            from ai_trace_store import append_event  # type: ignore
        except Exception:
            continue
        return append_event
    return None


def _cli_appender(env: Mapping[str, str]) -> Callable[..., dict[str, Any]] | None:
    candidates = [root / "bin" / "ai-trace" for root in _agent_core_candidates(env)]
    path_value = shutil.which("ai-trace")
    if path_value:
        candidates.append(Path(path_value))
    for exe in candidates:
        if not exe.is_file():
            continue

        def append_via_cli(**kwargs: Any) -> dict[str, Any]:
            payload = json.dumps(kwargs["payload"], ensure_ascii=False, sort_keys=True)
            cmd = [
                str(exe),
                "append",
                "--workspace", str(kwargs["workspace_value"]),
                "--trace-id", str(kwargs["trace_id"]),
                "--type", str(kwargs["event_type"]),
                "--summary", str(kwargs["summary"]),
                "--payload-json", payload,
                "--provider-id", str(kwargs["provider_id"]),
                "--tool-name", str(kwargs["tool_name"]),
                "--owner-path", str(kwargs["owner_path"]),
                "--status", str(kwargs["status"]),
                "--layer", str(kwargs["layer"]),
                "--category", str(kwargs["category"]),
                "--sensitivity-class", str(kwargs["sensitivity_class"]),
                "--owner-mode", str(kwargs["owner_mode"]),
                "--mirror-jsonl",
            ]
            if kwargs.get("turn_id"):
                cmd.extend(["--turn-id", str(kwargs["turn_id"])])
            completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
            try:
                return json.loads(completed.stdout or "{}")
            except json.JSONDecodeError:
                return {"stdout": completed.stdout}

        return append_via_cli
    return None


def _default_appender(env: Mapping[str, str]) -> Callable[..., dict[str, Any]] | None:
    return _direct_appender(env) or _cli_appender(env)


def emit_bridge_observation(
    *,
    subject: str,
    status: Any,
    duration_ms: Any = None,
    retained_evidence_path: str | None = None,
    evidence_summary: str | None = None,
    sensitivity_class: str = "internal",
    tool_name: str | None = None,
    error_class: str | None = None,
    error_summary: str | None = None,
    extra: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
    appender: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    values = os.environ if env is None else env
    context, diagnostic = resolve_trace_context(values)
    if context is None:
        result: dict[str, Any] = {"ok": True, "emitted": False, "reason": "missing_trace_context"}
        if diagnostic:
            result["diagnostic"] = diagnostic
        return result

    observation = build_observation(
        subject=subject,
        status=status,
        duration_ms=duration_ms,
        retained_evidence_path=retained_evidence_path,
        evidence_summary=evidence_summary,
        sensitivity_class=sensitivity_class,
        tool_name=tool_name,
        error_class=error_class,
        error_summary=error_summary,
        extra=extra,
    )
    event_status = _event_status(status)
    effective_tool = observation["tool_name"]
    effective_appender = appender or _default_appender(values)
    if effective_appender is None:
        return {"ok": True, "emitted": False, "reason": "trace_appender_unavailable"}
    try:
        append_result = effective_appender(
            workspace_value=context.workspace,
            trace_id=context.trace_id,
            event_type="evidence",
            summary=f"qa-mcp {observation['subject']} {observation['status']}",
            payload={"qa_bridge_observation": observation},
            turn_id=context.turn_id or None,
            provider_id=PROVIDER_ID,
            tool_name=effective_tool,
            owner_path=OWNER_PATH,
            status=event_status,
            layer="qa",
            category=QA_BRIDGE_KIND,
            sensitivity_class=observation.get("sensitivity_class") or sensitivity_class,
            owner_mode="strict",
            mirror_jsonl=True,
        )
    except Exception as exc:
        return {
            "ok": False,
            "emitted": False,
            "reason": "trace_append_failed",
            "error_class": exc.__class__.__name__,
            "error_summary": _truncate(exc),
        }
    return {"ok": True, "emitted": True, "append_result": append_result}

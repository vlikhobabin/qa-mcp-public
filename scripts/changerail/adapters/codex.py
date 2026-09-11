"""Construct the configured local Codex CLI invocation without a shell."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from scripts.changerail.contracts import DeliveryError


def session_command(
    root: Path,
    profile: Mapping[str, Any],
    *,
    model: str,
    reasoning: str,
    last_message: Path,
    prompt: str,
    resume_thread_id: str | None = None,
) -> list[str]:
    config = profile.get("adapters", {}).get("codex", {})
    launcher = config.get("launcher", "bin/codex")
    if (
        not isinstance(launcher, str)
        or not launcher
        or Path(launcher).is_absolute()
        or ".." in Path(launcher).parts
    ):
        raise DeliveryError("Codex launcher must be a project-relative path")
    command = [str(root / launcher), "exec"]
    if resume_thread_id:
        command.append("resume")
    command.extend(
        [
            "--json",
            "--dangerously-bypass-approvals-and-sandbox",
            "--model",
            model,
            "-c",
            f'model_reasoning_effort="{reasoning}"',
            "-c",
            f"tool_output_token_limit={int(profile.get('budgets', {}).get('tool_output_token_limit', 4000))}",
            "--output-last-message",
            str(last_message),
        ]
    )
    if resume_thread_id:
        command.append(resume_thread_id)
    command.append(prompt)
    return command

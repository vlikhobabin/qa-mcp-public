"""Action-step executor registry (card 74 Phase 3).

The missing bridge: maps a scenario action kind to a parametric command synthesizer in
`qa_mcp.protocol.navigation`. Action execution re-targets a CAPTURED command template
(`template_body`) with step params (row value, catalog, button, …) + live GUID rebinding +
sequence — the write-from-capture constraint. `render_action` produces the command bytes; the
live send/rebind chain reuses `qa_mcp.protocol.native_mutation.run_replay_with_renderers`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from qa_mcp.protocol.navigation import (
    render_form_command,
    render_open_card_command,
    render_open_list_command,
    render_select_row_command,
)


@dataclass(frozen=True)
class ActionSpec:
    fn: Callable[..., bytes]
    required: tuple[str, ...]
    accepted: tuple[str, ...]  # explicit allowlist (the forwarding renderers have **kw)


ACTION_REGISTRY: dict[str, ActionSpec] = {
    "open_list": ActionSpec(
        render_open_list_command, ("catalog", "main_frame_guid"),
        ("catalog", "main_frame_guid", "message_id", "sequence", "nonce"),
    ),
    "form_command": ActionSpec(
        render_form_command, (), ("guid_map", "text_params", "message_id", "sequence", "nonce"),
    ),
    "select_row": ActionSpec(
        render_select_row_command, ("old_value", "new_value"),
        ("old_value", "new_value", "guid_map", "message_id", "sequence", "nonce"),
    ),
    "open_card": ActionSpec(
        render_open_card_command, (), ("button", "guid_map", "message_id", "sequence", "nonce"),
    ),
    # click_button: press the captured button (identity command + GUID rebind); locate by marker.
    "click_button": ActionSpec(
        render_form_command, (), ("guid_map", "text_params", "message_id", "sequence", "nonce"),
    ),
    # input_text: re-target the field value (length-prefixed string) in the captured input command.
    "input_text": ActionSpec(
        render_select_row_command, ("old_value", "new_value"),
        ("old_value", "new_value", "guid_map", "message_id", "sequence", "nonce"),
    ),
    # --- Card 103 Wave 3 — new navigation/window ACTION kinds. Each replays its captured command frame
    # GUID-rebound to the live session (identity render via render_form_command). The frame is LOCATED by
    # the step marker (object name / window caption) in the action capture, and the live SecondaryFrame /
    # ManagedForm GUIDs rebind through the resolver. NOTE (live follow-up, Wave-3 boot): retargeting an
    # open-main-form to a DIFFERENT object than captured (config-agnostic) needs the variable-length
    # nav-link retarget (retarget_nav_link) confirmed against a genuine capture — identity here replays the
    # captured object/window. ---
    "open_main_form": ActionSpec(
        render_form_command, (), ("guid_map", "text_params", "message_id", "sequence", "nonce"),
    ),
    "close_window": ActionSpec(
        render_form_command, (), ("guid_map", "text_params", "message_id", "sequence", "nonce"),
    ),
    "close_all_windows": ActionSpec(
        render_form_command, (), ("guid_map", "text_params", "message_id", "sequence", "nonce"),
    ),
}


def render_action(
    kind: str,
    template_body: bytes,
    params: dict[str, Any],
    *,
    guid_map: dict[str, str] | None = None,
    sequence: int | None = None,
) -> bytes:
    """Render an action command frame by re-targeting a captured template with step params."""
    spec = ACTION_REGISTRY.get(kind)
    if spec is None:
        raise ValueError(f"Unknown action kind: {kind!r}")
    missing = [p for p in spec.required if p not in params]
    if missing:
        raise ValueError(f"action {kind!r} missing required params: {missing}")

    candidate: dict[str, Any] = dict(params)
    if guid_map is not None:
        candidate["guid_map"] = guid_map
    if sequence is not None:
        candidate.setdefault("sequence", sequence)
    kwargs = {k: v for k, v in candidate.items() if k in spec.accepted}
    return spec.fn(template_body, **kwargs)

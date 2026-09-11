"""Build action renderers for the live replay-driver (card 74 Phase 3 step 2).

Pure (no socket / no capture I/O): given the captured manager frames and a scenario's action
steps, locate each step's command-frame ordinal (by its captured marker) and build a renderer
`(captured_bytes, GuidRebinder) -> bytes` that re-targets the frame via `render_action` with the
step's params and the live GUID map. A tool feeds the result to
`qa_mcp.protocol.native_mutation.run_replay_with_renderers`.
"""

from __future__ import annotations

from typing import Any, Callable

from .actions import render_action
from .model import Step

from qa_mcp.protocol.native_mutation import substitute_guid_all_encodings


def find_ordinal(manager_chunks: list[dict[str, Any]], needle: bytes) -> int | None:
    for index, chunk in enumerate(manager_chunks):
        if needle in chunk["payload"]:
            return index
    return None


def find_marker_ordinal(manager_chunks: list[dict[str, Any]], marker: str) -> int | None:
    """Locate a command frame by a text marker, trying both wire encodings: navigation/row
    commands carry UTF-16LE strings; field text-input commands carry UTF-8."""
    for encoding in ("utf-16le", "utf-8"):
        ordinal = find_ordinal(manager_chunks, marker.encode(encoding))
        if ordinal is not None:
            return ordinal
    return None


def _make_renderer(kind: str, params: dict[str, Any]) -> Callable[[bytes, Any], bytes]:
    # factory binds kind/params per step (avoids the late-binding closure-in-loop bug)
    def renderer(captured: bytes, rebinder: Any) -> bytes:
        return render_action(kind, captured, params, guid_map=getattr(rebinder, "guid_map", None))

    return renderer


def build_action_renderers(
    manager_chunks: list[dict[str, Any]], action_steps: list[Step]
) -> tuple[dict[int, Callable[[bytes, Any], bytes]], list[dict[str, Any]]]:
    """Map each action step to a renderer at its located ordinal.

    Returns (renderers, plan) where plan records, per step, the located ordinal (or None if the
    marker was not found in the captured manager stream)."""
    renderers: dict[int, Callable[[bytes, Any], bytes]] = {}
    plan: list[dict[str, Any]] = []
    for step in action_steps:
        if not step.is_action:
            raise ValueError(f"step {step.name!r} kind {step.kind!r} is not an action step")
        if not step.marker:
            raise ValueError(f"action step {step.name!r} requires a 'marker' (captured value to locate its frame)")
        ordinal = find_marker_ordinal(manager_chunks, step.marker)
        if ordinal is not None:
            renderers[ordinal] = _make_renderer(step.kind, step.params)
        plan.append({"name": step.name, "kind": step.kind, "marker": step.marker, "ordinal": ordinal})
    return renderers, plan


class _SingleSessionActionRebinder:
    """Card 78 Phase A/C: rebind a captured action command frame for execution in a LIVE synthesized
    session via SessionHandle.run_action. ``apply`` (1) re-targets the frame for the step
    (``render_action`` — e.g. retarget the input value) and (2) substitutes the captured session's
    managed-form GUID with the live session's, so the command addresses the live open form."""

    def __init__(
        self,
        kind: str,
        params: dict[str, Any],
        captured_mfg: str | None,
        live_mfg: str | None,
        captured_sfg: str | None = None,
        live_sfg: str | None = None,
    ) -> None:
        self.kind = kind
        self.params = params
        self.captured_mfg = captured_mfg
        self.live_mfg = live_mfg
        self.captured_sfg = captured_sfg
        self.live_sfg = live_sfg

    def apply(self, payload: bytes) -> bytes:
        out = render_action(self.kind, payload, self.params, guid_map=None)
        if self.captured_mfg and self.live_mfg and self.captured_mfg != self.live_mfg:
            out = substitute_guid_all_encodings(out, self.captured_mfg, self.live_mfg)
        # The fixture form is a SecondaryFrame whose GUID is session-specific; rebind it too so the
        # action addresses the live open form (not just its ManagedForm child).
        if self.captured_sfg and self.live_sfg and self.captured_sfg != self.live_sfg:
            out = substitute_guid_all_encodings(out, self.captured_sfg, self.live_sfg)
        return out


def build_single_session_action_resolver(
    manager_chunks: list[dict[str, Any]],
    captured_managed_form_guid: str | None,
    captured_input_value: str | None = None,
    marker_ordinals: dict[str, int] | None = None,
    captured_secondary_frame_guid: str | None = None,
) -> Callable[[Step, Any], tuple[bytes, "_SingleSessionActionRebinder"]]:
    """Build an `action_resolver(step, handle)` for `ScenarioRunner.run_single_session`: locate the
    step's captured command frame (by marker) in `manager_chunks` and return it with a rebinder that
    re-targets it + maps the captured managed-form GUID to the live session's (read from the handle
    after bootstrap). `captured_managed_form_guid` is extracted by the caller from the capture's client
    responses (`extract_managed_form_guid`).

    `captured_input_value` makes `.feature`-driven input steps correct: the Gherkin transpiler can only
    set `old_value` to the field name (it can't know the value baked into the capture), so an
    `input_text` retarget would corrupt the frame. When `captured_input_value` is given, input_text
    steps retarget the CAPTURED value → the step's requested `new_value` (identity when they match).

    `marker_ordinals` (step.marker → explicit manager-frame ordinal) pins the command frame when the
    marker is not unique (e.g. a button name appears in both the form description and the click command,
    so first-match find_marker_ordinal is ambiguous). When absent, falls back to find_marker_ordinal."""

    def _effective_params(step: Step) -> dict[str, Any]:
        if step.kind == "input_text" and captured_input_value is not None:
            new_value = step.params.get("new_value", captured_input_value)
            return {"old_value": captured_input_value, "new_value": new_value}
        return step.params

    def resolver(step: Step, handle: Any) -> tuple[bytes, "_SingleSessionActionRebinder"]:
        if marker_ordinals and step.marker in marker_ordinals:
            ordinal: int | None = marker_ordinals[step.marker]
        else:
            ordinal = find_marker_ordinal(manager_chunks, step.marker or "")
        if ordinal is None:
            raise ValueError(f"action step {step.name!r}: marker {step.marker!r} not found in capture")
        payload = manager_chunks[ordinal]["payload"]
        state = getattr(handle, "state", None)
        live_mfg = getattr(state, "managed_form_guid", None)
        live_sfg = getattr(state, "secondary_frame_guid", None)
        return payload, _SingleSessionActionRebinder(
            step.kind,
            _effective_params(step),
            captured_managed_form_guid,
            live_mfg,
            captured_secondary_frame_guid,
            live_sfg,
        )

    return resolver

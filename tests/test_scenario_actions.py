"""Card 74 Phase 3: action-step executor registry (offline)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.scenario import ACTION_REGISTRY, Step, render_action  # noqa: E402
from qa_mcp.scenario.replay import build_action_renderers, find_ordinal  # noqa: E402


class _Rebinder:
    guid_map: dict[str, str] = {}


def _row_template(value: str = "Средний") -> bytes:
    # a frame carrying a 1-byte-count-prefixed UTF-16LE row value (as the synthesizers expect)
    return b"\x00" * 64 + bytes([len(value)]) + value.encode("utf-16le") + b"\xfd\x0d\x0a"


def test_registry_covers_the_action_kinds() -> None:
    assert set(ACTION_REGISTRY) == {
        "open_list", "form_command", "select_row", "open_card", "click_button", "input_text",
        # card 103 Wave 3 — navigation/window kinds (replay captured frame, GUID-rebound)
        "open_main_form", "close_window", "close_all_windows",
    }


def test_new_nav_window_kinds_render_identity_and_rebind() -> None:
    # Card 103 Wave 3: open_main_form / close_window / close_all_windows replay the captured command frame
    # (identity render) with the live SecondaryFrame/ManagedForm GUIDs rebound via guid_map.
    cap = "11112222-3333-4444-5555-666677778888"
    live = "aaaabbbb-cccc-dddd-eeee-ffff00001111"
    frame = b"head" + cap.encode("utf-16le") + b"tail"
    for kind in ("open_main_form", "close_window", "close_all_windows"):
        assert render_action(kind, frame, {}) == frame  # identity with no GUID map
        out = render_action(kind, frame, {}, guid_map={cap: live})
        assert cap.encode("utf-16le") not in out
        assert live.encode("utf-16le") in out


def test_click_button_identity_rebind() -> None:
    body = b"head" + "PF_RESET_STATE".encode("utf-16le") + b"tail"
    # click_button presses the captured button (identity command + GUID rebind)
    assert render_action("click_button", body, {}) == body


def test_input_text_retargets_field_value() -> None:
    body = b"\x00" * 8 + bytes([len("старое")]) + "старое".encode("utf-16le") + b"\xfd\x0d\x0a"
    out = render_action("input_text", body, {"old_value": "старое", "new_value": "новое"})
    assert "новое".encode("utf-16le") in out
    assert "старое".encode("utf-16le") not in out


def test_select_row_retargets_value() -> None:
    body = _row_template("Средний")
    out = render_action("select_row", body, {"old_value": "Средний", "new_value": "Малый"})
    assert "Малый".encode("utf-16le") in out
    assert "Средний".encode("utf-16le") not in out
    assert bytes([len("Малый")]) + "Малый".encode("utf-16le") in out  # count prefix updated


def test_open_card_identity_for_default_button() -> None:
    body = b"head" + "Изменить".encode("utf-16le") + b"tail"
    assert render_action("open_card", body, {}) == body


def test_missing_required_param_raises() -> None:
    with pytest.raises(ValueError, match="missing required params"):
        render_action("select_row", _row_template(), {"old_value": "Средний"})


def test_unexpected_param_is_filtered_not_forwarded() -> None:
    # open_card forwards **kw to render_form_command; an unknown param must be dropped, not raise
    body = b"head" + "Изменить".encode("utf-16le") + b"tail"
    out = render_action("open_card", body, {"old_value": "x", "new_value": "y"})
    assert out == body


def test_unknown_kind_raises() -> None:
    with pytest.raises(ValueError, match="Unknown action kind"):
        render_action("teleport", b"", {})


def test_action_step_model_validates() -> None:
    step = Step(kind="select_row", name="pick", params={"old_value": "A", "new_value": "B"})
    assert step.is_action
    assert step.params["new_value"] == "B"


def test_build_action_renderers_locates_ordinals_and_retargets() -> None:
    # synthetic manager stream: frame 0 = open-list, frame 1 = select-row (row value), frame 2 = other
    open_list = b"\x00" + "e1cib/list/Справочник.Склады".encode("utf-16le")
    select_row = b"\x00" * 16 + bytes([len("Средний")]) + "Средний".encode("utf-16le") + b"\xfd\x0d\x0a"
    manager_chunks = [{"payload": open_list}, {"payload": select_row}, {"payload": b"poll"}]
    steps = [
        Step(kind="form_command", name="open", marker="e1cib/list/"),
        Step(kind="select_row", name="pick", marker="Средний", params={"old_value": "Средний", "new_value": "Малый"}),
    ]
    renderers, plan = build_action_renderers(manager_chunks, steps)
    assert plan[0]["ordinal"] == 0 and plan[1]["ordinal"] == 1
    assert set(renderers) == {0, 1}
    # the select_row renderer re-targets the captured row value live
    out = renderers[1](select_row, _Rebinder())
    assert "Малый".encode("utf-16le") in out
    assert "Средний".encode("utf-16le") not in out


def test_build_action_renderers_reports_missing_marker() -> None:
    steps = [Step(kind="form_command", name="x", marker="NOT_PRESENT")]
    renderers, plan = build_action_renderers([{"payload": b"abc"}], steps)
    assert renderers == {}
    assert plan[0]["ordinal"] is None


def test_find_ordinal_basic() -> None:
    chunks = [{"payload": b"aaa"}, {"payload": "Средний".encode("utf-16le")}]
    assert find_ordinal(chunks, "Средний".encode("utf-16le")) == 1
    assert find_ordinal(chunks, "Нет".encode("utf-16le")) is None


class _FakeState:
    def __init__(self, mfg: str) -> None:
        self.managed_form_guid = mfg


class _FakeHandle:
    def __init__(self, mfg: str) -> None:
        self.state = _FakeState(mfg)


def test_single_session_action_resolver_locates_and_rebinds_mfg() -> None:
    from qa_mcp.scenario.replay import build_single_session_action_resolver

    cap_mfg = "4451d8b2-ff0f-4e70-b96a-bde7ac7ee9d4"
    live_mfg = "aaaa1111-2222-3333-4444-555566667777"
    # a click command frame carrying the captured managed-form GUID (UTF-16LE) + the button marker
    frame = b"head" + "PF_SHOW".encode("utf-16le") + cap_mfg.encode("utf-16le") + b"tail"
    manager_chunks = [{"payload": b"x"}, {"payload": frame}]
    steps = [Step(kind="click_button", name="press", marker="PF_SHOW")]
    resolver = build_single_session_action_resolver(manager_chunks, cap_mfg)

    payload, rebinder = resolver(steps[0], _FakeHandle(live_mfg))
    assert payload == frame
    out = rebinder.apply(payload)
    assert cap_mfg.encode("utf-16le") not in out  # captured mfg replaced
    assert live_mfg.encode("utf-16le") in out  # with the live one


def test_single_session_resolver_input_uses_captured_value_not_field_name() -> None:
    # Card 78: the Gherkin transpiler sets input_text old_value=field name (it can't know the captured
    # value). With captured_input_value, the resolver retargets the CAPTURED value instead (identity here).
    from qa_mcp.scenario.replay import build_single_session_action_resolver

    captured_value = "PF_INPUT_PROOF"
    field = "PF_EDIT_STRING"
    # captured input frame carries the captured value (UTF-16LE, length-prefixed, as render_select_row expects)
    frame = b"\x00" * 8 + bytes([len(captured_value)]) + captured_value.encode("utf-16le") + b"\xfd\x0d\x0a"
    # locate by the field marker (UTF-8, as Gherkin provides)
    locate = field.encode("utf-8")
    manager_chunks = [{"payload": b"x"}, {"payload": locate + b"|" + frame}]
    step = Step(kind="input_text", name="type", marker=field, params={"old_value": field, "new_value": captured_value})
    resolver = build_single_session_action_resolver(manager_chunks, None, captured_input_value=captured_value)

    _, rebinder = resolver(step, _FakeHandle("live"))
    # effective params retarget captured_value -> captured_value (identity): the field name is NOT touched
    assert rebinder.params == {"old_value": captured_value, "new_value": captured_value}
    out = rebinder.apply(manager_chunks[1]["payload"])
    assert field.encode("utf-8") in out  # field reference preserved (not corrupted)


def test_single_session_resolver_explicit_ordinal_overrides_first_match() -> None:
    # When a marker repeats (button name in form-desc AND the click command), an explicit ordinal pins
    # the right frame instead of find_marker_ordinal's first match.
    from qa_mcp.scenario.replay import build_single_session_action_resolver

    btn = "PF_SHOW_CHOICE_MENU".encode("utf-8")
    chunks = [{"payload": b"desc" + btn}, {"payload": b"poll"}, {"payload": b"cmd" + btn}]
    step = Step(kind="click_button", name="press", marker="PF_SHOW_CHOICE_MENU")
    resolver = build_single_session_action_resolver(chunks, None, marker_ordinals={"PF_SHOW_CHOICE_MENU": 2})
    payload, _ = resolver(step, _FakeHandle("live"))
    assert payload == chunks[2]["payload"]  # the explicit ordinal 2 (command), not first match (0)


def test_single_session_action_resolver_missing_marker_raises() -> None:
    from qa_mcp.scenario.replay import build_single_session_action_resolver

    resolver = build_single_session_action_resolver([{"payload": b"abc"}], "cap-mfg")
    with pytest.raises(ValueError, match="not found in capture"):
        resolver(Step(kind="click_button", name="c", marker="ABSENT"), _FakeHandle("live"))


def test_find_marker_ordinal_tries_both_encodings() -> None:
    from qa_mcp.scenario.replay import find_marker_ordinal

    utf16 = {"payload": "Средний".encode("utf-16le")}
    utf8 = {"payload": "PF_INPUT_PROOF".encode("utf-8")}
    chunks = [{"payload": b"x"}, utf16, utf8]
    assert find_marker_ordinal(chunks, "Средний") == 1  # navigation: utf-16le
    assert find_marker_ordinal(chunks, "PF_INPUT_PROOF") == 2  # field input: utf-8
    assert find_marker_ordinal(chunks, "absent") is None

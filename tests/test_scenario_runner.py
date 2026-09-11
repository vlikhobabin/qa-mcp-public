"""Card 74 Phase 1: native scenario runner spine (offline, fake session)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.scenario import Scenario, ScenarioRunner, Step  # noqa: E402


class _Ctx:
    def __init__(self, data: dict) -> None:
        self._data = data

    def to_result(self) -> dict:
        return self._data


class FakeSession:
    """Stand-in TestClientSession that returns canned read contexts."""

    def __init__(self, *, active_window=None, form_summary=None, element=None) -> None:
        self._aw = active_window or {"active_window_ref": ".HomePage[abc]"}
        self._fs = form_summary or {"elements": ["PF_FIELD_VERSION", "PF_TABLE_ITEMS"]}
        self._el = element or {"marker": "PF_FIELD_VERSION", "data": "protocol-fixture.v1"}

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def get_active_window_context(self, **_kw) -> _Ctx:
        return _Ctx(self._aw)

    def get_form_summary(self, **_kw) -> _Ctx:
        return _Ctx(self._fs)

    def get_form_element_details(self, **_kw) -> _Ctx:
        return _Ctx(self._el)


def _runner(tmp_path, **session_kw) -> ScenarioRunner:
    return ScenarioRunner(
        session_factory=lambda: FakeSession(**session_kw),
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
        synthesized=object(),
    )


def test_read_only_scenario_passes(tmp_path) -> None:
    scenario = Scenario(
        name="readonly-smoke",
        steps=[
            Step(kind="read_active_window", name="window", expect_contains="HomePage"),
            Step(kind="read_form_summary", name="form", expect_contains="PF_TABLE_ITEMS"),
            Step(kind="read_element", name="version", marker="PF_FIELD_VERSION", expect_contains="protocol-fixture.v1"),
        ],
    )
    result = _runner(tmp_path).run(scenario)
    assert result.passed
    assert [s.status for s in result.steps] == ["ok", "ok", "ok"]
    assert all(s.assertion for s in result.steps)


def test_failed_assertion_marks_scenario_failed(tmp_path) -> None:
    scenario = Scenario(
        name="bad-assert",
        steps=[Step(kind="read_active_window", name="window", expect_contains="NOT_THERE")],
    )
    result = _runner(tmp_path).run(scenario)
    assert not result.passed
    assert result.steps[0].status == "assert_failed"
    assert result.steps[0].assertion is False


def test_step_error_is_captured_not_raised(tmp_path) -> None:
    class Boom(FakeSession):
        def get_active_window_context(self, **_kw):
            raise RuntimeError("connection refused")

    runner = ScenarioRunner(
        session_factory=lambda: Boom(),
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
    )
    result = runner.run(Scenario(name="err", steps=[Step(kind="read_active_window", name="w")]))
    assert not result.passed
    assert result.steps[0].status == "error"
    assert "connection refused" in result.steps[0].error


class FakeHandle:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def active_window(self) -> _Ctx:
        self.calls.append("active_window")
        return _Ctx({"active_window_ref": ".HomePage[abc]"})

    def form_summary(self) -> _Ctx:
        self.calls.append("form_summary")
        return _Ctx({"elements": ["PF_TABLE_ITEMS"]})

    def read_form_value(self, *, field="PF_EDIT_STRING"):
        self.calls.append(f"read_form_value:{field}")
        return _Ctx({"field": field, "value": "PF_EDIT_STRING_VALUE", "value_mode_on": True})

    def run_action(self, command_payload, *, query_id="action", rebinder=None):
        self.calls.append(f"run_action:{query_id}")
        payload = rebinder.apply(command_payload) if rebinder is not None else command_payload
        return {"query_id": query_id, "sent_bytes": len(payload), "recv_bytes": 4, "accepted": True}


class FakeBootstrapSession(FakeSession):
    def __init__(self) -> None:
        super().__init__()
        self.handle = FakeHandle()

    def open_and_bootstrap(self, **_kw) -> FakeHandle:
        return self.handle


def test_single_session_runs_one_bootstrap_then_steps(tmp_path) -> None:
    session = FakeBootstrapSession()
    runner = ScenarioRunner(
        session_factory=lambda: session,
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
        synthesized=object(),
    )
    scenario = Scenario(
        name="single",
        steps=[
            Step(kind="read_active_window", name="w", expect_contains="HomePage"),
            Step(kind="read_form_summary", name="f", expect_contains="PF_TABLE_ITEMS"),
        ],
    )
    result = runner.run_single_session(scenario)
    assert result.passed
    # one bootstrap, then both ops on the same handle (no re-bootstrap)
    assert session.handle.calls == ["active_window", "form_summary"]


def test_single_session_dispatches_action_step_to_run_action(tmp_path) -> None:
    # Card 78 Phase B: a mixed read+action scenario runs both on one bootstrapped handle.
    session = FakeBootstrapSession()
    resolved: list[str] = []

    def resolver(step, handle):
        resolved.append(step.name)
        assert handle is session.handle  # resolver gets the live handle (to read session GUIDs)
        return b"CMD-" + step.name.encode(), None

    runner = ScenarioRunner(
        session_factory=lambda: session,
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
        synthesized=object(),
        action_resolver=resolver,
    )
    scenario = Scenario(
        name="mixed",
        steps=[
            Step(kind="read_active_window", name="w"),
            Step(kind="input_text", name="type", params={"old_value": "a", "new_value": "b"}),
        ],
    )
    result = runner.run_single_session(scenario)
    assert result.passed, result.to_dict()
    assert session.handle.calls == ["active_window", "run_action:type"]
    assert resolved == ["type"]


def test_single_session_dispatches_open_step_to_navigate_resolver(tmp_path) -> None:
    # Card 103 Wave 3 (live leg): open_main_form / open_list route to the navigate_resolver (live nav-link open),
    # NOT to the captured-frame action path. The step passes when the form actually opened.
    session = FakeBootstrapSession()
    seen: list[tuple[str, str]] = []

    def navigate(step, handle):
        assert handle is session.handle  # the resolver opens on the live bootstrapped handle
        seen.append((step.kind, step.marker or step.params.get("catalog", "")))
        return {"opened": True, "nav_link": "e1cib/list/Справочник.Валюты", "caption": "Валюты",
                "secondary_frame": "S", "managed_form": "F"}

    runner = ScenarioRunner(
        session_factory=lambda: session, bootstrap=object(), templates=object(),
        output_dir=tmp_path, synthesized=object(), navigate_resolver=navigate,
    )
    scenario = Scenario(name="open", steps=[
        Step(kind="open_main_form", name="open Валюты", marker="Валюты", params={"object_type": "справочника"}),
    ])
    result = runner.run_single_session(scenario)
    assert result.passed, result.to_dict()
    assert seen == [("open_main_form", "Валюты")]
    assert result.steps[0].assertion is True
    assert "Валюты" in result.steps[0].preview
    # the open went through navigate_resolver, NOT run_action (no captured-frame replay)
    assert session.handle.calls == []


def test_navigate_resolver_failure_marks_step_error(tmp_path) -> None:
    session = FakeBootstrapSession()
    runner = ScenarioRunner(
        session_factory=lambda: session, bootstrap=object(), templates=object(),
        output_dir=tmp_path, synthesized=object(),
        navigate_resolver=lambda step, handle: {"opened": False, "nav_link": "e1cib/list/Справочник.Нет"},
    )
    scenario = Scenario(name="open-fail", steps=[
        Step(kind="open_list", name="open X", marker="e1cib/list/", params={"catalog": "Нет"}),
    ])
    result = runner.run_single_session(scenario)
    assert not result.passed
    assert result.steps[0].status == "error"
    assert "did not open" in (result.steps[0].error or "")


def test_open_step_without_navigate_resolver_falls_through_to_action(tmp_path) -> None:
    # Backward-compat: with no navigate_resolver, open_main_form still routes to the action_resolver path
    # (offline single-frame replay) exactly as before — the live bridge is purely additive.
    session = FakeBootstrapSession()
    runner = ScenarioRunner(
        session_factory=lambda: session, bootstrap=object(), templates=object(),
        output_dir=tmp_path, synthesized=object(), action_resolver=lambda step, handle: (b"CMD", None),
    )
    scenario = Scenario(name="open-action", steps=[
        Step(kind="open_main_form", name="open Валюты", marker="Валюты", params={"object_type": "справочника"}),
    ])
    result = runner.run_single_session(scenario)
    assert result.passed, result.to_dict()
    assert session.handle.calls == ["run_action:open Валюты"]


def test_single_session_dispatches_read_form_value(tmp_path) -> None:
    # Card 79 (Fork 1): read_form_value opens the form + reads the field's LIVE value, asserting
    # the EFFECT (value present), not just acceptance.
    session = FakeBootstrapSession()
    runner = ScenarioRunner(
        session_factory=lambda: session,
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
        synthesized=object(),
    )
    scenario = Scenario(
        name="effect-read",
        steps=[
            Step(kind="read_form_summary", name="open"),
            Step(kind="read_form_value", name="value", marker="PF_EDIT_STRING",
                 expect_contains="PF_EDIT_STRING_VALUE"),
        ],
    )
    result = runner.run_single_session(scenario)
    assert result.passed, result.to_dict()
    assert session.handle.calls == ["form_summary", "read_form_value:PF_EDIT_STRING"]
    assert result.steps[1].assertion is True


def test_single_session_action_without_resolver_errors(tmp_path) -> None:
    runner = ScenarioRunner(
        session_factory=lambda: FakeBootstrapSession(),
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
    )
    result = runner.run_single_session(
        Scenario(name="x", steps=[Step(kind="click_button", name="c", marker="B")])
    )
    assert not result.passed
    assert "action_resolver" in result.steps[0].error


def test_single_session_action_rejected_is_error(tmp_path) -> None:
    class RejectHandle(FakeHandle):
        def run_action(self, command_payload, *, query_id="action", rebinder=None):
            self.calls.append("run_action")
            return {"query_id": query_id, "accepted": False, "recv_bytes": 0}

    class RejectSession(FakeBootstrapSession):
        def __init__(self) -> None:
            super().__init__()
            self.handle = RejectHandle()

    runner = ScenarioRunner(
        session_factory=lambda: RejectSession(),
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
        action_resolver=lambda step, handle: (b"CMD", None),
    )
    result = runner.run_single_session(
        Scenario(name="x", steps=[Step(kind="click_button", name="c", marker="B")])
    )
    assert not result.passed
    assert "rejected" in result.steps[0].error


def test_single_session_rejects_unsupported_kind(tmp_path) -> None:
    runner = ScenarioRunner(
        session_factory=lambda: FakeBootstrapSession(),
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
    )
    result = runner.run_single_session(
        Scenario(name="x", steps=[Step(kind="read_element", name="e", marker="PF_X")])
    )
    assert not result.passed
    assert result.steps[0].status == "error"


class FakeWriteSession:
    """Stand-in NativeWriteSession: records writes, echoes the value back as committed (unless the value
    starts with 'NOCOMMIT'), so the routing logic can be tested offline."""

    instances: list["FakeWriteSession"] = []

    def __init__(self, template, *, host, port, **_kw) -> None:
        self.template = template
        self.host = host
        self.port = port
        self.writes: list[str] = []
        self.fields: list[str | None] = []
        self.switches: list[str] = []
        FakeWriteSession.instances.append(self)

    def __enter__(self) -> "FakeWriteSession":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def write(self, value: str, field: str | None = None) -> dict:
        self.writes.append(value)
        self.fields.append(field)
        if field == "DATE_FIELD":
            return {"requested_value": value, "readback_value": f"{value} 0:00:00",
                    "committed": False, "field": field}
        committed = not value.startswith("NOCOMMIT")
        return {"requested_value": value, "readback_value": value if committed else None,
                "committed": committed, "field": field}

    def switch_page(self, target_page: str, base_page: str = "PF_PAGE_B") -> dict:
        self.switches.append(target_page)
        return {"base_page": base_page, "target_page": target_page, "accepted": True}


def _patch_write_path(monkeypatch):
    """Patch the lazy imports inside run_write_scenario so no live TestClient / capture is needed."""
    FakeWriteSession.instances = []
    import qa_mcp.protocol.bootstrap as bootstrap_mod
    import qa_mcp.protocol.native_write as nw_mod

    monkeypatch.setattr(bootstrap_mod, "resolve_capture_dir", lambda *a, **k: Path("/fake/capture"))
    monkeypatch.setattr(nw_mod, "derive_write_template", lambda *a, **k: ("TEMPLATE", a, k))
    monkeypatch.setattr(nw_mod, "NativeWriteSession", FakeWriteSession)


def test_write_scenario_routes_input_text_to_native_write(monkeypatch) -> None:
    # Card 83 step 2: each input_text step is routed through NativeWriteSession.write(new_value) and commits.
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    scenario = Scenario(
        name="write-two",
        steps=[
            Step(kind="input_text", name="t1", marker="PF_EDIT_STRING", params={"new_value": "HELLO"}),
            Step(kind="input_text", name="t2", marker="PF_EDIT_STRING", params={"new_value": "WORLD"}),
        ],
    )
    result = run_write_scenario(scenario, port=15381)
    assert result.passed, result.to_dict()
    # opened the session ONCE (multi-write fix) and wrote both values in order
    assert len(FakeWriteSession.instances) == 1
    assert FakeWriteSession.instances[0].writes == ["HELLO", "WORLD"]
    assert [s.status for s in result.steps] == ["ok", "ok"]


def test_write_scenario_routes_each_step_to_its_marker_field(monkeypatch) -> None:
    # Card 86b: input_text steps may target DIFFERENT fields (step.marker) on ONE session, capture-free.
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    scenario = Scenario(
        name="multi-field",
        steps=[
            Step(kind="input_text", name="a", marker="PF_EDIT_STRING", params={"new_value": "AAA"}),
            Step(kind="input_text", name="b", marker="PF_EDIT_NUMBER", params={"new_value": "42"}),
            Step(kind="input_text", name="c", marker="PF_PAGE_A_FIELD", params={"new_value": "ZZZ"}),
        ],
    )
    result = run_write_scenario(scenario, base_field="PF_EDIT_STRING")
    assert result.passed, result.to_dict()
    assert len(FakeWriteSession.instances) == 1  # one session for all fields
    assert FakeWriteSession.instances[0].fields == ["PF_EDIT_STRING", "PF_EDIT_NUMBER", "PF_PAGE_A_FIELD"]
    assert FakeWriteSession.instances[0].writes == ["AAA", "42", "ZZZ"]


def test_write_scenario_routes_switch_page(monkeypatch) -> None:
    # Card 86d: a switch_page step is routed through NativeWriteSession.switch_page on the same session.
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    scenario = Scenario(
        name="nav",
        steps=[
            Step(kind="input_text", name="t", marker="PF_EDIT_STRING", params={"new_value": "X"}),
            Step(kind="switch_page", name="to B", marker="PF_PAGE_B"),
            Step(kind="switch_page", name="to A", marker="PF_PAGE_A"),
        ],
    )
    result = run_write_scenario(scenario)
    assert result.passed, result.to_dict()
    assert FakeWriteSession.instances[0].switches == ["PF_PAGE_B", "PF_PAGE_A"]
    assert [s.status for s in result.steps] == ["ok", "ok", "ok"]


def test_write_scenario_assertion_on_readback(monkeypatch) -> None:
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    scenario = Scenario(
        name="write-assert",
        steps=[Step(kind="input_text", name="t", marker="PF_EDIT_STRING",
                    params={"new_value": "ABC123"}, expect_contains="ABC123")],
    )
    result = run_write_scenario(scenario)
    assert result.passed, result.to_dict()
    assert result.steps[0].assertion is True


def test_write_scenario_uncommitted_value_is_error(monkeypatch) -> None:
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    scenario = Scenario(
        name="write-fail",
        steps=[Step(kind="input_text", name="t", marker="PF_EDIT_STRING", params={"new_value": "NOCOMMIT_X"})],
    )
    result = run_write_scenario(scenario)
    assert not result.passed
    assert result.steps[0].status == "error"
    assert "did not commit" in result.steps[0].error


def test_write_scenario_non_write_step_unsupported(monkeypatch) -> None:
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    scenario = Scenario(
        name="mixed",
        steps=[
            Step(kind="input_text", name="t", marker="PF_EDIT_STRING", params={"new_value": "OK"}),
            Step(kind="read_form_summary", name="r"),
        ],
    )
    result = run_write_scenario(scenario)
    assert not result.passed
    assert result.steps[0].status == "ok"
    assert result.steps[1].status == "error"
    assert "not supported in write mode" in result.steps[1].error


def test_write_scenario_command_uses_executor(monkeypatch) -> None:
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    commands: list[str] = []

    def command_executor(step, session):
        commands.append(step.marker)
        return {"accepted": True, "command": step.marker}

    scenario = Scenario(
        name="save",
        steps=[
            Step(kind="input_text", name="t", marker="PF_EDIT_STRING", params={"new_value": "OK"}),
            Step(kind="click_button", name="save", marker="Записать"),
        ],
    )
    result = run_write_scenario(scenario, command_executor=command_executor)

    assert result.passed, result.to_dict()
    assert commands == ["Записать"]
    assert [s.status for s in result.steps] == ["ok", "ok"]


def test_write_scenario_command_fails_closed_without_executor(monkeypatch) -> None:
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    scenario = Scenario(name="save", steps=[Step(kind="click_button", name="save", marker="Записать")])
    result = run_write_scenario(scenario)

    assert not result.passed
    assert result.steps[0].status == "error"
    assert "command steps need command_executor" in result.steps[0].error


def test_write_scenario_date_field_accepts_time_suffix(monkeypatch) -> None:
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    scenario = Scenario(
        name="date",
        steps=[Step(kind="input_text", name="date", marker="DATE_FIELD",
                    params={"new_value": "01.02.2026", "value_type": "date"})],
    )
    result = run_write_scenario(scenario)

    assert result.passed, result.to_dict()
    assert FakeWriteSession.instances[0].writes == ["01.02.2026"]
    assert result.steps[0].status == "ok"
    assert "surface=form_field_date" in result.steps[0].preview


def test_write_scenario_date_field_validates(monkeypatch) -> None:
    from qa_mcp.scenario import run_write_scenario

    _patch_write_path(monkeypatch)
    scenario = Scenario(
        name="bad-date",
        steps=[Step(kind="input_text", name="date", marker="DATE_FIELD",
                    params={"new_value": "31.02.2026", "value_type": "date"})],
    )
    result = run_write_scenario(scenario)

    assert not result.passed
    assert result.steps[0].status == "error"
    assert "invalid date" in result.steps[0].error


# --- Card 103 Wave 3: runner-execution wiring for the broadened BDD vocabulary (offline) ---


class _AttrCtx:
    """A live-read context that exposes both attribute access (e.g. ``.value``, like the real
    FormValueContext) and ``to_result()`` (for the preview), driven by a single data dict."""

    def __init__(self, data: dict) -> None:
        self._data = dict(data)
        for key, value in self._data.items():
            setattr(self, key, value)

    def to_result(self) -> dict:
        return self._data


class FakeWave3Handle:
    """Configurable single-session handle: records every read so tests can pin the cache behavior."""

    def __init__(self, *, active=None, form=None, value=None) -> None:
        self.calls: list[str] = []
        self._active = active if active is not None else {"active_window_ref": ".HomePage[abc]"}
        self._form = form if form is not None else {"elements": ["PF_TABLE_ITEMS"]}
        self._value = value

    def active_window(self) -> _AttrCtx:
        self.calls.append("active_window")
        return _AttrCtx(self._active)

    def form_summary(self) -> _AttrCtx:
        self.calls.append("form_summary")
        return _AttrCtx(self._form)

    def read_form_value(self, *, field="PF_EDIT_STRING") -> _AttrCtx:
        self.calls.append(f"read_form_value:{field}")
        return _AttrCtx({"field": field, "value": self._value})


class FakeWave3Session:
    def __init__(self, handle: FakeWave3Handle) -> None:
        self.handle = handle

    def __enter__(self) -> "FakeWave3Session":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def open_and_bootstrap(self, **_kw) -> FakeWave3Handle:
        return self.handle


def _ss_runner(tmp_path, handle: FakeWave3Handle, **kw) -> ScenarioRunner:
    return ScenarioRunner(
        session_factory=lambda: FakeWave3Session(handle),
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
        synthesized=object(),
        **kw,
    )


def _odata_client(records, *, capture=None):
    """An ODataClient with an in-memory fetcher (no network)."""
    from qa_mcp.data import ODataClient

    def fetch(url, headers):
        if capture is not None:
            capture["url"] = url
        return {"value": records}

    return ODataClient(base_url="http://lab/odata", fetcher=fetch)


def test_assert_form_open_pass_and_fail(tmp_path) -> None:
    form = "Документ.Заказ.Форма.ФормаДокумента"
    h = FakeWave3Handle(active={"active_window_ref": f"{form}[g]"})
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="s", steps=[Step(kind="assert_form_open", name="open", marker=form)])
    )
    assert r.passed
    assert r.steps[0].assertion is True
    assert h.calls == ["active_window"]

    h2 = FakeWave3Handle(active={"active_window_ref": ".HomePage[abc]"})
    r2 = _ss_runner(tmp_path, h2).run_single_session(
        Scenario(name="s", steps=[Step(kind="assert_form_open", name="open", marker=form)])
    )
    assert not r2.passed
    assert r2.steps[0].status == "assert_failed"
    assert r2.steps[0].assertion is False


def test_assert_element_present_uses_single_cached_read(tmp_path) -> None:
    h = FakeWave3Handle(form={"elements": ["ДатаНачала", "ДатаОкончания", "PF_TABLE_ITEMS"]})
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="s", steps=[
            Step(kind="assert_element_present", name="a", marker="ДатаНачала"),
            Step(kind="assert_element_present", name="b", marker="ДатаОкончания"),
        ])
    )
    assert r.passed
    assert [s.assertion for s in r.steps] == [True, True]
    assert h.calls == ["form_summary"]  # cached: the form is read ONCE for both asserts


def test_read_summary_then_assert_reuses_one_cached_read(tmp_path) -> None:
    # Live regression (2026-06-21, card 103 boot session): a `read_form_summary` step followed by an
    # assert_element_present must REUSE the read — the linear cursor cannot re-advance to frame 17, so a
    # second form_summary() raised RuntimeError (reported as step "error"). The read must populate the cache.
    h = FakeWave3Handle(form={"elements": ["PF_EDIT_STRING", "PF_TABLE_ITEMS"]})
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="read+assert", steps=[
            Step(kind="read_form_summary", name="read"),
            Step(kind="assert_element_present", name="present", marker="PF_EDIT_STRING"),
        ])
    )
    assert r.passed, r.to_dict()
    assert [s.status for s in r.steps] == ["ok", "ok"]
    assert r.steps[1].assertion is True
    assert h.calls == ["form_summary"]  # ONE read — the assert reuses it (no second advance)


def test_read_active_window_then_window_assert_reuses_cache(tmp_path) -> None:
    h = FakeWave3Handle(active={"active_window_ref": "Договоры контрагентов[g]"})
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="read+winassert", steps=[
            Step(kind="read_active_window", name="read"),
            Step(kind="assert_window_open", name="win", marker="Договоры контрагентов"),
        ])
    )
    assert r.passed, r.to_dict()
    assert h.calls == ["active_window"]  # the window assert reuses the read


def test_assert_element_present_fails_when_absent(tmp_path) -> None:
    h = FakeWave3Handle(form={"elements": ["ДатаНачала"]})
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="s", steps=[Step(kind="assert_element_present", name="x", marker="НетТакого")])
    )
    assert not r.passed
    assert r.steps[0].status == "assert_failed"


def test_assert_window_open_and_wait_window_single_read(tmp_path) -> None:
    h = FakeWave3Handle(active={"active_window_ref": "Договоры контрагентов[g]"})
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="s", steps=[
            Step(kind="assert_window_open", name="win", marker="Договоры контрагентов"),
            Step(kind="wait_window", name="wait", marker="Договоры контрагентов",
                 params={"timeout_sec": 5}),
        ])
    )
    assert r.passed
    assert [s.assertion for s in r.steps] == [True, True]
    assert h.calls == ["active_window"]  # both window asserts share one cached active-window read


def test_assert_table_rows_pass_and_fail(tmp_path) -> None:
    h = FakeWave3Handle(form={"elements": ["ФайлыСервера"], "rows": ["data.xml", "image.png"]})
    table = [["Имя"], ["data.xml"], ["image.png"]]
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="s", steps=[
            Step(kind="assert_table_rows", name="rows", marker="ФайлыСервера", params={"table": table})
        ])
    )
    assert r.passed
    assert r.steps[0].assertion is True

    h2 = FakeWave3Handle(form={"rows": ["data.xml"]})
    table2 = [["Имя"], ["data.xml"], ["missing.bin"]]
    r2 = _ss_runner(tmp_path, h2).run_single_session(
        Scenario(name="s2", steps=[
            Step(kind="assert_table_rows", name="rows", marker="T", params={"table": table2})
        ])
    )
    assert not r2.passed
    assert r2.steps[0].status == "assert_failed"
    assert "missing.bin" in r2.steps[0].preview


def test_read_form_value_expect_equals_strict(tmp_path) -> None:
    h = FakeWave3Handle(value="Основной")
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="s", steps=[
            Step(kind="read_form_value", name="eq", marker="Договор", expect_equals="Основной")
        ])
    )
    assert r.passed
    assert r.steps[0].assertion is True

    h2 = FakeWave3Handle(value="Основной договор")  # substring would pass, strict-equality must NOT
    r2 = _ss_runner(tmp_path, h2).run_single_session(
        Scenario(name="s", steps=[
            Step(kind="read_form_value", name="eq", marker="Договор", expect_equals="Основной")
        ])
    )
    assert not r2.passed
    assert r2.steps[0].status == "assert_failed"


def test_skip_step_is_ok_and_does_not_touch_session(tmp_path) -> None:
    h = FakeWave3Handle()
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="s", steps=[
            Step(kind="skip_step", name="skip", params={"reason": "vanessa-runtime setting"})
        ])
    )
    assert r.passed
    assert r.steps[0].status == "ok"
    assert r.steps[0].assertion is None
    assert "skipped" in r.steps[0].preview
    assert h.calls == []


def test_assert_data_runs_without_a_testclient_session(tmp_path) -> None:
    captured: dict = {}
    client = _odata_client([{"Code": "000000001"}], capture=captured)

    def boom():
        raise AssertionError("session_factory must NOT be opened for a pure data-layer assert")

    runner = ScenarioRunner(
        session_factory=boom, bootstrap=object(), templates=object(),
        output_dir=tmp_path, odata_client=client,
    )
    scenario = Scenario(name="db", steps=[Step(
        kind="assert_data", name="db", marker="Catalog_Товары",
        params={"entity_set": "Catalog_Товары", "filter": "Description eq 'Обувь'",
                "field": "Code", "expected": "000000001", "match": "equals"})])
    r = runner.run(scenario)
    assert r.passed, r.to_dict()
    assert r.steps[0].assertion is True
    assert "Catalog_%D0%A2%D0%BE%D0%B2%D0%B0%D1%80%D1%8B" in captured["url"] or "Catalog_Товары" in captured["url"]


def test_assert_data_mismatch_fails(tmp_path) -> None:
    client = _odata_client([{"Code": "999"}])
    runner = ScenarioRunner(
        session_factory=lambda: None, bootstrap=object(), templates=object(),
        output_dir=tmp_path, odata_client=client,
    )
    scenario = Scenario(name="db", steps=[Step(
        kind="assert_data", name="db", marker="X",
        params={"entity_set": "X", "field": "Code", "expected": "000", "match": "equals"})])
    r = runner.run(scenario)
    assert not r.passed
    assert r.steps[0].status == "assert_failed"


def test_assert_data_in_single_session_does_not_touch_handle(tmp_path) -> None:
    client = _odata_client([{"Code": "111"}])
    h = FakeWave3Handle()
    runner = _ss_runner(tmp_path, h, odata_client=client)
    scenario = Scenario(name="ui+db", steps=[
        Step(kind="read_active_window", name="w"),
        Step(kind="assert_data", name="db", marker="X",
             params={"entity_set": "X", "field": "Code", "expected": "111", "match": "equals"}),
    ])
    r = runner.run_single_session(scenario)
    assert r.passed, r.to_dict()
    assert h.calls == ["active_window"]  # the data assert is session-independent


def test_run_subscenario_runs_callee_on_same_handle(tmp_path) -> None:
    h = FakeWave3Handle(active={"active_window_ref": "Договоры[g]"}, form={"elements": ["ДатаНачала"]})
    login = Scenario(name="Вход в систему",
                     steps=[Step(kind="assert_window_open", name="win", marker="Договоры")])
    runner = _ss_runner(tmp_path, h, scenario_registry={"Вход в систему": login})
    scenario = Scenario(name="main", steps=[
        Step(kind="run_subscenario", name="call login", marker="Вход в систему"),
        Step(kind="assert_element_present", name="el", marker="ДатаНачала"),
    ])
    r = runner.run_single_session(scenario)
    assert r.passed, r.to_dict()
    assert r.steps[0].status == "ok"
    assert r.steps[0].assertion is True
    # callee's window assert + outer element assert both ran on the one bootstrapped handle
    assert h.calls == ["active_window", "form_summary"]


def test_connect_client_is_runner_owned_noop(tmp_path) -> None:
    # Card 103 Wave 3: connect_client is is_action, but the runner OWNS the connection (session_factory),
    # so it is intercepted as a lifecycle no-op BEFORE the action_resolver lookup — no resolver needed,
    # no protocol command sent.
    h = FakeWave3Handle()
    r = _ss_runner(tmp_path, h).run_single_session(
        Scenario(name="s", steps=[Step(kind="connect_client", name="connect", marker="sample-thin")])
    )
    assert r.passed
    assert r.steps[0].status == "ok"
    assert r.steps[0].assertion is None
    assert "connect" in r.steps[0].preview.lower()
    assert h.calls == []


def test_run_subscenario_unknown_errors(tmp_path) -> None:
    runner = _ss_runner(tmp_path, FakeWave3Handle())
    r = runner.run_single_session(
        Scenario(name="m", steps=[Step(kind="run_subscenario", name="call", marker="NoSuch")])
    )
    assert not r.passed
    assert r.steps[0].status == "error"
    assert "unknown subscenario" in r.steps[0].error


def test_run_subscenario_recursion_guarded(tmp_path) -> None:
    self_call = Scenario(name="loop", steps=[Step(kind="run_subscenario", name="again", marker="loop")])
    runner = _ss_runner(tmp_path, FakeWave3Handle(), scenario_registry={"loop": self_call})
    r = runner.run_single_session(
        Scenario(name="m", steps=[Step(kind="run_subscenario", name="start", marker="loop")])
    )
    assert not r.passed
    # the inner self-call is caught as recursive → the loop's only step errors → outer summary fails
    assert r.steps[0].status == "assert_failed"


def test_scenario_from_dict_and_validation() -> None:
    scenario = Scenario.from_dict(
        {
            "name": "j",
            "steps": [
                {"kind": "read_active_window", "name": "w", "expect_contains": "HomePage"},
                {"kind": "read_element", "name": "e", "marker": "PF_X"},
            ],
        }
    )
    assert scenario.name == "j"
    assert scenario.steps[1].marker == "PF_X"
    with pytest.raises(ValueError):
        Step(kind="teleport", name="x")  # not a known step kind
    with pytest.raises(ValueError):
        Step(kind="read_element", name="x")  # missing marker

"""Card 74 Phase 5: native MCP server (offline — tools registered + pure helpers)."""

from __future__ import annotations

import asyncio
import inspect
import json
import sys
import types
from pathlib import Path
from typing import get_type_hints

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp import mcp_server  # noqa: E402


@pytest.fixture(autouse=True)
def clear_attached_testclient_context():
    mcp_server._clear_attached_testclient_context()
    yield
    mcp_server._clear_attached_testclient_context()


def test_tools_are_registered() -> None:
    import asyncio

    names = asyncio.run(mcp_server.mcp.list_tools())
    assert {"transpile", "run_scenario", "run_step"}.issubset({t.name for t in names})


def test_decorated_tool_annotations_are_resolved_before_fastmcp_registration() -> None:
    for name in ("run_scenario", "capture_screenshot"):
        tool = getattr(mcp_server, name)
        assert tool.__annotations__ == get_type_hints(tool, include_extras=True)


def test_http_bind_defaults_to_loopback() -> None:
    assert mcp_server._resolve_http_bind({}) == ("127.0.0.1", 8000)


def test_http_bind_rejects_wildcard_without_bearer_token() -> None:
    with pytest.raises(ValueError, match="QA_MCP_BEARER_TOKEN"):
        mcp_server._resolve_http_bind({"QA_MCP_HTTP_HOST": "0.0.0.0"})


def test_http_bind_unsafe_opt_in_cannot_bypass_authentication() -> None:
    with pytest.raises(ValueError, match="QA_MCP_BEARER_TOKEN"):
        mcp_server._resolve_http_bind({
            "QA_MCP_HTTP_HOST": "0.0.0.0",
            "QA_MCP_HTTP_ALLOW_UNSAFE_BIND": "1",
        })


def test_http_bind_allows_wildcard_with_bearer_token() -> None:
    assert mcp_server._resolve_http_bind({
        "QA_MCP_HTTP_HOST": "0.0.0.0",
        "QA_MCP_HTTP_PORT": "9000",
        "QA_MCP_BEARER_TOKEN": "standalone-secret",
    }) == ("0.0.0.0", 9000)


def test_legacy_sse_transport_cannot_claim_authenticated_non_loopback_bind() -> None:
    with pytest.raises(ValueError, match="streamable-http"):
        mcp_server._resolve_http_bind({
            "QA_MCP_TRANSPORT": "sse",
            "QA_MCP_HTTP_HOST": "0.0.0.0",
            "QA_MCP_BEARER_TOKEN": "standalone-secret",
        })


def _run_standalone_http_app(*, path: str, expected_token: str, authorization: str = ""):
    captured: dict[str, object] = {"called": False}
    sent: list[dict[str, object]] = []

    async def downstream(_scope, _receive, send):
        captured["called"] = True
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"downstream", "more_body": False})

    app = mcp_server._StandaloneHttpMiddleware(downstream, bearer_token=expected_token)
    headers = [(b"authorization", authorization.encode("latin1"))] if authorization else []
    scope = {"type": "http", "method": "GET", "path": path, "headers": headers}

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    asyncio.run(app(scope, receive, send))
    return captured, sent


def test_standalone_health_is_public_bounded_and_secret_free() -> None:
    captured, sent = _run_standalone_http_app(path="/health", expected_token="top-secret")

    assert captured == {"called": False}
    assert sent[0]["status"] == 200
    payload = json.loads(sent[1]["body"].decode("utf-8"))
    assert payload == {"status": "ok"}
    assert "secret" not in sent[1]["body"].decode("utf-8").lower()


@pytest.mark.parametrize("authorization", ["", "Bearer wrong", "Basic standalone-secret"])
def test_standalone_mcp_rejects_missing_or_wrong_bearer(authorization: str) -> None:
    captured, sent = _run_standalone_http_app(
        path="/mcp", expected_token="standalone-secret", authorization=authorization
    )

    assert captured == {"called": False}
    assert sent[0]["status"] == 401
    assert (b"www-authenticate", b"Bearer") in sent[0]["headers"]


def test_standalone_mcp_accepts_exact_bearer_before_dispatch() -> None:
    captured, sent = _run_standalone_http_app(
        path="/mcp",
        expected_token="standalone-secret",
        authorization="Bearer standalone-secret",
    )

    assert captured == {"called": True}
    assert sent[0]["status"] == 200


def _run_utf8_gate(body: bytes, content_type: str):
    captured: dict[str, object] = {"called": False}
    sent: list[dict[str, object]] = []

    async def downstream(_scope, receive, send):
        captured["called"] = True
        captured["body"] = (await receive()).get("body", b"")
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok", "more_body": False})

    app = mcp_server._JsonRpcUtf8BodyMiddleware(downstream)
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/mcp",
        "headers": [(b"content-type", content_type.encode("latin1"))],
    }
    delivered = False

    async def receive():
        nonlocal delivered
        if delivered:
            return {"type": "http.request", "body": b"", "more_body": False}
        delivered = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        sent.append(message)

    asyncio.run(app(scope, receive, send))
    return captured, sent


def test_direct_http_utf8_gate_allows_valid_utf8_body() -> None:
    body = '{"open_link":"e1cib/list/Справочник.Валюты"}'.encode("utf-8")
    captured, sent = _run_utf8_gate(body, "application/json; charset=utf-8")

    assert captured == {"called": True, "body": body}
    assert sent[0]["status"] == 200


def test_direct_http_utf8_gate_forwards_disconnect_after_replayed_body() -> None:
    """Streamable HTTP must be able to observe the real client disconnect."""
    observed: list[dict[str, object]] = []
    incoming = iter([
        {"type": "http.request", "body": b"{}", "more_body": False},
        {"type": "http.disconnect"},
    ])

    async def downstream(_scope, receive, _send):
        observed.append(await receive())
        observed.append(await receive())

    async def receive():
        return next(incoming)

    async def send(_message):
        return None

    app = mcp_server._JsonRpcUtf8BodyMiddleware(downstream)
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/mcp",
        "headers": [(b"content-type", b"application/json")],
    }

    asyncio.run(app(scope, receive, send))

    assert observed == [
        {"type": "http.request", "body": b"{}", "more_body": False},
        {"type": "http.disconnect"},
    ]


def test_direct_http_utf8_gate_rejects_non_utf8_charset() -> None:
    body = '{"open_link":"ok"}'.encode("utf-8")
    captured, sent = _run_utf8_gate(body, "application/json; charset=windows-1251")

    assert captured == {"called": False}
    assert sent[0]["status"] == 415
    payload = json.loads(sent[1]["body"].decode("utf-8"))
    assert payload["error"]["data"]["error"] == "jsonrpc-non-utf8-charset"
    assert "UTF-8" in payload["error"]["message"]


def test_direct_http_utf8_gate_rejects_invalid_utf8_bytes() -> None:
    captured, sent = _run_utf8_gate(b'{"open_link":"\xff"}', "application/json")

    assert captured == {"called": False}
    assert sent[0]["status"] == 400
    payload = json.loads(sent[1]["body"].decode("utf-8"))
    assert payload["error"]["data"]["error"] == "jsonrpc-invalid-utf8"
    assert "not valid UTF-8" in payload["error"]["message"]


def test_streamable_http_runner_uses_explicit_bind(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeConfig:
        def __init__(self, app, *, host: str, port: int, log_level: str):
            captured["app"] = app
            captured["host"] = host
            captured["port"] = port
            captured["log_level"] = log_level

    class FakeServer:
        def __init__(self, config: FakeConfig):
            captured["server_config"] = config

        async def serve(self) -> None:
            captured["served"] = True

    fake_uvicorn = types.SimpleNamespace(Config=FakeConfig, Server=FakeServer)
    fake_anyio = types.SimpleNamespace(
        run=lambda fn: captured.update(anyio_run=fn.__name__)
    )
    monkeypatch.setitem(sys.modules, "uvicorn", fake_uvicorn)
    monkeypatch.setitem(sys.modules, "anyio", fake_anyio)

    mcp_server._run_streamable_http_with_utf8_gate("127.0.0.1", 8123)

    assert isinstance(captured["app"], mcp_server._StandaloneHttpMiddleware)
    assert isinstance(captured["app"].app, mcp_server._JsonRpcUtf8BodyMiddleware)
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 8123
    assert captured["log_level"] == "info"
    assert captured["anyio_run"] == "serve"


def test_echo_jsonrpc_arguments_preserves_cyrillic_open_link() -> None:
    result = mcp_server.echo_jsonrpc_arguments(
        open_link="e1cib/list/Справочник.Валюты",
        arguments_json={"caption": "Валюты"},
    )

    assert result["ok"] is True
    assert result["received"]["open_link"] == "e1cib/list/Справочник.Валюты"
    assert result["received"]["arguments"]["caption"] == "Валюты"
    assert result["suspect_mojibake"] is False
    assert result["warnings"] == []


def test_echo_jsonrpc_arguments_flags_question_mark_mojibake() -> None:
    result = mcp_server.echo_jsonrpc_arguments(open_link="e1cib/list/??????????.??????")

    assert result["ok"] is True
    assert result["received"]["open_link"] == "e1cib/list/??????????.??????"
    assert result["suspect_mojibake"] is True
    assert result["warnings"][0]["path"] == "received.open_link"
    assert result["warnings"][0]["code"] == "question-mark-mojibake"


def test_echo_jsonrpc_arguments_flags_replacement_characters_in_nested_values() -> None:
    result = mcp_server.echo_jsonrpc_arguments(arguments_json={"values": ["bad�text"]})

    assert result["suspect_mojibake"] is True
    assert result["warnings"][0]["path"] == "received.arguments.values[0]"
    assert result["warnings"][0]["code"] == "unicode-replacement-character"


def test_scenario_from_feature_text() -> None:
    scenario, unmapped = mcp_server.scenario_from_input(
        None,
        "# language: ru\nСценарий: s\n  Дано я читаю активное окно\n  И я нажимаю на кнопку с именем 'X'\n",
    )
    assert [s.kind for s in scenario.steps] == ["read_active_window", "click_button"]
    assert unmapped == []


def test_scenario_from_json() -> None:
    scenario, unmapped = mcp_server.scenario_from_input(
        {"name": "j", "steps": [{"kind": "read_form_summary", "name": "f"}]}, None
    )
    assert scenario.name == "j"
    assert scenario.steps[0].kind == "read_form_summary"
    assert unmapped == []


def test_scenario_from_input_requires_one() -> None:
    with pytest.raises(ValueError):
        mcp_server.scenario_from_input(None, None)


def test_transpile_tool_pure() -> None:
    out = mcp_server.transpile(
        "Сценарий: s\n  Дано я открываю список 'Справочник.Склады'\n  И я выбираю строку 'Средний'\n"
    )
    assert out["scenario"] == "s"
    kinds = [s["kind"] for s in out["steps"]]
    assert kinds == ["open_list", "select_row"]
    assert out["steps"][0]["params"] == {"catalog": "Справочник.Склады"}


def test_run_scenario_builds_subscenario_registry_from_feature(monkeypatch) -> None:
    # Card 103 Wave 3: a multi-scenario feature registers EVERY scenario so a `run_subscenario` step
    # resolves its callee by name. Capture the registry `_run` receives without a live TestClient.
    captured: dict = {}

    def fake_run(scenario, host, port, capture_dir, manager_templates, single_session,
                 scenario_registry=None, action_resolver=None):
        captured["scenario"] = scenario.name
        captured["registry"] = scenario_registry
        return {"scenario": scenario.name, "status": "passed", "steps": []}

    monkeypatch.setattr(mcp_server, "_run", fake_run)
    feature = (
        "Сценарий: Главный\n"
        "  Дано я выполняю сценарий 'Вход в систему'\n"
        "Сценарий: Вход в систему\n"
        "  Дано я читаю активное окно\n"
    )
    out = mcp_server.run_scenario(feature_text=feature)
    assert out["scenario"] == "Главный"  # the first scenario runs
    assert set(captured["registry"]) == {"Главный", "Вход в систему"}  # all register as callees
    assert captured["registry"]["Вход в систему"].steps[0].kind == "read_active_window"


def test_run_scenario_builds_action_resolver_from_capture(monkeypatch) -> None:
    # Card 103 Wave 3: action_capture wires an action_resolver into the runner (the production bridge that
    # lets action steps EXECUTE). Verify run_scenario builds it + threads it through, parsing action_ordinals.
    captured: dict = {}
    sentinel = object()

    def fake_build(action_capture, *, captured_input_value=None, marker_ordinals=None):
        captured["action_capture"] = action_capture
        captured["input_value"] = captured_input_value
        captured["ordinals"] = marker_ordinals
        return sentinel

    def fake_run(scenario, host, port, capture_dir, manager_templates, single_session,
                 scenario_registry=None, action_resolver=None):
        captured["resolver"] = action_resolver
        return {"scenario": scenario.name, "status": "passed", "steps": []}

    monkeypatch.setattr(mcp_server, "_build_action_resolver", fake_build)
    monkeypatch.setattr(mcp_server, "_run", fake_run)
    feature = "Сценарий: s\n  Когда я нажимаю на кнопку с именем 'PF_ADD_ROW'\n"
    mcp_server.run_scenario(feature_text=feature, action_capture="genuine-x",
                            action_input_value="V", action_ordinals="PF_ADD_ROW=5")
    assert captured["action_capture"] == "genuine-x"
    assert captured["input_value"] == "V"
    assert captured["ordinals"] == {"PF_ADD_ROW": 5}
    assert captured["resolver"] is sentinel


def test_run_scenario_without_action_capture_has_no_resolver(monkeypatch) -> None:
    captured: dict = {}

    def fake_run(scenario, host, port, capture_dir, manager_templates, single_session,
                 scenario_registry=None, action_resolver=None):
        captured["resolver"] = action_resolver
        return {"scenario": scenario.name, "status": "passed", "steps": []}

    monkeypatch.setattr(mcp_server, "_run", fake_run)
    mcp_server.run_scenario(feature_text="Сценарий: s\n  Дано я читаю активное окно\n")
    assert captured["resolver"] is None


def test_run_scenario_json_has_no_registry(monkeypatch) -> None:
    captured: dict = {}

    def fake_run(scenario, host, port, capture_dir, manager_templates, single_session,
                 scenario_registry=None, action_resolver=None):
        captured["registry"] = scenario_registry
        return {"scenario": scenario.name, "status": "passed", "steps": []}

    monkeypatch.setattr(mcp_server, "_run", fake_run)
    mcp_server.run_scenario(scenario_json={"name": "j", "steps": [{"kind": "read_form_summary", "name": "f"}]})
    assert captured["registry"] is None


# --- Card 103 Wave 3 (live leg): nav-link derivation + the live-open navigate_resolver (offline) ---


def _step(kind, **kw):
    from qa_mcp.scenario import Step

    return Step(kind=kind, name=kw.pop("name", kind), **kw)


def test_nav_link_for_open_main_form_kinds() -> None:
    f = mcp_server._nav_link_for_step
    assert f(_step("open_main_form", marker="Валюты", params={"object_type": "справочника"})) == \
        "e1cib/list/Справочник.Валюты"
    assert f(_step("open_main_form", marker="Заказ", params={"object_type": "документа"})) == \
        "e1cib/list/Документ.Заказ"
    # reports + data processors open via e1cib/app/… (live-verified card 106)
    assert f(_step("open_main_form", marker="ЗакрытиеМесяца", params={"object_type": "обработки"})) == \
        "e1cib/app/Обработка.ЗакрытиеМесяца"
    assert f(_step("open_main_form", marker="ПрайсЛист", params={"object_type": "отчёта"})) == \
        "e1cib/app/Отчет.ПрайсЛист"
    # create forms (card 106 change 4): e1cib/data/<Type>.<Name> (no ?ref), live-verified «… (создание)»
    assert f(_step("open_create_form", marker="Заказ", params={"object_type": "документ"})) == \
        "e1cib/data/Документ.Заказ"
    assert f(_step("open_create_form", marker="Валюты", params={"object_type": "элемент справочника"})) == \
        "e1cib/data/Справочник.Валюты"
    # Subordinate catalogs need owner context; callers provide an explicit open_link on the scenario step.
    assert f(_step("open_create_form", marker="ДоговорыКонтрагентов", params={
        "object_type": "элемент справочника",
        "requires_owner": True,
    })) is None
    assert f(_step("open_main_form", marker="Курсы", params={"object_type": "регистра сведений"})) == \
        "e1cib/list/РегистрСведений.Курсы"
    # a fully-qualified «Тип.Имя» is opened verbatim as a list
    assert f(_step("open_main_form", marker="Справочник.Валюты", params={"object_type": "справочника"})) == \
        "e1cib/list/Справочник.Валюты"


def test_nav_link_for_open_list() -> None:
    f = mcp_server._nav_link_for_step
    assert f(_step("open_list", marker="e1cib/list/", params={"catalog": "Товары"})) == \
        "e1cib/list/Справочник.Товары"
    assert f(_step("open_list", marker="e1cib/list/", params={"catalog": "Документ.Заказ"})) == \
        "e1cib/list/Документ.Заказ"


def test_nav_link_for_unmapped_or_missing_returns_none() -> None:
    f = mcp_server._nav_link_for_step
    assert f(_step("open_main_form", marker="X", params={"object_type": "галактики"})) is None
    assert f(_step("open_main_form", marker="", params={"object_type": "справочника"})) is None
    assert f(_step("open_list", marker="e1cib/list/", params={})) is None
    assert f(_step("close_window", marker="W")) is None  # not an open kind


def test_build_navigate_resolver_opens_and_reports(monkeypatch) -> None:
    # The resolver derives the nav-link and opens the form via _open_form_by_link; verify the result dict for
    # both the opened (tuple) and unopened (None) cases without touching a live client.
    calls: list[str] = []

    def fake_open(handle, nav_link, splice_templates=None):
        calls.append(nav_link)
        assert splice_templates is not None  # the resolver loads + passes the value-read template set
        return ("Валюты", "SF-GUID", "MF-GUID") if "Валюты" in nav_link else None

    monkeypatch.setattr(mcp_server, "_open_form_by_link", fake_open)
    resolver = mcp_server._build_navigate_resolver()

    ok = resolver(_step("open_main_form", marker="Валюты", params={"object_type": "справочника"}), object())
    assert ok == {"opened": True, "nav_link": "e1cib/list/Справочник.Валюты", "caption": "Валюты",
                  "secondary_frame": "SF-GUID", "managed_form": "MF-GUID"}
    bad = resolver(_step("open_main_form", marker="Нет", params={"object_type": "справочника"}), object())
    assert bad["opened"] is False and bad["nav_link"] == "e1cib/list/Справочник.Нет"
    # an unmapped step never reaches _open_form_by_link
    none = resolver(_step("open_main_form", marker="X", params={"object_type": "галактики"}), object())
    assert none["opened"] is False and none["nav_link"] is None
    assert calls == ["e1cib/list/Справочник.Валюты", "e1cib/list/Справочник.Нет"]


def test_run_scenario_passes_navigate_resolver(monkeypatch) -> None:
    # run_scenario always threads a navigate_resolver so open_main_form/open_list steps open LIVE (no capture).
    captured: dict = {}

    def fake_runner(*a, navigate_resolver=None, **kw):
        captured["navigate_resolver"] = navigate_resolver

        class _R:
            def run_single_session(self, scenario):
                from qa_mcp.scenario import ScenarioResult
                return ScenarioResult(name=scenario.name, status="passed", steps=[])

            run = run_single_session
        return _R()

    monkeypatch.setattr(mcp_server, "ScenarioRunner", fake_runner)
    monkeypatch.setattr(mcp_server, "CaptureBootstrap", type("B", (), {"load": staticmethod(lambda *_: object())}))
    monkeypatch.setattr(mcp_server, "ProtocolTemplates", type("T", (), {"load": staticmethod(lambda *_: object())}))
    monkeypatch.setattr(mcp_server, "synthesize_bootstrap", lambda: object())
    mcp_server.run_scenario(feature_text="Сценарий: s\n  Дано я открываю основную форму справочника 'Валюты'\n")
    assert captured["navigate_resolver"] is not None


def test_autofill_required_fields_tool() -> None:
    # Card 106 change 4: the MCP tool derives the create-fill plan + a runnable feature from an object's .mdo.
    mdo = (
        '<mdclass:Catalog xmlns:mdclass="http://g5.1c.ru/v8/dt/metadata/mdclass">'
        "<name>Демо</name>"
        "<standardAttributes><name>Description</name><fillChecking>ShowError</fillChecking></standardAttributes>"
        '<attributes uuid="r"><name>Контрагент</name><type><types>CatalogRef.Контрагенты</types></type>'
        "<fillChecking>ShowError</fillChecking></attributes>"
        "</mdclass:Catalog>"
    )
    r = mcp_server.autofill_required_fields(mdo, "Справочник", "Демо")
    assert r["create_link"] == "e1cib/data/Справочник.Демо"
    assert [f["name"] for f in r["fillable"]] == ["Наименование"]
    assert [f["name"] for f in r["unfillable"]] == ["Контрагент"]
    # the feature is runnable: open the create form + fill the one primitive (the ref is skipped)
    scn, unmapped = mcp_server.scenario_from_input(None, r["feature"])
    assert unmapped == []
    assert [s.kind for s in scn.steps] == ["open_create_form", "input_text"]


# --- Card 98 #2: state / results / infobase tool-surface parity (offline) ---

CHANGE2_TOOLS = {"get_test_results", "infobase_info", "get_state", "get_window_list", "attach_test_client"}


def test_change2_tools_registered() -> None:
    import asyncio

    names = {t.name for t in asyncio.run(mcp_server.mcp.list_tools())}
    assert CHANGE2_TOOLS.issubset(names)


def _reset_results() -> None:
    mcp_server._RESULTS_LOG.clear()


def test_get_test_results_empty() -> None:
    _reset_results()
    r = mcp_server.get_test_results()
    assert r == {"scenarios": 0, "passed": 0, "failed": 0, "total_steps": 0,
                 "step_status_counts": {}, "results": []}


def test_record_and_aggregate_results() -> None:
    _reset_results()
    mcp_server._record_result({"scenario": "s1", "status": "passed",
                               "steps": [{"kind": "read_element", "name": "a", "status": "ok"}]})
    mcp_server._record_result({"scenario": "s2", "status": "failed",
                               "steps": [{"kind": "read_form_value", "name": "b", "status": "assert_failed"},
                                         {"kind": "x", "name": "c", "status": "error"}]})
    r = mcp_server.get_test_results()
    assert (r["scenarios"], r["passed"], r["failed"], r["total_steps"]) == (2, 1, 1, 3)
    assert r["step_status_counts"] == {"ok": 1, "assert_failed": 1, "error": 1}
    assert r["results"][0]["scenario"] == "s1" and r["results"][0]["step_count"] == 1


def test_record_result_emits_qa_bridge_observation(monkeypatch) -> None:
    _reset_results()
    calls: list[dict] = []
    monkeypatch.setattr(mcp_server, "_emit_qa_bridge_observation", lambda **kwargs: calls.append(kwargs))

    report = {"scenario": "bridge", "status": "failed", "duration_sec": 0.25,
              "steps": [{"kind": "read_element", "name": "a", "status": "error",
                         "error": "boom", "attachments": [".artifacts/qa/bridge.json"]}]}
    assert mcp_server._record_result(report) is report

    assert calls[0]["subject"] == "scenario_outcome"
    assert calls[0]["status"] == "failed"
    assert calls[0]["duration_ms"] == 250
    assert calls[0]["retained_evidence_path"] == ".artifacts/qa/bridge.json"
    assert calls[0]["tool_name"] == "qa.testclient.bridge.scenario_outcome"


def test_get_test_results_clear() -> None:
    _reset_results()
    mcp_server._record_result({"scenario": "s", "status": "passed", "steps": []})
    cleared = mcp_server.get_test_results(clear=True)
    assert cleared["cleared"] == 1
    assert mcp_server.get_test_results()["scenarios"] == 0   # log reset


def test_get_state_composes_views(tmp_path: Path) -> None:
    _reset_results()
    mcp_server._record_result({"scenario": "last-one", "status": "failed",
                               "steps": [{"kind": "k", "name": "n", "status": "error"}]})
    st = mcp_server.get_state(
        env_file=str(tmp_path / "missing.env"),
        port=59999,
    )
    assert st["connection"]["listening"] is False and st["connection"]["alive"] is None
    assert st["run_session"]["last_scenario"] == "last-one"
    assert st["run_session"]["last_status"] == "failed"
    assert st["infobase"]["password_set"] is False          # password never echoed
    assert "value_read_templates" in st["engine"]


def test_write_test_report_emits_qa_bridge_observation(tmp_path, monkeypatch) -> None:
    _reset_results()
    mcp_server._record_result({"scenario": "s", "status": "passed", "steps": []})
    calls: list[dict] = []
    monkeypatch.setattr(mcp_server, "_emit_qa_bridge_observation", lambda **kwargs: calls.append(kwargs))

    result = mcp_server.write_test_report(str(tmp_path), formats=["junit"], suite_name="qa")

    assert result["written"]["junit"].endswith("junit.xml")
    assert calls[-1]["subject"] == "test_report"
    assert calls[-1]["status"] == "ok"
    assert calls[-1]["retained_evidence_path"] == str(tmp_path)
    assert calls[-1]["tool_name"] == "qa.testclient.bridge.test_report"


def test_capture_screenshot_emits_qa_bridge_observation(tmp_path, monkeypatch) -> None:
    class Backend:
        name = "fake"

        def capture_screenshot(self, display, out, window=None):
            out.write_bytes(b"png")
            return {"path": str(out), "display": display, "window": window, "size_bytes": 3}

    calls: list[dict] = []
    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: Backend())
    monkeypatch.setattr(mcp_server, "_emit_qa_bridge_observation", lambda **kwargs: calls.append(kwargs))

    result = mcp_server.capture_screenshot(":99", out_path=str(tmp_path / "shot.png"))

    assert result["path"].endswith("shot.png")
    assert calls[0]["subject"] == "screenshot"
    assert calls[0]["status"] == "ok"
    assert calls[0]["retained_evidence_path"] == result["path"]
    assert calls[0]["tool_name"] == "qa.testclient.bridge.screenshot"


def test_infobase_info_reads_profile_redacts_password(tmp_path) -> None:
    env = tmp_path / "p.env"
    env.write_text(
        'INFOBASE_PATH="/opt/1c-dev/demo"\n'
        "TEST_CLIENT_USER=Администратор\n"
        "TEST_CLIENT_KIND=thick\n"
        "TEST_CLIENT_PASSWORD=s3cret\n"
        "PLATFORM_ROOT=/opt/1cv8/x86_64/8.3.27.2130\n",
        encoding="utf-8",
    )
    info = mcp_server.infobase_info(env_file=str(env), port=59999)
    assert info["env_present"] is True
    assert info["infobase"]["target"] == 'File="/opt/1c-dev/demo"'
    assert info["infobase"]["user"] == "Администратор"
    assert info["infobase"]["kind"] == "thick"
    assert info["infobase"]["password_set"] is True         # set, but the value is NOT echoed
    assert "s3cret" not in str(info)
    assert info["client_bin"].endswith("1cv8")
    assert info["listening"] is False


def test_infobase_info_missing_profile(tmp_path) -> None:
    info = mcp_server.infobase_info(env_file=str(tmp_path / "absent.env"), port=59999)
    assert info["env_present"] is False                      # no profile → defaults, no crash
    assert info["infobase"]["user"] == "Администратор"


def test_public_status_paths_inherit_listener_only_relay_probe(monkeypatch, tmp_path) -> None:
    observed: list[tuple[tuple[str, int], float]] = []
    monkeypatch.setenv(
        mcp_server.client_transport.RELAY_ENDPOINT_ENV, "station.example:15382"
    )
    monkeypatch.setenv(
        mcp_server.client_transport.RELAY_TOKEN_ENV, "relay-secret"
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "relay_listener_reachable",
        lambda address, timeout: observed.append((address, timeout)) is None,
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "connect_testclient",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("public relay status must not authenticate or dial the target")
        ),
    )
    env_file = tmp_path / "relay-status.env"
    env_file.write_text("INFOBASE_PATH=/opt/1c-dev/demo\n", encoding="utf-8")

    status = mcp_server.test_client_status(host="station.example", port=15382)
    info = mcp_server.infobase_info(
        env_file=str(env_file), host="station.example", port=15382
    )
    state = mcp_server.get_state(
        env_file=str(env_file), host="station.example", port=15382
    )

    assert status["listening"] is True
    assert info["listening"] is True
    assert state["connection"]["listening"] is True
    assert observed == [(('station.example', 15382), 0.5)] * 3


@pytest.mark.parametrize(
    "tool_name",
    [
        "transpile",
        "search_for_steps",
        "echo_jsonrpc_arguments",
        "launch_test_client",
        "attach_test_client",
        "test_client_status",
        "qa_mcp_doctor",
        "stop_test_client",
        "get_test_results",
        "write_test_report",
        "assert_data",
        "assert_data_count",
        "query_com",
        "assert_com_count",
        "com_connector_doctor",
        "role_data_matrix",
        "generate_smoke_suite",
        "autofill_required_fields",
        "infobase_info",
        "get_state",
    ],
)
def test_direct_tools_resolve_annotations_before_fastmcp_registration(tool_name: str) -> None:
    tool = getattr(mcp_server, tool_name)
    assert tool.__annotations__ == get_type_hints(
        tool, include_extras=True
    )


def test_attach_test_client_tool_delegates(monkeypatch) -> None:
    class Handle:
        def status(self) -> dict:
            return {"attached": True, "owns_process": False, "host": "h", "port": 1}

    captured: dict = {}

    def fake_attach(**kwargs):
        captured.update(kwargs)
        return Handle()

    monkeypatch.setattr(mcp_server.client_lifecycle, "attach_test_client", fake_attach)
    result = mcp_server.attach_test_client(host="h", port=1, connect_timeout_sec=0.25)
    assert result["attached"] is True
    assert result["owns_process"] is False
    assert result["active_attachment"]["host"] == "h"
    assert result["active_attachment"]["port"] == 1
    assert captured == {"host": "h", "port": 1, "connect_timeout_sec": 0.25}


def test_attach_test_client_remote_records_nonowning_host_client_target(monkeypatch) -> None:
    class Handle:
        def status(self) -> dict:
            return {"attached": True, "owns_process": False, "host": "station.example", "port": 15444}

    class FakeBackend:
        def test_client_status(self, *, pid=None, port=None):
            assert pid is None
            assert port == 15444
            return {
                "ok": True,
                "pid": 4321,
                "port": 15444,
                "listening": True,
                "client_target": {
                    "kind": "host-agent-testclient",
                    "pid": 4321,
                    "port": 15444,
                },
            }

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(
        mcp_server.client_display.RemoteAgentBackend,
        "from_env",
        classmethod(lambda cls: FakeBackend()),
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "attach_test_client", lambda **_kwargs: Handle())

    result = mcp_server.attach_test_client(host="station.example", port=15444)

    assert result["owns_process"] is False
    assert result["client_target"] == {
        "kind": "host-agent-testclient",
        "pid": 4321,
        "port": 15444,
    }
    assert result["active_attachment"]["client_target"] == result["client_target"]


def test_display_backend_requires_target_for_active_remote_context(monkeypatch) -> None:
    backend = mcp_server.client_display.RemoteAgentBackend("host:8001", client_port=15444)
    mcp_server._remember_attached_testclient({
        "attached": True,
        "owns_process": False,
        "host": "station.example",
        "port": 15444,
        "client_target_error": {"error": "client-target-missing"},
    })
    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: backend)

    selected = mcp_server._display_backend()

    assert selected is backend
    assert selected.client_target is None
    assert selected.client_target_required is True


@pytest.mark.parametrize("configured_window", ["", "*"])
def test_remote_list_diagnostic_inherits_active_client_target(
    monkeypatch, configured_window: str,
) -> None:
    target = {
        "kind": "host-agent-testclient",
        "lifecycle_id": "launch-1",
        "pid": 4321,
        "port": 15444,
    }
    backend = mcp_server.client_display.RemoteAgentBackend(
        "host:8001",
        target_window=configured_window,
        client_port=15444,
        client_target=target,
        client_target_required=True,
    )
    calls: list[tuple[str, dict]] = []
    monkeypatch.setattr(mcp_server.client_display, "remote_client_enabled", lambda: True)
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    monkeypatch.setattr(
        backend,
        "_ensure_ready",
        lambda: {"capabilities": [mcp_server.client_display.HOST_AGENT_TESTCLIENT_WINDOW_TARGET_CAPABILITY]},
    )

    def fake_json(method, path, token=True, payload=None, timeout=None):
        calls.append((path, payload))
        if path == "/window_list":
            return {"ok": True, "windows": []}
        return {"ok": True, "cells": []}

    monkeypatch.setattr(backend, "_json", fake_json)

    diagnostic = mcp_server._remote_client_list_diagnostic("read_list_grid")

    assert diagnostic is not None
    assert diagnostic["target_source"] == "active-client-target"
    assert "target_window" not in diagnostic
    visible_payload = next(payload for path, payload in calls if path == "/uia/visible_list_cells")
    assert visible_payload["window"] == ""
    assert visible_payload["client_target"] == target


def test_attach_reuses_ready_remote_relay_launch_without_target_probe(monkeypatch) -> None:
    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(
        mcp_server.client_transport,
        "relay_configuration",
        lambda: (("station.example", 15382), "relay-secret"),
    )
    monkeypatch.setattr(
        mcp_server.client_transport,
        "relay_listener_reachable",
        lambda address, timeout=0.5: address == ("station.example", 15382),
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "attach_test_client",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("relay target probe must not run")),
    )
    mcp_server._remember_attached_testclient(
        {
            "host": "station.example",
            "port": 15382,
            "listening": True,
            "host_agent": {"ok": True, "alive": True, "listening": True, "pid": 4321},
        }
    )

    result = mcp_server.attach_test_client(host="station.example", port=15382)

    assert result["attached"] is True
    assert result["listening"] is True
    assert result["host_agent"]["pid"] == 4321


ENDPOINT_TOUCHING_TOOLS = frozenset({
    "run_scenario",
    "run_step",
    "write_form_value",
    "write_form_date",
    "write_form_value_xtest",
    "write_form_values",
    "run_write_scenario_tool",
    "write_form_fields_by_label",
    "switch_page",
    "toggle_checkbox",
    "set_choice",
    "set_table_cell",
    "set_table_date_cell",
    "select_table_row",
    "open_list",
    "search_list",
    "set_list_view",
    "advanced_search",
    "run_report",
    "read_spreadsheet_cell",
    "choose_from_list",
    "answer_dialog",
    "set_reference_field",
    "open_card",
    "close_window",
    "activate_window",
    "read_user_messages",
    "choose_from_menu",
    "click_command",
    "add_table_row",
    "delete_table_row",
    "move_table_row",
    "copy_table_row",
    "select_all_table_rows",
    "assert_form_value",
    "wait_for_form_value",
    "read_form_descriptor",
    "read_record",
    "read_table_cell",
    "read_list_column",
    "read_list_row",
    "read_list_grid",
    "get_window_list_testclient",
    "measure_scenario",
})

HOST_PORT_NON_PROTOCOL_TOOLS = frozenset({
    "attach_test_client",
    "test_client_status",
    "qa_mcp_doctor",
    "infobase_info",
    "get_state",
})


def _registered_tool_names() -> set[str]:
    return {tool.name for tool in asyncio.run(mcp_server.mcp.list_tools())}


def test_endpoint_tool_classification_covers_registered_host_port_tools() -> None:
    import inspect

    registered = _registered_tool_names()
    host_port_tools = {
        name
        for name in registered
        if hasattr(mcp_server, name)
        and {"host", "port"}.issubset(inspect.signature(getattr(mcp_server, name)).parameters)
    }

    assert host_port_tools == ENDPOINT_TOUCHING_TOOLS | HOST_PORT_NON_PROTOCOL_TOOLS
    for name in ENDPOINT_TOUCHING_TOOLS:
        assert getattr(getattr(mcp_server, name), "_qa_mcp_testclient_tool", False), name


def test_decorated_endpoint_tool_uses_attached_endpoint_and_annotates(monkeypatch) -> None:
    captured: dict[str, object] = {}
    sentinel_template = object()

    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15446, "listening": True}
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda host, port: True)
    monkeypatch.setattr(mcp_server, "resolve_capture_dir", lambda name, root=None: "/capture")
    monkeypatch.setattr(mcp_server, "derive_page_switch", lambda capture_dir, base_page: sentinel_template)

    def fake_switch(template, target_page, *, host, port):
        captured["template"] = template
        captured["target_page"] = target_page
        captured["host"] = host
        captured["port"] = port
        return {"accepted": True}

    monkeypatch.setattr(mcp_server, "native_switch_page", fake_switch)

    result = mcp_server.switch_page("PF_PAGE_A")

    assert result["accepted"] is True
    assert result["attached_endpoint"]["host"] == "attached-host"
    assert captured == {
        "template": sentinel_template,
        "target_page": "PF_PAGE_A",
        "host": "attached-host",
        "port": 15446,
    }


@pytest.mark.parametrize(
    "native_result",
    [
        {"ok": False, "error": "retarget_failed", "field": "Контрагент", "accepted": False},
        {"accepted": False, "failure_reason": "send_timeout", "send_timeout_at": 2},
    ],
)
def test_testclient_tool_preserves_structured_native_failures(monkeypatch, native_result) -> None:
    captured: dict[str, object] = {}

    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15448, "listening": True}
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda host, port: True)

    @mcp_server.testclient_tool(phase="write")
    def fake_tool(*, host: str = "127.0.0.1", port: int = 15381) -> dict[str, object]:
        captured["host"] = host
        captured["port"] = port
        return dict(native_result)

    result = fake_tool()

    assert captured == {"host": "attached-host", "port": 15448}
    assert result["attached_endpoint"]["host"] == "attached-host"
    for key, value in native_result.items():
        assert result[key] == value


def test_endpoint_tool_rejects_stale_attached_endpoint(monkeypatch) -> None:
    called = False

    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15449, "listening": True}
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda host, port: False)

    @mcp_server.testclient_tool(phase="descriptor")
    def fake_tool(*, host: str = mcp_server.DEFAULT_CLIENT_HOST, port: int = mcp_server.DEFAULT_CLIENT_PORT) -> dict[str, object]:
        nonlocal called
        called = True
        return {"ok": True, "host": host, "port": port}

    result = fake_tool()

    assert called is False
    assert result["ok"] is False
    assert result["error"] == "stale-attached-testclient"
    assert result["attached_endpoint"]["listening"] is False
    assert "qa-mcp-testclient" in result["action_hint"]


def test_stale_attachment_does_not_block_explicit_endpoint(monkeypatch) -> None:
    captured: dict[str, object] = {}

    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15450, "listening": True}
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda host, port: False)

    @mcp_server.testclient_tool(phase="descriptor")
    def fake_tool(*, host: str = mcp_server.DEFAULT_CLIENT_HOST, port: int = mcp_server.DEFAULT_CLIENT_PORT) -> dict[str, object]:
        captured["host"] = host
        captured["port"] = port
        return {"ok": True}

    result = fake_tool(host="explicit-host", port=15555)

    assert result == {"ok": True}
    assert captured == {"host": "explicit-host", "port": 15555}


def test_read_form_descriptor_without_open_link_returns_actionable_guid_error(monkeypatch) -> None:
    monkeypatch.setattr(mcp_server, "_resolve_testclient_endpoint", lambda host, port, phase: (host, int(port), None))

    def fake_read(**_kwargs):
        raise ValueError("managed_form_guid_ascii template field requires a live ManagedForm GUID")

    monkeypatch.setattr(mcp_server, "_read_form_descriptor", fake_read)

    result = mcp_server.read_form_descriptor()

    assert result["ok"] is False
    assert result["error"] == "open-link-required"
    assert result["detail"] == "cannot infer current ManagedForm GUID; pass open_link"
    assert "managed_form_guid_ascii" not in result["detail"]
    assert "open_link" in result["action_hint"]


def test_read_form_descriptor_reports_empty_after_bounded_warmup(monkeypatch) -> None:
    monkeypatch.setattr(mcp_server, "_resolve_testclient_endpoint", lambda host, port, phase: (host, int(port), None))
    monkeypatch.setattr(
        mcp_server,
        "_SETTINGS",
        types.SimpleNamespace(descriptor_warmup_attempts=2, descriptor_warmup_delay_sec=0.0),
    )
    monkeypatch.setattr(
        mcp_server,
        "_read_form_descriptor",
        lambda **_kwargs: {"opened": None, "elements": [], "element_count": 0, "fields": {}},
    )

    result = mcp_server.read_form_descriptor(open_link="e1cib/list/Справочник.Валюты", gherkin=False)

    assert result["ok"] is False
    assert result["error"] == "descriptor-empty"
    assert result["warmup_attempts"] == 2


def test_read_table_cell_without_open_link_returns_actionable_guid_error(monkeypatch) -> None:
    monkeypatch.setattr(mcp_server, "_resolve_testclient_endpoint", lambda host, port, phase: (host, int(port), None))

    def fake_read(**_kwargs):
        raise ValueError("managed_form_guid_ascii template field requires a live ManagedForm GUID")

    monkeypatch.setattr(mcp_server, "_read_table_cell", fake_read)

    result = mcp_server.read_table_cell("Валюты", "Код")

    assert result["ok"] is False
    assert result["error"] == "open-link-required"
    assert result["detail"] == "cannot infer current ManagedForm GUID; pass open_link"
    assert "managed_form_guid_ascii" not in result["detail"]
    assert "open_link" in result["action_hint"]


ENDPOINT_CONTRACT_CASES = [
    ("switch_page", ("PF_PAGE_A",), "native_switch_page"),
    ("toggle_checkbox", ("PF_CHECKBOX_TRUE",), "native_toggle_checkbox"),
    ("set_choice", ("PF_CHOICE_B",), "native_set_choice"),
    ("set_table_cell", ("NEW",), "native_set_table_cell"),
    ("set_table_date_cell", ("05.03.2026",), "_set_table_date_cell"),
    ("select_table_row", ("PF_ROW_002_TEXT",), "native_select_table_row"),
    ("open_list", (), "native_open_list"),
    ("search_list", ("Молоко",), "native_search_list"),
    ("set_list_view", ("Список",), "native_set_list_view"),
    ("advanced_search", ("Молоко",), "native_advanced_search"),
    ("run_report", (), "native_click_command"),
    ("read_spreadsheet_cell", (), "native_read_spreadsheet_cell"),
    ("choose_from_list", ("PF_CHOICE_A",), "native_choose_from_list"),
    ("answer_dialog", (), "native_answer_dialog"),
    ("set_reference_field", ("Пантера АО",), "native_set_reference_field"),
    ("open_card", (), "native_open_card"),
    ("close_window", (), "native_close_window"),
    ("activate_window", (), "native_activate_window"),
    ("read_user_messages", (), "native_read_user_messages"),
    ("choose_from_menu", ("PF_MENU_2",), "native_choose_from_list"),
    ("click_command", ("PF_ADD_ROW",), "native_click_command"),
    ("add_table_row", (), "native_click_command"),
    ("delete_table_row", (), "native_click_command"),
    ("move_table_row", (), "native_click_command"),
    ("copy_table_row", (), "native_click_command"),
    ("select_all_table_rows", (), "native_click_command"),
]


@pytest.mark.parametrize("capture", [None, "", "   "])
def test_open_list_omitted_or_blank_capture_uses_navigation_templates(monkeypatch, capture) -> None:
    observed: dict[str, object] = {}
    sentinel_assets = object()

    def fail_capture_resolution(*_args, **_kwargs):
        raise AssertionError("template-backed open_list must not resolve the public capture selector")

    def fake_prepare(*, manager_templates, repo_root):
        observed.update({
            "manager_templates": manager_templates,
            "repo_root": repo_root,
        })
        return sentinel_assets

    def fake_open(assets, nav_link, *, host, port, repo_root):
        observed.update({
            "assets": assets,
            "nav_link": nav_link,
            "host": host,
            "port": port,
            "open_repo_root": repo_root,
        })
        return ("Валюты", "secondary-frame", "managed-form")

    monkeypatch.setattr(mcp_server, "resolve_capture_dir", fail_capture_resolution)
    monkeypatch.setattr(mcp_server.protocol_introspection, "prepare_open_list_navigation_assets", fake_prepare)
    monkeypatch.setattr(mcp_server.protocol_introspection, "open_list_from_navigation_assets", fake_open)

    result = mcp_server.open_list(catalog="Справочник.Валюты", capture=capture)

    assert result["ok"] is True
    assert result["accepted"] is True
    assert result["navigation_method"] == "template-backed"
    assert observed["assets"] is sentinel_assets
    assert observed["nav_link"] == "e1cib/list/Справочник.Валюты"
    assert observed["manager_templates"] == mcp_server.VALUE_READ_TEMPLATES
    assert observed["host"] == mcp_server.DEFAULT_CLIENT_HOST
    assert observed["port"] == mcp_server.DEFAULT_CLIENT_PORT


def test_open_list_preflights_before_attached_endpoint_liveness(monkeypatch) -> None:
    events: list[str] = []
    sentinel_assets = object()
    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15449, "listening": True}
    )

    def fake_prepare(**_kwargs):
        events.append("asset-preflight")
        return sentinel_assets

    def fake_liveness(host, port):
        events.append(f"liveness:{host}:{port}")
        return True

    def fake_open(assets, _nav_link, *, host, port, repo_root):
        assert assets is sentinel_assets
        events.append(f"open:{host}:{port}")
        return ("Валюты", "secondary-frame", "managed-form")

    monkeypatch.setattr(mcp_server.protocol_introspection, "prepare_open_list_navigation_assets", fake_prepare)
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", fake_liveness)
    monkeypatch.setattr(mcp_server.protocol_introspection, "open_list_from_navigation_assets", fake_open)

    result = mcp_server.open_list(catalog="Справочник.Валюты")

    assert result["ok"] is True
    assert result["attached_endpoint"]["host"] == "attached-host"
    assert events == ["asset-preflight", "liveness:attached-host:15449", "open:attached-host:15449"]


def test_open_list_explicit_bundled_capture_keeps_legacy_derivation(monkeypatch) -> None:
    observed: dict[str, object] = {}
    sentinel_template = object()

    monkeypatch.setattr(
        mcp_server,
        "_open_list_from_navigation_templates",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("explicit capture must keep capture replay")),
    )
    def fake_resolve(name, root=None):
        observed["resolved_capture"] = (name, root)
        return "/bundled/listform-read"

    monkeypatch.setattr(mcp_server, "resolve_capture_dir", fake_resolve)

    def fake_derive(capture_dir, base_link):
        observed["derive"] = (capture_dir, base_link)
        return sentinel_template

    def fake_native(template, catalog, *, host, port):
        observed["native"] = (template, catalog, host, port)
        return {"accepted": True}

    monkeypatch.setattr(mcp_server, "derive_open_list", fake_derive)
    monkeypatch.setattr(mcp_server, "native_open_list", fake_native)

    result = mcp_server.open_list(catalog="Справочник.Валюты", capture="listform-read")

    assert result == {"accepted": True}
    assert observed["resolved_capture"][0] == "listform-read"
    assert observed["derive"][1] == "e1cib/list/Справочник.Товары"
    assert observed["native"] == (
        sentinel_template,
        "Справочник.Валюты",
        mcp_server.DEFAULT_CLIENT_HOST,
        mcp_server.DEFAULT_CLIENT_PORT,
    )


def test_open_list_missing_navigation_template_fails_before_session(monkeypatch, tmp_path) -> None:
    liveness_calls: list[tuple[str, int]] = []

    class FailIfSessionConstructed:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("asset preflight must finish before TestClientSession construction")

    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "stale-host", "port": 15449, "listening": True}
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "port_is_listening",
        lambda host, port: liveness_calls.append((host, port)) or False,
    )
    monkeypatch.setattr(mcp_server.protocol_introspection, "TestClientSession", FailIfSessionConstructed)

    result = mcp_server.open_list(navigation_templates=str(tmp_path / "missing-navigation.json"))

    assert result["ok"] is False
    assert result["error"] == "open-list-navigation-unavailable"
    assert result["capability"] == "template-backed-open-list"
    assert result["asset_class"] == "navigation-templates"
    assert result["protocol_write_attempted"] is False
    assert str(tmp_path) not in json.dumps(result)
    assert liveness_calls == []


@pytest.mark.parametrize(
    ("missing_frame", "expected_reason"),
    [
        (8, "required-bootstrap-frame-unavailable"),
        (9, "required-bootstrap-frame-unavailable"),
        (10, "required-bootstrap-frame-unavailable"),
        (218, "required-splice-frame-unavailable"),
    ],
)
def test_open_list_incomplete_navigation_template_fails_before_session(
    monkeypatch, tmp_path, missing_frame, expected_reason
) -> None:
    liveness_calls: list[tuple[str, int]] = []

    class FailIfSessionConstructed:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("incomplete templates must fail before TestClientSession construction")

    source = Path(mcp_server.VALUE_READ_TEMPLATES).resolve()
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    data["templates"] = [item for item in data["templates"] if item["frame_index"] != missing_frame]
    incomplete = tmp_path / f"missing-frame-{missing_frame}.json"
    incomplete.write_text(json.dumps(data), encoding="utf-8")
    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "stale-host", "port": 15449, "listening": True}
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "port_is_listening",
        lambda host, port: liveness_calls.append((host, port)) or False,
    )
    monkeypatch.setattr(mcp_server.protocol_introspection, "TestClientSession", FailIfSessionConstructed)

    result = mcp_server.open_list(navigation_templates=str(incomplete))

    assert result["ok"] is False
    assert result["error"] == "open-list-navigation-unavailable"
    assert result["asset_class"] == "navigation-templates"
    assert result["reason"] == expected_reason
    assert result["protocol_write_attempted"] is False
    assert str(tmp_path) not in json.dumps(result)
    assert liveness_calls == []


def test_open_list_navigation_template_without_splice_marker_fails_before_session(monkeypatch, tmp_path) -> None:
    liveness_calls: list[tuple[str, int]] = []

    class FailIfSessionConstructed:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("splice structure must fail before TestClientSession construction")

    source = Path(mcp_server.VALUE_READ_TEMPLATES).resolve()
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    frame218 = next(item for item in data["templates"] if item["frame_index"] == 218)
    marker = mcp_server.protocol_introspection._WINDOW_COMMAND_HEADER_MARKER
    body = bytes.fromhex(frame218["body_hex"])
    assert marker in body
    frame218["body_hex"] = body.replace(marker, b"\x00" * len(marker)).hex()
    malformed = tmp_path / "missing-splice-marker.json"
    malformed.write_text(json.dumps(data), encoding="utf-8")
    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "stale-host", "port": 15449, "listening": True}
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "port_is_listening",
        lambda host, port: liveness_calls.append((host, port)) or False,
    )
    monkeypatch.setattr(mcp_server.protocol_introspection, "TestClientSession", FailIfSessionConstructed)

    result = mcp_server.open_list(navigation_templates=str(malformed))

    assert result["ok"] is False
    assert result["error"] == "open-list-navigation-unavailable"
    assert result["reason"] == "required-splice-frame-unavailable"
    assert result["protocol_write_attempted"] is False
    assert str(tmp_path) not in json.dumps(result)
    assert liveness_calls == []


def test_open_list_explicit_bundled_navigation_template_preflights_before_open(monkeypatch) -> None:
    observed: dict[str, object] = {}

    def fake_open(assets, nav_link, *, host, port, repo_root):
        observed.update({
            "template_path": assets.templates.path,
            "nav_link": nav_link,
            "host": host,
            "port": port,
            "repo_root": repo_root,
        })
        return ("Валюты", "secondary-frame", "managed-form")

    monkeypatch.setattr(mcp_server.protocol_introspection, "open_list_from_navigation_assets", fake_open)

    result = mcp_server.open_list(
        catalog="Справочник.Валюты",
        navigation_templates=mcp_server.VALUE_READ_TEMPLATES,
    )

    assert result["ok"] is True
    assert result["navigation_method"] == "template-backed"
    assert result["target_link"] == "e1cib/list/Справочник.Валюты"
    assert observed["template_path"] == Path(mcp_server.VALUE_READ_TEMPLATES).resolve()


def test_open_list_public_default_contains_no_development_capture_name() -> None:
    signature = inspect.signature(mcp_server.open_list)

    assert signature.parameters["capture"].default is None
    assert "genuine-card" not in str(signature)
    assert "traffic-selfcontained" not in str(signature)


@pytest.mark.parametrize(("tool_name", "args", "native_name"), ENDPOINT_CONTRACT_CASES)
def test_attach_endpoint_contract_for_action_tools(monkeypatch, tool_name, args, native_name) -> None:
    captured: dict[str, tuple[str, int]] = {}
    sentinel_template = object()

    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15447, "listening": True}
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda host, port: True)
    monkeypatch.setattr(mcp_server, "resolve_capture_dir", lambda name, root=None: "/capture")
    monkeypatch.setattr(mcp_server, "_force_list_refresh", lambda: ("none", ""))
    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: object())
    monkeypatch.setattr(
        mcp_server.protocol_introspection,
        "prepare_open_list_navigation_assets",
        lambda **_kwargs: sentinel_template,
    )

    def fake_open_list_from_assets(_assets, _nav_link, *, host, port, repo_root):
        captured["native_open_list"] = (host, port)
        return ("Валюты", "secondary-frame", "managed-form")

    monkeypatch.setattr(
        mcp_server.protocol_introspection,
        "open_list_from_navigation_assets",
        fake_open_list_from_assets,
    )

    for derive_name in (
        "derive_page_switch",
        "derive_checkbox_toggle",
        "derive_choice_set",
        "derive_table_cell_write",
        "derive_open_list",
        "derive_search_list",
        "derive_advanced_search",
        "derive_command_click",
        "derive_read_spreadsheet_cell",
        "derive_choose_from_list",
        "derive_answer_dialog",
        "derive_set_reference_field",
        "derive_open_card",
        "derive_close_window",
        "derive_activate_window",
        "derive_read_user_messages",
        "derive_table_command",
    ):
        monkeypatch.setattr(mcp_server, derive_name, lambda *a, **kw: sentinel_template)

    def fake_native(*_args, host, port, **_kwargs):
        captured[native_name] = (host, port)
        return {"ok": True, "accepted": True}

    monkeypatch.setattr(mcp_server, native_name, fake_native)

    result = getattr(mcp_server, tool_name)(*args)

    assert result["attached_endpoint"]["host"] == "attached-host"
    assert captured[native_name] == ("attached-host", 15447)


def test_open_list_explicit_capture_uses_attached_endpoint(monkeypatch) -> None:
    observed: dict[str, object] = {}
    sentinel_template = object()
    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15447, "listening": True}
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda host, port: True)
    monkeypatch.setattr(mcp_server, "resolve_capture_dir", lambda name, root=None: "/capture")
    monkeypatch.setattr(mcp_server, "derive_open_list", lambda *_args, **_kwargs: sentinel_template)

    def fake_native(template, catalog, *, host, port):
        observed["call"] = (template, catalog, host, port)
        return {"accepted": True}

    monkeypatch.setattr(mcp_server, "native_open_list", fake_native)

    result = mcp_server.open_list(catalog="Справочник.Валюты", capture="listform-read")

    assert result["attached_endpoint"]["host"] == "attached-host"
    assert observed["call"] == (sentinel_template, "Справочник.Валюты", "attached-host", 15447)


def test_endpoint_tool_bad_capture_returns_structured_error() -> None:
    result = mcp_server.switch_page("PF_PAGE_A", capture="definitely-missing-capture")

    assert result["ok"] is False
    assert result["error"] == "capture-not-found"
    assert result["tool"] == "switch_page"


def test_endpoint_tool_invalid_argument_returns_structured_error() -> None:
    result = mcp_server.move_table_row(direction="sideways")

    assert result["ok"] is False
    assert result["error"] == "invalid-arguments"
    assert result["tool"] == "move_table_row"


def test_list_table_resolution_reports_manager_handshake_drift(monkeypatch) -> None:
    def fake_read_descriptor(**_kwargs):
        raise ValueError("client ACK GUID not found in response after manager frame 3")

    monkeypatch.setattr(mcp_server, "_read_form_descriptor", fake_read_descriptor)

    table, diagnostic = mcp_server._resolve_list_table_for_read(
        host="127.0.0.1",
        port=15381,
        open_link="e1cib/list/Справочник.Валюты",
    )

    assert table is None
    assert diagnostic["ok"] is False
    assert diagnostic["error"] == "manager-handshake-moved"
    assert diagnostic["phase"] == "list_read"
    assert diagnostic["available_tables"] == []
    assert diagnostic["handshake_drift"]["error"] == "manager-handshake-moved"
    assert "refresh" in diagnostic["handshake_drift"]["action_hint"].lower()


def test_descriptor_reports_manager_handshake_drift_instead_of_invalid_arguments(monkeypatch) -> None:
    monkeypatch.setattr(
        mcp_server,
        "_resolve_testclient_endpoint",
        lambda host, port, **_kwargs: (host, port, None),
    )
    monkeypatch.setattr(
        mcp_server,
        "_read_form_descriptor",
        lambda **_kwargs: (_ for _ in ()).throw(
            ValueError("client ACK GUID not found in response after manager frame 3")
        ),
    )

    result = mcp_server.read_form_descriptor(open_link="e1cib/list/Справочник.Валюты")

    assert result["ok"] is False
    assert result["error"] == "manager-handshake-moved"
    assert result["phase"] == "descriptor"
    assert "refresh" in result["action_hint"].lower()


def test_measure_scenario_remote_client_guard(monkeypatch) -> None:
    from qa_mcp.debug import measure as measure_module

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(
        measure_module,
        "measure_scenario",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("measure must not start in remote mode")),
    )

    result = mcp_server.measure_scenario("Сценарий: offline\n")

    assert result["ok"] is False
    assert result["error"] == "local-boot-disabled-remote-client"
    assert result["tool"] == "measure_scenario"


def test_launch_test_client_remote_routes_to_host_agent_and_attaches(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeBackend:
        def launch_test_client(self, **kwargs):
            captured.update(kwargs)
            return {
                "ok": True,
                "pid": 4321,
                "port": kwargs["port"],
                "response_id": "testclient-launch",
                "command_summary": "1cv8 ENTERPRISE ...",
                "owns_process": True,
                "lifecycle_owner": "host-agent",
                "lifecycle_id": "launch-1",
                "lifecycle_handle": {
                    "kind": "host-agent-testclient",
                    "id": "launch-1",
                    "pid": 4321,
                    "port": kwargs["port"],
                },
            }

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server, "DEFAULT_CLIENT_HOST", "host.docker.internal")
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "load_env_file",
        lambda _path: {
            "INFOBASE_PATH": "C:/Bases/vanessa_client",
            "TEST_CLIENT_USER": "Tester",
            "TEST_CLIENT_PASSWORD": "secret",
            "PLATFORM_ROOT": "C:/Program Files/1cv8/8.3.27.2130/bin",
        },
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "port_is_listening",
        lambda host, port, timeout_sec=0.5: host == "host.docker.internal" and port == 15444,
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "ensure_test_client",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("local launch must not run")),
    )

    result = mcp_server.launch_test_client(port=15444, wait_sec=0, use_hardware_licenses=True)

    assert result["listening"] is True
    assert result["owns_process"] is True
    assert result["lifecycle_owner"] == "host-agent"
    assert result["lifecycle_id"] == "launch-1"
    assert result["lifecycle_handle"]["id"] == "launch-1"
    assert result["client_target"] == {
        "kind": "host-agent-testclient",
        "lifecycle_id": "launch-1",
        "pid": 4321,
        "port": 15444,
    }
    assert result["active_attachment"]["host"] == "host.docker.internal"
    assert result["active_attachment"]["port"] == 15444
    assert result["active_attachment"]["owns_process"] is True
    assert result["active_attachment"]["lifecycle_id"] == "launch-1"
    assert result["active_attachment"]["client_target"] == result["client_target"]
    assert captured["infobase_path"] == "C:/Bases/vanessa_client"
    assert captured["user"] == "Tester"
    assert captured["password"] == "secret"
    assert captured["platform_version"] == "8.3.27.2130"
    assert captured["use_hardware_licenses"] is True
    assert "secret" not in result["host_command"]


def test_launch_test_client_remote_owned_host_ready_skips_consuming_probe(monkeypatch) -> None:
    class FakeBackend:
        def launch_test_client(self, **kwargs):
            return {
                "ok": True,
                "pid": 4321,
                "port": kwargs["port"],
                "alive": True,
                "listening": True,
                "readiness": "ready",
                "response_id": "testclient-launch",
                "owns_process": True,
                "lifecycle_owner": "host-agent",
                "lifecycle_id": "launch-1",
                "lifecycle_handle": {
                    "kind": "host-agent-testclient",
                    "id": "launch-1",
                    "pid": 4321,
                    "port": kwargs["port"],
                },
            }

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server, "DEFAULT_CLIENT_HOST", "127.0.0.1")
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(
        mcp_server.client_display.RemoteAgentBackend,
        "from_env",
        classmethod(lambda cls: FakeBackend()),
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "load_env_file",
        lambda _path: {"INFOBASE_PATH": "C:/Bases/demo10413", "TEST_CLIENT_USER": "Tester"},
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "port_is_listening",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not consume TestClient socket")),
    )

    result = mcp_server.launch_test_client(port=15661, wait_sec=0)

    assert result["listening"] is True
    assert result["owns_process"] is True
    assert result["client_target"]["lifecycle_id"] == "launch-1"
    assert result["remote_reachability"]["method"] == "host_agent_lifecycle_ready"
    assert result["remote_reachability"]["probe_skipped"] is True
    assert result["active_attachment"]["client_target"] == result["client_target"]


def test_launch_test_client_remote_legacy_host_agent_result_stays_unowned(monkeypatch) -> None:
    class FakeBackend:
        def launch_test_client(self, **kwargs):
            return {
                "ok": True,
                "pid": 4321,
                "port": kwargs["port"],
                "alive": True,
                "listening": True,
                "readiness": "ready",
                "response_id": "testclient-launch",
            }

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server, "DEFAULT_CLIENT_HOST", "host.docker.internal")
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "load_env_file",
        lambda _path: {"INFOBASE_PATH": "C:/Bases/vanessa_client", "TEST_CLIENT_USER": "Tester"},
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "port_is_listening",
        lambda host, port, timeout_sec=0.5: host == "host.docker.internal" and port == 15444,
    )

    result = mcp_server.launch_test_client(port=15444, wait_sec=0)

    assert result["listening"] is True
    assert result["owns_process"] is False
    assert "lifecycle_handle" not in result
    assert result["active_attachment"]["owns_process"] is False
    assert "lifecycle_handle" not in result["active_attachment"]


def test_stop_test_client_remote_routes_to_host_agent(monkeypatch) -> None:
    captured: dict[str, object] = {}
    handle = {"kind": "host-agent-testclient", "id": "launch-1", "pid": 4321, "port": 15444}

    class FakeBackend:
        def stop_test_client(self, **kwargs):
            captured.update(kwargs)
            return {
                "ok": True,
                "pid": kwargs["pid"],
                "state": "stopped",
                "stopped": True,
                "refused": False,
            }

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "stop_by_pid",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("local stop must not run")),
    )

    result = mcp_server.stop_test_client(pid=4321, port=15444, lifecycle_handle=handle)

    assert captured == {"pid": 4321, "port": 15444, "lifecycle_id": "launch-1", "lifecycle_handle": handle}
    assert result["ok"] is True
    assert result["state"] == "stopped"
    assert result["mode"] == "remote-client"
    assert result["tool"] == "stop_test_client"


def test_stop_test_client_remote_preserves_idempotent_final_state(monkeypatch) -> None:
    handle = {"kind": "host-agent-testclient", "id": "launch-1", "pid": 4321, "port": 15444}
    responses = [
        {"ok": True, "pid": 4321, "state": "stopped", "stopped": True, "refused": False},
        {"ok": True, "pid": 4321, "state": "already_stopped", "stopped": False, "refused": False},
    ]

    class FakeBackend:
        def stop_test_client(self, **_kwargs):
            return responses.pop(0)

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))

    first = mcp_server.stop_test_client(pid=4321, lifecycle_handle=handle)
    second = mcp_server.stop_test_client(pid=4321, lifecycle_handle=handle)

    assert first["state"] == "stopped"
    assert second["state"] == "already_stopped"
    assert second["refused"] is False


def test_stop_test_client_remote_refuses_attach_only_pid(monkeypatch) -> None:
    class FakeBackend:
        def stop_test_client(self, **kwargs):
            raise AssertionError("host-agent stop must not be called without lifecycle_handle.id")

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))

    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15444, "listening": True}
    )

    result = mcp_server.stop_test_client(pid=9876)

    assert result["state"] == "not_owned"
    assert result["refused"] is True
    assert result["reason"] == "missing_lifecycle_handle"
    assert mcp_server._active_attached_testclient_status()["owns_process"] is False


def test_stop_test_client_remote_refuses_pid_only_even_when_same_pid_is_active(monkeypatch) -> None:
    class FakeBackend:
        def stop_test_client(self, **_kwargs):
            raise AssertionError("PID-only remote stop must not reach host-agent")

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))

    mcp_server._remember_attached_testclient(
        {
            "attached": True,
            "owns_process": True,
            "pid": 4321,
            "host": "host.docker.internal",
            "port": 15444,
            "listening": True,
            "lifecycle_id": "new-lifecycle",
            "lifecycle_handle": {
                "kind": "host-agent-testclient",
                "id": "new-lifecycle",
                "pid": 4321,
                "port": 15444,
            },
        }
    )

    result = mcp_server.stop_test_client(pid=4321)

    assert result["state"] == "not_owned"
    assert result["refused"] is True
    assert result["reason"] == "missing_lifecycle_handle"
    assert mcp_server._active_attached_testclient_status()["lifecycle_id"] == "new-lifecycle"


def test_stop_test_client_remote_refuses_mismatched_lifecycle_ids(monkeypatch) -> None:
    class FakeBackend:
        def stop_test_client(self, **_kwargs):
            raise AssertionError("mismatched lifecycle ids must not reach host-agent")

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))

    result = mcp_server.stop_test_client(
        pid=4321,
        lifecycle_id="top-level",
        lifecycle_handle={"kind": "host-agent-testclient", "id": "nested", "pid": 4321, "port": 15444},
    )

    assert result["state"] == "not_owned"
    assert result["refused"] is True
    assert result["reason"] == "lifecycle_handle_mismatch"


def test_stop_test_client_remote_reports_unsupported_lifecycle_host_agent(monkeypatch) -> None:
    handle = {"kind": "host-agent-testclient", "id": "launch-1", "pid": 4321, "port": 15444}

    class FakeBackend:
        def stop_test_client(self, **_kwargs):
            raise mcp_server.client_display.DisplayBackendError(
                "host-agent-testclient-lifecycle-unsupported",
                (
                    "host agent version 0.1.9-testclient-owned-lifecycle does not advertise "
                    "lifecycle-handle TestClient stop support"
                ),
                payload={
                    "version": "0.1.9-testclient-owned-lifecycle",
                    "version_relationship": "protocol-compatible",
                },
            )

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))

    result = mcp_server.stop_test_client(pid=4321, lifecycle_handle=handle)

    assert result["ok"] is False
    assert result["error"] == "host-agent-testclient-lifecycle-unsupported"
    assert "host_agent" not in result
    assert result["detail"] == "host agent request failed"


def test_launch_test_client_separates_local_tport_from_authenticated_relay_endpoint(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeBackend:
        def launch_test_client(self, **kwargs):
            captured.update(kwargs)
            return {"ok": True, "pid": 4321, "alive": True, "listening": True}

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server, "DEFAULT_CLIENT_HOST", "station.example")
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "load_env_file",
        lambda _path: {"INFOBASE_PATH": "C:/Bases/demo10413", "TEST_CLIENT_USER": "Tester"},
    )
    monkeypatch.setattr(
        mcp_server,
        "_remote_protocol_endpoint",
        lambda target: ("station.example", 15382),
    )
    observed_probes: list[tuple[str, int]] = []
    monkeypatch.setattr(
        mcp_server.client_transport,
        "relay_configuration",
        lambda: (("station.example", 15382), "relay-secret"),
    )
    monkeypatch.setattr(
        mcp_server.client_transport,
        "relay_listener_reachable",
        lambda address, timeout=0.5: observed_probes.append(address) is None or address == ("station.example", 15382),
    )

    result = mcp_server.launch_test_client(port=15381, wait_sec=0)

    assert captured["port"] == 15381
    assert observed_probes == [("station.example", 15382)]
    assert result["host"] == "station.example"
    assert result["port"] == 15382
    assert result["connection"]["port"] == 15382
    assert result["active_attachment"]["port"] == 15382
    assert "-TPort 15381" in result["host_command"]


@pytest.mark.parametrize(
    "code",
    ["testclient-exited-early", "testclient-not-listening", "testclient-pid-handoff-failed"],
)
def test_launch_test_client_remote_preserves_host_agent_not_ready(monkeypatch, code: str) -> None:
    host_payload = {
        "ok": False,
        "error": code,
        "detail": "host-agent classified launch as not ready",
        "pid": 4321,
        "port": 15444,
        "alive": code != "testclient-exited-early",
        "listening": False,
        "readiness": "failed",
    }

    class FakeBackend:
        def launch_test_client(self, **_kwargs):
            raise mcp_server.client_display.DisplayBackendError(
                code,
                "host-agent classified launch as not ready",
                status=502,
                payload=host_payload,
            )

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server, "DEFAULT_CLIENT_HOST", "host.docker.internal")
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "load_env_file",
        lambda _path: {
            "INFOBASE_PATH": "C:/Bases/vanessa_client",
            "TEST_CLIENT_USER": "Tester",
            "TEST_CLIENT_PASSWORD": "secret",
        },
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "port_is_listening",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("container probe must not run")),
    )

    result = mcp_server.launch_test_client(port=15444)

    assert result["ok"] is False
    assert result["error"] == code
    assert "host_agent" not in result
    assert result["detail"] == "host agent request failed"
    assert "active_attachment" not in result
    assert mcp_server._active_attached_testclient_status() is None
    assert "secret" not in result["host_command"]


def test_launch_test_client_remote_not_ready_exposes_cleanup_handle(monkeypatch) -> None:
    host_payload = {
        "ok": False,
        "error": "testclient-not-listening",
        "detail": "host-agent classified launch as not ready",
        "pid": 4321,
        "port": 15444,
        "alive": True,
        "listening": False,
        "readiness": "not_listening",
        "owns_process": True,
        "lifecycle_owner": "host-agent",
        "lifecycle_id": "launch-1",
        "lifecycle_handle": {
            "kind": "host-agent-testclient",
            "id": "launch-1",
            "pid": 4321,
            "port": 15444,
        },
    }

    class FakeBackend:
        def launch_test_client(self, **_kwargs):
            raise mcp_server.client_display.DisplayBackendError(
                "testclient-not-listening",
                "host-agent classified launch as not ready",
                status=504,
                payload=host_payload,
            )

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server, "DEFAULT_CLIENT_HOST", "host.docker.internal")
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "load_env_file",
        lambda _path: {"INFOBASE_PATH": "C:/Bases/vanessa_client", "TEST_CLIENT_USER": "Tester"},
    )

    result = mcp_server.launch_test_client(port=15444)

    assert result["ok"] is False
    assert result["error"] == "testclient-not-listening"
    assert result["pid"] == 4321
    assert result["owns_process"] is True
    assert result["lifecycle_owner"] == "host-agent"
    assert result["lifecycle_id"] == "launch-1"
    assert result["lifecycle_handle"] == host_payload["lifecycle_handle"]
    assert "active_attachment" not in result
    assert mcp_server._active_attached_testclient_status() is None


def test_launch_test_client_remote_requires_container_reachability_after_host_ready(monkeypatch) -> None:
    class FakeBackend:
        def launch_test_client(self, **kwargs):
            return {
                "ok": True,
                "pid": 4321,
                "port": kwargs["port"],
                "alive": True,
                "listening": True,
                "readiness": "ready",
                "response_id": "testclient-launch",
            }

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server, "DEFAULT_CLIENT_HOST", "host.docker.internal")
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: True)
    monkeypatch.setattr(mcp_server.client_display.RemoteAgentBackend, "from_env", classmethod(lambda cls: FakeBackend()))
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "load_env_file",
        lambda _path: {"INFOBASE_PATH": "C:/Bases/vanessa_client", "TEST_CLIENT_USER": "Tester"},
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda *_args, **_kwargs: False)

    result = mcp_server.launch_test_client(port=15444, wait_sec=0)

    assert result["ok"] is False
    assert result["error"] == "remote-testclient-port-not-listening"
    assert "host_agent" not in result
    assert "active_attachment" not in result
    assert "active_attachment" not in result
    assert mcp_server._active_attached_testclient_status() is None


def test_launch_test_client_remote_fallback_has_redacted_host_command(monkeypatch) -> None:
    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setattr(mcp_server, "DEFAULT_CLIENT_HOST", "host.docker.internal")
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda: False)
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "load_env_file",
        lambda _path: {
            "CONNECTION_STRING": "File=\"C:/Bases/vanessa_client\";Pwd=secret;",
            "TEST_CLIENT_USER": "Tester",
            "TEST_CLIENT_PASSWORD": "secret",
            "PLATFORM_ROOT": "C:/Program Files/1cv8/8.3.27.2130/bin",
        },
    )

    result = mcp_server.launch_test_client(port=15445)

    assert result["ok"] is False
    assert result["error"] == "host-agent-not-configured"
    assert "-TPort 15445" in result["host_command"]
    assert "Tester" in result["host_command"]
    assert "secret" not in result["host_command"]
    assert "<redacted-password>" in result["host_command"]


def test_write_form_value_uses_attached_endpoint_by_default(monkeypatch) -> None:
    captured: dict = {}

    class FakeNativeWriteSession:
        def __init__(self, template, *, host, port):
            captured["host"] = host
            captured["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return None

        def write(self, value, *, field):
            return {"field": field, "value": value, "committed": True}

    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15444, "listening": True}
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda host, port: True)
    monkeypatch.setattr(mcp_server, "resolve_capture_dir", lambda name, root=None: "/capture")
    monkeypatch.setattr(mcp_server, "derive_write_template", lambda *args, **kwargs: object())
    monkeypatch.setattr(mcp_server, "NativeWriteSession", FakeNativeWriteSession)

    result = mcp_server.write_form_value("VALUE")

    assert result["committed"] is True
    assert captured == {"host": "attached-host", "port": 15444}


def test_write_form_value_open_link_routes_to_label_writer(monkeypatch) -> None:
    captured: dict = {}

    def fake_open_link_write(**kwargs):
        captured.update(kwargs)
        # card 125 #4 — the real writer now attaches a protocol value-read; committed flows from it.
        return {
            "foregrounded": True,
            "all_targeted": True,
            "all_committed": True,
            "results": [{"label": kwargs["labels"][0], "targeted": True, "committed": True,
                         "readback_value": kwargs["values"][0], "click_xy": [10, 20]}],
            "readback": {"opened": "Договор (создание)", "verified": True, "field_count": 1,
                         "fields": {kwargs["labels"][0]: kwargs["values"][0]}},
            "screenshot": "shot.png",
        }

    monkeypatch.setattr(mcp_server, "_write_open_link_fields_by_label", fake_open_link_write)
    result = mcp_server.write_form_value(
        "VALUE",
        field="Наименование",
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        display=":99",
        save=True,
    )

    assert result["committed"] is True                       # read back from the form model
    assert result["readback_value"] == "VALUE"
    assert result["verification"] == "value_readback"
    assert result["write_mode"] == "open_link_label_xtest"
    assert result["open_link"] == "e1cib/data/Справочник.ДоговорыКонтрагентов"
    assert result["field"] == "Наименование"
    assert captured["labels"] == ["Наименование"]
    assert captured["values"] == ["VALUE"]
    assert captured["display"] == ":99"
    assert captured["save"] is True


def test_write_form_date_validates_and_routes_open_link(monkeypatch) -> None:
    captured: dict = {}

    def fake_open_link_write(**kwargs):
        captured.update(kwargs)
        # card 125 #4 — committed reflects the value-read of the open form, not just on-screen targeting.
        return {
            "foregrounded": True,
            "all_targeted": True,
            "all_committed": True,
            "results": [{"label": kwargs["labels"][0], "targeted": True, "committed": True,
                         "readback_value": kwargs["values"][0]}],
            "readback": {"opened": "Договор (создание)", "verified": True, "field_count": 1,
                         "fields": {kwargs["labels"][0]: kwargs["values"][0]}},
        }

    monkeypatch.setattr(mcp_server, "_write_open_link_fields_by_label", fake_open_link_write)

    invalid = mcp_server.write_form_date(
        "31.02.2026",
        field="ДатаДоговора",
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
    )
    assert invalid["ok"] is False
    assert invalid["error"] == "invalid-date"

    result = mcp_server.write_form_date(
        "01.02.2026",
        field="ДатаДоговора",
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        display=":91",
    )
    assert result["surface"] == "form_field_date"
    assert result["requested_value"] == "01.02.2026"
    assert result["committed"] is True
    assert captured["labels"] == ["ДатаДоговора"]
    assert captured["values"] == ["01.02.2026"]
    assert captured["display"] == ":91"


def test_set_table_date_cell_rejects_invalid_date_before_backend(monkeypatch) -> None:
    def fail_backend():
        raise AssertionError("display backend must not be requested for invalid dates")

    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", fail_backend)

    result = mcp_server.set_table_date_cell("99.99.2026")

    assert result["status"] == "blocked"
    assert result["reason"] == "invalid_date"
    assert result["requested_date"] == "99.99.2026"


def test_set_table_date_cell_valid_date_routes_normalized_parts(monkeypatch) -> None:
    captured: dict = {}
    backend = object()

    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: backend)
    monkeypatch.setattr(
        mcp_server,
        "_set_table_date_cell",
        lambda **kwargs: captured.update(kwargs) or {"status": "set", "requested_date": kwargs["date"]},
    )

    result = mcp_server.set_table_date_cell("5.03.2026")

    assert result["status"] == "blocked"
    assert result["reason"] == "invalid_date"

    result = mcp_server.set_table_date_cell("05.03.2026")

    assert result == {"status": "set", "requested_date": "05.03.2026"}
    assert captured["date"] == "05.03.2026"
    assert captured["date_parts"] == (5, 3, 2026)
    assert captured["backend"] is backend


def test_drive_calendar_pick_blocks_backward_year_before_opening_dropdown(tmp_path) -> None:
    class FakeBackend:
        def __init__(self) -> None:
            self.clicks: list[tuple[int, int, str]] = []

        def click(self, x: int, y: int, *, display: str) -> None:
            self.clicks.append((x, y, display))

    backend = FakeBackend()

    result = mcp_server._drive_calendar_pick(
        display=":92",
        button=(100, 200),
        d=5,
        m=3,
        y=2025,
        from_year=2026,
        settle_sec=0,
        out_dir=tmp_path,
        column="Date",
        table="Items",
        requested_date="05.03.2025",
        activation_screenshot="activated.png",
        backend=backend,
    )

    assert result["status"] == "blocked"
    assert result["year_nav"]["offset"] == -1
    assert backend.clicks == []


def test_run_write_scenario_tool_uses_attached_endpoint(monkeypatch) -> None:
    captured: dict = {}

    class Result:
        def to_dict(self):
            return {"scenario": "write", "status": "passed", "steps": []}

    def fake_run_write_scenario(scenario, *, host, port, capture, base_field, captured_value, default_value):
        captured["host"] = host
        captured["port"] = port
        return Result()

    mcp_server._remember_attached_testclient(
        {"attached": True, "owns_process": False, "host": "attached-host", "port": 15445, "listening": True}
    )
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda host, port: True)
    monkeypatch.setattr(mcp_server, "run_write_scenario", fake_run_write_scenario)

    result = mcp_server.run_write_scenario_tool(scenario_json='{"name":"write","steps":[]}')

    assert result["status"] == "passed"
    assert result["attached_endpoint"]["host"] == "attached-host"
    assert captured == {"host": "attached-host", "port": 15445}


def test_run_write_scenario_tool_open_link_create_flow(monkeypatch) -> None:
    captured: dict = {}

    def fake_open_link_write(**kwargs):
        captured.update(kwargs)
        return {
            "foregrounded": True,
            "all_targeted": True,
            "all_selected": True,
            "saved": bool(kwargs["save"]),
            "results": [
                {"label": "ДатаДоговора", "targeted": True, "click_xy": [10, 20]},
                {"label": "Номер", "targeted": True, "click_xy": [10, 50]},
            ],
            "screenshot": "create.png",
        }

    monkeypatch.setattr(mcp_server, "_write_open_link_fields_by_label", fake_open_link_write)
    scenario = {
        "name": "create-contract",
        "steps": [
            {
                "kind": "open_create_form",
                "name": "create",
                "marker": "ДоговорыКонтрагентов",
                "params": {
                    "object_type": "элемент справочника",
                    "open_link": "e1cib/data/Справочник.ДоговорыКонтрагентов?ref=owner-supplied",
                },
            },
            {
                "kind": "input_text",
                "name": "date",
                "marker": "ДатаДоговора",
                "params": {"new_value": "05.03.2026", "value_type": "date"},
            },
            {
                "kind": "input_text",
                "name": "number",
                "marker": "Номер",
                "params": {"new_value": "QA-001"},
            },
            {"kind": "click_button", "name": "save", "marker": "Записать"},
        ],
    }

    result = mcp_server.run_write_scenario_tool(scenario_json=scenario, display=":92")

    assert result["status"] == "failed"
    assert result["open_link"] == "e1cib/data/Справочник.ДоговорыКонтрагентов?ref=owner-supplied"
    assert result["write_mode"] == "open_link_label_xtest"
    assert captured["labels"] == ["ДатаДоговора", "Номер"]
    assert captured["values"] == ["05.03.2026", "QA-001"]
    assert captured["save"] is True
    assert captured["display"] == ":92"
    assert result["persistence_verification"]["status"] == "provider_gap"
    assert result["cleanup_verification"]["status"] == "missing"


def test_run_write_scenario_tool_persistence_and_cleanup_success(monkeypatch) -> None:
    def fake_open_link_write(**kwargs):
        return {
            "foregrounded": True,
            "all_targeted": True,
            "all_selected": True,
            "saved": True,
            "results": [
                {"label": "Контрагент", "targeted": True, "selected": True, "field_mode": "reference"},
                {"label": "Description", "targeted": True},
            ],
            "screenshot": "create.png",
        }

    monkeypatch.setattr(mcp_server, "_write_open_link_fields_by_label", fake_open_link_write)
    scenario = {
        "name": "create-contract",
        "steps": [
            {
                "kind": "input_text",
                "name": "owner",
                "marker": "Владелец",
                "params": {"new_value": "Корнет ЗАО", "field_mode": "reference"},
            },
            {
                "kind": "input_text",
                "name": "description",
                "marker": "Description",
                "params": {"new_value": "QA-DEMO-1"},
            },
            {"kind": "click_button", "name": "save", "marker": "Записать"},
        ],
    }
    persistence = {
        "ok": True,
        "status": "verified",
        "route": "data_assertion",
        "artifact_path": ".artifacts/openspec/change/run/data-assertion.json",
        "created_records": [{"Ref_Key": "first"}, {"Ref_Key": "second"}],
        "assertions": [
            {"contract": "first-contract", "field": "Наименование", "expected": "QA-DEMO-1", "actual": "QA-DEMO-1", "ok": True},
            {"contract": "first-contract", "field": "Основной", "expected": False, "actual": False, "ok": True},
            {"contract": "second-contract", "field": "Наименование", "expected": "QA-DEMO-2", "actual": "QA-DEMO-2", "ok": True},
            {"contract": "second-contract", "field": "Основной", "expected": False, "actual": False, "ok": True},
        ],
    }
    cleanup = {
        "ok": True,
        "status": "restored",
        "route": "infobase_snapshot_restore",
        "artifact_path": ".artifacts/openspec/change/run/cleanup-summary.json",
        "unresolved_leftovers": [],
        "final_state": {"contract_count": 0},
    }

    result = mcp_server.run_write_scenario_tool(
        scenario_json=scenario,
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        persistence_verification_json=json.dumps(persistence, ensure_ascii=False),
        cleanup_evidence_json=json.dumps(cleanup, ensure_ascii=False),
        require_cleanup=True,
    )

    assert result["status"] == "passed"
    assert result["persistence_verification"]["status"] == "verified"
    assert result["cleanup_verification"]["status"] == "restored"
    contracts = result["persistence_verification"]["contract_assertions"]
    assert contracts[0]["contract"] == "first-contract"
    assert contracts[0]["assertions"]["Наименование"]["actual"] == "QA-DEMO-1"
    assert contracts[0]["assertions"]["Основной"]["actual"] is False
    assert contracts[1]["contract"] == "second-contract"
    assert contracts[1]["assertions"]["Наименование"]["actual"] == "QA-DEMO-2"
    assert contracts[1]["assertions"]["Основной"]["actual"] is False


def test_run_write_scenario_tool_persistence_failure_blocks_save_claim(monkeypatch) -> None:
    def fake_open_link_write(**kwargs):
        return {
            "foregrounded": True,
            "all_targeted": True,
            "all_selected": True,
            "saved": True,
            "results": [{"label": "Description", "targeted": True}],
            "screenshot": "create.png",
        }

    monkeypatch.setattr(mcp_server, "_write_open_link_fields_by_label", fake_open_link_write)
    persistence = {
        "ok": False,
        "status": "assertion_failed",
        "reason": "created record was not found",
        "assertions": [{"contract": "first-contract", "field": "Наименование", "expected": "QA", "actual": None, "ok": False}],
    }
    cleanup = {"ok": True, "status": "restored", "unresolved_leftovers": []}

    result = mcp_server.run_write_scenario_tool(
        scenario_json={
            "name": "create-contract",
            "steps": [
                {"kind": "input_text", "name": "description", "marker": "Description", "params": {"new_value": "QA"}},
                {"kind": "click_button", "name": "save", "marker": "Записать"},
            ],
        },
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        persistence_verification_json=json.dumps(persistence, ensure_ascii=False),
        cleanup_evidence_json=json.dumps(cleanup, ensure_ascii=False),
    )

    assert result["status"] == "failed"
    assert result["persistence_verification"]["status"] == "assertion_failed"
    verification_step = next(step for step in result["steps"] if step["name"] == "persistence verification")
    assert verification_step["status"] == "assert_failed"


def test_run_write_scenario_tool_cleanup_required_failure(monkeypatch) -> None:
    def fake_open_link_write(**kwargs):
        return {
            "foregrounded": True,
            "all_targeted": True,
            "all_selected": True,
            "saved": True,
            "results": [{"label": "Description", "targeted": True}],
            "screenshot": "create.png",
        }

    monkeypatch.setattr(mcp_server, "_write_open_link_fields_by_label", fake_open_link_write)
    persistence = {
        "ok": True,
        "status": "verified",
        "assertions": [{"contract": "first-contract", "field": "Наименование", "expected": "QA", "actual": "QA", "ok": True}],
    }
    cleanup = {
        "ok": True,
        "status": "restored",
        "unresolved_leftovers": [{"Description": "QA-leftover"}],
    }

    result = mcp_server.run_write_scenario_tool(
        scenario_json={
            "name": "create-contract",
            "steps": [
                {"kind": "input_text", "name": "description", "marker": "Description", "params": {"new_value": "QA"}},
                {"kind": "click_button", "name": "save", "marker": "Записать"},
            ],
        },
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        persistence_verification_json=json.dumps(persistence, ensure_ascii=False),
        cleanup_evidence_json=json.dumps(cleanup, ensure_ascii=False),
        require_cleanup=True,
    )

    assert result["status"] == "failed"
    assert result["cleanup_verification"]["status"] == "restored"
    assert result["cleanup_verification"]["ok"] is False
    assert result["cleanup_verification"]["unresolved_leftovers"] == [{"Description": "QA-leftover"}]


def test_run_write_scenario_tool_open_link_reference_field(monkeypatch) -> None:
    captured: dict = {}

    def fake_open_link_write(**kwargs):
        captured.update(kwargs)
        return {
            "foregrounded": True,
            "all_targeted": True,
            "all_selected": True,
            "saved": False,
            "results": [
                {
                    "label": "Контрагент",
                    "value": "Корнет ЗАО",
                    "targeted": True,
                    "selected": True,
                    "field_mode": "reference",
                    "click_xy": [10, 20],
                    "selection_screenshot": "select.png",
                },
            ],
            "screenshot": "create.png",
        }

    monkeypatch.setattr(mcp_server, "_write_open_link_fields_by_label", fake_open_link_write)
    scenario = {
        "name": "select-owner",
        "steps": [
            {
                "kind": "open_create_form",
                "name": "create",
                "marker": "ДоговорыКонтрагентов",
                "params": {"object_type": "элемент справочника"},
            },
            {
                "kind": "input_text",
                "name": "owner",
                "marker": "Владелец",
                "params": {"new_value": "Корнет ЗАО", "field_mode": "reference"},
            },
        ],
    }

    result = mcp_server.run_write_scenario_tool(
        scenario_json=scenario,
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        display=":92",
    )

    assert result["status"] == "passed"
    # card 125: the owner field is targeted by its real live label «Владелец» (demo10413), not the retired
    # vanessa-only «Контрагент» alias which has been removed.
    assert captured["labels"] == ["Владелец"]
    assert captured["values"] == ["Корнет ЗАО"]
    assert captured["field_modes"] == ["reference"]
    owner_step = next(step for step in result["steps"] if step["name"] == "owner")
    assert owner_step["status"] == "ok"
    assert "form_field_reference" in owner_step["preview"]
    assert owner_step["attachments"] == ["select.png", "create.png"]


def test_run_write_scenario_tool_reference_failure_blocks_save(monkeypatch) -> None:
    def fake_open_link_write(**kwargs):
        return {
            "foregrounded": True,
            "all_targeted": True,
            "all_selected": False,
            "saved": False,
            "save_blocked_reason": "not all fields were targeted and selected",
            "results": [
                {
                    "label": "Контрагент",
                    "value": "Unknown owner",
                    "targeted": True,
                    "selected": False,
                    "field_mode": "reference",
                    "reason": "requested reference value not visible after input",
                },
            ],
            "screenshot": "create.png",
        }

    monkeypatch.setattr(mcp_server, "_write_open_link_fields_by_label", fake_open_link_write)
    scenario = {
        "name": "select-owner",
        "steps": [
            {
                "kind": "input_text",
                "name": "owner",
                "marker": "Владелец",
                "params": {"new_value": "Unknown owner", "field_mode": "reference"},
            },
            {"kind": "click_button", "name": "save", "marker": "Записать"},
        ],
    }

    result = mcp_server.run_write_scenario_tool(
        scenario_json=scenario,
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        display=":92",
    )

    assert result["status"] == "failed"
    owner_step = next(step for step in result["steps"] if step["name"] == "owner")
    save_step = [step for step in result["steps"] if step["name"] == "save"][-1]
    assert owner_step["status"] == "error"
    assert save_step["status"] == "error"
    assert "not all fields were targeted and selected" in save_step["error"]


def test_run_write_scenario_tool_choice_field_does_not_require_selection(monkeypatch) -> None:
    captured: dict = {}

    def fake_open_link_write(**kwargs):
        captured.update(kwargs)
        return {
            "foregrounded": True,
            "all_targeted": True,
            "all_selected": True,
            "saved": True,
            "results": [
                {"label": "Вид договора", "value": "Продажа", "targeted": True, "field_mode": "choice"},
            ],
            "screenshot": "create.png",
        }

    monkeypatch.setattr(mcp_server, "_write_open_link_fields_by_label", fake_open_link_write)
    scenario = {
        "name": "set-choice",
        "steps": [
            {
                "kind": "input_text",
                "name": "contract kind",
                "marker": "Вид договора",
                "params": {"new_value": "Продажа", "field_mode": "choice"},
            },
        ],
    }

    result = mcp_server.run_write_scenario_tool(
        scenario_json=scenario,
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        save=False,
    )

    assert result["status"] == "passed"
    assert captured["field_modes"] == ["choice"]
    step = next(step for step in result["steps"] if step["name"] == "contract kind")
    assert step["status"] == "ok"
    assert "form_field_choice" in step["preview"]


def test_normalize_data_ref_link_encodes_dashed_ref() -> None:
    # A natural ?ref=<dashed Ref_Key> link is re-encoded to the e1cib hex token (card 99); other links untouched.
    norm = mcp_server._normalize_data_ref_link
    assert (
        norm("e1cib/data/Справочник.Товары?ref=a7a30aaf-321b-11dd-8d3a-000d8843cd1b")
        == "e1cib/data/Справочник.Товары?ref=8d3a000d8843cd1b11dd321ba7a30aaf"
    )
    # already-encoded hex is idempotent; list links and bad refs pass through unchanged
    enc = "e1cib/data/Справочник.Товары?ref=8d3a000d8843cd1b11dd321ba7a30aaf"
    assert norm(enc) == enc
    assert norm("e1cib/list/Справочник.Товары") == "e1cib/list/Справочник.Товары"
    assert norm("e1cib/data/Справочник.Товары?ref=garbage") == "e1cib/data/Справочник.Товары?ref=garbage"


def test_bare_create_data_link_classifier_keeps_record_and_list_links_out() -> None:
    is_create = mcp_server._is_bare_create_data_link
    assert is_create("e1cib/data/Справочник.Валюты") is True
    assert is_create("e1cib/data/Документ.Заказ") is True
    assert is_create("e1cib/data/Справочник.Валюты?ref=8d3a000d8843cd1b11dd321ba7a30aaf") is False
    assert is_create("e1cib/list/Справочник.Валюты") is False
    assert is_create("e1cib/app/Обработка.Печать") is False


def test_splice_window_activate_command_targets_resolved_form() -> None:
    header = b"prefix\xcb\x23\x95old-body"
    frame = mcp_server._splice_window_activate_command(
        header,
        "11111111-1111-1111-1111-111111111111",
    )

    assert frame.startswith(b"prefix\xcb\x23\x95")
    assert b"old-body" not in frame
    assert b"SecondaryFrame[11111111-1111-1111-1111-111111111111]" in frame
    assert b"ManagedForm[" not in frame
    assert b"CommandPanel" not in frame
    assert b"\x88\x82\x81" in frame


def test_open_link_visible_label_uses_live_field_name_no_alias() -> None:
    # card 125 — the owner/reference label is the requested field name (the live on-screen label), with no
    # baked-in config-specific alias. On demo10413 the owner field «Владелец» resolves to «Владелец», NOT the
    # retired vanessa «Контрагент»; and no fixture-specific owner-label constant remains.
    assert mcp_server._open_link_visible_label(
        "e1cib/data/Справочник.ДоговорыКонтрагентов", "Владелец", "reference") == "Владелец"
    assert mcp_server._open_link_visible_label(
        "e1cib/data/Справочник.Валюты", "Код", "text") == "Код"


def test_mcp_date_normalizer_uses_shared_scenario_parser() -> None:
    assert mcp_server._normalize_form_date(" 02.07.2026 ") == "02.07.2026"
    with pytest.raises(ValueError, match="date must be DD.MM.YYYY"):
        mcp_server._normalize_form_date("2026-07-02")


def test_write_form_fields_by_label_date_mode_types_digits_into_mask(monkeypatch) -> None:
    # card 125 — field_mode="date" clicks the input MASK (date_input_offset, NOT the default input_offset
    # that lands on the calendar button) and types the date as DIGIT keys, never the dotted string via type_text.
    events: dict[str, object] = {"keys": [], "type_text_called": False}

    class Resource:
        def close(self):
            pass

    class Backend:
        def send_keys(self, keys, *, display):
            events["keys"].append(list(keys))

        def capture_screenshot(self, display, path):
            path.write_bytes(b"png")

        def click(self, x, y, *, display):
            events["click"] = (x, y)

        def type_text(self, value, *, display, unicode):
            events["type_text_called"] = True

    def fake_create(open_link, *, host, port):
        return Resource(), {"foreground_method": "create_listreplay", "partial_foreground_replay": True}

    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: Backend())
    monkeypatch.setattr(mcp_server, "_open_bare_create_form_for_write", fake_create)
    monkeypatch.setattr(mcp_server, "_read_open_form_field_values",
                        lambda **kw: {"opened": None, "fields": {}, "field_count": 0})
    import qa_mcp.protocol.native_xtest as native_xtest
    monkeypatch.setattr(native_xtest, "locate_text", lambda path, text, **kw: (200, 300))

    result = mcp_server.write_form_fields_by_label(
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        labels=["Дата договора"], values=["30.06.2026"], field_modes=["date"],
        display=":92", input_offset=170, date_input_offset=90, settle_sec=0.0,
    )

    assert result["all_targeted"] is True
    # clicked into the mask at label_x + date_input_offset (90), NOT + input_offset (170 -> the calendar button)
    assert events["click"] == (200 + 90, 300)
    # typed the date as digit keys (no dots), not via type_text
    assert ["3", "0", "0", "6", "2", "0", "2", "6"] in events["keys"]
    assert events["type_text_called"] is False


def test_write_form_fields_by_label_two_pass_clicks_shared_input_column(monkeypatch) -> None:
    # card 125 #2 — a short reference label like «Владелец» and a short «Код» must click into the SAME right-aligned
    # input column (rightmost located label edge + gap), not each label-center + input_offset (which under-reaches
    # for a short label and lands in a neighbour). Two labels locate at different right edges; both click at
    # max(right)+gap.
    clicks: list[tuple[int, int]] = []

    class Resource:
        def close(self):
            pass

    class Backend:
        def send_keys(self, keys, *, display):
            pass

        def capture_screenshot(self, display, path):
            path.write_bytes(b"png")

        def click(self, x, y, *, display):
            clicks.append((x, y))

        def type_text(self, value, *, display, unicode):
            pass

    def fake_create(open_link, *, host, port):
        return Resource(), {"foreground_method": "create_listreplay", "partial_foreground_replay": True}

    boxes = {"Владелец": (100, 300, 80), "Код": (100, 340, 40)}  # (center_x, center_y, width) -> right = cx + w//2

    def fake_locate(path, text, *, diag=None, **kw):
        base = text.rstrip(":")
        if base not in boxes:
            return None
        cx, cy, w = boxes[base]
        if diag is not None:
            diag["box"] = {"cx": cx, "cy": cy, "w": w, "left": cx - w // 2, "right": cx + w // 2}
        return (cx, cy)

    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: Backend())
    monkeypatch.setattr(mcp_server, "_open_bare_create_form_for_write", fake_create)
    monkeypatch.setattr(mcp_server, "_read_open_form_field_values",
                        lambda **kw: {"opened": None, "fields": {}, "field_count": 0})
    import qa_mcp.protocol.native_xtest as native_xtest
    monkeypatch.setattr(native_xtest, "locate_text", fake_locate)

    result = mcp_server.write_form_fields_by_label(
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        labels=["Владелец", "Код"], values=["Корнет ЗАО", "QA-001"],
        field_modes=["text", "text"], display=":92", input_offset=170, input_column_gap=24, settle_sec=0.0,
    )

    # rightmost edge = 140 (Владелец: 100 + 80//2); column = 140 + 24 = 164; both fields click that column at their y
    assert clicks == [(164, 300), (164, 340)]
    assert [r["geometry"] for r in result["results"]] == ["input_column", "input_column"]
    assert result["all_targeted"] is True


def test_write_form_fields_by_label_committed_only_when_read_back(monkeypatch) -> None:
    # card 125 #4 — committed is TRUE only when the requested value is read back from the open form model, not merely
    # because the label was targeted on screen (the old false positive). OData cannot verify a test-client-held base.
    class Resource:
        def close(self):
            pass

    class Backend:
        def send_keys(self, keys, *, display):
            pass

        def capture_screenshot(self, display, path):
            path.write_bytes(b"png")

        def click(self, x, y, *, display):
            pass

        def type_text(self, value, *, display, unicode):
            pass

    def fake_create(open_link, *, host, port):
        return Resource(), {"foreground_method": "create_listreplay", "partial_foreground_replay": True}

    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: Backend())
    monkeypatch.setattr(mcp_server, "_open_bare_create_form_for_write", fake_create)
    import qa_mcp.protocol.native_xtest as native_xtest
    monkeypatch.setattr(native_xtest, "locate_text",
                        lambda path, text, **kw: (20, 40) if text.rstrip(":") == "Наименование" else None)

    # value read back -> committed True
    monkeypatch.setattr(mcp_server, "_read_open_form_field_values",
                        lambda **kw: {"opened": "Договор (создание)", "fields": {"Наименование": "QA-TEST"},
                                      "field_count": 1})
    ok = mcp_server.write_form_fields_by_label(
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        labels=["Наименование"], values=["QA-TEST"], display=":92", settle_sec=0.0,
    )
    assert ok["results"][0]["committed"] is True
    assert ok["results"][0]["readback_value"] == "QA-TEST"
    assert ok["all_committed"] is True
    assert ok["readback"]["verified"] is True

    # value NOT read back -> committed False even though the label was targeted
    monkeypatch.setattr(mcp_server, "_read_open_form_field_values",
                        lambda **kw: {"opened": "Договор (создание)", "fields": {"Наименование": "ОТЛИЧАЕТСЯ"},
                                      "field_count": 1})
    bad = mcp_server.write_form_fields_by_label(
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        labels=["Наименование"], values=["QA-TEST"], display=":92", settle_sec=0.0,
    )
    assert bad["results"][0]["targeted"] is True
    assert bad["results"][0]["committed"] is False
    assert bad["all_committed"] is False

    # stale text prefix is not a commit: "123" must not verify an existing "123456".
    monkeypatch.setattr(mcp_server, "_read_open_form_field_values",
                        lambda **kw: {"opened": "Договор (создание)", "fields": {"Наименование": "123456"},
                                      "field_count": 1})
    prefix = mcp_server.write_form_fields_by_label(
        open_link="e1cib/data/Справочник.ДоговорыКонтрагентов",
        labels=["Наименование"], values=["123"], display=":92", settle_sec=0.0,
    )
    assert prefix["results"][0]["targeted"] is True
    assert prefix["results"][0]["committed"] is False
    assert prefix["all_committed"] is False


def test_label_locate_retry_methods_match_production_foregrounds() -> None:
    assert mcp_server._should_retry_label_locate("create_listreplay", 0, None) is True
    assert mcp_server._should_retry_label_locate("listreplay", 0, None) is True
    assert mcp_server._should_retry_label_locate("create_splice", 0, None) is False
    assert mcp_server._should_retry_label_locate("create_listreplay", 1, None) is False
    assert mcp_server._should_retry_label_locate("create_listreplay", 0, (20, 40)) is False


def test_write_form_fields_by_label_retries_first_create_screenshot_miss(monkeypatch) -> None:
    calls: dict[str, object] = {"activate": 0, "closed": False, "shots": []}

    class Resource:
        def activate(self):
            calls["activate"] = int(calls["activate"]) + 1
            return {"accepted": True}

        def close(self):
            calls["closed"] = True

    class Backend:
        def send_keys(self, keys, *, display):
            pass

        def capture_screenshot(self, display, path):
            calls["shots"].append(path.name)
            path.write_bytes(b"png")

        def click(self, x, y, *, display):
            calls["click"] = (x, y)

        def type_text(self, value, *, display, unicode):
            calls["typed"] = (value, display, unicode)

    def fake_create(open_link, *, host, port):
        return Resource(), {"foreground_method": "create_listreplay", "partial_foreground_replay": True}

    def fake_locate(path, text, *, diag=None, **kw):
        if text.rstrip(":") != "Наименование":
            return None
        if "retry" not in path:
            return None
        if diag is not None:
            diag["box"] = {"cx": 20, "cy": 40, "w": 60, "left": -10, "right": 50}
        return (20, 40)

    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: Backend())
    monkeypatch.setattr(mcp_server, "_open_bare_create_form_for_write", fake_create)
    monkeypatch.setattr(mcp_server, "_read_open_form_field_values",
                        lambda **kw: {"opened": None, "fields": {}, "field_count": 0})
    import qa_mcp.protocol.native_xtest as native_xtest
    monkeypatch.setattr(native_xtest, "locate_text", fake_locate)

    result = mcp_server.write_form_fields_by_label(
        open_link="e1cib/data/Справочник.Валюты",
        labels=["Наименование"],
        values=["QA"],
        display=":92",
        settle_sec=0.0,
    )

    assert calls["activate"] == 1
    assert "locate-00-retry.png" in calls["shots"]
    assert result["all_targeted"] is True
    assert result["results"][0]["activation_retry"] == "protocol_window_command"
    assert result["activation_result"] == {"accepted": True}
    assert calls["typed"] == ("QA", ":92", True)
    assert calls["closed"] is True


def test_value_matches_readback_verifies_by_value_presence() -> None:
    # card 125 #4 — a write is verified by VALUE equivalence in the form value-read
    # (the writer targets by on-screen LABEL, whose name differs from the descriptor field name).
    assert mcp_server._value_matches_readback("Корнет ЗАО", ["Корнет ЗАО"]) == "Корнет ЗАО"  # reference presentation
    assert mcp_server._value_matches_readback("30.06.2026", ["30.06.2026"]) == "30.06.2026"  # date
    assert mcp_server._value_matches_readback("QA-001", ["ДРУГОЕ", "QA-001"]) == "QA-001"     # among several fields
    # date echoed with a time suffix -> matched by the read-back value starting with the requested date
    assert mcp_server._value_matches_readback("30.06.2026", ["30.06.2026 0:00:00"]) == "30.06.2026 0:00:00"
    # reference prefix matching is opt-in by field mode; ordinary text must not accept a stale prefix value
    assert mcp_server._value_matches_readback("Кор", ["Корнет ЗАО"], allow_prefix=True) == "Корнет ЗАО"
    assert mcp_server._value_matches_readback("123", ["123456"]) is None
    assert mcp_server._value_matches_readback("QA-TEST", ["Совсем другое"]) is None           # absent -> unverified
    assert mcp_server._value_matches_readback("", ["x"]) is None                              # trivially-short guard
    # review fix (no false positives): a requested value that only appears as a substring INSIDE an unrelated value,
    # or a short read-back value that is a substring of the requested value, must NOT match.
    assert mcp_server._value_matches_readback("С поставщиком", ["Договор с поставщиком №5"]) is None  # not a prefix
    assert mcp_server._value_matches_readback("QA-001", ["00"]) is None                              # no backward match


def test_readback_verification_matches_own_field_not_whole_form() -> None:
    # card 125 #4 review fix — a FAILED field must not borrow an unrelated committed field's value. Each label maps
    # to its OWN read-back field («Номер договора» -> НомерДоговора by space-normalization); a failed enum value that
    # is a substring of the committed Наименование is NOT reported committed.
    results = [
        {"label": "Наименование", "value": "Договор с поставщиком №5", "targeted": True},
        {"label": "Вид договора", "value": "С поставщиком", "targeted": True},   # did NOT commit (empty own value)
        {"label": "Номер договора", "value": "QA-001", "targeted": True},
    ]
    readback = {"Наименование": "Договор с поставщиком №5", "ВидДоговора": "", "НомерДоговора": "QA-001"}
    mcp_server._apply_readback_verification(results, readback)
    by_label = {r["label"]: r for r in results}
    assert by_label["Наименование"]["committed"] is True
    assert by_label["Номер договора"]["committed"] is True    # space-normalized label resolves to НомерДоговора
    assert by_label["Вид договора"]["committed"] is False     # own value empty; NOT borrowed from Наименование
    assert by_label["Вид договора"]["readback_value"] is None


def test_read_open_form_retries_past_cold_client_zero(monkeypatch) -> None:
    # card 125 #4 — the FIRST value-read on a freshly launched client enumerates the element tree but echoes empty
    # values (cold-client boundary: field_count 0 with element_count > 0); a retry on a fresh connection returns the
    # materialised values. The read helper retries until it reads a value.
    calls = {"n": 0}

    def fake_once(**kw):
        calls["n"] += 1
        if calls["n"] < 3:
            return {"opened": "Форма (создание)", "fields": {}, "field_count": 0, "element_count": 8}
        return {"opened": "Форма (создание)", "fields": {"Наименование": "QA"}, "field_count": 1, "element_count": 8}

    monkeypatch.setattr(mcp_server, "_read_open_form_once", fake_once)
    monkeypatch.setattr(mcp_server.time, "sleep", lambda *a, **k: None)

    res = mcp_server._read_open_form_field_values(host="127.0.0.1", port=15381, retries=4, retry_delay=0.0)
    assert res["field_count"] == 1
    assert res["fields"] == {"Наименование": "QA"}
    assert res["read_attempts"] == 3

    # exhausts retries and returns the last (empty) result honestly when the client never materialises values
    calls["n"] = 0
    monkeypatch.setattr(mcp_server, "_read_open_form_once",
                        lambda **kw: {"opened": "Форма", "fields": {}, "field_count": 0, "element_count": 8})
    exhausted = mcp_server._read_open_form_field_values(host="127.0.0.1", port=15381, retries=3, retry_delay=0.0)
    assert exhausted["field_count"] == 0
    assert exhausted["read_attempts"] == 3


def test_mark_odata_deprecated_is_additive() -> None:
    # card 125 #1 — OData tools annotate their result with a deprecation for a test-client-held base WITHOUT
    # changing the underlying ok/values (additive), pointing at the protocol value-read.
    marked = mcp_server._mark_odata_deprecated({"ok": True, "actual": "X", "record_count": 1})
    assert marked["ok"] is True and marked["actual"] == "X" and marked["record_count"] == 1
    assert marked["deprecated"] is True
    assert "exclusively locked" in marked["deprecation"] and "value-read" in marked["deprecation"]


def test_write_form_fields_by_label_uses_create_foreground_for_bare_data_link(monkeypatch) -> None:
    calls: dict[str, object] = {"closed": False}

    class Resource:
        def close(self):
            calls["closed"] = True

    class Backend:
        def send_keys(self, keys, *, display):
            pass

        def capture_screenshot(self, display, path):
            path.write_bytes(b"png")

        def click(self, x, y, *, display):
            calls["click"] = (x, y, display)

        def type_text(self, value, *, display, unicode):
            calls["typed"] = (value, display, unicode)

    def fake_create(open_link, *, host, port):
        calls["create"] = (open_link, host, port)
        return Resource(), {"foreground_method": "create_listreplay", "partial_foreground_replay": True}

    def fail_list_replay(*args, **kwargs):
        raise AssertionError("list replay must not be used for bare-create links")

    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: Backend())
    monkeypatch.setattr(mcp_server, "_open_bare_create_form_for_write", fake_create)
    monkeypatch.setattr(mcp_server, "_foreground_form_by_link", fail_list_replay)
    monkeypatch.setattr(mcp_server, "_read_open_form_field_values",
                        lambda **kw: {"opened": None, "fields": {}, "field_count": 0})
    import qa_mcp.protocol.native_xtest as native_xtest
    monkeypatch.setattr(native_xtest, "locate_text", lambda path, text, **kw: (20, 40) if text in {"Наименование:", "Наименование"} else None)

    result = mcp_server.write_form_fields_by_label(
        open_link="e1cib/data/Справочник.Валюты",
        labels=["Наименование"],
        values=["QA"],
        display=":92",
        host="127.0.0.1",
        port=15400,
    )

    assert result["foregrounded"] is True
    assert result["foreground_method"] == "create_listreplay"
    assert result["partial_foreground_replay"] is True
    assert result["all_targeted"] is True
    assert calls["create"] == ("e1cib/data/Справочник.Валюты", "127.0.0.1", 15400)
    assert calls["typed"] == ("QA", ":92", True)
    assert calls["closed"] is True


def test_open_bare_create_form_uses_partial_foreground_replay(monkeypatch) -> None:
    class Resource:
        pass

    calls: dict[str, object] = {}
    resource = Resource()

    def fake_foreground(open_link, **kwargs):
        calls["foreground"] = (open_link, kwargs)
        return resource

    monkeypatch.setattr(mcp_server, "_foreground_form_by_link", fake_foreground)

    result, meta = mcp_server._open_bare_create_form_for_write(
        "e1cib/data/Справочник.Валюты", host="127.0.0.1", port=15400,
    )

    assert result is resource
    assert meta["foreground_method"] == "create_listreplay"
    assert meta["partial_foreground_replay"] is True
    assert calls["foreground"][0] == "e1cib/data/Справочник.Валюты"
    assert calls["foreground"][1]["allow_partial"] is True


def test_write_form_fields_by_label_keeps_list_replay_for_record_links(monkeypatch) -> None:
    calls: dict[str, object] = {"closed": False}

    class Resource:
        def close(self):
            calls["closed"] = True

    class Backend:
        def send_keys(self, keys, *, display):
            pass

        def capture_screenshot(self, display, path):
            path.write_bytes(b"png")

        def click(self, x, y, *, display):
            pass

        def type_text(self, value, *, display, unicode):
            pass

    def fake_list_replay(open_link, *, host, port):
        calls["list_replay"] = (open_link, host, port)
        return Resource()

    def fail_create(*args, **kwargs):
        raise AssertionError("create foreground must not be used for record links")

    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: Backend())
    monkeypatch.setattr(mcp_server, "_foreground_form_by_link", fake_list_replay)
    monkeypatch.setattr(mcp_server, "_open_bare_create_form_for_write", fail_create)
    monkeypatch.setattr(mcp_server, "_read_open_form_field_values",
                        lambda **kw: {"opened": None, "fields": {}, "field_count": 0})
    import qa_mcp.protocol.native_xtest as native_xtest
    monkeypatch.setattr(native_xtest, "locate_text", lambda path, text, **kw: (20, 40))

    link = "e1cib/data/Справочник.Валюты?ref=8d3a000d8843cd1b11dd321ba7a30aaf"
    result = mcp_server.write_form_fields_by_label(
        open_link=link,
        labels=["Наименование"],
        values=["QA"],
        display=":92",
        host="127.0.0.1",
        port=15400,
    )

    assert result["foregrounded"] is True
    assert result["foreground_method"] == "listreplay"
    assert calls["list_replay"] == (link, "127.0.0.1", 15400)
    assert calls["closed"] is True

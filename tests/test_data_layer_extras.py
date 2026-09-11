"""Offline tests for the deeper data-layer (roadmap 111, item 7): count assertions + role/security matrix.

All offline via the ODataClient's injectable ``fetcher`` (no network), incl. simulating a 401 (access denied).
"""

from __future__ import annotations

import base64
import urllib.error

from qa_mcp import mcp_server
from qa_mcp.data import ODataClient, assert_data_count_value, role_data_matrix
from qa_mcp.scenario.model import Scenario
from qa_mcp.scenario.runner import ScenarioRunner


def _client_returning(n: int) -> ODataClient:
    rows = [{"Ref_Key": str(i)} for i in range(n)]
    return ODataClient("http://lab/odata", "Администратор", "", fetcher=lambda url, h: {"value": rows})


# --- count assertions ----------------------------------------------------------------------------------------

def test_count_records_counts_rows():
    assert _client_returning(3).count_records("Catalog_Банки") == 3
    assert _client_returning(0).count_records("Catalog_Банки") == 0


def test_assert_data_count_ops():
    c = _client_returning(5)
    assert assert_data_count_value(c, "Catalog_X", 5, op="eq")["ok"]
    assert assert_data_count_value(c, "Catalog_X", 0, op="gt")["ok"]
    assert assert_data_count_value(c, "Catalog_X", 10, op="lt")["ok"]
    assert assert_data_count_value(c, "Catalog_X", 5, op="ge")["ok"]
    assert assert_data_count_value(c, "Catalog_X", 5, op="le")["ok"]
    assert assert_data_count_value(c, "Catalog_X", 4, op="ne")["ok"]
    assert not assert_data_count_value(c, "Catalog_X", 6, op="eq")["ok"]


def test_assert_data_count_absence():
    res = assert_data_count_value(_client_returning(0), "Catalog_X", 0, op="eq", filter="Description eq 'Нет'")
    assert res["ok"] and res["count"] == 0


def test_assert_data_count_unknown_op_raises():
    import pytest
    with pytest.raises(ValueError):
        assert_data_count_value(_client_returning(1), "Catalog_X", 1, op="approx")


# --- role/security matrix ------------------------------------------------------------------------------------

def _role_fetcher(url, headers):
    """Fake OData: the 'restricted' user gets 401; everyone else reads 2 rows."""
    creds = base64.b64decode(headers.get("Authorization", "Basic Og==").split()[1]).decode()
    user = creds.split(":", 1)[0]
    if user == "restricted":
        raise urllib.error.HTTPError(url, 401, "Unauthorized", {}, None)
    return {"value": [{"Ref_Key": "a"}, {"Ref_Key": "b"}]}


def test_role_matrix_distinguishes_read_and_denied():
    res = role_data_matrix(
        "Catalog_Банки",
        [
            {"label": "admin", "user": "Администратор", "password": "", "expect_access": "read", "min_count": 1},
            {"label": "restricted", "user": "restricted", "password": "x", "expect_access": "denied"},
        ],
        base_url="http://lab/odata", fetcher=_role_fetcher,
    )
    assert res["ok"]
    by = {r["label"]: r for r in res["roles"]}
    assert by["admin"]["access"] == "read" and by["admin"]["count"] == 2 and by["admin"]["ok"]
    assert by["restricted"]["access"] == "denied" and by["restricted"]["http"] == 401 and by["restricted"]["ok"]


def test_role_matrix_fails_when_expectation_unmet():
    res = role_data_matrix(
        "Catalog_Банки",
        [{"label": "admin", "user": "Администратор", "password": "", "expect_access": "denied"}],  # wrong expectation
        base_url="http://lab/odata", fetcher=_role_fetcher,
    )
    assert not res["ok"] and res["roles"][0]["access"] == "read" and not res["roles"][0]["ok"]


def test_role_matrix_no_expectation_is_informational():
    res = role_data_matrix("Catalog_Банки", [{"label": "admin", "user": "Администратор", "password": ""}],
                           base_url="http://lab/odata", fetcher=_role_fetcher)
    assert res["ok"] and res["roles"][0]["ok"] and res["roles"][0]["access"] == "read"


# --- Gherkin + runner ----------------------------------------------------------------------------------------

def test_count_steps_transpile():
    f = ("Сценарий: s\n"
         "  Когда В базе 'Catalog_Товары' где \"Code ne ''\" количество записей больше 0\n"
         "  И В базе 'Catalog_Товары' где \"Description eq 'Нет'\" записей нет\n")
    out = mcp_server.transpile(feature_text=f)
    assert out["unmapped"] == []
    gt, absent = out["steps"][0], out["steps"][1]
    assert gt["kind"] == "assert_data_count" and gt["params"]["op"] == "gt" and gt["params"]["expected"] == 0
    assert absent["kind"] == "assert_data_count" and absent["params"]["op"] == "eq" and absent["params"]["expected"] == 0


def test_count_comparator_words():
    def op(line):
        return mcp_server.transpile(feature_text=f"Сценарий: s\n  Когда {line}\n")["steps"][0]["params"]["op"]
    base = "В базе 'C' где \"Code ne ''\" количество записей"
    assert op(f"{base} равно 3") == "eq"
    assert op(f"{base} меньше 3") == "lt"
    assert op(f"{base} не меньше 3") == "ge"
    assert op(f"{base} не больше 3") == "le"


def test_runner_executes_count_step(tmp_path):
    client = _client_returning(2)
    runner = ScenarioRunner(session_factory=lambda: None, bootstrap=object(), templates=object(),
                            output_dir=tmp_path, odata_client=client)
    sc = Scenario.from_dict({"name": "s", "steps": [
        {"kind": "assert_data_count", "name": "count>0",
         "params": {"entity_set": "Catalog_Банки", "filter": "", "op": "gt", "expected": 0}},
    ]})
    res = runner.run(sc)
    assert res.steps[0].status == "ok" and res.status == "passed"

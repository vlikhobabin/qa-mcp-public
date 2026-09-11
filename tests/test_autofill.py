"""Card 106 change 4 (write side) — metadata-driven required-field autofill (offline, self-contained mdo)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.scenario import (  # noqa: E402
    build_autofill_plan, create_fill_feature, enum_values_from_mdo, reference_entity_set, required_fields_from_mdo,
    resolve_enum_value, resolve_reference_value, smoke_value_for_type, transpile_feature,
)
from qa_mcp.data import ODataClient  # noqa: E402


def _fake_odata(records_by_set: dict) -> ODataClient:
    """An ODataClient whose fetch returns canned records keyed by entity set (offline ref resolution). The client
    percent-encodes the (Cyrillic) entity set in the URL, so match on the encoded form."""
    import urllib.parse

    def fetch(url: str, _headers: dict) -> dict:
        for es, recs in records_by_set.items():
            if urllib.parse.quote(es) in url:
                return {"value": recs}
        return {"value": []}

    return ODataClient(base_url="http://lab/odata", fetcher=fetch)

# a minimal EDT .mdo (namespace on the root, unprefixed children — exactly the real shape) with: a required
# standard Description, a NON-required standard Code, a required custom String, a required custom reference, and a
# non-required custom String. Mirrors vanessa_client's Валюты (Description fillChecking=ShowError).
CATALOG_MDO = """<?xml version="1.0" encoding="UTF-8"?>
<mdclass:Catalog xmlns:mdclass="http://g5.1c.ru/v8/dt/metadata/mdclass" xmlns:core="http://g5.1c.ru/v8/dt/mcore">
  <name>Демо</name>
  <standardAttributes>
    <name>Description</name>
    <fillChecking>ShowError</fillChecking>
  </standardAttributes>
  <standardAttributes>
    <name>Code</name>
  </standardAttributes>
  <attributes uuid="x">
    <name>СтрокаОбяз</name>
    <type><types>String</types></type>
    <fillChecking>ShowError</fillChecking>
  </attributes>
  <attributes uuid="y">
    <name>КонтрагентОбяз</name>
    <type><types>CatalogRef.Контрагенты</types></type>
    <fillChecking>ShowError</fillChecking>
  </attributes>
  <attributes uuid="z">
    <name>НеОбяз</name>
    <type><types>String</types></type>
  </attributes>
</mdclass:Catalog>
"""

DOC_MDO = """<?xml version="1.0"?>
<mdclass:Document xmlns:mdclass="http://g5.1c.ru/v8/dt/metadata/mdclass">
  <name>Заказ</name>
  <standardAttributes>
    <name>Date</name>
    <fillChecking>ShowError</fillChecking>
  </standardAttributes>
  <standardAttributes>
    <name>Number</name>
  </standardAttributes>
  <attributes uuid="a">
    <name>Контрагент</name>
    <type><types>CatalogRef.Контрагенты</types></type>
    <fillChecking>ShowError</fillChecking>
  </attributes>
</mdclass:Document>
"""


def test_smoke_value_for_type() -> None:
    assert smoke_value_for_type("String") == "QASMOKE"
    assert smoke_value_for_type("Number") == "1"
    assert smoke_value_for_type("Boolean") == "Истина"
    assert smoke_value_for_type("Date") == "01.01.2030"
    # references / unknown -> not auto-fillable
    assert smoke_value_for_type("CatalogRef.Контрагенты") is None
    assert smoke_value_for_type("DocumentRef.Заказ") is None
    assert smoke_value_for_type("") is None


def test_required_fields_catalog() -> None:
    fields = required_fields_from_mdo(CATALOG_MDO)
    by_name = {f.name: f for f in fields}
    # only fillChecking=ShowError attributes; standard Description -> Наименование
    assert set(by_name) == {"Наименование", "СтрокаОбяз", "КонтрагентОбяз"}
    assert by_name["Наименование"].standard is True
    assert by_name["Наименование"].type == "String" and by_name["Наименование"].value == "QASMOKE"
    assert by_name["СтрокаОбяз"].standard is False and by_name["СтрокаОбяз"].fillable is True
    # a required reference is reported but not auto-fillable
    assert by_name["КонтрагентОбяз"].type == "CatalogRef.Контрагенты"
    assert by_name["КонтрагентОбяз"].value is None and by_name["КонтрагентОбяз"].fillable is False
    # Code (no fillChecking) and НеОбяз (no fillChecking) are NOT required
    assert "Код" not in by_name and "НеОбяз" not in by_name


def test_required_fields_document_date() -> None:
    fields = {f.name: f for f in required_fields_from_mdo(DOC_MDO)}
    assert set(fields) == {"Дата", "Контрагент"}
    assert fields["Дата"].type == "Date" and fields["Дата"].value == "01.01.2030"
    assert fields["Контрагент"].fillable is False  # reference


def test_build_autofill_plan() -> None:
    plan = build_autofill_plan(CATALOG_MDO, "Справочник", "Демо")
    assert plan["object"] == "Справочник.Демо"
    assert plan["create_link"] == "e1cib/data/Справочник.Демо"
    assert [f["name"] for f in plan["fillable"]] == ["Наименование", "СтрокаОбяз"]
    assert [f["name"] for f in plan["unfillable"]] == ["КонтрагентОбяз"]


def test_create_fill_feature_transpiles_100_percent() -> None:
    fields = required_fields_from_mdo(CATALOG_MDO)
    feature = create_fill_feature("элемент справочника", "Демо", fields)
    results = transpile_feature(feature)
    assert len(results) == 1
    r = results[0]
    assert r.unmapped == [], r.unmapped
    # open the create form, then one input_text per FILLABLE field (the reference is skipped)
    assert [s.kind for s in r.scenario.steps] == ["open_create_form", "input_text", "input_text"]
    assert r.scenario.steps[1].marker == "Наименование"
    assert r.scenario.steps[1].params["new_value"] == "QASMOKE"


def test_reference_entity_set() -> None:
    assert reference_entity_set("CatalogRef.Контрагенты") == "Catalog_Контрагенты"
    assert reference_entity_set("DocumentRef.Заказ") == "Document_Заказ"
    assert reference_entity_set("EnumRef.СостоянияЗаказов") is None  # enums aren't OData sets
    assert reference_entity_set("String") is None
    assert reference_entity_set("") is None


def test_resolve_reference_value() -> None:
    client = _fake_odata({"Catalog_Контрагенты": [{"Description": "ООО Ромашка", "Code": "000001"}]})
    assert resolve_reference_value("CatalogRef.Контрагенты", client) == "ООО Ромашка"
    # document presentation falls back to Number when no Description
    docs = _fake_odata({"Document_Заказ": [{"Number": "00-0001", "Date": "2026-01-01T00:00:00"}]})
    assert resolve_reference_value("DocumentRef.Заказ", docs) == "00-0001"
    # empty set / enum / no client -> None
    assert resolve_reference_value("CatalogRef.Пусто", _fake_odata({})) is None
    assert resolve_reference_value("EnumRef.X", client) is None
    assert resolve_reference_value("CatalogRef.X", None) is None


def test_build_autofill_plan_resolves_references() -> None:
    # the catalog mdo has a required CatalogRef.Контрагенты — with an OData client it becomes fillable (odata-ref)
    client = _fake_odata({"Catalog_Контрагенты": [{"Description": "ООО Ромашка"}]})
    plan = build_autofill_plan(CATALOG_MDO, "Справочник", "Демо", odata_client=client)
    by_name = {r["name"]: r for r in plan["required"]}
    assert by_name["Наименование"]["source"] == "synthesized"
    assert by_name["КонтрагентОбяз"]["fillable"] is True
    assert by_name["КонтрагентОбяз"]["value"] == "ООО Ромашка"
    assert by_name["КонтрагентОбяз"]["source"] == "odata-ref"
    assert [f["name"] for f in plan["fillable"]] == ["Наименование", "СтрокаОбяз", "КонтрагентОбяз"]
    assert plan["unfillable"] == []
    # the generated feature now fills the reference too
    feature = create_fill_feature("элемент справочника", "Демо", plan["fillable"])
    r = transpile_feature(feature)[0]
    assert r.unmapped == []
    assert [s.kind for s in r.scenario.steps] == ["open_create_form", "input_text", "input_text", "input_text"]


def test_build_autofill_plan_without_odata_leaves_refs_unfillable() -> None:
    # backward-compat: no odata_client -> references stay unfillable (as before the follow-on)
    plan = build_autofill_plan(CATALOG_MDO, "Справочник", "Демо")
    assert [f["name"] for f in plan["unfillable"]] == ["КонтрагентОбяз"]


ENUM_MDO = """<?xml version="1.0"?>
<mdclass:Enum xmlns:mdclass="http://g5.1c.ru/v8/dt/metadata/mdclass">
  <name>СостоянияЗаказов</name>
  <standardAttributes><name>Ref</name></standardAttributes>
  <enumValues uuid="1"><name>Открыт</name><synonym><key>ru</key><value>Открыт</value></synonym></enumValues>
  <enumValues uuid="2"><name>ВРаботе</name><synonym><key>ru</key><value>В работе</value></synonym></enumValues>
  <enumValues uuid="3"><name>Закрыт</name></enumValues>
</mdclass:Enum>
"""


def test_enum_values_from_mdo() -> None:
    vals = enum_values_from_mdo(ENUM_MDO)
    assert [v["name"] for v in vals] == ["Открыт", "ВРаботе", "Закрыт"]
    assert vals[1]["synonym"] == "В работе"
    assert vals[2]["synonym"] is None  # no synonym -> falls back to name elsewhere


def test_resolve_enum_value() -> None:
    provider = lambda n: ENUM_MDO if n == "СостоянияЗаказов" else None  # noqa: E731
    assert resolve_enum_value("EnumRef.СостоянияЗаказов", provider) == "Открыт"  # first value's synonym
    assert resolve_enum_value("EnumRef.Нет", provider) is None
    assert resolve_enum_value("CatalogRef.X", provider) is None  # not an enum
    assert resolve_enum_value("EnumRef.X", None) is None


def test_build_autofill_plan_resolves_enum() -> None:
    # a document mdo with a required EnumRef -> resolved via the enum provider (source="enum")
    doc = DOC_MDO.replace(
        '<attributes uuid="a">\n    <name>Контрагент</name>\n    <type><types>CatalogRef.Контрагенты</types></type>\n'
        "    <fillChecking>ShowError</fillChecking>\n  </attributes>",
        '<attributes uuid="a"><name>Состояние</name><type><types>EnumRef.СостоянияЗаказов</types></type>'
        "<fillChecking>ShowError</fillChecking></attributes>")
    provider = lambda n: ENUM_MDO if n == "СостоянияЗаказов" else None  # noqa: E731
    plan = build_autofill_plan(doc, "Документ", "Заказ", enum_mdo_provider=provider)
    by_name = {r["name"]: r for r in plan["required"]}
    assert by_name["Состояние"]["value"] == "Открыт"
    assert by_name["Состояние"]["source"] == "enum"
    assert by_name["Состояние"]["fillable"] is True

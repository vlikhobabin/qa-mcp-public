"""Card 106 (E-XV) — metadata-driven smoke-test generation (offline)."""
from __future__ import annotations

from qa_mcp.scenario import (
    generate_smoke_feature, generate_smoke_scenarios, open_link_for, smoke_coverage, transpile_feature,
)

OBJECTS = [
    {"kind": "Справочник", "name": "Контрагенты"},
    {"kind": "Документ", "name": "Заказ"},
    {"kind": "Обработка", "name": "ЗакрытиеМесяца"},
    {"kind": "Отчёт", "name": "ОборотноСальдовая"},
    {"kind": "РегистрСведений", "name": "Курсы"},   # unsupported kind -> skipped
    {"kind": "Справочник", "name": ""},               # no name -> skipped
]


def test_open_link_for_known_and_unknown_kinds() -> None:
    assert open_link_for("Справочник", "Контрагенты") == "e1cib/list/Справочник.Контрагенты"
    assert open_link_for("Document", "Заказ") == "e1cib/list/Документ.Заказ"
    # reports + data processors open via e1cib/app/… (live-verified card 106; e1cib/command/… does not open)
    assert open_link_for("Обработка", "X") == "e1cib/app/Обработка.X"
    assert open_link_for("Отчёт", "ПрайсЛист") == "e1cib/app/Отчет.ПрайсЛист"
    assert open_link_for("РегистрСведений", "Курсы") is None


def test_generate_scenarios_skips_unsupported_and_nameless() -> None:
    scns = generate_smoke_scenarios(OBJECTS)
    assert [s["name"] for s in scns] == ["Контрагенты", "Заказ", "ЗакрытиеМесяца", "ОборотноСальдовая"]
    # each scenario opens the main form + reads the summary
    assert scns[0]["steps"] == ["Я открываю основную форму списка справочника 'Контрагенты'",
                                 "Я получаю сводку формы"]
    assert scns[0]["open_link"] == "e1cib/list/Справочник.Контрагенты"


def test_generated_feature_transpiles_100_percent() -> None:
    # the generator must only emit canonical steps -> zero unmapped (self-consistency with card 103)
    feature = generate_smoke_feature(OBJECTS)
    results = transpile_feature(feature)
    assert len(results) == 4  # 4 supported objects
    for r in results:
        assert r.unmapped == [], f"{r.scenario.name}: {r.unmapped}"
        assert [s.kind for s in r.scenario.steps] == ["open_main_form", "read_form_summary"]


def test_smoke_coverage_counts() -> None:
    cov = smoke_coverage(OBJECTS, opened={"Контрагенты", "Заказ"})
    assert cov["total"] == 6
    assert cov["supported"] == 4
    assert cov["covered"] == 2
    assert set(cov["missing"]) == {"ЗакрытиеМесяца", "ОборотноСальдовая"}
    assert "Курсы" in cov["unsupported"]

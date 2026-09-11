"""Card 106 (E-XV) — metadata-driven smoke-test generation.

Vanessa Automation requires hand-authored features. qa-mcp can ENUMERATE a configuration from metadata
(`meta-mcp` / the live descriptor) and auto-generate a runnable smoke suite — "does every form still open and
render?" — a capability beyond Vanessa. The generator is pure (takes a metadata listing), so it is unit-testable
offline; the live enumeration (meta-mcp) and execution (read_form_descriptor / run_scenario) are the orchestration
layer around it.

A listing entry is ``{"kind": <metadata kind>, "name": <object name>}`` (kind ru or en). The generated feature
uses the canonical card-103 steps, so it transpiles 100%.
"""
from __future__ import annotations

from typing import Any

# metadata kind (ru / en) -> (open-form step otype phrase, nav-link prefix).
# Link formats are LIVE-VERIFIED on vanessa_client (card 106 broadening, 2026-06-21): catalogs/documents open via
# `e1cib/list/…`; reports AND data processors open via `e1cib/app/…` (NOT `e1cib/command/…`, which does not open
# the form — it returned the bare main window). See evidence/card106-broaden-live-2026-06-21/.
_KINDS: dict[str, tuple[str, str]] = {
    "справочник": ("списка справочника", "e1cib/list/Справочник."),
    "catalog": ("списка справочника", "e1cib/list/Справочник."),
    "документ": ("документа", "e1cib/list/Документ."),
    "document": ("документа", "e1cib/list/Документ."),
    "обработка": ("обработки", "e1cib/app/Обработка."),
    "dataprocessor": ("обработки", "e1cib/app/Обработка."),
    "отчет": ("отчёта", "e1cib/app/Отчет."),
    "отчёт": ("отчёта", "e1cib/app/Отчет."),
    "report": ("отчёта", "e1cib/app/Отчет."),
}


def _norm_kind(kind: str) -> str:
    return (kind or "").strip().lower()


def open_link_for(kind: str, name: str) -> str | None:
    """Nav-link for a metadata object (for `read_form_descriptor(open_link=…)`), or None for an unknown kind."""
    entry = _KINDS.get(_norm_kind(kind))
    return f"{entry[1]}{name}" if entry else None


def _open_step(kind: str, name: str) -> str | None:
    entry = _KINDS.get(_norm_kind(kind))
    return f"Я открываю основную форму {entry[0]} '{name}'" if entry else None


def generate_smoke_scenarios(objects: list[dict[str, str]]) -> list[dict[str, Any]]:
    """One smoke entry per supported object: {kind, name, open_link, steps}. Unsupported kinds are skipped."""
    out: list[dict[str, Any]] = []
    for obj in objects:
        kind, name = obj.get("kind", ""), obj.get("name", "")
        step = _open_step(kind, name)
        if step is None or not name:
            continue
        out.append({
            "kind": kind,
            "name": name,
            "open_link": open_link_for(kind, name),
            "steps": [step, "Я получаю сводку формы"],
        })
    return out


def generate_smoke_feature(objects: list[dict[str, str]], feature_name: str = "smoke — формы открываются") -> str:
    """Render a runnable .feature: one scenario per object (open the main form + read its summary). Uses only
    canonical card-103 steps, so it transpiles with zero unmapped lines."""
    lines = ["# language: ru", f"Функционал: {feature_name}", ""]
    for scn in generate_smoke_scenarios(objects):
        lines.append(f"  Сценарий: {scn['kind']}.{scn['name']}")
        lines.append(f"    Дано {scn['steps'][0]}")
        lines.append(f"    Тогда {scn['steps'][1]}")
        lines.append("")
    return "\n".join(lines)


def smoke_coverage(objects: list[dict[str, str]], opened: list[str] | set[str]) -> dict[str, Any]:
    """Coverage of a smoke run: how many enumerated objects were actually opened. ``opened`` is the set of object
    names that rendered. Returns {total, supported, covered, missing, unsupported}."""
    opened_set = set(opened)
    supported = generate_smoke_scenarios(objects)
    supported_names = [s["name"] for s in supported]
    covered = [n for n in supported_names if n in opened_set]
    missing = [n for n in supported_names if n not in opened_set]
    unsupported = [o.get("name", "") for o in objects
                   if _norm_kind(o.get("kind", "")) not in _KINDS or not o.get("name")]
    return {
        "total": len(objects),
        "supported": len(supported_names),
        "covered": len(covered),
        "missing": missing,
        "unsupported": unsupported,
    }

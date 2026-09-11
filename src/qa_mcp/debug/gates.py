"""CI quality gates over scenario timing + debug-measure coverage (roadmap card 111, item 6).

Card 110 proved scenario-level coverage + perf/APDEX via the `/e1crdbg/` debug protocol (`measure_scenario`).
This module turns those signals into ENFORCEABLE gates:

- `evaluate_perf_budget` — per-step wall-clock budget over a scenario's recorded step durations (the «каждый шаг
  выполняется быстрее N мс» Gherkin step is backed by this; the runner evaluates it inline).
- `evaluate_coverage_gate` — a threshold over a `measure_scenario` coverage report (min covered lines / min
  modules / specific required modules), so a CI run can go RED below an agreed coverage bar.

Both are PURE (plain dict/list in → verdict dict out) — no lab, no imports from `scenario`/`mcp_server`, so the
runner can import `evaluate_perf_budget` with no import cycle. The CLI (`python -m qa_mcp.debug.gates`) applies the
coverage gate to a saved or freshly-measured report and exits non-zero on a breach.
"""

from __future__ import annotations

from typing import Any


def evaluate_perf_budget(steps: list[dict[str, Any]], max_ms: float,
                         per_step_ms: dict[str, float] | None = None) -> dict[str, Any]:
    """Flag steps whose wall-clock exceeds a budget. ``steps`` items: ``{name, kind, duration_sec}``.

    ``max_ms`` is the default per-step budget (0/None = no default); ``per_step_ms`` overrides it by step name.
    A step with no applicable budget (default 0 and no override) is skipped.
    """
    per_step_ms = per_step_ms or {}
    violations: list[dict[str, Any]] = []
    checked = 0
    for s in steps:
        budget = per_step_ms.get(s.get("name")) or max_ms
        if not budget or budget <= 0:
            continue
        checked += 1
        ms = float(s.get("duration_sec") or 0.0) * 1000.0
        if ms > budget:
            violations.append({"name": s.get("name"), "kind": s.get("kind"),
                               "ms": round(ms, 1), "budget_ms": float(budget)})
    return {"ok": not violations, "checked": checked, "violations": violations}


def _module_keys(report: dict[str, Any]) -> set[str]:
    """Every way a `required_modules` entry may name a covered module: bare object, and ``Object :: Module``."""
    keys: set[str] = set()
    for m in report.get("modules") or []:
        obj, mod = m.get("object"), m.get("module")
        if obj:
            keys.add(str(obj))
        if obj and mod:
            keys.add(f"{obj} :: {mod}")
            keys.add(f"{obj}::{mod}")
    return keys


def evaluate_coverage_gate(report: dict[str, Any], *, min_lines: int = 0, min_modules: int = 0,
                           required_modules: "list[str] | tuple[str, ...]" = ()) -> dict[str, Any]:
    """Apply a coverage threshold to a `measure_scenario` report.

    ``report`` may be the raw report (``{modules, totals}``) or the full `measure_scenario` output (``{report:
    {...}}``) — both are accepted. A breach of ANY configured threshold makes the gate fail (``ok=False``).
    """
    if "totals" not in report and isinstance(report.get("report"), dict):
        report = report["report"]
    totals = report.get("totals") or {}
    covered_lines = int(totals.get("covered_lines") or 0)
    covered_modules = int(totals.get("modules") or 0)
    present = _module_keys(report)
    missing_required = [r for r in (required_modules or []) if r not in present]

    reasons: list[str] = []
    if min_lines and covered_lines < min_lines:
        reasons.append(f"covered_lines {covered_lines} < min {min_lines}")
    if min_modules and covered_modules < min_modules:
        reasons.append(f"covered modules {covered_modules} < min {min_modules}")
    if missing_required:
        reasons.append(f"required modules not covered: {', '.join(missing_required)}")
    return {"ok": not reasons, "covered_lines": covered_lines, "covered_modules": covered_modules,
            "missing_required": missing_required, "reasons": reasons}


def main(argv: list[str] | None = None) -> int:
    """`python -m qa_mcp.debug.gates` — apply the coverage gate to a saved or freshly-measured report.

      # gate a saved report (offline / CI):
      python -m qa_mcp.debug.gates --report out/measure.json --min-lines 10 --min-modules 1
      # measure live, then gate:
      python -m qa_mcp.debug.gates --feature scenario.feature --min-lines 10 \
          --required "Документ.Заказ :: МодульОбъекта"
    """
    import argparse
    import json
    from pathlib import Path

    ap = argparse.ArgumentParser(prog="qa_mcp.debug.gates", description="coverage gate over a measure report")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--report", help="path to a saved measure report JSON")
    src.add_argument("--feature", help="path to a .feature to measure live, then gate")
    ap.add_argument("--min-lines", type=int, default=0)
    ap.add_argument("--min-modules", type=int, default=0)
    ap.add_argument("--required", default="", help="comma-separated required modules ('Object :: Module')")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=15381)
    ap.add_argument("--env", default=".ai1c/vanessa-qa-mcp.env")
    ap.add_argument("--src-root", default="")
    args = ap.parse_args(argv)

    if args.report:
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    else:
        from .. import mcp_server  # lazy: live measure boots its own debug client
        report = mcp_server.measure_scenario(
            feature_text=Path(args.feature).read_text(encoding="utf-8"),
            host=args.host, port=args.port, env_file=args.env, src_root=args.src_root)

    required = [r.strip() for r in args.required.split(",") if r.strip()]
    verdict = evaluate_coverage_gate(report, min_lines=args.min_lines, min_modules=args.min_modules,
                                     required_modules=required)
    tag = "OK" if verdict["ok"] else "FAIL"
    print(f"[coverage-gate] {tag} — {verdict['covered_lines']} covered line(s), "
          f"{verdict['covered_modules']} module(s)"
          + (f"; {'; '.join(verdict['reasons'])}" if verdict["reasons"] else ""))
    return 0 if verdict["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Pure orchestration core for the live-regression harness.

This module has NO lab dependency — it runs an arbitrary list of `Check`s against an opaque context object,
captures their outcomes, and aggregates a `RegressionReport`. It is fully unit-testable offline with fake checks;
the live wiring (boot, MCP tools, OData) lives in `checks` and `__main__`.

Phase model: each `Check` declares a `phase`. The CLI groups checks by phase and runs each group at the right
moment relative to the TestClient boot (data-layer checks need Apache UP; the UI boot STOPS Apache — exactly the
handoff's always-restart-Apache discipline). `run_checks` itself is phase-agnostic: it just runs the list it is
given. Phases: `data_pre` (Apache up, pre-boot) · `ui` (client up) · `data_post` (Apache restored, post-boot) ·
`measure` (standalone; `measure_scenario` owns its own client).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

# A check runs against the context and returns (ok, detail) — or raises (a raise is treated as an errored check,
# i.e. a regression or a lab failure, never swallowed).
CheckFn = Callable[[Any], "tuple[bool, dict[str, Any]]"]

PHASES = ("data_pre", "ui", "data_post", "measure")


@dataclass
class Check:
    """A single named live-regression check."""

    name: str
    category: str
    run: CheckFn
    phase: str = "ui"
    required: bool = True  # a non-required check that fails does not fail the whole run (informational)


@dataclass
class CheckResult:
    name: str
    category: str
    phase: str
    ok: bool
    detail: dict[str, Any] = field(default_factory=dict)
    error: str | None = None  # exception text when the check RAISED (vs a clean assertion miss)
    duration_sec: float = 0.0
    required: bool = True

    @property
    def status(self) -> str:
        """JUnit/Allure-compatible step status: ``ok`` · ``error`` (raised) · ``assert_failed`` (clean miss)."""
        if self.ok:
            return "ok"
        return "error" if self.error else "assert_failed"


def run_check(check: Check, ctx: Any, *, clock: Callable[[], float] = time.monotonic) -> CheckResult:
    """Run one check, timing it and converting a raised exception into an errored result."""
    t0 = clock()
    try:
        ok, detail = check.run(ctx)
    except Exception as exc:  # noqa: BLE001 — a raised check is a real failure signal, recorded not swallowed
        return CheckResult(
            check.name, check.category, check.phase, False,
            error=f"{type(exc).__name__}: {exc}", duration_sec=max(0.0, clock() - t0),
            required=check.required,
        )
    if not isinstance(detail, dict):
        detail = {"value": detail}
    return CheckResult(
        check.name, check.category, check.phase, bool(ok),
        detail=detail, duration_sec=max(0.0, clock() - t0), required=check.required,
    )


def run_checks(checks: list[Check], ctx: Any, *, clock: Callable[[], float] = time.monotonic,
               into: "RegressionReport | None" = None) -> "RegressionReport":
    """Run every check in ``checks`` against ``ctx``. Append into ``into`` if given (phase accumulation)."""
    report = into if into is not None else RegressionReport()
    for check in checks:
        report.results.append(run_check(check, ctx, clock=clock))
    return report


@dataclass
class RegressionReport:
    results: list[CheckResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.ok)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.ok)

    @property
    def ok(self) -> bool:
        """Green iff no REQUIRED check failed (a failed informational check does not break the run)."""
        return all(r.ok for r in self.results if r.required)

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1

    def to_scenario_results(self) -> list[dict[str, Any]]:
        """Adapt to the `scenario.reporting` shape so `junit_xml` / `write_allure_results` consume it directly."""
        out: list[dict[str, Any]] = []
        for r in self.results:
            out.append({
                "scenario": r.name,
                "category": r.category,
                "phase": r.phase,
                "duration_sec": r.duration_sec,
                "status": "passed" if r.ok else "failed",
                "steps": [{"kind": r.category, "name": r.name, "status": r.status,
                           "error": r.error, "detail": r.detail}],
            })
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "results": [
                {"name": r.name, "category": r.category, "phase": r.phase, "ok": r.ok,
                 "required": r.required, "status": r.status, "error": r.error,
                 "duration_sec": round(r.duration_sec, 3), "detail": r.detail}
                for r in self.results
            ],
        }

    def render(self) -> str:
        """Human-readable summary — one line per check + a totals footer."""
        lines = []
        for r in self.results:
            mark = "PASS" if r.ok else ("ERR " if r.error else "FAIL")
            opt = "" if r.required else " (optional)"
            extra = ""
            if r.error:
                extra = f"  — {r.error}"
            elif r.detail:
                extra = "  " + ", ".join(f"{k}={v}" for k, v in r.detail.items())
            lines.append(f"  [{mark}] {r.phase:9} {r.name}{opt}  ({r.duration_sec:.1f}s){extra}")
        verdict = "GREEN" if self.ok else "RED"
        lines.append(f"\n{verdict} — {self.passed}/{self.total} passed, {self.failed} failed")
        return "\n".join(lines)

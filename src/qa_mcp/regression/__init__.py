"""Live-regression harness for qa-mcp (roadmap card 111, item 3).

The offline `pytest` suite proves "qa-mcp encodes the protocol correctly"; it can never prove "a real 1C
TestClient still ACCEPTS what we send". That gap was historically closed by one-shot, hand-run evidence scripts
per board card. This package turns those into a single, repeatable, **gated** live run: boot a native
`/TESTCLIENT`, exercise a curated set of the LIVE-verified capabilities, compare against pinned expectations, emit
a pass/fail report and a non-zero exit code on any regression.

- `harness` — the pure, offline-testable orchestration core (`Check`, `CheckResult`, `RegressionReport`,
  `run_checks`). No lab dependency.
- `checks` — the curated live checks (data-layer assert, read/introspect, assert family, open actions; opt-in
  write-roundtrip and debug-measure). These call the real MCP tools and need the lab.
- `__main__` — the CLI: phase-aware boot → run → report → teardown (always restart Apache). Run it with
  `python -m qa_mcp.regression`.
"""

from .harness import Check, CheckResult, RegressionReport, run_check, run_checks

__all__ = ["Check", "CheckResult", "RegressionReport", "run_check", "run_checks"]

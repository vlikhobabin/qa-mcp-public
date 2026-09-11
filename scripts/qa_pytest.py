"""qa-mcp's explicit, affected-module pytest policy and runtime lane reporting."""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone

import pytest

from scripts.qa_test_selection import catalog, changed_paths, select


def pytest_addoption(parser):
    group = parser.getgroup("qa-mcp")
    group.addoption("--qa-changed", action="store_true", help="Select affected product tests")
    group.addoption("--qa-base", default=None, help="Git base for changed modules (default HEAD)")
    group.addoption("--qa-full", choices=("epic", "approved"), help="Explicitly authorized full lane")
    group.addoption("--qa-reason", default="", help="Epic card or operator agreement for full run")
    group.addoption("--qa-lane", choices=("offline", "integration", "live-linux", "live-windows"),
                    default="offline", help="Separate execution contour")
    group.addoption("--qa-live-authorized", action="store_true",
                    help="Operator authorized the concrete runtime target and preflight")
    group.addoption("--qa-plan", action="store_true", help="Collect selected tests without executing")
    group.addoption("--qa-inventory", action="store_true", help="Collect every lane for inventory; never execute")


def pytest_configure(config):
    if not (config.rootpath / "config/test-selection.json").exists():
        return
    full, lane = config.getoption("qa_full"), config.getoption("qa_lane")
    inventory = config.getoption("qa_inventory")
    if full and not config.getoption("qa_reason").strip():
        raise pytest.UsageError("--qa-full requires --qa-reason: epic card or explicit operator agreement")
    if full and config.getoption("qa_changed"):
        raise pytest.UsageError("Choose --qa-full or --qa-changed")
    if lane.startswith("live-") and not inventory and not config.getoption("qa_live_authorized"):
        raise pytest.UsageError("Live lane requires concrete runtime authorization and preflight; use --qa-live-authorized only after both")
    entries = catalog(config.rootpath)
    original = config.invocation_params.args
    explicit = any(str(arg).split("::")[0].endswith(".py") for arg in original)
    targeted = not full and not inventory and (config.getoption("qa_changed") or not explicit)
    reasons, unmapped = {}, []
    if targeted:
        base = config.getoption("qa_base") or os.environ.get("QA_TEST_BASE", "HEAD")
        try:
            changed = changed_paths(config.rootpath, base)
        except Exception as exc:
            raise pytest.UsageError(f"Cannot determine changed modules: {type(exc).__name__}") from exc
        reasons, unmapped = select(config.rootpath, changed, lane, entries=entries)
        if unmapped:
            raise pytest.UsageError("Changed product modules have no test mapping: " + ", ".join(unmapped))
        selected = set(reasons)
        lane_files = {p for p, d in entries.items() if d["lane"] == lane}
        if lane == "offline" and lane_files and selected == lane_files:
            raise pytest.UsageError("All tests in this lane are affected; full execution needs --qa-full and --qa-reason")
    else:
        selected = {p for p, d in entries.items() if inventory or d["lane"] == lane}
    config._qa_selection = {"files": selected, "targeted": targeted, "lane": lane,
                            "reasons": reasons, "start": time.monotonic(), "empty": False,
                            "inventory": inventory}
    if config.getoption("qa_plan") or inventory:
        config.option.collectonly = True


def pytest_ignore_collect(collection_path, config):
    state = getattr(config, "_qa_selection", None)
    if state is None or not collection_path.is_file() or not collection_path.name.startswith("test_"):
        return None
    try:
        relative = collection_path.relative_to(config.rootpath).as_posix()
    except ValueError:
        return None
    if relative.startswith("tests/") and relative not in state["files"]:
        return True
    return None


def pytest_collection_modifyitems(config, items):
    state = getattr(config, "_qa_selection", None)
    if state is None:
        return
    keep, excluded = [], []
    for item in items:
        path = item.path.relative_to(config.rootpath).as_posix()
        live = item.get_closest_marker("live") is not None
        selected = path in state["files"] and (state["inventory"] or not live or state["lane"].startswith("live-"))
        (keep if selected else excluded).append(item)
    if excluded:
        config.hook.pytest_deselected(items=excluded)
    items[:] = keep
    state["empty"] = (not items and state["targeted"] and not state["files"]
                      and not state["lane"].startswith("live-"))
    reporter = config.pluginmanager.getplugin("terminalreporter")
    if reporter:
        reporter.write_line(f"QA LANE START {state['lane']} {datetime.now(timezone.utc).isoformat()} | {len(items)} selected cases")
        if not items and state["lane"].startswith("live-") and not state["inventory"]:
            reporter.write_line("runtime_gap: no live checks selected; this is not runtime qualification")
        for path, reasons in sorted(state["reasons"].items()):
            reporter.write_line(f"  {path} <- {', '.join(reasons)}")


def pytest_runtest_logstart(nodeid, location):
    if "tests/runtime/" in nodeid:
        print(f"\nQA RUNTIME START {datetime.now(timezone.utc).isoformat()} {nodeid}", flush=True)


def pytest_runtest_logreport(report):
    if "tests/runtime/" in report.nodeid and (report.when == "teardown" or report.failed):
        print(f"\nQA RUNTIME {report.when.upper()} END {datetime.now(timezone.utc).isoformat()} {report.nodeid} {report.outcome} {report.duration:.3f}s", flush=True)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    state = getattr(session.config, "_qa_selection", None)
    if state is None:
        return
    if exitstatus == 5 and state["empty"]:
        session.exitstatus = 0
    reporter = session.config.pluginmanager.getplugin("terminalreporter")
    if reporter:
        reporter.ensure_newline()
        reporter.write_line("")
        reporter.write_line(f"QA LANE END {state['lane']} {datetime.now(timezone.utc).isoformat()} | exit={session.exitstatus} elapsed={time.monotonic()-state['start']:.3f}s")

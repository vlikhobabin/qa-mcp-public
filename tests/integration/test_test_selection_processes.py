"""Changed-module selection checks that exercise real Git or pytest subprocesses."""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.qa_test_selection import changed_paths
from tests.support.selection_inputs import workspace


def test_git_selection_includes_staged_unstaged_untracked_and_both_rename_sides(tmp_path):
    def git(*args):
        return subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)
    git("init", "-b", "main")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Fixture")
    for name in ("old.py", "unstaged.py"):
        (tmp_path / name).write_text("before\n")
    git("add", ".")
    git("-c", "core.hooksPath=/dev/null", "commit", "-m", "fixture")
    (tmp_path / "old.py").rename(tmp_path / "new.py")
    git("add", "-A")
    (tmp_path / "unstaged.py").write_text("after\n")
    (tmp_path / "untracked.py").write_text("new\n")
    assert changed_paths(tmp_path) == ["new.py", "old.py", "unstaged.py", "untracked.py"]


@pytest.mark.parametrize("arguments", [
    ["--qa-full=approved"], ["--qa-lane=live-windows"],
])
def test_real_pytest_refuses_unexplained_full_or_unauthorized_live(arguments):
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", *arguments],
                            cwd=root, capture_output=True, text=True, timeout=20)
    assert result.returncode == 4
    assert "QA LANE START" not in result.stdout
    assert "requires" in result.stderr


def test_real_pytest_changed_selection_executes_consumer_and_never_unrelated(tmp_path):
    root = workspace(tmp_path)
    (root / "src/qa_mcp/leaf.py").write_text("value = 1\n")
    (root / "tests/test_consumer.py").write_text(
        "from qa_mcp.leaf import value\ndef test_changed(): assert value == 2\n")
    (root / "tests/test_unrelated.py").write_text(
        "raise AssertionError('unrelated module must not even be imported')\n")
    for args in [("init", "-b", "main"), ("config", "user.email", "test@example.invalid"),
                 ("config", "user.name", "Fixture"), ("add", "."),
                 ("-c", "core.hooksPath=/dev/null", "commit", "-m", "fixture")]:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
    (root / "src/qa_mcp/leaf.py").write_text("value = 2\n")
    repository = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "scripts.qa_pytest", "--qa-changed", "-v"],
        cwd=root, env={**os.environ, "QA_TEST_BASE": "HEAD",
                       "PYTHONPATH": os.pathsep.join([str(root / "src"), str(repository)])},
        capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 passed" in result.stdout
    assert re.search(r"(?m)^tests/test_consumer.py::test_changed PASSED[^\n]*\n", result.stdout)
    assert not re.search(r"PASSED[^\n]*QA LANE", result.stdout)
    assert "QA LANE START offline" in result.stdout and "QA LANE END offline" in result.stdout
    # With no source changes the same deliberately failing baseline test must not run.
    subprocess.run(["git", "-C", str(root), "restore", "src/qa_mcp/leaf.py"],
                   check=True, capture_output=True)
    unchanged = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "scripts.qa_pytest", "--qa-changed", "-q"],
        cwd=root, env={**os.environ, "QA_TEST_BASE": "HEAD",
                       "PYTHONPATH": os.pathsep.join([str(root / "src"), str(repository)])},
        capture_output=True, text=True, timeout=20)
    assert unchanged.returncode == 0, unchanged.stdout + unchanged.stderr
    assert "0 selected cases" in unchanged.stdout and "1 passed" not in unchanged.stdout

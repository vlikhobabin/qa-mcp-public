from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_python_manager_client_module():
    module_path = REPO_ROOT / "tools" / "protocol-research" / "python_manager_client.py"
    spec = importlib.util.spec_from_file_location("python_manager_client_wrapper", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_python_manager_client_reexports_package_session_api() -> None:
    module = load_python_manager_client_module()

    assert module.repo_root_from_script() == REPO_ROOT
    assert module.TestClientSession.__module__ == "qa_mcp.protocol.session"
    assert module.CaptureBootstrap.__module__ == "qa_mcp.protocol.bootstrap"
    assert module.ProtocolTemplates.__module__ == "qa_mcp.protocol.templates"


def test_python_manager_probe_help_uses_package_backed_queries() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/protocol-research/python_manager_probe.py", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "active-window-context" in completed.stdout
    assert "form-element-details" in completed.stdout


def test_protocol_corpus_runner_cli_still_available() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/protocol-research/protocol_corpus_runner.py", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "--case-set" in completed.stdout
    assert "manager-fixture-v2-safe-action" in completed.stdout


def test_v2_safe_action_tools_cli_still_available() -> None:
    for script in (
        "tools/protocol-research/v2_safe_action_tooling.py",
        "tools/protocol-research/report_manager_fixture_v2_safe_action.py",
    ):
        completed = subprocess.run(
            [sys.executable, script, "--help"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        assert completed.returncode == 0
        assert "safe-action" in completed.stdout

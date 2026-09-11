"""Shared temporary workspace setup for selection checks (not a test module)."""
import json
from pathlib import Path


def workspace(tmp_path: Path) -> Path:
    (tmp_path / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n")
    (tmp_path / "config").mkdir()
    (tmp_path / "config/test-selection.json").write_text(json.dumps({"tests": {}}))
    (tmp_path / "src/qa_mcp").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "src/qa_mcp/__init__.py").write_text("")
    return tmp_path

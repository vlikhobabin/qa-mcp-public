"""Pure changed-module selection checks."""
import json

from scripts.qa_test_selection import select
from tests.support.selection_inputs import workspace


def test_changed_leaf_selects_transitive_consumer_without_unrelated_test(tmp_path):
    root = workspace(tmp_path)
    (root / "src/qa_mcp/leaf.py").write_text("value = 1\n")
    (root / "src/qa_mcp/service.py").write_text("from .leaf import value\n")
    (root / "tests/test_service.py").write_text("from qa_mcp.service import value\n")
    (root / "tests/test_other.py").write_text("def test_other(): pass\n")
    selected, missing = select(root, ["src/qa_mcp/leaf.py"])
    assert selected == {"tests/test_service.py": ["src/qa_mcp/leaf.py"]}
    assert not missing


def test_deleted_module_still_selects_importing_test(tmp_path):
    root = workspace(tmp_path)
    (root / "tests/test_old.py").write_text("from qa_mcp.old import value\n")
    selected, missing = select(root, ["src/qa_mcp/old.py"])
    assert list(selected) == ["tests/test_old.py"] and not missing


def test_package_initializer_change_selects_submodule_consumer(tmp_path):
    root = workspace(tmp_path)
    (root / "src/qa_mcp/leaf.py").write_text("value = 1\n")
    (root / "tests/test_leaf.py").write_text("from qa_mcp.leaf import value\n")
    selected, missing = select(root, ["src/qa_mcp/__init__.py"])
    assert list(selected) == ["tests/test_leaf.py"] and not missing


def test_unmapped_new_product_code_requires_mapping_without_full_fallback(tmp_path):
    root = workspace(tmp_path)
    (root / "tests/test_other.py").write_text("def test_other(): pass\n")
    for changed in ("src/qa_mcp/new.py", "src/qa_mcp/protocol/new.json"):
        selected, missing = select(root, [changed])
        assert selected == {} and missing == [changed]


def test_live_and_integration_consumers_do_not_enter_offline_lane(tmp_path):
    root = workspace(tmp_path)
    for name in ("unit", "integration", "windows"):
        (root / f"tests/test_{name}.py").write_text("from qa_mcp.leaf import value\n")
    (root / "config/test-selection.json").write_text(json.dumps({"tests": {
        "tests/test_integration.py": {"lane": "integration"},
        "tests/test_windows.py": {"lane": "live-windows"},
    }}))
    selected, missing = select(root, ["src/qa_mcp/leaf.py"])
    assert list(selected) == ["tests/test_unit.py"] and not missing
    assert list(select(root, ["src/qa_mcp/leaf.py"], "live-windows")[0]) == ["tests/test_windows.py"]

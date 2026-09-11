"""Compile only changed qa-mcp Python inputs; never test installed tooling."""
import os
import py_compile
from pathlib import Path

from scripts.qa_test_selection import changed_paths


def main():
    root = Path(__file__).resolve().parents[1]
    selected = [p for p in changed_paths(root, os.environ.get("QA_TEST_BASE", "HEAD"))
                if p.endswith(".py") and (root / p).is_file()
                and (p.startswith(("src/qa_mcp/", "tests/", "scripts/qa_")) or p == "conftest.py")]
    for path in selected:
        py_compile.compile(str(root / path), doraise=True)
    print(f"Compiled {len(selected)} changed product/test Python files")


if __name__ == "__main__":
    main()

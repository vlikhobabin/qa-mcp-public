"""Produce a source-bound product-test inventory without executing tests."""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from scripts.qa_test_selection import catalog, imports


def build(root: Path, collection: Path) -> dict:
    nodes = [line for line in collection.read_text().splitlines()
             if line.startswith("tests/") and "::" in line]
    counts = Counter(node.split("::")[0] for node in nodes)
    entries = catalog(root)
    if set(counts) != set(entries):
        raise ValueError("Collection and current test files differ; collect again with --qa-inventory")
    clones, helpers, rows = defaultdict(list), defaultdict(list), []
    for relative, config in entries.items():
        file = root / relative
        tree = ast.parse(file.read_text())
        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for node in functions:
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                body = body[1:]
            locator = f"{relative}:{node.lineno}:{node.name}"
            if len(body) >= 2:
                signature = ast.dump(ast.Module(body=body, type_ignores=[]), include_attributes=False)
                clones[signature].append(locator)
            if node.name in {"_context", "_bound_context", "_full_local_context", "_resolution", "_settings"}:
                helpers[node.name].append(locator)
        own_nodes = [node for node in nodes if node.split("::")[0] == relative]
        groups = Counter(node.split("[")[0].split("::", 1)[1] for node in own_nodes)
        rows.append({"file": relative, "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                     "cases": counts[relative], "test_functions": sum(n.name.startswith("test_") for n in functions),
                     "lane": config["lane"],
                     "direct_inputs": sorted(p for p in imports(root, relative) if (root / p).is_file()),
                     "dependency_count": len(config["inputs"]),
                     "largest_parameter_groups": groups.most_common(3)})
    go = []
    for file in sorted((root / "host-agent/windows-display-agent").glob("*_test.go")):
        source = file.read_text()
        go.append({"file": file.relative_to(root).as_posix(),
                   "test_functions": len(re.findall(r"(?m)^func Test\w+\(", source)),
                   "windows_only": file.name.endswith("_windows_test.go") or "//go:build windows" in source,
                   "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    return {"schema": "qa-mcp.test-inventory.v1", "observed_at": datetime.now(timezone.utc).isoformat(),
            "method": "pytest collection only plus static source/import analysis; no full test execution or timing claim",
            "collection_sha256": hashlib.sha256(collection.read_bytes()).hexdigest(),
            "total_python_cases": len(nodes), "python_files": rows, "go_files": go,
            "cases_by_lane": dict(Counter({lane: sum(row['cases'] for row in rows if row['lane'] == lane)
                                           for lane in sorted({row['lane'] for row in rows})})),
            "exact_function_body_duplicates": [items for items in clones.values() if len(items) > 1],
            "repeated_context_helpers": dict(helpers)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = build(Path(__file__).resolve().parents[1], args.collection)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cases": data["total_python_cases"], "lanes": data["cases_by_lane"],
                      "duplicate_groups": len(data["exact_function_body_duplicates"])}))


if __name__ == "__main__":
    main()

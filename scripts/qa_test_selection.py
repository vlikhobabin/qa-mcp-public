"""Product test dependencies and Git change selection; independent of ChangeRail."""
from __future__ import annotations

import ast
import fnmatch
import json
import subprocess
from pathlib import Path


def changed_paths(root: Path, base: str = "HEAD") -> list[str]:
    def git(*args: str) -> list[str]:
        result = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
        return [p.decode() for p in result.stdout.split(b"\0") if p]
    # No rename collapsing: both the removed and added module select consumers.
    return sorted(set(git("diff", "--name-only", "--no-renames", "-z", base, "--")
                      + git("ls-files", "--others", "--exclude-standard", "-z")))


def policy(root: Path) -> dict:
    return json.loads((root / "config/test-selection.json").read_text())


def imports(root: Path, path: str) -> set[str]:
    """Resolve static local imports, including relative imports and public reexports."""
    source = root / path
    if not source.is_file() or source.suffix != ".py":
        return set()
    tree = ast.parse(source.read_text(), filename=path)
    package = path.removeprefix("src/").removesuffix(".py").split("/")[:-1]
    if source.name == "__init__.py":
        package = path.removeprefix("src/").split("/")[:-1]
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            parent = package[:len(package) - node.level + 1] if node.level else []
            prefix = ".".join(parent + ([node.module] if node.module else []))
            modules.add(prefix)
            modules.update(f"{prefix}.{alias.name}" for alias in node.names if alias.name != "*")
    found = set()
    def literal_path(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left, right = literal_path(node.left), literal_path(node.right)
            return "/".join(part.strip("/") for part in (left, right) if part)
        return ""
    for node in ast.walk(tree):
        value = literal_path(node)
        if value.startswith(("src/", "tools/", "docker/", "delivery/", "config/", "host-agent/", "tests/fixtures/", ".github/")):
            if (root / value).is_file():
                found.add(value)
    for module in modules:
        rel = module.replace(".", "/")
        for parts in range(1, len(module.split("."))):
            package_init = "src/" + "/".join(module.split(".")[:parts]) + "/__init__.py"
            if (root / package_init).is_file():
                found.add(package_init)
        for prefix in ("src/", ""):
            candidates = [f"{prefix}{rel}.py", f"{prefix}{rel}/__init__.py"]
            found.update(p for p in candidates if (root / p).is_file())
        # Keep deleted product-module references so deleting code selects its tests.
        parents = module.split(".")
        is_member = any((root / ("src/" + "/".join(parents[:n]) + ".py")).is_file()
                        for n in range(1, len(parents)))
        if module.startswith("qa_mcp.") and not is_member:
            found.add(f"src/{rel}.py")
        if "." not in module:
            for directory in ("tools/protocol-research", "tools/release"):
                candidate = f"{directory}/{module}.py"
                if (root / candidate).is_file():
                    found.add(candidate)
    return found


def catalog(root: Path) -> dict[str, dict]:
    settings = policy(root)
    cache: dict[str, set[str]] = {}
    def closure(path: str) -> set[str]:
        pending, result = [path], set()
        while pending:
            item = pending.pop()
            if item in result:
                continue
            result.add(item)
            if item not in cache:
                cache[item] = imports(root, item)
            pending.extend(cache[item] - result)
        return result
    result = {}
    for file in sorted((root / "tests").rglob("test_*.py")):
        path = file.relative_to(root).as_posix()
        overrides = settings.get("tests", {}).get(path, {})
        inputs = closure(path)
        for extra in overrides.get("inputs", []):
            inputs.update(closure(extra) if extra.endswith(".py") and (root / extra).is_file() else {extra})
        lane = overrides.get("lane", "offline")
        if path.startswith("tests/runtime/windows/"):
            lane = "live-windows"
        elif path.startswith("tests/runtime/linux/"):
            lane = "live-linux"
        result[path] = {"inputs": sorted(inputs), "lane": lane}
    return result


def select(root: Path, changed: list[str], lane: str = "offline", *, entries=None) -> tuple[dict, list[str]]:
    entries = catalog(root) if entries is None else entries
    selected, covered = {}, set()
    for test, data in entries.items():
        matches = sorted({p for p in changed for pattern in data["inputs"]
                          if fnmatch.fnmatchcase(p, pattern)})
        if matches:
            covered.update(matches)
            if data["lane"] == lane:
                selected[test] = matches
    # Missing coverage never silently turns into either a full run or a green claim.
    unmapped = sorted(p for p in changed if p.startswith("src/qa_mcp/") and p not in covered)
    return selected, unmapped

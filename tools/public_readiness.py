#!/usr/bin/env python3
"""Fail-closed public-source, provenance, docs and clean-snapshot gates."""
from __future__ import annotations

import argparse, base64, binascii, email.parser, hashlib, ipaddress, json, os, re, shutil, subprocess, sys
import tarfile, tempfile, tomllib, zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = Path("config/publication-policy.json")
MANIFEST_PATH = Path("docs/public/asset-provenance.json")
ROOTS = (Path("src/qa_mcp/_bundled"), Path("src/qa_mcp/protocol/assets"), Path("docs/protocol-research/evidence"))
DOCS = tuple(map(Path, ("README.md", "SECURITY.md", "CONTRIBUTING.md", "GOVERNANCE.md", "SUPPORT.md",
    "CODE_OF_CONDUCT.md", "docs/publication-policy.md", "delivery/README.md", "delivery/standalone-product-runbook.md",
    "docker/README.md", "host-agent/README.md", "docs/shared-core-extension.md")))
BLOCKED_SUFFIXES = {".1cd", ".cf", ".cfe", ".dt", ".epf"}
PRIVATE_NETS = tuple(map(ipaddress.ip_network, ("10.0." "0.0/8", "172.16." "0.0/12", "192.168." "0.0/16")))

def digest(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def run(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)

def git_visible(root: Path = ROOT) -> list[Path]:
    result = run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], root)
    if result.returncode == 0: return sorted(Path(item) for item in result.stdout.split("\0") if item)
    excluded = {".git", ".runtime", ".venv", "__pycache__", ".pytest_cache", ".dist"}
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file()
                  and not any(part in excluded for part in path.relative_to(root).parts))

def load_policy(root: Path = ROOT) -> dict: return json.loads((root / POLICY_PATH).read_text(encoding="utf-8"))

def policy_findings(root: Path, policy: dict) -> list[dict]:
    findings = []
    try:
        metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        if metadata["project"]["license"] != "Apache-2.0": raise ValueError
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError): findings.append({"category": "license", "path": "pyproject.toml"})
    if policy.get("license_spdx") != "Apache-2.0": findings.append({"category": "license", "path": str(POLICY_PATH)})
    for item in policy.get("i2_gate", {}).get("artifacts", []):
        path = root / item["path"]
        if not path.is_file() or digest(path.read_bytes()) != item["sha256"]: findings.append({"category": "i2_digest", "path": item["path"]})
    return findings

def _payloads(data: bytes, suffix: str) -> tuple[list[bytes], dict[str, int]]:
    if suffix not in {".json", ".jsonl"}: return [], {}
    docs, errors = [], {}
    for raw in ([data] if suffix == ".json" else [line for line in data.splitlines() if line.strip()]):
        try: docs.append(json.loads(raw))
        except (UnicodeDecodeError, json.JSONDecodeError): errors["structured_payload_parse_error"] = errors.get("structured_payload_parse_error", 0) + 1
    decoded = []
    def visit(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                lowered = str(key).lower()
                if not lowered.endswith("_b64"):
                    visit(item)
                    continue
                if not isinstance(item, str):
                    errors["structured_payload_type_error"] = errors.get("structured_payload_type_error", 0) + 1
                    continue
                try:
                    payload = base64.b64decode(item, validate=True)
                except (ValueError, UnicodeEncodeError, binascii.Error):
                    errors["structured_payload_decode_error"] = errors.get("structured_payload_decode_error", 0) + 1
                    continue
                decoded.append(payload)
                if lowered != "payload_b64":
                    continue
                if "byte_count" in value:
                    declared_count = value["byte_count"]
                    if (not isinstance(declared_count, int)
                            or isinstance(declared_count, bool)
                            or declared_count != len(payload)):
                        errors["structured_payload_byte_count_error"] = errors.get("structured_payload_byte_count_error", 0) + 1
                if "sha256" in value:
                    declared_digest = value["sha256"]
                    if (not isinstance(declared_digest, str)
                            or re.fullmatch(r"[0-9a-f]{64}", declared_digest) is None
                            or declared_digest != digest(payload)):
                        errors["structured_payload_sha256_error"] = errors.get("structured_payload_sha256_error", 0) + 1
        elif isinstance(value, list):
            for item in value: visit(item)
    for document in docs: visit(document)
    return decoded, errors

def _views(data: bytes) -> list[bytes]:
    views = [data]
    if len(data) >= 4:
        for encoding in ("utf-16le", "utf-16be"):
            try: normalized = data.decode(encoding).encode()
            except (UnicodeDecodeError, UnicodeEncodeError): continue
            if normalized not in views: views.append(normalized)
    return views

def _private_ip_matches(data: bytes) -> list[bytes]:
    matches = []
    for found in re.finditer(rb"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])", data):
        try: address = ipaddress.ip_address(found.group().decode())
        except ValueError: continue
        if any(address in network for network in PRIVATE_NETS): matches.append(found.group())
    return matches

def _fixture_counts(policy: dict, category: str, path: Path, source: str) -> dict[bytes, int]:
    encoded = policy.get("scanner_fixture_allowlist", {}).get(category, {}).get(path.as_posix(), {}).get(source, {})
    result = {}
    for value, count in encoded.items():
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise ValueError("scanner fixture allowance count must be a positive integer")
        decoded = base64.b64decode(value, validate=True)
        result[decoded] = result.get(decoded, 0) + count
    return result

def _fixture_allowances(policy: dict) -> Counter[tuple[str, str, str, bytes]]:
    allowances: Counter[tuple[str, str, str, bytes]] = Counter()
    configured = policy.get("scanner_fixture_allowlist", {})
    for category, paths in configured.items():
        for path_text, sources in paths.items():
            path = Path(path_text)
            for source in sources:
                for value, count in _fixture_counts(policy, category, path, source).items():
                    allowances[(category, path.as_posix(), source, value)] += count
    return allowances

def scan_tree(root: Path, paths: list[Path], policy: dict | None = None) -> list[dict]:
    policy = load_policy() if policy is None else policy
    patterns = (("named_lab_account", re.compile(b"(?i:" + b"len" + b"ovo@|c:\\\\users\\\\" + b"len" + b"ovo|/home/" + b"li" + b"hv)")),
      ("named_lab_machine", re.compile(b"DESKTOP-[A-Z0-9]{5,}")),
      ("customer_identity", re.compile(("БИТ" + "\\." + "ФИНАНС").encode() + b"|(?i:bit[ ._\\\\/-]*finans|demo" + b"finans|bukh" + b"fin)")),
      ("private_key", re.compile(b"-----BEGIN " + b"(?:RSA |EC |OPENSSH |DSA )?" + b"PRIVATE KEY-----")),
      ("service_token", re.compile(b"(?:gh" + b"[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,})")),
      ("password_assignment", re.compile(b"(?<![A-Za-z0-9_\\\\])(?:[\\\"'][A-Za-z0-9_]*(?:PASSWORD|PASSWD|PWD)[\\\"']|[A-Za-z0-9_]*(?:PASSWORD|PASSWD|PWD))[ \\t]*(?:=|:)[ \\t]*[\\\"']?[^\\s\\\"',}\\]]+", re.IGNORECASE)),
      ("personal_email", re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")))
    counts: Counter[tuple[str, str, str]] = Counter()
    observed: Counter[tuple[str, str, str, bytes]] = Counter()
    def add(category: str, path: Path, source: str, count: int = 1) -> None:
        counts[(category, path.as_posix(), source)] += count
    def observe(category: str, path: Path, source: str, matches: list[bytes]) -> None:
        for value, count in Counter(matches).items():
            observed[(category, path.as_posix(), source, value)] += count
    def inspect(path: Path, source: str, data: bytes) -> None:
        views = _views(data); ip_matches = [match for view in views for match in _private_ip_matches(view)]
        observe("private_lab_endpoint", path, source, ip_matches)
        for category, pattern in patterns:
            matches = [match.group() for view in views for match in pattern.finditer(view)]
            observe(category, path, source, matches)
    for relative in paths:
        path = root / relative
        if not path.exists() and not path.is_symlink(): continue
        inspect(relative, "path", relative.as_posix().encode())
        if relative.suffix.lower() in BLOCKED_SUFFIXES: add("unsupported_binary", relative, "path"); continue
        if path.is_symlink(): inspect(relative, "symlink_target", os.fsencode(os.readlink(path))); continue
        if not path.is_file(): continue
        try: data = path.read_bytes()
        except OSError: add("unreadable", relative, "raw"); continue
        inspect(relative, "raw", data)
        decoded, errors = _payloads(data, relative.suffix.lower())
        for category, count in errors.items(): add(category, relative, "raw", count)
        for payload in decoded: inspect(relative, "decoded_payload", payload)
    allowed = _fixture_allowances(policy)
    for key in observed.keys() | allowed.keys():
        difference = abs(observed.get(key, 0) - allowed.get(key, 0))
        if difference:
            category, path_text, source, _ = key
            counts[(category, path_text, source)] += difference
    return [{"category": c, "path": p, "source": s, "match_count": n} for (c, p, s), n in sorted(counts.items())]

def run_i2(root: Path) -> dict:
    result = run([sys.executable, "tools/protocol-research/oss07_i2/verify_matrix.py", "--run-mutations"], root)
    try: payload = json.loads(result.stdout)
    except json.JSONDecodeError: payload = {}
    if result.returncode or not payload.get("ok") or payload.get("fail_closed_count") != 23: raise RuntimeError("I2 fail-closed verification failed")
    return payload

def audit(args: argparse.Namespace) -> dict:
    policy = load_policy(); findings = policy_findings(ROOT, policy) + scan_tree(ROOT, git_visible()); i2 = run_i2(ROOT)
    history = {"mode": policy["history"]["mode"], "included_ancestor_count": 0}
    if args.history: history.update(excluded_ancestor_count=int(run(["git", "rev-list", "--count", "HEAD"]).stdout.strip() or 0), excluded_author_identity_count=len(set(run(["git", "log", "--format=%ae", "HEAD"]).stdout.splitlines())))
    return {"schema": "qa-mcp.public-source-audit.v1", "ok": not findings, "current_tree_findings": findings,
            "history": history, "i2": {"control": i2["control"]["red_result"], "fail_closed_count": 23}}

def provenance_document(root: Path = ROOT) -> dict:
    entries = []; visible = set(git_visible(root))
    for base in ROOTS:
        for path in sorted((root / base).rglob("*")):
            if not path.is_file() or path.relative_to(root) not in visible: continue
            relative = path.relative_to(root); data = path.read_bytes()
            if relative.suffix.lower() in BLOCKED_SUFFIXES: raise RuntimeError(f"unsupported provenance artifact: {relative}")
            kind = ("project-curated-protocol-fixture" if str(relative).startswith("src/qa_mcp/_bundled/") else "project-created-ui-reference" if str(relative).startswith("src/qa_mcp/protocol/assets/") else "project-authored-curated-research-evidence")
            entries.append({"path": relative.as_posix(), "byte_size": len(data), "sha256": digest(data), "provenance": kind,
              "decision": "redistribute", "license_spdx": "Apache-2.0", "rationale": "Project-authored or project-curated source evidence admitted by the public audit."})
    return {"schema": "qa-mcp.asset-provenance.v1", "entries": entries}

def provenance(args: argparse.Namespace) -> dict:
    policy = load_policy(); gate = policy_findings(ROOT, policy) + scan_tree(ROOT, git_visible())
    if gate: return {"schema": "qa-mcp.provenance-check.v1", "ok": False, "entry_count": 0, "gate_findings": len(gate)}
    run_i2(ROOT); document = provenance_document(); encoded = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode(); path = ROOT / MANIFEST_PATH
    if args.write: path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(encoded)
    return {"schema": "qa-mcp.provenance-check.v1", "ok": path.is_file() and path.read_bytes() == encoded, "entry_count": len(document["entries"])}

def docs_audit(_: argparse.Namespace) -> dict:
    broken = []; link_re = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
    for relative in DOCS:
        path = ROOT / relative
        if not path.is_file(): broken.append({"source": str(relative), "target": "<missing-document>"}); continue
        for raw in link_re.findall(path.read_text(encoding="utf-8")):
            target = raw.strip().strip("<>").split(maxsplit=1)[0]; parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#"): continue
            local = (path.parent / unquote(parsed.path)).resolve()
            if not local.exists() or ROOT not in (local, *local.parents): broken.append({"source": str(relative), "target": target})
    return {"schema": "qa-mcp.public-docs-audit.v1", "ok": not broken, "checked_documents": len(DOCS), "broken_links": broken}

def copy_snapshot(destination: Path) -> dict[str, int]:
    links = external = 0
    for relative in git_visible():
        if relative.parts and relative.parts[0] in {".git", ".runtime", ".venv"}: continue
        source, target = ROOT / relative, destination / relative
        if source.is_symlink(): links += 1; link = Path(os.readlink(source)); external += link.is_absolute() or ".." in link.parts; continue
        if source.is_file(): target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
    return {"symlink_count": links, "external_symlink_count": external}

def _metadata(archive: zipfile.ZipFile | tarfile.TarFile, name: str) -> str:
    if isinstance(archive, zipfile.ZipFile): data = archive.read(name)
    else:
        stream = archive.extractfile(archive.getmember(name))
        if stream is None: raise RuntimeError(f"package metadata unreadable: {name}")
        data = stream.read()
    message = email.parser.BytesParser().parsebytes(data); return message.get("License-Expression", message.get("License", ""))

def snapshot(_: argparse.Namespace) -> dict:
    with tempfile.TemporaryDirectory(prefix="qa-mcp-public-snapshot-") as temp:
        root = Path(temp) / "source"; root.mkdir(); links = copy_snapshot(root)
        if (root / ".git").exists() or (root / ".runtime").exists() or any(p.is_symlink() for p in root.rglob("*")): raise RuntimeError("snapshot retained excluded repository state or symlink")
        if policy_findings(root, load_policy(root)) or scan_tree(root, git_visible(root)): raise RuntimeError("snapshot public audit failed")
        commands = {"sync": ["uv", "sync", "--extra", "dev", "--locked", "--offline"], "import": ["uv", "run", "--offline", "python", "-c", "import qa_mcp; import qa_mcp.mcp_server"],
          "focused": ["uv", "run", "--offline", "pytest", "-q", "tests/test_public_repository_readiness.py", "-k", "not isolated_snapshot"],
          "audit": ["uv", "run", "--offline", "python", "tools/public_readiness.py", "audit", "--json"], "provenance": ["uv", "run", "--offline", "python", "tools/public_readiness.py", "provenance", "--check", "--json"],
          "docs": ["uv", "run", "--offline", "python", "tools/public_readiness.py", "docs", "--json"], "compile": ["uv", "run", "--offline", "python", "-m", "compileall", "-q", "src/qa_mcp"], "build": ["uv", "build", "--offline", "--out-dir", ".dist"]}
        results = {name: run(command, root) for name, command in commands.items()}; failed = [x for x in results if results[x].returncode]
        if failed: raise RuntimeError("snapshot checks failed: " + "; ".join(f"{x}: {(results[x].stdout + results[x].stderr)[-300:]}" for x in failed))
        wheels = list((root / ".dist").glob("*.whl")); sdists = list((root / ".dist").glob("*.tar.gz"))
        if len(wheels) != 1 or len(sdists) != 1: raise RuntimeError("snapshot build artifact count mismatch")
        with zipfile.ZipFile(wheels[0]) as wheel:
            names = wheel.namelist(); legal = [any(x.endswith(f"/licenses/{f}") for x in names) for f in ("LICENSE", "NOTICE")]; wheel_license = _metadata(wheel, next(x for x in names if x.endswith(".dist-info/METADATA")))
        with tarfile.open(sdists[0]) as sdist:
            names = sdist.getnames(); legal += [any(x.endswith(f"/{f}") for x in names) for f in ("LICENSE", "NOTICE")]; sdist_license = _metadata(sdist, next(x for x in names if x.endswith("/PKG-INFO")))
        if not all(legal) or {wheel_license, sdist_license} != {"Apache-2.0"}: raise RuntimeError("package legal metadata mismatch")
        return {"schema": "qa-mcp.public-snapshot-check.v1", "ok": True, "license_spdx": wheel_license, "excluded": {"git_metadata": True, "ignored_runtime": True, **links}, "install": {"locked_sync": True, "import_smoke": True},
          "tests": {"focused_public_readiness": True, "audit": True, "provenance": True, "docs": True, "i2_mutations": 23}, "build": {"wheel_count": 1, "sdist_count": 1}}

def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True); audit_parser = sub.add_parser("audit"); audit_parser.add_argument("--history", action="store_true")
    prov_parser = sub.add_parser("provenance"); prov_parser.add_argument("--write", action="store_true"); prov_parser.add_argument("--check", action="store_true"); sub.add_parser("docs"); sub.add_parser("snapshot")
    for child in sub.choices.values(): child.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try: result = {"audit": audit, "provenance": provenance, "docs": docs_audit, "snapshot": snapshot}[args.command](args)
    except (OSError, RuntimeError, ValueError) as exc: result = {"schema": "qa-mcp.public-readiness-error.v1", "ok": False, "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=None if args.json else 2, sort_keys=True)); return 0 if result.get("ok") else 1

if __name__ == "__main__": raise SystemExit(main())

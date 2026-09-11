#!/usr/bin/env python3
"""Build and verify the source-bound qa-mcp Windows host-agent artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence


SCHEMA = "qa-mcp.windows-host-bridge-artifact.v1"
EXE_NAME = "qa-mcp-host-agent.exe"
MANIFEST_NAME = "qa-mcp-host-agent.manifest.json"
SHA_NAME = f"{EXE_NAME}.sha256"
REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "host-agent" / "windows-display-agent"
REQUIRED_MARKERS = (
    "qa-mcp.windows-host-bridge",
    "/v1/capabilities",
    "/testclient/launch",
    "/testclient/status",
    "/testclient/stop",
    "/screenshot",
    "/uia/visible_list_cells",
    "testclient-relay-addr",
    "QA-MCP-TESTCLIENT-RELAY/1",
    "interactive_task_shell_broker",
)
FORBIDDEN_MARKERS = (
    "/agent/complete",
    "/bsl/diagnostics",
    "/com/execute",
    "/path/infobase",
    "/platform/execute",
    "registry-url",
    "onboarding-grant-file",
)


class ArtifactError(RuntimeError):
    """A concise, operator-actionable artifact validation failure."""


def _run(
    argv: Sequence[str],
    *,
    cwd: Path = REPO_ROOT,
    env: dict[str, str] | None = None,
) -> str:
    completed = subprocess.run(
        list(argv),
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise ArtifactError(f"command failed ({' '.join(argv)}): {detail or completed.returncode}")
    return completed.stdout


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(args: Sequence[str]) -> str:
    return _run(["git", *args]).strip()


def source_dirty_entries() -> list[str]:
    output = _git(["status", "--porcelain", "--untracked-files=all"])
    return output.splitlines() if output else []


def require_clean_source(dirty_entries: Sequence[str], *, allow_dirty: bool) -> None:
    if dirty_entries and not allow_dirty:
        preview = "; ".join(dirty_entries[:8])
        suffix = " ..." if len(dirty_entries) > 8 else ""
        raise ArtifactError(
            "dirty host-agent build inputs/worktree; commit first or use --allow-dirty "
            f"for a local verification artifact: {preview}{suffix}"
        )


def source_files() -> list[Path]:
    files = sorted(SOURCE_ROOT.rglob("*.go"))
    for name in ("go.mod", "go.sum"):
        candidate = SOURCE_ROOT / name
        if candidate.is_file():
            files.append(candidate)
    return sorted(files)


def source_fingerprint() -> tuple[str, list[str]]:
    digest = hashlib.sha256()
    relative_paths: list[str] = []
    for path in source_files():
        relative = path.relative_to(REPO_ROOT).as_posix()
        relative_paths.append(relative)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    if not relative_paths:
        raise ArtifactError(f"no host-agent Go inputs found under {SOURCE_ROOT}")
    return digest.hexdigest(), relative_paths


def agent_version() -> str:
    text = (SOURCE_ROOT / "main.go").read_text(encoding="utf-8")
    match = re.search(r'\bAgentVersion\s*=\s*"([^"]+)"', text)
    if not match:
        raise ArtifactError("AgentVersion was not found in host-agent main.go")
    return match.group(1)


def inspect_pe(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise ArtifactError(f"invalid PE DOS header: {path}")
    pe_offset = int.from_bytes(data[0x3C:0x40], "little")
    if pe_offset < 0x40 or pe_offset + 24 > len(data) or data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ArtifactError(f"invalid PE signature: {path}")
    coff = pe_offset + 4
    machine = int.from_bytes(data[coff : coff + 2], "little")
    optional_size = int.from_bytes(data[coff + 16 : coff + 18], "little")
    optional = coff + 20
    if optional_size < 70 or optional + optional_size > len(data):
        raise ArtifactError(f"invalid PE optional header: {path}")
    magic = int.from_bytes(data[optional : optional + 2], "little")
    subsystem = int.from_bytes(data[optional + 68 : optional + 70], "little")
    if machine != 0x8664:
        raise ArtifactError(f"PE machine is not amd64: 0x{machine:04x}")
    if magic != 0x20B:
        raise ArtifactError(f"PE optional header is not PE32+: 0x{magic:04x}")
    if subsystem != 2:
        raise ArtifactError(f"PE subsystem is not Windows GUI: {subsystem}")
    return {
        "machine": "amd64",
        "machine_code": "0x8664",
        "optional_header": "PE32+",
        "subsystem": "windows_gui",
        "subsystem_code": 2,
    }


def verify_required_markers(path: Path, *, agent_version: str) -> list[str]:
    data = path.read_bytes()
    required = [*REQUIRED_MARKERS, agent_version]
    missing = [marker for marker in required if marker.encode("utf-8") not in data]
    if missing:
        raise ArtifactError(f"required capability markers are missing: {', '.join(missing)}")
    forbidden = [marker for marker in FORBIDDEN_MARKERS if marker.encode("utf-8") in data]
    if forbidden:
        raise ArtifactError(f"removed product markers are present: {', '.join(forbidden)}")
    return required


def read_go_build_info(path: Path) -> dict[str, Any]:
    output = _run(["go", "version", "-m", str(path)])
    lines = output.splitlines()
    if not lines or ": go" not in lines[0]:
        raise ArtifactError(f"Go build metadata is missing from {path}")
    go_version = lines[0].rsplit(": ", 1)[-1]
    package_path = ""
    module = ""
    settings: dict[str, str] = {}
    for line in lines[1:]:
        fields = line.strip().split("\t")
        if not fields:
            continue
        if fields[0] == "path" and len(fields) > 1:
            package_path = fields[1]
        elif fields[0] == "mod" and len(fields) > 1:
            module = fields[1]
        elif fields[0] == "build" and len(fields) > 1 and "=" in fields[1]:
            key, value = fields[1].split("=", 1)
            settings[key] = value
    expected = {"GOOS": "windows", "GOARCH": "amd64", "CGO_ENABLED": "0", "-trimpath": "true"}
    mismatches = [f"{key}={settings.get(key)!r}" for key, value in expected.items() if settings.get(key) != value]
    if mismatches:
        raise ArtifactError(f"unexpected Go build settings: {', '.join(mismatches)}")
    return {
        "go_version": go_version,
        "package_path": package_path,
        "module": module,
        "settings": dict(sorted(settings.items())),
    }


def inspect_artifact(path: Path, *, expected_agent_version: str) -> dict[str, Any]:
    if not path.is_file():
        raise ArtifactError(f"host-agent executable does not exist: {path}")
    pe = inspect_pe(path)
    markers = verify_required_markers(path, agent_version=expected_agent_version)
    build_info = read_go_build_info(path)
    return {
        "filename": path.name,
        "sha256": _sha256(path),
        "size": path.stat().st_size,
        "pe": pe,
        "go_build": build_info,
        "required_markers": markers,
    }


def _source_record(*, dirty_entries: Sequence[str]) -> dict[str, Any]:
    fingerprint, inputs = source_fingerprint()
    return {
        "git_revision": _git(["rev-parse", "HEAD"]),
        "git_dirty": bool(dirty_entries),
        "dirty_entries": list(dirty_entries),
        "fingerprint_sha256": fingerprint,
        "inputs": inputs,
        "agent_version": agent_version(),
    }


def _validate_vcs(artifact: dict[str, Any], source: dict[str, Any]) -> None:
    settings = artifact["go_build"]["settings"]
    revision = settings.get("vcs.revision")
    modified = settings.get("vcs.modified")
    if not revision:
        raise ArtifactError("binary VCS revision metadata is missing")
    if revision != source["git_revision"]:
        raise ArtifactError(
            f"binary VCS revision mismatch: expected {source['git_revision']}, found {revision}"
        )
    if modified not in {"true", "false"}:
        raise ArtifactError("binary VCS modified metadata is missing or invalid")
    expected_modified = "true" if source["git_dirty"] else "false"
    if modified != expected_modified:
        raise ArtifactError(
            "binary VCS modified state mismatch: "
            f"expected {expected_modified}, found {modified}"
        )


def build_bundle(output_dir: Path, *, allow_dirty: bool) -> dict[str, Any]:
    dirty_entries = source_dirty_entries()
    require_clean_source(dirty_entries, allow_dirty=allow_dirty)
    source = _source_record(dirty_entries=dirty_entries)
    output_dir.mkdir(parents=True, exist_ok=True)
    final_exe = output_dir / EXE_NAME
    with tempfile.TemporaryDirectory(prefix="qa-mcp-host-agent-build-") as temp:
        built = Path(temp) / EXE_NAME
        env = os.environ.copy()
        env.update(
            {
                "GOOS": "windows",
                "GOARCH": "amd64",
                "CGO_ENABLED": "0",
                "SOURCE_DATE_EPOCH": _git(["show", "-s", "--format=%ct", "HEAD"]),
                # The delivery workspace may itself live below another Git
                # checkout. Bind Go's VCS stamping to this exact worktree so
                # it cannot discover the enclosing repository instead.
                "GIT_DIR": _git(["rev-parse", "--absolute-git-dir"]),
                "GIT_WORK_TREE": _git(["rev-parse", "--show-toplevel"]),
            }
        )
        _run(
            [
                "go",
                "build",
                "-trimpath",
                "-buildvcs=true",
                "-ldflags=-H windowsgui",
                "-o",
                str(built),
                ".",
            ],
            cwd=SOURCE_ROOT,
            env=env,
        )
        artifact = inspect_artifact(built, expected_agent_version=source["agent_version"])
        _validate_vcs(artifact, source)
        shutil.copyfile(built, final_exe)
    artifact["filename"] = EXE_NAME
    manifest = {
        "schema": SCHEMA,
        "source": source,
        "build": {
            "target": "windows/amd64",
            "cgo_enabled": False,
            "trimpath": True,
            "windows_subsystem": "gui",
        },
        "artifact": artifact,
    }
    (output_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / SHA_NAME).write_text(f"{artifact['sha256']}  {EXE_NAME}\n", encoding="ascii")
    return manifest


def verify_executable(path: Path, *, allow_dirty: bool) -> dict[str, Any]:
    dirty_entries = source_dirty_entries()
    require_clean_source(dirty_entries, allow_dirty=allow_dirty)
    source = _source_record(dirty_entries=dirty_entries)
    artifact = inspect_artifact(path, expected_agent_version=source["agent_version"])
    _validate_vcs(artifact, source)
    return artifact


def verify_bundle(bundle_dir: Path, *, allow_dirty: bool) -> dict[str, Any]:
    manifest_path = bundle_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        raise ArtifactError(f"artifact manifest does not exist: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArtifactError(f"invalid artifact manifest: {exc}") from exc
    if manifest.get("schema") != SCHEMA:
        raise ArtifactError(f"unsupported artifact manifest schema: {manifest.get('schema')!r}")
    dirty_entries = source_dirty_entries()
    require_clean_source(dirty_entries, allow_dirty=allow_dirty)
    current_source = _source_record(dirty_entries=dirty_entries)
    recorded_source = manifest.get("source") or {}
    for key in ("git_revision", "git_dirty", "fingerprint_sha256", "agent_version"):
        if recorded_source.get(key) != current_source[key]:
            raise ArtifactError(
                f"artifact source {key} mismatch: expected {current_source[key]!r}, "
                f"found {recorded_source.get(key)!r}"
            )
    artifact = inspect_artifact(
        bundle_dir / EXE_NAME,
        expected_agent_version=current_source["agent_version"],
    )
    recorded_artifact = manifest.get("artifact") or {}
    for key in ("sha256", "size", "pe", "go_build", "required_markers"):
        if recorded_artifact.get(key) != artifact[key]:
            raise ArtifactError(f"artifact manifest {key} does not match executable")
    sha_path = bundle_dir / SHA_NAME
    expected_sidecar = f"{artifact['sha256']}  {EXE_NAME}\n"
    if not sha_path.is_file() or sha_path.read_text(encoding="ascii") != expected_sidecar:
        raise ArtifactError(f"artifact sha sidecar is missing or invalid: {sha_path}")
    _validate_vcs(artifact, current_source)
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="build and verify a Windows amd64 GUI bundle")
    build.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / ".artifacts" / "windows-host-agent",
    )
    build.add_argument("--allow-dirty", action="store_true")
    verify = subparsers.add_parser("verify", help="verify an existing bundle or executable")
    source = verify.add_mutually_exclusive_group(required=True)
    source.add_argument("--bundle-dir", type=Path)
    source.add_argument("--exe", type=Path)
    verify.add_argument("--allow-dirty", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "build":
            manifest = build_bundle(args.output_dir.resolve(), allow_dirty=args.allow_dirty)
            print(
                f"built and verified {args.output_dir / EXE_NAME} "
                f"sha256={manifest['artifact']['sha256']}"
            )
        elif args.bundle_dir:
            manifest = verify_bundle(args.bundle_dir.resolve(), allow_dirty=args.allow_dirty)
            print(
                f"verified {args.bundle_dir / EXE_NAME} "
                f"sha256={manifest['artifact']['sha256']}"
            )
        else:
            artifact = verify_executable(args.exe.resolve(), allow_dirty=args.allow_dirty)
            print(f"verified {args.exe} sha256={artifact['sha256']}")
    except ArtifactError as exc:
        print(f"windows_host_agent_artifact: ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

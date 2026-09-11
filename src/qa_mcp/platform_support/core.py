"""Core logic for the platform-support factory (probe / validate / bless / matrix).

This module only *composes* existing machinery — it adds no protocol knowledge of its own:

  * version selection / detection  → :mod:`qa_mcp.versioning`, :mod:`qa_mcp._bundled`
  * live GREEN/RED proof           → ``python -m qa_mcp.regression`` (subprocess; it owns boot + teardown)
  * drift preflight + manifest I/O → :mod:`qa_mcp.regression.versioning`
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .._bundled import (
    PROTOCOL_DATA_FALLBACKS,
    SUPPORTED_VERSION_KEYS,
    has_protocol_data,
    version_key,
)
from ..versioning import DEFAULT_PLATFORM_ROOT, load_env_file, platform_version_from_root
from ..regression.versioning import (
    detect_drift,
    manifest_path_for,
    read_manifest,
    repo_root,
    write_manifest,
)

# The lab's OData endpoint (vanessa_client on 8.3 IB). Settings.odata_url defaults to "" so we supply it here; the
# reg user is Администратор with an empty password (a local test IB — not a secret).
DEFAULT_ODATA_URL = "http://127.0.0.1:8316/vanessa_client/odata/standard.odata"
DEFAULT_ENV_FILE = ".ai1c/vanessa-qa-mcp.env"
PLATFORM_BASE_DIR = str(Path(DEFAULT_PLATFORM_ROOT).parent)  # /opt/1cv8/x86_64
RUNTIME_DIR = "runtime/platform-support"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def platform_root_for(version: str) -> str:
    """The install dir for a full ``x.y.z.w`` build under the standard 1C Linux layout."""
    return str(Path(PLATFORM_BASE_DIR) / version)


def installed_platforms(base_dir: str = PLATFORM_BASE_DIR) -> list[str]:
    """Every full ``x.y.z.w`` build installed under ``base_dir`` (sorted)."""
    base = Path(base_dir)
    if not base.is_dir():
        return []
    out = [p.name for p in base.iterdir() if p.is_dir() and platform_version_from_root(p.name)]
    return sorted(out, key=_version_sort_key)


def _version_sort_key(v: str) -> tuple[int, ...]:
    parts = (platform_version_from_root(v) or v).split(".")
    return tuple(int(p) if p.isdigit() else 0 for p in parts)


# --------------------------------------------------------------------------------------------------------------
# probe — offline classification
# --------------------------------------------------------------------------------------------------------------

@dataclass
class Probe:
    version: str                    # full x.y.z.w
    family: str | None              # e.g. "8.3"
    platform_root: str
    installed: bool
    family_supported: bool
    protocol_data_available: bool   # family has its own bundle OR a validated fallback
    already_blessed: bool           # version == manifest baseline or already in compatible list
    manifest_path: str | None
    manifest_baseline: str | None
    case: str                       # "already" | "A" | "B" | "unknown"
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version, "family": self.family, "platform_root": self.platform_root,
            "installed": self.installed, "family_supported": self.family_supported,
            "protocol_data_available": self.protocol_data_available, "already_blessed": self.already_blessed,
            "manifest_path": self.manifest_path, "manifest_baseline": self.manifest_baseline,
            "case": self.case, "reason": self.reason,
        }


def probe(version: str, *, root: Path | None = None) -> Probe:
    """Classify a version offline into an action case (no client boot).

    * ``already`` — the build is the manifest baseline or already in ``compatible_platform_versions``.
    * ``A``       — supported family with protocol data (own or fallback), build not yet blessed: validate + bless.
    * ``B``       — an unsupported family (a new wire contour): route to the Codex/OpenSpec capture pipeline.
    * ``unknown`` — the string is not a recognizable platform version.
    """
    root = root or repo_root()
    version = version.strip()
    fam = version_key(version)
    proot = platform_root_for(version)
    installed = Path(proot).is_dir()

    if fam is None:
        return Probe(version, None, proot, installed, False, False, False, None, None,
                     "unknown", f"{version!r} is not a recognizable x.y.z.w platform version")

    family_supported = fam in SUPPORTED_VERSION_KEYS
    data_available = has_protocol_data(fam) or fam in PROTOCOL_DATA_FALLBACKS

    manifest_rel = manifest_path_for(fam)
    manifest_abs = root / manifest_rel
    already = False
    baseline: str | None = None
    if manifest_abs.exists():
        man = read_manifest(manifest_abs)
        baseline = man.platform_version
        blessed = {man.platform_version, *man.compatible_platform_versions}
        already = version in blessed

    if already:
        case, reason = "already", f"{version} already blessed in {manifest_rel} (baseline {baseline})"
    elif family_supported and data_available:
        case, reason = "A", (f"same family {fam} (supported, protocol data available) — validate live, "
                             f"then append {version} to {manifest_rel}")
    else:
        case, reason = "B", (f"family {fam} is a new wire contour (not in SUPPORTED_VERSION_KEYS) — needs the "
                             f"lab/capture pipeline (OpenSpec card + headless Codex), not this deterministic path")

    return Probe(version, fam, proot, installed, family_supported, data_available, already,
                 manifest_rel, baseline, case, reason)


# --------------------------------------------------------------------------------------------------------------
# validate — live GREEN/RED proof
# --------------------------------------------------------------------------------------------------------------

@dataclass
class ValidateVerdict:
    version: str
    family: str | None
    platform_root: str
    green: bool
    exit_code: int
    include_write: bool
    odata_url: str
    drift: dict[str, Any] | None
    passed: int
    failed: int
    total: int
    failed_checks: list[str]
    report_json: str | None
    started_at: str
    finished_at: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version, "family": self.family, "platform_root": self.platform_root,
            "green": self.green, "exit_code": self.exit_code, "include_write": self.include_write,
            "odata_url": self.odata_url, "drift": self.drift, "passed": self.passed, "failed": self.failed,
            "total": self.total, "failed_checks": self.failed_checks, "report_json": self.report_json,
            "started_at": self.started_at, "finished_at": self.finished_at, "error": self.error,
        }


def _write_version_env(version: str, out_dir: Path, base_env_file: str) -> Path:
    """Clone the base env profile, overriding only PLATFORM_ROOT so the harness boots THIS build.

    Everything else (INFOBASE_PATH, TEST_CLIENT_KIND/USER/PASSWORD) is inherited verbatim — same lab IB, so an
    8.3-family build validates against the existing 8.3 vanessa_client with no conversion.
    """
    base = Path(base_env_file)
    lines: list[str] = base.read_text(encoding="utf-8").splitlines() if base.is_file() else []
    proot = platform_root_for(version)
    replaced = False
    out_lines: list[str] = []
    for line in lines:
        if line.strip().startswith("PLATFORM_ROOT="):
            out_lines.append(f"PLATFORM_ROOT={proot}")
            replaced = True
        else:
            out_lines.append(line)
    if not replaced:
        out_lines.append(f"PLATFORM_ROOT={proot}")
    out_dir.mkdir(parents=True, exist_ok=True)
    env_path = out_dir / "env"
    env_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return env_path


def _drift_preflight(version: str, *, root: Path) -> dict[str, Any] | None:
    fam = version_key(version)
    if fam is None:
        return None
    manifest_abs = root / manifest_path_for(fam)
    if not manifest_abs.exists():
        return {"severity": "missing", "message": f"no manifest for family {fam}", "ok": False}
    return detect_drift(read_manifest(manifest_abs), version, root=root).to_dict()


def _newest_report(out_dir: Path) -> Path | None:
    candidates = sorted(out_dir.glob("*/report.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def validate(
    version: str,
    *,
    odata_url: str = DEFAULT_ODATA_URL,
    include_write: bool = True,
    base_env_file: str = DEFAULT_ENV_FILE,
    root: Path | None = None,
    timeout_sec: float = 900.0,
    extra_regression_args: list[str] | None = None,
) -> ValidateVerdict:
    """Boot a /TESTCLIENT on ``version`` and run the live-regression harness; return a machine-readable verdict.

    The harness owns the boot/teardown (Apache management, Xvfb display, WM, lock clearing). We only point it at
    this build two ways that must agree: the env-file ``PLATFORM_ROOT`` (which binary boots) and the process
    ``QA_MCP_PLATFORM_VERSION`` / ``PLATFORM_ROOT`` (which version string the synth handshake declares).
    """
    root = root or repo_root()
    fam = version_key(version)
    proot = platform_root_for(version)
    out_dir = root / RUNTIME_DIR / version
    reg_out = out_dir / "regression"
    started = _now()

    if not Path(proot).is_dir():
        return ValidateVerdict(version, fam, proot, False, 127, include_write, odata_url, None, 0, 0, 0, [],
                               None, started, _now(), error=f"platform not installed at {proot}")

    drift = _drift_preflight(version, root=root)
    env_path = _write_version_env(version, out_dir, base_env_file)

    child_env = {
        **os.environ,
        "QA_MCP_PLATFORM_VERSION": version,   # full x.y.z.w → synth declares THIS version to the client
        "PLATFORM_ROOT": proot,               # belt-and-braces for resolve_synth_platform_version's second source
        "QA_MCP_ODATA_URL": odata_url,
    }
    cmd = [
        sys.executable, "-m", "qa_mcp.regression",
        "--env", str(env_path),
        "--odata-url", odata_url,
        "--out", str(reg_out),
    ]
    if include_write:
        cmd.append("--include-write")
    if extra_regression_args:
        cmd += extra_regression_args

    try:
        proc = subprocess.run(cmd, cwd=str(root), env=child_env, text=True,
                              capture_output=True, timeout=timeout_sec)
        exit_code = proc.returncode
        run_error: str | None = None if exit_code in (0, 1) else (proc.stderr or "")[-2000:]
    except subprocess.TimeoutExpired:
        exit_code, run_error = 124, f"regression timed out after {timeout_sec}s"

    passed = failed = total = 0
    failed_checks: list[str] = []
    report_json: str | None = None
    report_path = _newest_report(reg_out)
    if report_path is not None:
        report_json = str(report_path.relative_to(root))
        try:
            rep = json.loads(report_path.read_text(encoding="utf-8"))
            passed, failed, total = rep.get("passed", 0), rep.get("failed", 0), rep.get("total", 0)
            failed_checks = [r["name"] for r in rep.get("results", [])
                             if not r.get("ok") and r.get("required", True)]
        except (OSError, json.JSONDecodeError):
            pass

    green = exit_code == 0
    verdict = ValidateVerdict(version, fam, proot, green, exit_code, include_write, odata_url, drift,
                              passed, failed, total, failed_checks, report_json, started, _now(),
                              error=run_error)
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return verdict


# --------------------------------------------------------------------------------------------------------------
# bless — record a validated build in its family manifest (the supported-build list)
# --------------------------------------------------------------------------------------------------------------

@dataclass
class BlessResult:
    version: str
    family: str | None
    manifest_path: str | None
    changed: bool
    compatible_before: list[str]
    compatible_after: list[str]
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version, "family": self.family, "manifest_path": self.manifest_path,
            "changed": self.changed, "compatible_before": self.compatible_before,
            "compatible_after": self.compatible_after, "message": self.message,
        }


def bless(version: str, *, root: Path | None = None, notes: str | None = None,
          require_green: bool = True) -> BlessResult:
    """Append a validated same-family build to its capture manifest's ``compatible_platform_versions``.

    Guardrails: refuses unless ``probe`` says case A (same family) and — when ``require_green`` — a GREEN verdict
    for this version exists on disk (``runtime/platform-support/<version>/verdict.json``). Baseline builds and
    already-blessed builds are no-ops. Only mutates the manifest (the deterministic supported-build surface); the
    scoped commit + broader doc sync is the caller's opsx-pub step.
    """
    root = root or repo_root()
    pr = probe(version, root=root)

    if pr.case == "unknown":
        return BlessResult(version, None, None, False, [], [], f"refused: {pr.reason}")
    if pr.case == "already":
        return BlessResult(version, pr.family, pr.manifest_path, False, [], [], f"no-op: {pr.reason}")
    if pr.case == "B":
        return BlessResult(version, pr.family, pr.manifest_path, False, [], [],
                           f"refused: case B — {pr.reason}")

    if require_green:
        verdict_path = root / RUNTIME_DIR / version / "verdict.json"
        if not verdict_path.exists():
            return BlessResult(version, pr.family, pr.manifest_path, False, [], [],
                               "refused: no validate verdict on disk — run `validate` first")
        v = json.loads(verdict_path.read_text(encoding="utf-8"))
        if not v.get("green"):
            return BlessResult(version, pr.family, pr.manifest_path, False, [], [],
                               f"refused: last validate for {version} was RED "
                               f"(failed: {', '.join(v.get('failed_checks') or []) or '?'})")

    manifest_abs = root / pr.manifest_path
    man = read_manifest(manifest_abs)
    before = list(man.compatible_platform_versions)
    if version == man.platform_version or version in before:
        return BlessResult(version, pr.family, pr.manifest_path, False, before, before,
                           f"no-op: {version} already recorded")
    man.compatible_platform_versions = sorted({*before, version}, key=_version_sort_key)
    # Idempotent note append: blessing N builds in one run must not duplicate the same phrase N times.
    if notes and notes not in man.notes:
        man.notes = (man.notes + " " if man.notes else "") + notes
    write_manifest(manifest_abs, man)
    return BlessResult(version, pr.family, pr.manifest_path, True, before, man.compatible_platform_versions,
                       f"blessed {version} into {pr.manifest_path} (compatible list now "
                       f"{len(man.compatible_platform_versions)} builds)")

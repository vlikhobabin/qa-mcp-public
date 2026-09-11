"""Protocol-version resilience (roadmap card 111, item 4).

qa-mcp drives 1C by replaying a captured irreducible handshake + per-element frame templates. Those bytes are
faithful to ONE platform protocol version (the `8.3.27.x` the capture was recorded on). A platform upgrade can
silently move the handshake or a field offset, with no early signal — failures then look like "random breakage"
instead of "the protocol moved".

This module makes that explicit:

- **Version-stamped capture manifest** — `CaptureManifest` records which platform version the committed frame
  templates were captured on, plus a content hash of each template (so a silent template edit is detectable).
- **Live platform-version detection** — read the version out of `PLATFORM_ROOT` (the path carries it).
- **Drift detection** — `detect_drift` compares the live platform version + on-disk template hashes against the
  manifest and returns a specific verdict (version drift · template drift · missing), so a regression failure is
  *diagnosed* ("platform 8.3.27.1936 ≠ capture baseline 8.3.27.2130 — refresh per the runbook") not guessed.

The CLI (`python -m qa_mcp.regression.versioning`) stamps and checks. The live confirmation that the handshake
still WORKS is the live-regression harness itself (`python -m qa_mcp.regression`); this is the cheap, no-boot
preflight that tells you WHERE to look when it goes red.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .._bundled import DEFAULT_VERSION_KEY, SUPPORTED_VERSION_KEYS, version_key
from ..versioning import (
    DEFAULT_PLATFORM_ROOT,
    PLATFORM_VERSION_ENV,
    active_version_key,
    detect_live_platform_version,
    platform_version_from_root,
)

SCHEMA = "qa-mcp.protocol-capture-manifest.v1"

# The capture manifest is **per platform-version family**: a separate stamped file per family records which exact
# `8.x.y.z` the committed templates were captured on, so the drift detector compares against the set matching the
# *live* version (an 8.3 manifest never spuriously flags an 8.5 platform and vice-versa).
MANIFEST_DIR = "config"
MANIFEST_BASENAME = "protocol-capture-manifest"

def manifest_path_for(family: str) -> str:
    """Repo-relative per-version manifest path, e.g. ``config/protocol-capture-manifest-8.3.json``."""
    return f"{MANIFEST_DIR}/{MANIFEST_BASENAME}-{family}.json"


# Default manifest = the default version family's file (back-compat for callers referencing MANIFEST_PATH).
MANIFEST_PATH = manifest_path_for(DEFAULT_VERSION_KEY)

# The committed irreducible-handshake / frame templates (versioned), + the runtime-generated value-read templates
# (recorded for reference, hash NOT enforced — it is regenerated per machine and lives under git-ignored runtime/).
DEFAULT_TEMPLATES = "docs/protocol-research/evidence/templates/20260602-frames08-106-utf16-managedform/manager_frame_templates.json"
VALUE_READ_TEMPLATES = "runtime/protocol-research/templates/tm-v1-open-plus-valueread/manager_frame_templates.json"
TEMPLATE_SPEC = [
    # (logical name, repo-relative path, committed?)
    ("manager_frame_templates", DEFAULT_TEMPLATES, True),
    ("value_read_templates", VALUE_READ_TEMPLATES, False),
]

def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class TemplateRef:
    name: str
    path: str          # repo-relative
    committed: bool     # enforce hash integrity only for committed templates
    present: bool
    sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "path": self.path, "committed": self.committed,
                "present": self.present, "sha256": self.sha256}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TemplateRef":
        return cls(d["name"], d["path"], bool(d.get("committed", True)),
                   bool(d.get("present", True)), d.get("sha256", ""))


@dataclass
class CaptureManifest:
    platform_version: str = ""
    compatible_platform_versions: list[str] = field(default_factory=list)
    captured_at: str = ""
    schema: str = SCHEMA
    notes: str = ""
    templates: list[TemplateRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"schema": self.schema, "platform_version": self.platform_version,
                "compatible_platform_versions": list(self.compatible_platform_versions),
                "captured_at": self.captured_at, "notes": self.notes,
                "templates": [t.to_dict() for t in self.templates]}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CaptureManifest":
        return cls(platform_version=d.get("platform_version", ""),
                   compatible_platform_versions=list(d.get("compatible_platform_versions", [])),
                   captured_at=d.get("captured_at", ""),
                   schema=d.get("schema", SCHEMA), notes=d.get("notes", ""),
                   templates=[TemplateRef.from_dict(t) for t in d.get("templates", [])])


def build_manifest(*, platform_version: str, captured_at: str, notes: str = "",
                   root: Path | None = None, spec: list[tuple[str, str, bool]] = TEMPLATE_SPEC) -> CaptureManifest:
    """Stamp a manifest: record the platform version + a content hash of each template that exists on disk."""
    root = root or repo_root()
    refs: list[TemplateRef] = []
    for name, rel, committed in spec:
        p = root / rel
        present = p.exists()
        refs.append(TemplateRef(name, rel, committed, present, file_sha256(p) if present else ""))
    return CaptureManifest(platform_version=platform_version, captured_at=captured_at,
                           notes=notes, templates=refs)


def read_manifest(path: str | Path) -> CaptureManifest:
    return CaptureManifest.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def write_manifest(path: str | Path, manifest: CaptureManifest) -> None:
    Path(path).write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@dataclass
class DriftVerdict:
    ok: bool
    severity: str              # "ok" | "version" | "template" | "missing"
    recorded_version: str
    live_version: str | None
    version_match: bool
    template_drift: list[str]  # committed templates whose on-disk hash changed since the stamp
    missing: list[str]         # committed templates that were present at stamp but are gone now
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "severity": self.severity, "recorded_version": self.recorded_version,
                "live_version": self.live_version, "version_match": self.version_match,
                "template_drift": self.template_drift, "missing": self.missing, "message": self.message}


def detect_drift(manifest: CaptureManifest, live_version: str | None, *, root: Path | None = None) -> DriftVerdict:
    """Compare the live platform version + on-disk template hashes against the manifest.

    Integrity (template hash / missing) is enforced only for COMMITTED templates — a template-content change or a
    vanished committed template is a HARD drift (re-stamp / investigate). A platform-version mismatch is a SOFT
    drift (a bump may be protocol-compatible) — loud, but not a hard fail unless `--strict`.
    """
    root = root or repo_root()
    compatible_versions = {manifest.platform_version, *manifest.compatible_platform_versions}
    version_match = bool(live_version) and live_version in compatible_versions
    template_drift: list[str] = []
    missing: list[str] = []
    for ref in manifest.templates:
        if not ref.committed:
            continue
        p = root / ref.path
        if not p.exists():
            if ref.present:
                missing.append(ref.name)
            continue
        if ref.present and ref.sha256 and file_sha256(p) != ref.sha256:
            template_drift.append(ref.name)

    if missing:
        sev, ok = "missing", False
        msg = (f"MISSING committed template(s): {', '.join(missing)} — the versioned capture is gone. "
               f"Restore it or re-stamp the manifest.")
    elif template_drift:
        sev, ok = "template", False
        msg = (f"TEMPLATE DRIFT: {', '.join(template_drift)} changed since the manifest was stamped "
               f"(version {manifest.platform_version}). Re-capture+re-stamp, or revert the edit.")
    elif not version_match:
        sev, ok = "version", False
        msg = (f"PLATFORM VERSION DRIFT: live {live_version} ≠ capture baseline {manifest.platform_version}. "
               f"Captures may be stale; if live-regression goes red, refresh per docs/capture-refresh-runbook.md. "
               f"If live-regression stays GREEN, re-stamp the manifest to bless {live_version}.")
    else:
        sev, ok = "ok", True
        if live_version == manifest.platform_version:
            msg = f"OK — platform {live_version} matches the capture baseline; committed templates intact."
        else:
            msg = (f"OK — platform {live_version} is validated-compatible with capture baseline "
                   f"{manifest.platform_version}; committed templates intact.")
    return DriftVerdict(ok=ok, severity=sev, recorded_version=manifest.platform_version,
                        live_version=live_version, version_match=version_match,
                        template_drift=template_drift, missing=missing, message=msg)


def main(argv: list[str] | None = None) -> int:
    """`python -m qa_mcp.regression.versioning` — stamp or check the protocol-capture manifest.

    check (default): exit 0 if OK; exit 1 on template/missing drift (always) or version drift under --strict.
      python -m qa_mcp.regression.versioning [--env .ai1c/vanessa-qa-mcp.env] [--strict]
    stamp: record the current platform version + template hashes into the manifest.
      python -m qa_mcp.regression.versioning --stamp [--platform-root <path>] [--notes "..."]
    """
    import argparse
    from datetime import datetime, timezone

    ap = argparse.ArgumentParser(prog="qa_mcp.regression.versioning")
    ap.add_argument("--manifest", default=None,
                    help="explicit manifest path (else the per-version file for the live/declared family)")
    ap.add_argument("--version", default=None,
                    help="target version family (e.g. 8.5) — overrides the PLATFORM_ROOT-derived family")
    ap.add_argument("--platform-root", default=None, help="override the platform root (else env / default)")
    ap.add_argument("--env", default=".ai1c/vanessa-qa-mcp.env", help="env profile carrying PLATFORM_ROOT")
    ap.add_argument("--stamp", action="store_true", help="(re)write the manifest for the current platform")
    ap.add_argument("--notes", default="", help="notes to record when stamping")
    ap.add_argument("--strict", action="store_true", help="treat a platform-version drift as a hard failure")
    args = ap.parse_args(argv)

    root = repo_root()
    live = detect_live_platform_version(platform_root=args.platform_root, env_file=args.env)
    # Per-version manifest: select the file matching the target family (explicit --version → live → default), so a
    # check/stamp acts on the manifest for the platform actually in play.
    family = version_key(args.version) or version_key(live) or DEFAULT_VERSION_KEY
    manifest_arg = args.manifest or manifest_path_for(family)
    manifest_path = (root / manifest_arg) if not Path(manifest_arg).is_absolute() else Path(manifest_arg)

    if args.stamp:
        version = live or platform_version_from_root(DEFAULT_PLATFORM_ROOT) or "unknown"
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest = build_manifest(platform_version=version, captured_at=stamp, notes=args.notes, root=root)
        write_manifest(manifest_path, manifest)
        print(f"stamped {manifest_path} @ platform {version}")
        for t in manifest.templates:
            print(f"  [{'committed' if t.committed else 'runtime  '}] "
                  f"{'present' if t.present else 'ABSENT '} {t.name}  {t.sha256[:12] or '-'}")
        return 0

    if not manifest_path.exists():
        print(f"NO MANIFEST at {manifest_path} — run with --stamp first.")
        return 1
    verdict = detect_drift(read_manifest(manifest_path), live, root=root)
    print(f"[drift] {verdict.severity.upper()}: {verdict.message}")
    hard = verdict.severity in ("template", "missing") or (verdict.severity == "version" and args.strict)
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())

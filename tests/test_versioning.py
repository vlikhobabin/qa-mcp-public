"""Offline tests for protocol-version resilience (roadmap 111, item 4)."""

from __future__ import annotations

import ast
from pathlib import Path

from qa_mcp import versioning as leaf_v
from qa_mcp.regression import versioning as v


def test_leaf_versioning_is_import_leaf():
    tree = ast.parse(Path(leaf_v.__file__).read_text(encoding="utf-8"))
    imported_modules = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert not any(module.startswith("protocol") for module in imported_modules)
    assert not any(module.startswith("regression") for module in imported_modules)


def test_regression_versioning_reexports_leaf_helpers():
    assert v.active_version_key is leaf_v.active_version_key
    assert v.detect_live_platform_version is leaf_v.detect_live_platform_version
    assert v.platform_version_from_root is leaf_v.platform_version_from_root
    assert v.PLATFORM_VERSION_ENV == leaf_v.PLATFORM_VERSION_ENV


def test_platform_version_from_root():
    assert v.platform_version_from_root("/opt/1cv8/x86_64/8.3.27.2130") == "8.3.27.2130"
    assert v.platform_version_from_root("/opt/1cv8/x86_64/8.3.27.1936") == "8.3.27.1936"
    assert v.platform_version_from_root("/no/version/here") is None
    assert v.platform_version_from_root(None) is None


def test_detect_live_platform_version_priority(tmp_path):
    # explicit platform_root wins
    assert v.detect_live_platform_version(platform_root="/x/8.3.27.9999") == "8.3.27.9999"
    # else env file's PLATFORM_ROOT
    env = tmp_path / "e.env"
    env.write_text("PLATFORM_ROOT=/opt/1cv8/x86_64/8.3.27.1936\n", encoding="utf-8")
    assert v.detect_live_platform_version(env_file=str(env)) == "8.3.27.1936"


def _manifest_with(
    tmp_path: Path,
    name="t",
    body=b"frames",
    committed=True,
    version="8.3.27.2130",
    compatible_versions=None,
):
    f = tmp_path / "t.json"
    f.write_text(body.decode() if isinstance(body, bytes) else body, encoding="utf-8")
    ref = v.TemplateRef(name, "t.json", committed, True, v.file_sha256(f))
    return v.CaptureManifest(
        platform_version=version,
        compatible_platform_versions=list(compatible_versions or []),
        captured_at="2026-06-22T00:00:00Z",
        templates=[ref],
    ), f


def test_drift_ok_when_version_and_hash_match(tmp_path):
    manifest, _ = _manifest_with(tmp_path)
    verdict = v.detect_drift(manifest, "8.3.27.2130", root=tmp_path)
    assert verdict.ok and verdict.severity == "ok" and verdict.version_match


def test_drift_version_mismatch_is_soft(tmp_path):
    manifest, _ = _manifest_with(tmp_path)
    verdict = v.detect_drift(manifest, "8.3.27.1936", root=tmp_path)
    assert not verdict.ok and verdict.severity == "version"
    assert not verdict.version_match and not verdict.template_drift and not verdict.missing
    assert "8.3.27.1936" in verdict.message and "8.3.27.2130" in verdict.message


def test_drift_compatible_version_is_ok(tmp_path):
    manifest, _ = _manifest_with(tmp_path, compatible_versions=["8.3.27.2074"])
    verdict = v.detect_drift(manifest, "8.3.27.2074", root=tmp_path)
    assert verdict.ok and verdict.severity == "ok" and verdict.version_match
    assert "validated-compatible" in verdict.message


def test_drift_template_hash_change_is_hard(tmp_path):
    manifest, f = _manifest_with(tmp_path)
    f.write_text("EDITED frames", encoding="utf-8")  # committed template content changed since stamp
    verdict = v.detect_drift(manifest, "8.3.27.2130", root=tmp_path)
    assert not verdict.ok and verdict.severity == "template" and verdict.template_drift == ["t"]


def test_drift_missing_committed_template_is_hard(tmp_path):
    manifest, f = _manifest_with(tmp_path)
    f.unlink()
    verdict = v.detect_drift(manifest, "8.3.27.2130", root=tmp_path)
    assert not verdict.ok and verdict.severity == "missing" and verdict.missing == ["t"]


def test_runtime_template_hash_not_enforced(tmp_path):
    # a NON-committed (runtime) template whose hash changed must NOT trip drift
    manifest, f = _manifest_with(tmp_path, committed=False)
    f.write_text("regenerated locally", encoding="utf-8")
    verdict = v.detect_drift(manifest, "8.3.27.2130", root=tmp_path)
    assert verdict.ok and verdict.severity == "ok"


def test_manifest_roundtrip(tmp_path):
    manifest, _ = _manifest_with(tmp_path)
    path = tmp_path / "m.json"
    v.write_manifest(path, manifest)
    back = v.read_manifest(path)
    assert back.platform_version == manifest.platform_version
    assert back.compatible_platform_versions == manifest.compatible_platform_versions
    assert back.templates[0].sha256 == manifest.templates[0].sha256
    assert back.templates[0].committed is True


def test_build_manifest_hashes_present_templates(tmp_path):
    (tmp_path / "a.json").write_text("AAA", encoding="utf-8")
    spec = [("present_one", "a.json", True), ("absent_one", "missing.json", True)]
    m = v.build_manifest(platform_version="8.3.27.2130", captured_at="2026-06-22T00:00:00Z",
                         root=tmp_path, spec=spec)
    refs = {r.name: r for r in m.templates}
    assert refs["present_one"].present and refs["present_one"].sha256
    assert not refs["absent_one"].present and refs["absent_one"].sha256 == ""


def test_committed_manifest_matches_current_platform_and_templates():
    """The committed manifest must be self-consistent: stamped on the default platform and the committed
    template's recorded hash equals its current on-disk hash (a content edit without a re-stamp fails HERE)."""
    root = v.repo_root()
    manifest_path = root / v.MANIFEST_PATH  # per-version default (config/protocol-capture-manifest-8.3.json)
    assert manifest_path.exists(), f"{v.MANIFEST_PATH} missing — run versioning --stamp"
    manifest = v.read_manifest(manifest_path)
    # the baseline records a real 8.3.x.y version
    assert v.platform_version_from_root(manifest.platform_version) == manifest.platform_version
    # committed templates' recorded hashes are intact on disk (no version drift assumed here)
    verdict = v.detect_drift(manifest, manifest.platform_version, root=root)
    assert verdict.severity in ("ok", "version"), verdict.message
    assert not verdict.template_drift and not verdict.missing, verdict.message

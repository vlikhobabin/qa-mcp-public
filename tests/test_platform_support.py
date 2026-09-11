"""Offline unit tests for the platform-support factory (probe classification + bless guardrails).

Hermetic: no client boot, no Apache, no OData. `validate` (the one live entrypoint) is exercised by the
live-regression run, not here. These tests pin the deterministic decision logic that routes a version to the
same-family bless path (case A) vs the Codex/OpenSpec capture pipeline (case B).
"""

from __future__ import annotations

import json

from qa_mcp.platform_support import bless, installed_platforms, probe
from qa_mcp.regression.versioning import CaptureManifest, write_manifest


def _seed_manifest(root, family="8.3", baseline="8.3.27.2130", compatible=("8.3.27.1606",)):
    (root / "config").mkdir(parents=True, exist_ok=True)
    man = CaptureManifest(platform_version=baseline, compatible_platform_versions=list(compatible),
                          captured_at="2026-01-01T00:00:00Z", notes="test")
    write_manifest(root / f"config/protocol-capture-manifest-{family}.json", man)


def _seed_verdict(root, version, *, green):
    d = root / "runtime/platform-support" / version
    d.mkdir(parents=True, exist_ok=True)
    (d / "verdict.json").write_text(json.dumps({
        "version": version, "green": green, "failed_checks": [] if green else ["ui.read_descriptor"],
    }), encoding="utf-8")


def test_probe_baseline_is_already(tmp_path):
    _seed_manifest(tmp_path)
    pr = probe("8.3.27.2130", root=tmp_path)
    assert pr.case == "already" and pr.family == "8.3"


def test_probe_compatible_is_already(tmp_path):
    _seed_manifest(tmp_path, compatible=("8.3.27.1606", "8.3.27.1719"))
    assert probe("8.3.27.1719", root=tmp_path).case == "already"


def test_probe_new_same_family_build_is_case_a(tmp_path):
    _seed_manifest(tmp_path)
    pr = probe("8.3.27.9999", root=tmp_path)
    assert pr.case == "A" and pr.family_supported and pr.protocol_data_available


def test_probe_supported_family_with_fallback_is_case_a(tmp_path):
    # 8.5 is supported and reuses 8.3 data (PROTOCOL_DATA_FALLBACKS) → a new 8.5 build is case A, not B.
    _seed_manifest(tmp_path, family="8.5", baseline="8.5.1.1343", compatible=())
    pr = probe("8.5.1.9999", root=tmp_path)
    assert pr.case == "A" and pr.family == "8.5"


def test_probe_new_family_is_case_b(tmp_path):
    pr = probe("8.4.1.100", root=tmp_path)
    assert pr.case == "B" and not pr.family_supported


def test_probe_garbage_is_unknown(tmp_path):
    assert probe("not-a-version", root=tmp_path).case == "unknown"


def test_bless_refuses_without_verdict(tmp_path):
    _seed_manifest(tmp_path)
    r = bless("8.3.27.9999", root=tmp_path)
    assert not r.changed and "no validate verdict" in r.message


def test_bless_refuses_red_verdict(tmp_path):
    _seed_manifest(tmp_path)
    _seed_verdict(tmp_path, "8.3.27.9999", green=False)
    r = bless("8.3.27.9999", root=tmp_path)
    assert not r.changed and "RED" in r.message


def test_bless_appends_green_same_family(tmp_path):
    _seed_manifest(tmp_path)
    _seed_verdict(tmp_path, "8.3.27.9999", green=True)
    r = bless("8.3.27.9999", root=tmp_path)
    assert r.changed and "8.3.27.9999" in r.compatible_after
    # Persisted to the manifest, sorted.
    man = json.loads((tmp_path / "config/protocol-capture-manifest-8.3.json").read_text(encoding="utf-8"))
    assert "8.3.27.9999" in man["compatible_platform_versions"]


def test_bless_baseline_is_noop(tmp_path):
    _seed_manifest(tmp_path)
    _seed_verdict(tmp_path, "8.3.27.2130", green=True)
    r = bless("8.3.27.2130", root=tmp_path)
    assert not r.changed and "already" in r.message


def test_bless_refuses_case_b(tmp_path):
    r = bless("8.4.1.100", root=tmp_path)
    assert not r.changed and "case B" in r.message


def test_bless_force_skips_verdict_requirement(tmp_path):
    _seed_manifest(tmp_path)
    r = bless("8.3.27.9999", root=tmp_path, require_green=False)
    assert r.changed


def test_installed_platforms_sorted(tmp_path):
    base = tmp_path / "x86_64"
    base.mkdir()
    for v in ["8.3.27.2130", "8.3.27.1606", "8.5.1.1343", "not-a-version"]:
        (base / v).mkdir()
    got = installed_platforms(str(base))
    assert got == ["8.3.27.1606", "8.3.27.2130", "8.5.1.1343"]

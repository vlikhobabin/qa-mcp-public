"""Offline tests for the per-version bundled-asset architecture (epic 112 P0, card 113).

The package selects bundled protocol assets (genuine captures, frame templates, accepted_mappings) by platform
**version family**, then maps supported empty families through an explicit protocol-data fallback. These assert:
the version→set mapping, active-version precedence (QA_MCP_PLATFORM_VERSION → PLATFORM_ROOT → default),
fail-closed unsupported platforms, and that 8.5 uses the validated 8.3 protocol data until a dedicated 8.5 bundle
exists.
"""

from __future__ import annotations

import pytest

from qa_mcp import _bundled as b
from qa_mcp.protocol.bootstrap import resolve_capture_dir
from qa_mcp.protocol.evidence import default_accepted_mappings_path
from qa_mcp.regression import versioning as v


# --- version → family-key mapping --------------------------------------------------------------------------

def test_version_key_maps_full_and_bare_versions():
    assert b.version_key("8.3.27.2130") == "8.3"
    assert b.version_key("8.5.1.1343") == "8.5"
    assert b.version_key("8.5") == "8.5"            # bare family passes through
    assert b.version_key("/opt/1cv8/x86_64/8.3.27.2130") == "8.3"  # extracts from a path too


def test_version_key_returns_none_for_unparseable():
    assert b.version_key(None) is None
    assert b.version_key("") is None
    assert b.version_key("garbage") is None


def test_supported_keys_and_default():
    assert b.SUPPORTED_VERSION_KEYS == ("8.3", "8.5")
    assert b.DEFAULT_VERSION_KEY == "8.3"


# --- active-version selection precedence + fail-closed ------------------------------------------------------

def test_active_version_default_is_8_3():
    # no env override, no platform root → DEFAULT_PLATFORM_ROOT (8.3.27.x) → "8.3"
    assert v.active_version_key(env={}) == "8.3"


@pytest.mark.parametrize("override,expected", [("8.5", "8.5"), ("8.5.1.1343", "8.5"), ("8.3", "8.3")])
def test_active_version_env_override(override, expected):
    assert v.active_version_key(env={v.PLATFORM_VERSION_ENV: override}) == expected


def test_active_version_from_platform_root():
    assert v.active_version_key(platform_root="/opt/1cv8/x86_64/8.5.1.1343", env={}) == "8.5"
    assert v.active_version_key(platform_root="/opt/1cv8/x86_64/8.3.27.2130", env={}) == "8.3"


def test_active_version_env_override_beats_platform_root():
    assert v.active_version_key(
        platform_root="/opt/1cv8/x86_64/8.5.1.1343", env={v.PLATFORM_VERSION_ENV: "8.3"}) == "8.3"


@pytest.mark.parametrize("bad_root", ["/opt/1cv8/x86_64/8.2.19.100", "/opt/1cv8/x86_64/9.0.1.1"])
def test_active_version_unsupported_fails_closed(bad_root):
    with pytest.raises(ValueError) as exc:
        v.active_version_key(platform_root=bad_root, env={})
    msg = str(exc.value)
    assert "no protocol assets bundled for platform" in msg
    assert "supported: 8.3, 8.5" in msg
    assert "capture-refresh-runbook" in msg


def test_active_version_unsupported_env_override_fails_closed():
    with pytest.raises(ValueError) as exc:
        v.active_version_key(env={v.PLATFORM_VERSION_ENV: "9.0"})
    assert "supported: 8.3, 8.5" in str(exc.value)


def test_active_version_unparseable_env_override_raises():
    with pytest.raises(ValueError) as exc:
        v.active_version_key(env={v.PLATFORM_VERSION_ENV: "garbage"})
    assert "not a recognizable platform version" in str(exc.value)


# --- bundled-asset path resolution per version --------------------------------------------------------------

def test_bundled_8_3_set_is_populated():
    assert b.has_protocol_data("8.3")
    assert b.protocol_data_version_key("8.3") == "8.3"
    cap = b.capture_dir("commit-conn", "8.3")
    assert cap is not None and (cap / "traffic.jsonl").exists()
    assert b.template("manager_frame_templates.json", "8.3").exists()
    assert b.template("value_read_templates.json", "8.3").exists()
    assert b.accepted_mappings_path("8.3").exists()


def test_bundled_8_5_slot_uses_8_3_protocol_data_fallback():
    assert not b.has_protocol_data("8.5")
    assert b.protocol_data_version_key("8.5") == "8.3"
    assert b.protocol_data_version_key("8.5.1.1343") == "8.3"
    cap = b.capture_dir("commit-conn", "8.5")
    assert cap is not None and cap.parent.parent.name == "8.3"
    assert b.version_root("8.5").name == "8.5"
    assert b.template("manager_frame_templates.json", "8.5").parent.parent.name == "8.3"


def test_8_3_and_8_5_declared_roots_are_distinct_but_protocol_data_may_fallback():
    assert b.version_root("8.3") != b.version_root("8.5")
    assert b.accepted_mappings_path("8.3").parent.name == "8.3"
    assert b.accepted_mappings_path("8.5").parent.name == "8.3"


# --- resolvers thread the active version (8.3 default — no runtime regression) ------------------------------

def test_resolve_capture_dir_defaults_to_8_3(monkeypatch):
    monkeypatch.delenv(v.PLATFORM_VERSION_ENV, raising=False)
    resolved = resolve_capture_dir("commit-conn")
    assert resolved.name == "commit-conn"
    assert resolved.parent.parent.name == "8.3"  # _bundled/8.3/captures/<name>


def _as_posix(p) -> str:
    return str(p).replace("\\", "/")


def test_resolve_capture_dir_explicit_version_selects_set():
    # 8.3 resolves to the populated bundled set...
    assert resolve_capture_dir("commit-conn", version="8.3").parent.parent.name == "8.3"
    # 8.5 is declared supported by validate-first evidence and uses the populated 8.3 protocol data until an
    # 8.5-specific bundle is populated.
    resolved = resolve_capture_dir("commit-conn", version="8.5")
    assert "/_bundled/8.3/" in _as_posix(resolved)


def test_resolve_capture_dir_honors_env_override(monkeypatch):
    # the env override flows through resolve_capture_dir's active-version resolution
    monkeypatch.setenv(v.PLATFORM_VERSION_ENV, "8.5")
    resolved = resolve_capture_dir("commit-conn")
    assert "/_bundled/8.3/" in _as_posix(resolved)
    monkeypatch.setenv(v.PLATFORM_VERSION_ENV, "8.3")
    assert resolve_capture_dir("commit-conn").parent.parent.name == "8.3"


def test_default_accepted_mappings_path_defaults_to_8_3(monkeypatch):
    monkeypatch.delenv(v.PLATFORM_VERSION_ENV, raising=False)
    path = default_accepted_mappings_path()
    assert path.exists() and path.name == "accepted_mappings.json"
    assert path.parent.name == "8.3"


def test_default_accepted_mappings_path_explicit_version_falls_back_when_absent():
    # 8.5 bundle is empty → uses the validated bundled 8.3 accepted mappings.
    path = default_accepted_mappings_path(version="8.5")
    assert "_bundled/8.5/" not in str(path).replace("\\", "/")
    assert "_bundled/8.3/" in str(path).replace("\\", "/")


# --- per-version manifest path ------------------------------------------------------------------------------

def test_manifest_path_is_per_version():
    assert v.manifest_path_for("8.3") == "config/protocol-capture-manifest-8.3.json"
    assert v.manifest_path_for("8.5") == "config/protocol-capture-manifest-8.5.json"
    # the default MANIFEST_PATH points at the default family's file
    assert v.MANIFEST_PATH == v.manifest_path_for(b.DEFAULT_VERSION_KEY)

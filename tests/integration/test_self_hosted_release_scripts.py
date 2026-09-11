from __future__ import annotations

import fnmatch
import hashlib
import io
import json
import os
import subprocess
import tarfile
from pathlib import Path

import pytest

from tests.support.archives import tar_bytes as _tar_bytes


ROOT = Path(__file__).resolve().parents[2]
HOST_AGENT_LAUNCHER = ROOT / "bin" / "ai-build-windows-host-agent"


def _write(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _write_docker_archive(path: Path, *, repo_tags: list[str] | None = None) -> Path:
    tags = repo_tags or ["qa-mcp-thin:test"]
    asset_patterns = (
        "_bundled/*/accepted_mappings.json",
        "_bundled/*/templates/*.json",
        "_bundled/*/captures/*/traffic.jsonl",
        "protocol/*.json",
        "protocol/assets/*.png",
        "schemas/*.json",
    )
    package_entries = {}
    for source in (ROOT / "src/qa_mcp").rglob("*"):
        if not source.is_file() or "__pycache__" in source.parts:
            continue
        relative = source.relative_to(ROOT / "src/qa_mcp").as_posix()
        if relative.endswith(".py") or any(
            fnmatch.fnmatchcase(relative, pattern) for pattern in asset_patterns
        ):
            package_entries[
                f"usr/local/lib/python3.12/site-packages/qa_mcp/{relative}"
            ] = source.read_bytes()
    layer = _tar_bytes(package_entries)
    manifest = json.dumps([{"Config": "config.json", "RepoTags": tags, "Layers": ["layer.tar"]}]).encode()
    config = json.dumps(
        {
            "config": {
                "Labels": {
                    "org.opencontainers.image.revision": subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
                    ).strip()
                }
            },
            "history": [{"created_by": "COPY readable package source"}],
        }
    ).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, mode="w") as archive:
        for name, data in {
            "manifest.json": manifest,
            "config.json": config,
            "layer.tar": layer,
        }.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return path


def _write_minisig(path: Path) -> Path:
    return _write(path, b"untrusted comment: test signature\nsignature\n")


@pytest.fixture(scope="session")
def verified_host_agent_exe(tmp_path_factory: pytest.TempPathFactory) -> Path:
    bundle = tmp_path_factory.mktemp("verified-windows-host-agent")
    completed = subprocess.run(
        [str(HOST_AGENT_LAUNCHER), "build", "--output-dir", str(bundle), "--allow-dirty"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stderr
    return bundle / "qa-mcp-host-agent.exe"


def test_publish_helper_stages_manifest_and_sidecars() -> None:
    script_path = ROOT / "tools" / "release" / "publish_self_hosted.sh"
    script = script_path.read_text(encoding="utf-8")

    assert "tools/release/component_manifest.py" in script
    assert "tools/release/windows_host_agent_artifact.py" in script
    assert 'set -- build --output-dir "$BUILD_ROOT_ABS/windows-host-agent"' in script
    assert 'set -- verify --bundle-dir "$HOST_AGENT_BUNDLE_DIR"' in script
    assert "GOOS=windows GOARCH=amd64 go build" not in script
    assert "sha256_write" in script
    assert "host-agent/install-windows-host-agent.ps1" in script
    assert "--com-worker-exe" not in script
    assert "COM_WORKER_EXE" not in script
    assert "ai-com-worker.exe" not in script
    assert ".ai1c/release.env" in script
    assert "--server-root" in script
    assert "--activate" in script
    assert "--server-root is retired" in script
    assert "--activate is retired" in script
    assert "https://releases.aifor1c.ru/qa-mcp/download/versions" in script
    assert (
        "RELEASE_BASE_URL=https://releases.aifor1c.ru:58443/qa-mcp"
        not in script
    )
    assert "validate_component_manifest" in script
    assert "AI1C_COMPONENT_MANIFEST_VALIDATOR" in script
    assert "tools/release/validate_component_manifest.py" in script
    assert "verify_open_archive" in script
    assert "--expected-broker-sha256" not in script
    assert "verify_image_archive_tag" in script
    assert "QA_MCP_RELEASE_PYTHON" in script
    assert "run_python" in script
    assert "python3 docker/verify_open_image.py" not in script
    assert 'python3 "$validator"' not in script
    assert "python3 tools/release/component_manifest.py" not in script
    assert "load_release_env_defaults" in script
    assert script.index("load_release_env_defaults") < script.index('while [ "$#" -gt 0 ]')
    assert "stage_manifest_signature" in script
    assert "manifest.json.minisig" in script
    assert "agent-install-runbook.md" in script
    assert "standalone-product-runbook.md" in script
    assert "render_standalone_bootstrap.py" in script
    assert "SERVER_VERSION_TMP" not in script
    assert "SERVER_PUBLIC_DIR" not in script
    assert "docker/verify_open_image.py" in script
    assert "DOCKER_BUILDKIT=1 docker build -f docker/Dockerfile.thin" in script
    assert "--secret" not in script

    result = subprocess.run(["sh", "-n", str(script_path)], cwd=ROOT, check=False)
    assert result.returncode == 0


def test_publish_helper_aborts_when_manifest_validation_fails(
    tmp_path: Path, verified_host_agent_exe: Path
) -> None:
    image = _write_docker_archive(tmp_path / "input" / "qa-mcp-thin-test.tar")
    host_agent = verified_host_agent_exe
    minisig = _write_minisig(tmp_path / "input" / "manifest.json.minisig")
    staging_root = tmp_path / "staging"
    validator = tmp_path / "reject_manifest.py"
    validator.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "print('rejecting manifest', file=sys.stderr)\n"
        "raise SystemExit(7)\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            "sh",
            str(ROOT / "tools" / "release" / "publish_self_hosted.sh"),
            "--version",
            "v0.0.0-invalid-manifest",
            "--release-link-id",
            "r-test-invalid-manifest",
            "--staging-root",
            str(staging_root),
            "--skip-gates",
            "--skip-build",
            "--allow-dirty",
            "--image-archive",
            str(image),
            "--host-agent-exe",
            str(host_agent),
            "--image-tag",
            "qa-mcp-thin:test",
            "--manifest-minisig",
            str(minisig),
        ],
        cwd=ROOT,
        env={**os.environ, "AI1C_COMPONENT_MANIFEST_VALIDATOR": str(validator)},
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 7
    assert "validating component release manifest" in completed.stdout
    assert not (staging_root / "versions" / "v0.0.0-invalid-manifest").exists()


def test_publish_helper_cli_values_override_release_env_defaults(
    tmp_path: Path, verified_host_agent_exe: Path
) -> None:
    image = _write_docker_archive(tmp_path / "input" / "qa-mcp-thin-test.tar")
    host_agent = verified_host_agent_exe
    minisig = _write_minisig(tmp_path / "input" / "manifest.json.minisig")
    staging_root = tmp_path / "staging"
    release_env = ROOT / ".ai" / "release.env"
    original_release_env = release_env.read_bytes() if release_env.exists() else None

    try:
        release_env.parent.mkdir(parents=True, exist_ok=True)
        release_env.write_text(
            "VERSION=v0.0.0-env\n"
            "RELEASE_LINK_ID=r-env\n"
            "IMAGE_TAG=qa-mcp-thin:env\n",
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                "sh",
                str(ROOT / "tools" / "release" / "publish_self_hosted.sh"),
                "--version",
                "v0.0.0-cli",
                "--release-link-id",
                "r-cli",
                "--staging-root",
                str(staging_root),
                "--skip-gates",
                "--skip-build",
                "--allow-dirty",
                "--image-archive",
                str(image),
                "--host-agent-exe",
                str(host_agent),
                "--image-tag",
                "qa-mcp-thin:test",
                "--manifest-minisig",
                str(minisig),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    finally:
        if original_release_env is None:
            release_env.unlink(missing_ok=True)
        else:
            release_env.write_bytes(original_release_env)

    assert (
        "https://releases.aifor1c.ru/qa-mcp/download/versions/"
        "v0.0.0-cli/bootstrap.ps1"
    ) in completed.stdout
    assert "ignoring retired --release-link-id" in completed.stdout
    assert "r-env/bootstrap.ps1" not in completed.stdout
    assert (staging_root / "versions" / "v0.0.0-cli").is_dir()
    assert not (staging_root / "versions" / "v0.0.0-env").exists()
    manifest = json.loads((staging_root / "versions" / "v0.0.0-cli" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "v0.0.0-cli"
    version_dir = staging_root / "versions" / "v0.0.0-cli"
    staged_bootstrap = (version_dir / "bootstrap.ps1").read_text(
        encoding="utf-8-sig"
    )
    staged_guidance = "\n".join(
        (version_dir / name).read_text(encoding="utf-8")
        for name in (
            "README.md",
            "windows-agent-runbook.md",
            "agent-install-runbook.md",
        )
    )
    assert (
        "https://releases.aifor1c.ru/qa-mcp/download/versions/"
        "v0.0.0-cli"
    ) in staged_bootstrap
    assert "https://aifor1c.ru/license" not in staged_bootstrap
    assert "ai1c-license" not in staged_bootstrap
    assert "QA_MCP_LICENSE_" not in staged_bootstrap
    assert "AI1C_LICENSE_" not in staged_bootstrap
    assert "[string]$PasswordFile" in staged_bootstrap
    assert "[string]$LicenseKeyFile" not in staged_bootstrap
    assert "[string]$PortalEmail" in staged_bootstrap
    assert "[string]$PortalPassword =" in staged_bootstrap
    assert "[string]$PortalPasswordFile" in staged_bootstrap
    assert "[string]$Password =" not in staged_bootstrap
    assert "[string]$LicenseKey =" not in staged_bootstrap
    assert "Bundled" + "DataKey" not in staged_bootstrap
    assert "Обычно предустановлен" not in staged_bootstrap
    assert "Проверьте -LicenseKey и" not in staged_bootstrap
    assert "Проверьте -LicenseKeyFile и" not in staged_bootstrap
    assert "AI1C-QAMCP-ALPHA-C19884D77AEA7A6B" not in staged_bootstrap
    assert "Q4dfh5lyk8HIRJccxVeEW4vn+B11fMxCdAItw6VsGFE=" not in staged_bootstrap
    assert ":58443" not in staged_bootstrap
    assert "one\nWindows workstation only" in staged_guidance
    assert "Team deployment is not supported" in staged_guidance
    assert ":58443" not in staged_guidance


def test_publish_helper_rejects_image_archive_tag_mismatch_before_staging(
    tmp_path: Path, verified_host_agent_exe: Path
) -> None:
    image = _write_docker_archive(tmp_path / "input" / "qa-mcp-thin-test.tar", repo_tags=["qa-mcp-thin:other"])
    host_agent = verified_host_agent_exe
    minisig = _write_minisig(tmp_path / "input" / "manifest.json.minisig")
    staging_root = tmp_path / "staging"

    completed = subprocess.run(
        [
            "sh",
            str(ROOT / "tools" / "release" / "publish_self_hosted.sh"),
            "--version",
            "v0.0.0-tag-mismatch",
            "--release-link-id",
            "r-tag-mismatch",
            "--staging-root",
            str(staging_root),
            "--skip-gates",
            "--skip-build",
            "--allow-dirty",
            "--image-archive",
            str(image),
            "--host-agent-exe",
            str(host_agent),
            "--image-tag",
            "qa-mcp-thin:expected",
            "--manifest-minisig",
            str(minisig),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode != 0
    assert "image archive tag mismatch" in completed.stderr
    assert not (staging_root / "versions" / "v0.0.0-tag-mismatch").exists()


def test_publish_helper_rejects_retired_activation_before_staging(
    tmp_path: Path, verified_host_agent_exe: Path
) -> None:
    image = _write_docker_archive(tmp_path / "input" / "qa-mcp-thin-test.tar")
    host_agent = verified_host_agent_exe
    minisig = _write_minisig(tmp_path / "input" / "manifest.json.minisig")
    staging_root = tmp_path / "staging"
    server_root = tmp_path / "server"
    public_dir = server_root / "qa-mcp" / "public"
    public_dir.mkdir(parents=True)
    marker = public_dir / "not-a-symlink"
    marker.write_text("keep\n", encoding="utf-8")

    completed = subprocess.run(
        [
            "sh",
            str(ROOT / "tools" / "release" / "publish_self_hosted.sh"),
            "--version",
            "v0.0.0-activate",
            "--release-link-id",
            "r-activate",
            "--staging-root",
            str(staging_root),
            "--server-root",
            str(server_root),
            "--activate",
            "--skip-gates",
            "--skip-build",
            "--allow-dirty",
            "--image-archive",
            str(image),
            "--host-agent-exe",
            str(host_agent),
            "--image-tag",
            "qa-mcp-thin:test",
            "--manifest-minisig",
            str(minisig),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode != 0
    assert "--server-root is retired" in completed.stderr
    assert not (staging_root / "versions" / "v0.0.0-activate").exists()
    assert not (public_dir / "r-activate").exists()
    assert marker.read_text(encoding="utf-8") == "keep\n"


def test_publish_helper_rejects_unverified_supplied_binary_even_with_skip_gates(
    tmp_path: Path,
) -> None:
    image = _write_docker_archive(tmp_path / "input" / "qa-mcp-thin-test.tar")
    host_agent = _write(tmp_path / "unverified" / "qa-mcp-host-agent.exe", b"host-agent")
    minisig = _write_minisig(tmp_path / "input" / "manifest.json.minisig")
    staging_root = tmp_path / "staging"

    completed = subprocess.run(
        [
            "sh",
            str(ROOT / "tools" / "release" / "publish_self_hosted.sh"),
            "--version",
            "v0.0.0-unverified-host-agent",
            "--release-link-id",
            "r-unverified-host-agent",
            "--staging-root",
            str(staging_root),
            "--skip-gates",
            "--skip-build",
            "--allow-dirty",
            "--image-archive",
            str(image),
            "--host-agent-exe",
            str(host_agent),
            "--image-tag",
            "qa-mcp-thin:test",
            "--manifest-minisig",
            str(minisig),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode != 0
    assert "artifact manifest does not exist" in completed.stderr
    assert not (staging_root / "versions" / "v0.0.0-unverified-host-agent").exists()

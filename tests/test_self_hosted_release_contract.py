"""Offline source/configuration contracts; no builds or native Windows proof."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]

def test_bootstrap_is_self_hosted_manifest_driven() -> None:
    script = (ROOT / "delivery" / "bootstrap.ps1").read_text(encoding="utf-8-sig")

    assert "manifest.json" in script
    assert "manifest.json.minisig" in script
    assert "[string]$PortalEmail" in script
    assert "[string]$PortalPassword =" in script
    assert "[string]$PortalPasswordFile" in script
    assert "Save-ReleaseAsset" in script
    assert "Get-ReleaseRequestHeaders" in script
    assert "Invoke-ReleaseRequestNoRedirect" in script
    assert "AllowAutoRedirect = $false" in script
    assert "MaximumRedirection 0" not in script
    assert "Protected qa-mcp downloads require portal credentials" in script
    assert "Pass -PortalEmail plus -PortalPassword or -PortalPasswordFile" in script
    assert "Pass only one portal password source" in script
    assert '$ReleaseBasePlaceholder = "__QA_MCP_" + "RELEASE_BASE__"' in script
    assert "Assert-HttpsReleaseBase $ReleaseBase" in script
    assert "Assert-ManifestSignature" in script
    assert "ManifestPublicKey or ManifestPublicKeyFile is required" in script
    assert "-ManifestPublicKey" in script
    assert "ManifestPublicKeyFile" in script
    assert "Download-ReleaseAsset $Manifest" in script
    assert "Test-ManifestAsset" in script
    assert "ai-com-worker.exe" not in script
    assert "ComWorkerExe" not in script
    assert "Assert-AssetSha256" in script
    assert "docker load -i $ImageArchive" in script
    assert "-e QA_MCP_BEARER_TOKEN=$McpToken" in script
    assert '-p "127.0.0.1:${McpPort}:8080"' in script
    assert 'Authorization = "Bearer $McpToken"' in script
    assert "github.com/vlikhobabin/qa-mcp-dist" not in script
    assert "ghcr.io/vlikhobabin/qa-mcp-thin" not in script
    assert "docker pull" not in script


def test_bootstrap_uses_owned_lifecycle_and_authenticated_relay() -> None:
    script = (ROOT / "delivery" / "bootstrap.ps1").read_text(encoding="utf-8-sig")

    assert 'if (Test-TcpPortOpen "127.0.0.1" $ClientPort)' in script
    assert "already accepts TCP before this bootstrap run" in script
    assert '"http://127.0.0.1:$AgentPort/testclient/launch"' in script
    assert "$LaunchResult.owns_process" in script
    assert "$LaunchResult.lifecycle_id" in script
    assert "$LaunchResult.client_target" in script
    assert '"-TestClientRelayAddress", "0.0.0.0:$RelayPort"' in script
    assert '-e QA_MCP_CLIENT_PORT=$RelayPort' in script
    assert '-e QA_MCP_TESTCLIENT_RELAY_ENDPOINT="host.docker.internal:$RelayPort"' in script
    assert "QA_MCP_TESTCLIENT_RELAY_TOKEN=$Token" in script
    assert "TestClientSession" in script
    assert "CLIENT_READ_OK" in script
    assert "QA_MCP_HOST_AGENT_WINDOW=" not in script
    assert "launch-testclient.ps1" not in script
    assert "Get-Process 1cv8" not in script


def test_bootstrap_and_runbooks_use_canonical_mcp_path_and_windows_guidance() -> None:
    script = (ROOT / "delivery" / "bootstrap.ps1").read_text(encoding="utf-8-sig")
    readme = (ROOT / "delivery" / "README.md").read_text(encoding="utf-8")
    runbook = (ROOT / "delivery" / "windows-agent-runbook.md").read_text(encoding="utf-8")

    assert '$mcpUrl = "http://127.0.0.1:$McpPort/mcp"' in script
    assert "сохраните завершающий /mcp/" not in script
    assert "docker info --format" in script
    assert "-WindowTitle сохранён только для совместимости" in script

    assert '"url": "http://127.0.0.1:8000/mcp"' in readme
    assert "путь ровно `/mcp`" in readme
    assert "параметр `-Password` надо **опустить**" in readme
    assert "docker info" in readme

    assert "GET /v1/capabilities" in runbook
    assert "QA_MCP_HOST_AGENT=host.docker.internal:8001" in runbook
    assert "missing capability" in runbook
    assert "exact-owned lifecycle PID/handle" in runbook


def test_standalone_renderer_uses_restricted_password_file_without_product_license() -> None:
    import importlib.util

    renderer_path = ROOT / "tools/release/render_standalone_bootstrap.py"
    spec = importlib.util.spec_from_file_location(
        "render_standalone_bootstrap_tested", renderer_path
    )
    assert spec and spec.loader
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    source = (ROOT / "delivery/bootstrap.ps1").read_text(
        encoding="utf-8-sig"
    )

    rendered = renderer.render(
        source,
        "https://releases.aifor1c.ru/qa-mcp/download/versions/v0.4.0",
    )

    assert "[string]$PasswordFile" in rendered
    assert "[string]$LicenseKeyFile" not in rendered
    assert "[string]$PortalEmail" in rendered
    assert "[string]$PortalPassword =" in rendered
    assert "[string]$PortalPasswordFile" in rendered
    assert "[string]$Password =" not in rendered
    assert "[string]$LicenseKey =" not in rendered
    assert "Read-ProtectedInputFile" in rendered
    assert "AreAccessRulesProtected" in rendered
    assert "Save-ReleaseAsset" in rendered
    assert "Protected qa-mcp downloads require portal credentials" in rendered
    assert "Pass -PortalEmail plus -PortalPassword or -PortalPasswordFile" in rendered
    assert "--entrypoint sh" not in rendered
    assert "ai-mcp-proxy" not in rendered
    assert "-e QA_MCP_BEARER_TOKEN=$McpToken" in rendered
    assert "LicenseServerUrl" not in rendered
    assert "LicenseComponents" not in rendered
    assert "QA_MCP_LICENSE_" not in rendered
    assert "AI1C_LICENSE_" not in rendered
    assert "ai1c-license" not in rendered
    assert "qa-mcp-license" not in rendered
    assert "Обычно предустановлен" not in rendered
    assert "Проверьте -LicenseKey и" not in rendered
    assert "Проверьте -LicenseKeyFile и" not in rendered
    assert "Bundled" + "DataKey" not in rendered


def test_distribution_has_no_product_license_broker_assets() -> None:
    dockerfile = (ROOT / "docker/Dockerfile.thin").read_text(encoding="utf-8")
    verifier = (ROOT / "docker/verify_open_image.py").read_text(encoding="utf-8")

    assert not (ROOT / "delivery/broker").exists()
    assert not (ROOT / "docker/refresh_broker.sh").exists()
    for text in (dockerfile, verifier):
        assert "ai1c-license" not in text
        assert "license_gate" not in text
        assert "QA_MCP_LICENSE_" not in text


def test_container_dependency_layers_precede_mutable_source() -> None:
    cases = (
        (
            ROOT / "Dockerfile",
            "qa-mcp-build-requirements.txt",
            "qa-mcp-runtime-requirements.txt",
            "RUN pip install --no-cache-dir --no-deps --no-build-isolation .",
        ),
        (
            ROOT / "docker" / "Dockerfile.thin",
            "COPY pyproject.toml uv.lock ./",
            "uv pip install --system --no-cache --require-hashes",
            "RUN pip install --no-cache-dir --no-deps --no-build-isolation .",
        ),
    )

    for dockerfile_path, dependency_input, dependency_install, project_install in cases:
        dockerfile = dockerfile_path.read_text(encoding="utf-8")
        dependency_input_index = dockerfile.index(dependency_input)
        dependency_install_index = dockerfile.index(dependency_install)
        mutable_source = dockerfile.index("COPY src ./src")
        source_install = dockerfile.index(project_install)

        assert dependency_input_index < mutable_source
        assert dependency_install_index < mutable_source
        assert mutable_source < source_install


def test_source_visible_image_has_no_secret_or_compile_stage() -> None:
    dockerfile = (ROOT / "docker" / "Dockerfile.thin").read_text(encoding="utf-8")
    assert "COPY src ./src" in dockerfile
    assert "verify_open_image.py" in dockerfile
    assert "--mount=type=secret" not in dockerfile
    assert "ARG PUBLIC_BASE_IMAGE=ghcr.io/astral-sh/uv:" in dockerfile
    assert "FROM ${PUBLIC_BASE_IMAGE}" in dockerfile
    assert "COPY pyproject.toml uv.lock ./" in dockerfile
    assert "uv export --quiet --frozen" in dockerfile
    assert "uv pip install --system --no-cache --require-hashes" in dockerfile

    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "@sha256:[0-9a-f]{64}" in workflow
    assert workflow.index("--component-manifest dist/manifest.json") < workflow.index(
        'docker push "${{ env.IMAGE }}:${{ steps.tag.outputs.tag }}"'
    )


@pytest.mark.smoke
def test_publish_helper_source_has_no_com_worker_surface() -> None:
    script = (ROOT / "tools" / "release" / "publish_self_hosted.sh").read_text(encoding="utf-8")
    bootstrap = (ROOT / "delivery" / "bootstrap.ps1").read_text(encoding="utf-8-sig")

    for source in (script, bootstrap):
        assert "ai-com-worker.exe" not in source
        assert "ComWorkerExe" not in source
    assert "COM_WORKER_EXE" not in script
    assert "--com-worker-exe" not in script

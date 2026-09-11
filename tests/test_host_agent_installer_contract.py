from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "host-agent" / "install-windows-host-agent.ps1"


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8-sig")


def test_installer_requires_verified_public_artifact() -> None:
    script = _script()
    assert "ExePath is required" in script
    assert "bin/ai-build-windows-host-agent" in script
    assert "GOOS=windows GOARCH=amd64 go build" not in script


def test_installer_rebinds_executable_and_token_acls() -> None:
    script = _script()
    acl = script.split("function Set-TokenFileAcl", 1)[1].split(
        "function Write-Utf8NoBom", 1
    )[0]
    assert "New-Object System.Security.AccessControl.FileSecurity" in acl
    assert "WindowsIdentity]::GetCurrent().User" in acl
    assert 'SecurityIdentifier("S-1-5-18")' in acl
    assert 'SecurityIdentifier("S-1-5-32-544")' in acl
    assert script.index("Copy-Item -Force $ExePath $TargetExe") < script.index(
        "Set-TokenFileAcl -Path $TargetExe"
    ) < script.index("Register-ScheduledTask -TaskName $TaskName")


def test_installer_creates_install_dir_independently_of_external_token_parent() -> None:
    script = _script()
    install_dir_create = "New-Item -ItemType Directory -Force -Path $InstallDir"
    assert install_dir_create in script
    assert script.index(install_dir_create) < script.index("$TokenParent = Split-Path -Parent $TokenFile")


def test_installer_wires_only_standalone_lifecycle_and_relay_inputs() -> None:
    script = _script()
    for marker in (
        "$TestClientRelayAddress",
        "$TestClientPort = 15381",
        '"-testclient-relay-addr"',
        '"-testclient-relay-target-port"',
        '"-platform-catalog"',
        "QA_MCP_TESTCLIENT_RELAY_ENDPOINT",
    ):
        assert marker in script
    for forbidden in (
        "AgentCli",
        "BslAgent",
        "ComWorker",
        "Onboarding",
        "Registry",
        '"-agent',
        '"-bsl',
        '"-com-worker',
        '"-onboarding',
        '"-registry',
    ):
        assert forbidden not in script


def test_installer_reconciles_secret_safe_profile_idempotently() -> None:
    script = _script()
    for marker in (
        "function Get-SecretSafeSha256",
        "$DesiredProfileFingerprint",
        '"task-action-drift"',
        '"running-process-arguments-drift"',
        '"host-agent-artifact-drift"',
        '"token-file-drift"',
        "Host-agent restart skipped: running task already matches desired profile",
    ):
        assert marker in script
    assert "$RestartRequired = $RestartReasons.Count -gt 0" in script


def test_installer_uninstall_is_exact_owned_and_idempotent() -> None:
    script = _script()
    assert "[switch]$Uninstall" in script
    assert "its executable is not the owned bridge path" in script
    assert "Where-Object { try { $_.Path -eq $TargetExe }" in script
    assert "Unregister-ScheduledTask -TaskName $TaskName" in script
    assert "function Get-InstalledTestClientRelayPort" in script
    assert "$OwnedRelayPort = Get-InstalledTestClientRelayPort" in script
    assert 'qa-mcp TestClient relay $OwnedRelayPort' in script
    assert script.index("$OwnedRelayPort = Get-InstalledTestClientRelayPort") < script.index(
        "foreach ($OwnedFile"
    )
    assert "Get-Process 1cv8" not in script
    assert "taskkill" not in script.lower()


def test_installer_keeps_lan_firewall_explicitly_scoped() -> None:
    script = _script()
    assert "RemoteAddress is required for non-loopback bind" in script
    assert "-AllowUnsafeLan" in script
    assert "New-NetFirewallRule" in script

#!/usr/bin/env python3
"""Render the signed standalone bootstrap without changing the active source."""

from __future__ import annotations

import argparse
from pathlib import Path


class RenderError(ValueError):
    pass


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RenderError(f"{label}: expected one source marker, found {count}")
    return text.replace(old, new, 1)


def render(source: str, release_base: str) -> str:
    if (
        not release_base.startswith("https://")
        or "/qa-mcp/download/versions/" not in release_base
        or release_base.endswith("/")
    ):
        raise RenderError(
            "release base must identify one HTTPS "
            "/qa-mcp/download/versions/<version> path"
        )
    rendered = source.replace(
        "__QA_MCP_RELEASE_BASE__", release_base.rstrip("/")
    )
    rendered = rendered.replace(
        "https://releases.aifor1c.ru:58443/qa-mcp/r-YYYYMMDD-.../",
        release_base.rstrip("/") + "/",
    )
    rendered = replace_once(
        rendered,
        ' -User "Tester" -Password "pw"',
        ' -User "Tester" -PasswordFile "$env:LOCALAPPDATA\\qa-mcp-inputs\\1c-password.txt"',
        "password example",
    )
    rendered = replace_once(
        rendered,
        '    [string]$Password = "",',
        '    [string]$PasswordFile = "",                    # ACL-protected UTF-8 file; omit for a passwordless 1C user',
        "password parameter",
    )
    function_marker = "function Write-Utf8NoBom([string]$Path, [string]$Value) {"
    protected_reader = r'''function Read-ProtectedInputFile(
    [string]$Path,
    [string]$Label,
    [bool]$Optional = $false
) {
    if ([string]::IsNullOrWhiteSpace($Path)) {
        if ($Optional) { return "" }
        Die "$Label file is required."
    }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $Item -or $Item.PSIsContainer) { Die "$Label file not found: $Path" }
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Die "$Label file must not be a symlink or reparse point: $Path"
    }
    $Acl = Get-Acl -LiteralPath $Item.FullName
    if (-not $Acl.AreAccessRulesProtected) {
        Die "$Label file ACL must disable inherited access: $Path"
    }
    $AllowedSids = @(
        [Security.Principal.WindowsIdentity]::GetCurrent().User.Value,
        "S-1-5-18",
        "S-1-5-32-544"
    )
    foreach ($Rule in $Acl.Access) {
        $Sid = $Rule.IdentityReference.Translate(
            [Security.Principal.SecurityIdentifier]
        ).Value
        if (
            $Rule.AccessControlType -eq "Allow" -and
            $AllowedSids -notcontains $Sid
        ) {
            Die "$Label file grants access outside the current user/SYSTEM/Administrators: $Path"
        }
    }
    $Value = [IO.File]::ReadAllText($Item.FullName).TrimEnd("`r", "`n")
    if ([string]::IsNullOrEmpty($Value) -and -not $Optional) {
        Die "$Label file is empty: $Path"
    }
    return $Value
}
'''
    rendered = replace_once(
        rendered,
        function_marker,
        protected_reader + function_marker,
        "protected input function insertion",
    )
    assignment_marker = (
        'if ($DistBase -and (($ReleaseBase -eq $ReleaseBasePlaceholder) '
        "-or [string]::IsNullOrWhiteSpace($ReleaseBase))) {"
    )
    protected_assignments = (
        '$Password = Read-ProtectedInputFile -Path $PasswordFile '
        '-Label "1C password" -Optional $true\n\n'
    )
    rendered = replace_once(
        rendered,
        assignment_marker,
        protected_assignments + assignment_marker,
        "protected input assignment insertion",
    )
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--release-base", required=True)
    args = parser.parse_args()
    try:
        result = render(
            args.source.read_text(encoding="utf-8-sig"),
            args.release_base,
        )
    except (OSError, UnicodeError, RenderError) as exc:
        parser.error(str(exc))
    args.output.write_text(result, encoding="utf-8-sig", newline="\r\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

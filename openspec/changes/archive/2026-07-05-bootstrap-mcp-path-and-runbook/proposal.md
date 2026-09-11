## Why

The standalone bootstrap printed `http://127.0.0.1:8000/mcp/`, but the HTTP MCP
server responds on `/mcp` without the trailing slash. The same tester pass also
found runbook ambiguity around empty passwords, Docker Desktop readiness,
PowerShell UTF-8 bytes, and `-WindowTitle` guidance.

## What Changes

- Print and document the working MCP URL as `/mcp` without a trailing slash.
- Keep bootstrap/runbook guidance explicit that an empty 1C password means
  omitting `-Password`, not passing `-Password ""`.
- Ensure Docker Desktop readiness and manual UTF-8 PowerShell request guidance
  are visible in delivery docs.
- Keep `-WindowTitle` guidance aligned with the host-agent window-list fix.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-self-hosted-release`: bootstrap and delivery runbooks must print a
  usable MCP path and unambiguous install guidance for Docker, empty passwords,
  UTF-8 manual calls, and window title selection.

## Impact

- Touches `delivery/bootstrap.ps1`, `delivery/README.md`, and
  `delivery/windows-agent-runbook.md`.
- May touch delivery tests that assert generated URLs or runbook text.
- Requires local script/doc tests and `git diff --check`; Windows E2E bootstrap
  remains an external smoke artifact.

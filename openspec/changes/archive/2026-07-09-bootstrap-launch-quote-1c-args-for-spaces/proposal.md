## Why

`delivery/bootstrap.ps1` generates `launch-testclient.ps1` with an ARRAY-form
`Start-Process -ArgumentList @(…, '/N<user>', …)`. For a 1C user name (or infobase
path) containing spaces — e.g. the [redacted third-party configuration] demo user `Тестовый Пользователь (Демо)` —
PowerShell wraps the element as `"/N<name>"` (quote BEFORE `/N`), but 1C requires
`/N"<name>"` (quote AFTER `/N`). The TestClient then fails login
(`Пользователь ИБ не идентифицирован`), never binds its TPort, and bootstrap aborts.
demo10413's `/NАдминистратор` (no spaces) masked this; the earlier BOM fix handled the
Cyrillic-encoding case but not the spaces case. Every [redacted third-party configuration] demo base is affected.

## What Changes

- `delivery/bootstrap.ps1`: build ONE command-line string with 1C-correct quoting —
  each value wrapped as a single command-line token with internal double-quotes doubled,
  the flag glued to its quoted value (`/N"…"`, `/P"…"`, `/IBConnectionString "…"`) — and
  the generated launcher passes it via `Start-Process -ArgumentList '<one string>'`.
- `delivery/windows-agent-runbook.md`: the manual launch snippet uses the same form.
- `tests/test_self_hosted_release_scripts.py`: pin the single-string launcher and the
  `/N"…"` / `/IBConnectionString "…"` quoting; assert the old array form is gone.

## Impact

- Affected capability: `qa-mcp-self-hosted-release`
- Affected files: `delivery/bootstrap.ps1`, `delivery/windows-agent-runbook.md`,
  `tests/test_self_hosted_release_scripts.py`
- Restores bootstrap TestClient launch for any 1C base whose user name / path contains
  spaces. The host-agent Go launch path (`exec` `[]string`) was already correct.

# Card: bootstrap launch-testclient breaks 1C user names / paths with spaces

Status: done
Owner: qa-mcp
Capability: `qa-mcp-self-hosted-release`
Change: `bootstrap-launch-quote-1c-args-for-spaces` (archived `2026-07-09-…`)

## Problem

`delivery/bootstrap.ps1` builds the TestClient launch command as an ARRAY and the
generated `launch-testclient.ps1` calls
`Start-Process -ArgumentList @(…, '/N<user>', …)`. For a 1C user name (or infobase
path) that contains **spaces** — e.g. the [redacted third-party configuration] demo user
`Тестовый Пользователь (Демо)` — PowerShell wraps the element as `"/N<name>"` (quote
BEFORE `/N`), but 1C needs `/N"<name>"` (quote AFTER `/N`). The client then dies in
~4s with `Пользователь ИБ не идентифицирован`, never binds the TPort, and bootstrap
aborts at the TestClient step. demo10413 `/NАдминистратор` (no spaces) masked the bug;
the earlier BOM fix (`3cb6f00`) handled the Cyrillic-encoding case but not spaces.

The host-agent Go launch path (`host-agent/windows-display-agent/testclient_launch.go`,
`exec` `[]string`) is unaffected — only the PowerShell launcher.

Observed LIVE on .201 (2026-07-09): array form → "не идентифицирован"; single-string
form `/IBConnectionString "File=""<path>"";" /N"Тестовый Пользователь (Демо)"` → logs in +
binds TPort (verified on redacted-third-party-configuration TPort 15385/15386).

## Change 1: `bootstrap-launch-quote-1c-args-for-spaces`

Capability: `qa-mcp-self-hosted-release`.

**What.** Emit ONE command-line string with 1C-correct quoting from `bootstrap.ps1`:
each value wrapped as a single token with internal double-quotes doubled, flag glued to
the quoted value (`/N"…"`, `/P"…"`, `/IBConnectionString "…"`); the generated launcher
uses `Start-Process -ArgumentList '<one string>'` (verbatim command line). Update the
manual `windows-agent-runbook.md` to the same form and the release-script test.

**Why.** Restores TestClient launch for every 1C base whose user name or path contains
spaces (all [redacted third-party configuration] demo bases), without which bootstrap cannot reach a running client.

**Tasks.**
- [x] `bootstrap.ps1`: single-string launcher with 1C-correct token quoting
- [x] `delivery/windows-agent-runbook.md`: same single-string form
- [x] `tests/test_self_hosted_release_scripts.py`: assert single-string + `/N"…"` + `/IBConnectionString "…"`; assert the old `@($argLine)` array form is gone
- [x] Verify live on .201 that the single-string form logs in + binds (redacted-third-party-configuration, TPort 15386)

## Log
- 2026-07-09: Discovered during the [redacted third-party configuration] auto-window re-proof; root cause = array-form
  `Start-Process` quoting of a spaced `/N` element; fix implemented + `pytest
  tests/test_self_hosted_release_scripts.py` green (11) + verified live; filed to formalize.

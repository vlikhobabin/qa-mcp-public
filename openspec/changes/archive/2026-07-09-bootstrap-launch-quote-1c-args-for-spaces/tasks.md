## 1. Quote the 1C launch arguments correctly

- [x] 1.1 `bootstrap.ps1`: emit a single-string command line with 1C-correct token quoting
      (`/N"…"`, `/P"…"`, `/IBConnectionString "…"`, internal double-quotes doubled)
- [x] 1.2 Generated `launch-testclient.ps1` uses `Start-Process -ArgumentList '<one string>'`
- [x] 1.3 `delivery/windows-agent-runbook.md`: manual snippet uses the same form

## 2. Verify

- [x] 2.1 `tests/test_self_hosted_release_scripts.py` pins the single-string launcher +
      quoting and rejects the old array form; `uv run pytest` green
- [x] 2.2 Live: single-string form logs in + binds on .201 redacted-third-party-configuration
      (user `Тестовый Пользователь (Демо)`, TPort 15386) where the array form failed
- [x] 2.3 `openspec validate <change> --strict` passes

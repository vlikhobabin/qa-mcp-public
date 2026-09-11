## 1. Workflow Gate

- [x] 1.1 Add a push/pull-request CI workflow that installs with `uv sync --extra dev --locked`.
- [x] 1.2 Run `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60` in the CI workflow.
- [x] 1.3 Add the same Python pytest gate to the release workflow before protected artifact build/publish.
- [x] 1.4 Make the release build/publish job depend on the pytest gate.

## 2. Pytest Configuration And Docs

- [x] 2.1 Add `pytest-cov` to development dependencies and refresh the lockfile.
- [x] 2.2 Register pytest markers for `offline`, `live`, `integration`, `slow`, and `capture`.
- [x] 2.3 Update README verification docs with the `uv` pytest coverage command and marker split.

## 3. Verification

- [x] 3.1 Run `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60` — 662 passed, total coverage 68%, 60% floor passed.
- [x] 3.2 Run `openspec validate ci-pytest-job --strict` — passed.
- [x] 3.3 Run `git diff --check` — passed.
- [x] 3.4 Record Windows-native verification as N/A because this change modifies Linux GitHub Actions and adds no Windows, PowerShell, `.cmd`, `.bat`, or WSL workflow entrypoints.

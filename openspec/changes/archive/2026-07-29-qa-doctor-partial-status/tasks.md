## 1. Doctor Aggregation
- [x] 1.1 Add `required` metadata to doctor checks.
- [x] 1.2 Mark optional unavailable probes, including effective-user absence
  and unconfigured COM doctor input, as optional skips.
- [x] 1.3 Keep configured/required probe failures blocking with `ok=false` and
  `status=fail`.

## 2. Tests
- [x] 2.1 Add tests for optional effective-user skip producing
  `ok=true`/`status=partial`.
- [x] 2.2 Update auth-missing tests to assert the required failure contract.
- [x] 2.3 Confirm healthy all-pass output remains `ok=true`/`status=pass`.

## 3. Verification
- [x] 3.1 Run `uv run pytest -q tests/test_doctor.py tests/test_config.py`.
- [x] 3.2 Run `openspec validate qa-doctor-partial-status --strict`.
- [x] 3.3 Run `git diff --check`.

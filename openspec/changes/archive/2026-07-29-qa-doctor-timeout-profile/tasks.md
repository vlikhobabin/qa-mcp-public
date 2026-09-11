## 1. Settings And Doctor Runtime
- [x] 1.1 Add `QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS` to the centralized settings
  constants, supported-variable documentation, dataclass, and parser.
- [x] 1.2 Resolve doctor effective timeout from settings when CLI/tool callers
  omit an explicit timeout.
- [x] 1.3 Include the effective COM doctor timeout in `com_connector_doctor`
  check data without exposing secrets.

## 2. Tests
- [x] 2.1 Add config tests for parsing the doctor COM timeout setting.
- [x] 2.2 Add doctor tests proving env default and explicit override behavior.
- [x] 2.3 Update MCP wrapper tests for the optional timeout default.

## 3. Verification
- [x] 3.1 Run `uv run pytest -q tests/test_doctor.py tests/test_config.py`.
- [x] 3.2 Run `openspec validate qa-doctor-timeout-profile --strict`.
- [x] 3.3 Run `git diff --check`.

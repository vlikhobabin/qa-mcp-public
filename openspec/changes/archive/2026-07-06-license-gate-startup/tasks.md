## 1. Add the license-check module

- [x] 1.1 Added `src/qa_mcp/license_gate.py` (suite-consistent name; mirrors the 4
  shipped providers, NOT the separate-`evaluate` sketch — the DI-runner pattern is
  cleaner and proven). `check_qa_mcp_startup_license(*, executable, timeout_seconds,
  runner=None)` implements the ALLOW predicate (exit 0 + `allowed` + status
  `licensed`/`offline_grace` + schema `ai1c.license.check.output.v1` + component
  `qa-mcp`) and raises `QaMcpLicenseGateDenied` (with a `LicenseGateDecision`
  carrying a stable reason code + the grace timestamp) for every other case.
- [x] 1.2 The injectable `runner` maps missing-broker (`FileNotFoundError`) /
  timeout (`TimeoutExpired`) / launch errors / malformed JSON to DENY decisions; raw
  broker stdout/stderr is never copied. `_resolve_license_broker_executable` finds
  the broker on PATH (image) or the suite `license/ai1c-license/bin` candidates.

## 2. Wire the gate into `main()`

- [x] 2.1 Added `_enforce_startup_license_gate()` called at the top of
  `mcp_server.main()`: when `QA_MCP_LICENSE_GATE` is set, run the check and ALLOW →
  continue (on `offline_grace`, print a diagnostic-safe grace line incl. the grace
  timestamp to stderr); DENY → `SystemExit(1)` after a diagnostic-safe stderr line.
  Flag unset → no broker call, current behavior.
- [x] 2.2 Reads broker path/timeout from `QA_MCP_LICENSE_BROKER` /
  `QA_MCP_LICENSE_TIMEOUT` (defaults `ai1c-license` / 5.0s).

## 3. Tests (fake broker, no live dependency)

- [x] 3.1 `tests/test_license_gate.py`: a fake-broker `runner` + the contract matrix
  — allowed / offline_grace / denied (allowed:false, non-zero exit, bad status,
  component mismatch, unsupported schema) / malformed / missing-broker / timeout —
  each asserting allow-or-fail-closed.
- [x] 3.2 Diagnostic safety: the deny + grace rendered diagnostics contain no raw
  broker stdout/stderr, lease/activation/key ids; `secret_values == "not_reported"`;
  the grace timestamp (non-secret) IS surfaced.
- [x] 3.3 Free-delivery parity: with `QA_MCP_LICENSE_GATE` unset,
  `_enforce_startup_license_gate()` makes **no** broker call (spy). Plus enabled →
  denied exits 1, enabled → allowed starts.

## 4. Verification

- [x] 4.1 Offline `pytest` green: `tests/test_license_gate.py` 17 passed; full suite
  `536 passed`. See the Verification Matrix in `design.md`.
- [x] 4.2 OFF-by-default confirmed (flag unset → current delivery unaffected, no
  broker call). **Enforcement NOT enabled here.** NOTE: the gate lives in
  `mcp_server.py` + `license_gate.py`, which the card-122 `nuitka-protocol-build-stage`
  does NOT compile (it compiles only `protocol/`). Compiling the gate-bearing modules
  (so the gate can't be edited out of the image) is card 123 D2's scope (extend the
  Nuitka stage to the non-protocol modules); sequence it before turning the gate ON
  (`license-activation-bootstrap`).

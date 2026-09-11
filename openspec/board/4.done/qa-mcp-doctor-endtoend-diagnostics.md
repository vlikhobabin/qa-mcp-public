# qa_mcp_doctor — one end-to-end diagnostics tool/command + legible errors

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Change Set
- `qa-mcp-doctor-endtoend-diagnostics` — one diagnostic chain plus related structured error states.

## Source
- `docs/qa-mcp-connection-issues-2.md` — the report's headline recommendation,
  covering findings **#1, #2, #5, #6, #7, #8** (and consuming the COM check from
  the COM card). Real-base test 2026-07-07.

## Problem
The container was healthy and the final attach succeeded, but verifying the setup
was manual and error-prone, and several failures were false negatives:
- **#5** host-agent listens on `[::]:8001` (IPv6 wildcard) → raw
  `Get-NetTCPConnection -LocalPort 8001` looked "not listening" while HTTP on
  `127.0.0.1:8001` and `[::1]:8001` both returned 200. Port enumeration lies.
- **#6** container→host route (`host.docker.internal:8001`) works but isn't
  summarized until a tool is invoked.
- **#2** a valid configured MCP server appears `unauthorized` when the bearer
  `QA_MCP_BEARER_TOKEN` isn't in the active process env; the error doesn't
  distinguish "bad token" from "token env var missing".
- **#7** `get_window_list_testclient` failed `open-link-required` after a good
  attach — looks like a connection failure but is a missing param; no low-level
  "MCP↔TestClient connected" smoke that doesn't need `open_link`.
- **#8** wrong `-User` (`Администратор` vs the base's `Админ`) left the client at
  the «Доступ к информационной базе» dialog; attach still reported the configured
  `Администратор`, not the effective user.
- **#1** (Codex-side): configured MCP server not loaded as native tools — NOT
  qa-mcp's bug, but a doctor + docs help users self-diagnose.

## Scope
1. **`qa_mcp_doctor`** — one MCP tool (and a CLI form) returning a single
   pass/fail chain: MCP proxy auth (with `token_env_present` — no secret),
   host-agent reachability by **HTTP** (not raw port; handles `[::]`),
   container→host-agent route, 1C platform discovery, test-client TPort
   reachability, and the COM-connector check (from the COM card).
2. **Legible auth error** (#2): include a non-secret `token_env_present:false`
   hint in `unauthorized`.
3. **Low-level testclient smoke** (#7): a "connected to test client" check that
   does not require `open_link`; clarify `get_window_list_testclient` error + add
   an `open_link` example (`e1cib/list/<metadata>`) to the schema description.
4. **Effective-user + login-dialog state** (#8): report the effective infobase
   user if queryable; detect the login/access-dialog stuck state as a distinct
   diagnostic (a stuck login must not look like a connect success).

## Change 1: `qa-mcp-doctor-endtoend-diagnostics`

### Why
Users need one diagnostic command that separates infrastructure reachability,
auth configuration, TestClient protocol connectivity, and login/user state
instead of interpreting several unrelated false-negative errors.

### Goal
Add the doctor MCP/CLI surface, low-level TestClient smoke, secret-safe auth
presence hints, and attach/user-state diagnostics with focused offline tests and
docs.

### Scope
- Python manager/MCP code under `src/qa_mcp/`.
- Runtime settings for non-secret diagnostic inputs.
- Offline tests for doctor result shape and error cases.
- Existing troubleshooting/tool-reference docs.
- No host-agent auth semantics change and no COM execution expansion.

### Acceptance
- `qa_mcp_doctor` returns a single ordered pass/fail/skipped chain and never
  leaks tokens or passwords.
- Missing `QA_MCP_BEARER_TOKEN` is reported as `token_env_present:false`.
- A TestClient smoke can pass without `open_link`.
- Login-dialog-stuck and effective-user mismatch states are represented as
  distinct diagnostics when evidence is available.

### Depends On
- `qa-mcp-com-query-tool-and-worker-bundle` (COMConnector doctor endpoint)

### Related
- `openspec/changes/archive/2026-07-07-qa-mcp-doctor-endtoend-diagnostics/`

### Notes For `$openspec-ff-change`
- Extend existing endpoint/container/runtime specs rather than creating a new
  capability namespace.
- Include a 1C verification matrix because this changes QA/TestClient runtime
  diagnostics; live Windows proof may be a provider/environment gap in Linux.

## Acceptance
- `qa_mcp_doctor` on the .205-style setup returns a single result with each link
  pass/fail; on a healthy stack all green; with the bearer env missing it flags
  `token_env_present:false` (not a generic unauthorized).
- A login-dialog-stuck client is reported as a distinct state, not "attached".
- A testclient smoke passes without `open_link`.

## Related
- `docs/qa-mcp-connection-issues-2.md` (#1/#2/#5/#6/#7/#8), epic 111.
- Consumes the COM-connector check from
  `qa-mcp-com-query-tool-and-worker-bundle`.
- `openspec/changes/archive/2026-07-07-qa-mcp-doctor-endtoend-diagnostics/`

## Result
Delivered `qa_mcp_doctor` as both an MCP tool and `qa-mcp-doctor` CLI. The
doctor reports proxy bearer-env presence, host-agent HTTP health, container
route reachability, platform discovery, TestClient TPort/smoke status,
login-dialog/effective-user diagnostics, and the bounded COMConnector doctor
link without exposing tokens or passwords.

Synced and archived OpenSpec change:
`openspec/changes/archive/2026-07-07-qa-mcp-doctor-endtoend-diagnostics/`.

Verification retained:
- `openspec validate qa-mcp-doctor-endtoend-diagnostics --strict`
- `openspec validate qa-mcp-runtime-configuration --strict`
- `openspec validate qa-mcp-tool-endpoint-contract --strict`
- `openspec validate qa-mcp-suite-container-delivery --strict`
- `openspec validate --all`
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py --mode preflight ...`
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py --mode archive ...`
- `uv run --with pytest --with pyyaml pytest`
- `uv run --with pytest --with pyyaml pytest -m smoke`
- `python3 -m compileall -q src/qa_mcp tests/test_doctor.py`
- `git diff --check`
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py`

Runtime evidence retained outside git under
`.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/20260707T202930Z/`.
The live Windows login-dialog screenshot proof remains a recorded provider gap
for an operator-owned Windows model-B contour.

Publish commit message: `feat(qa-mcp): add end-to-end doctor diagnostics`.

## Next
- None.

## Log
- 2026-07-07 filed from the real-base report; the single highest-leverage item.
- 2026-07-07 decomposed into one card-owned OpenSpec change with apply-ready artifacts.
- 2026-07-07 moved to in-progress for implementation.
- 2026-07-07 implemented, verified, synced to specs and archived.
- 2026-07-07 publish verification passed and scoped commit prepared.

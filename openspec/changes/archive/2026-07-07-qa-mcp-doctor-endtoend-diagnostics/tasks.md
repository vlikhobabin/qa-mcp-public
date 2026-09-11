## Implementation

- [x] 1. Add the shared doctor implementation and CLI/MCP entry points.
  - [x] 1.1 Create a reusable Python doctor module that returns an ordered,
        secret-safe check chain and an overall verdict.
  - [x] 1.2 Expose `qa_mcp_doctor` through `src/qa_mcp/mcp_server.py`.
  - [x] 1.3 Add a CLI entry point that emits JSON and exits non-zero when the
        overall verdict fails.
- [x] 2. Add doctor checks and structured diagnostics.
  - [x] 2.1 Report proxy bearer-token environment presence as
        `token_env_present` without exposing the token.
  - [x] 2.2 Check host-agent reachability and container-to-host route by HTTP,
        not raw port enumeration.
  - [x] 2.3 Include platform discovery, TestClient TPort reachability, and the
        existing COM doctor link where configured.
  - [x] 2.4 Add an open-link-free TestClient smoke and wire doctor output to it.
  - [x] 2.5 Detect login/access-dialog stuck state and effective-user mismatch
        when evidence is available.
- [x] 3. Improve existing tool guidance.
  - [x] 3.1 Clarify `get_window_list_testclient` and form-level
        `open-link-required` guidance with an `e1cib/list/<metadata>` example.
  - [x] 3.2 Keep failures structured so a good attach plus missing `open_link`
        no longer looks like a connection failure.
- [x] 4. Add focused tests.
  - [x] 4.1 Cover healthy doctor output, missing bearer env, rejected bearer
        env, host-agent HTTP success on wildcard-style listener evidence,
        skipped COM, and failed TestClient smoke.
  - [x] 4.2 Cover login-dialog-stuck and effective-user mismatch result shape
        with offline fakes.
  - [x] 4.3 Cover CLI JSON output and failure exit code.
- [x] 5. Update docs for the one-command doctor and false-negative cases.

## Verification

- [x] 6. Run `openspec validate qa-mcp-doctor-endtoend-diagnostics --strict`.
- [x] 7. Run focused pytest for doctor/config/MCP server behavior.
- [x] 8. Run `uv run --with pytest --with pyyaml pytest`.
- [x] 9. Run `git diff --check`.
- [x] 10. Run the 1C verification matrix checker in preflight and archive-gate
      modes, retaining outputs under
      `.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/<run-id>/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `qa_mcp_doctor`, attach diagnostics, open-link-free TestClient smoke | Offline pytest with monkeypatched TestClient/session and structured result assertions | scenario_file, scenario_log, qa_testclient_bundle | `.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/20260707T202930Z/doctor-offline-evidence.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Model-B container/host-agent HTTP route, platform discovery, COM doctor link | Offline HTTP fake-server tests plus retained live-contour gap summary when Windows host is unavailable | source_preflight, scenario_log, runtime_apply_log | `.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/20260707T202930Z/model-b-doctor-evidence.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Managed form layout | Login/access dialog stuck-state distinction and effective-user reporting | Offline detection tests; real Windows login-dialog proof only when an operator-owned host is available | qa_testclient_bundle, active_window, screenshot | `.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/20260707T202930Z/login-dialog-gap.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Linux workspace has no attached Windows GUI/TestClient login-dialog contour; offline detection remains required, live screenshot proof is deferred. |
| BSL-only module edit | N/A | No BSL modules are changed by this Python/host-agent diagnostic work | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | No BSL source is edited. | None for this change. |

## Provider Gaps

| provider_id | owner_path | matrix_row | missing_capability | missing_evidence_type | impact | current_workaround |
| --- | --- | --- | --- | --- | --- | --- |
| qa-mcp | /opt/ai-dev-suite-for-1c/qa-mcp | Managed form layout | operator-owned Windows GUI/TestClient contour for login-dialog screenshot and effective-user proof | qa_testclient_bundle | blocks live screenshot proof for the managed-form row during this Linux delivery | implement offline detection with faked TestClient/window evidence and retain `.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/20260707T202930Z/login-dialog-gap.json` |

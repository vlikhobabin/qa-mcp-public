## Context

This change addresses the model-B verification failures captured in
`docs/qa-mcp-connection-issues-2.md`: raw port checks can lie when the
host-agent binds `[::]`, container-to-host reachability is only discovered after
calling a tool, proxy auth errors do not identify a missing bearer env var,
`get_window_list_testclient` can fail with `open-link-required` despite a good
TPort connection, and a wrong 1C `-User` can leave the client at the login
dialog while attach still looks successful.

The current Linux workspace can implement and test the Python/MCP behavior
offline. Real Windows host-agent, COMConnector, and login-dialog proof remain
operator-contour evidence unless that host is available during delivery.

## Decisions

- Implement `qa_mcp_doctor` as a small reusable Python module that the MCP tool
  and CLI both call. The module should return data, not print-only text, so
  tests can assert individual links.
- Check host-agent reachability through HTTP requests to existing endpoints
  (`/version`, `/health`, platform and COM doctor endpoints where configured).
  Do not add raw TCP port enumeration as the primary verdict source.
- Keep secret handling explicit: return presence booleans such as
  `token_env_present`, never token values.
- Add the open-link-free TestClient smoke as a protocol-level connection check.
  It should verify bootstrap/handshake reachability without requiring a
  managed-form GUID.
- Reuse existing attach-aware endpoint resolution and structured wrapper errors
  so the doctor does not create a second endpoint-selection model.
- Detect login/access dialog state using bounded TestClient/window evidence
  when available. If effective user cannot be queried on the current contour,
  report that link as skipped with a stable reason rather than guessing.
- Do not change host-agent authentication semantics or broaden COM execution;
  COM remains bounded to the existing doctor endpoint and read-only policy.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `qa_mcp_doctor`, attach diagnostics, open-link-free TestClient smoke | Offline pytest with monkeypatched TestClient/session and structured result assertions | scenario_file, scenario_log, qa_testclient_bundle | `.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/20260707T202930Z/doctor-offline-evidence.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Model-B container/host-agent HTTP route, platform discovery, COM doctor link | Offline HTTP fake-server tests plus retained live-contour gap summary when Windows host is unavailable | source_preflight, scenario_log, runtime_apply_log | `.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/20260707T202930Z/model-b-doctor-evidence.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Managed form layout | Login/access dialog stuck-state distinction and effective-user reporting | Offline detection tests; real Windows login-dialog proof only when an operator-owned host is available | qa_testclient_bundle, active_window, screenshot | `.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/20260707T202930Z/login-dialog-gap.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Linux workspace has no attached Windows GUI/TestClient login-dialog contour; offline detection remains required, live screenshot proof is deferred. |
| BSL-only module edit | N/A | No BSL modules are changed by this Python/host-agent diagnostic work | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | No BSL source is edited. | None for this change. |

### Provider Gap: Windows Login-Dialog Live Proof

| provider_id | owner_path | matrix_row | missing_capability | missing_evidence_type | impact | current_workaround |
| --- | --- | --- | --- | --- | --- | --- |
| qa-mcp | /opt/ai-dev-suite-for-1c/qa-mcp | Managed form layout | operator-owned Windows GUI/TestClient contour for login-dialog screenshot and effective-user proof | qa_testclient_bundle | blocks live screenshot proof for the managed-form row during this Linux delivery | implement offline detection with faked TestClient/window evidence and retain `.artifacts/openspec/qa-mcp-doctor-endtoend-diagnostics/20260707T202930Z/login-dialog-gap.json` |

## Risks

- A single doctor can be mistaken for a live proof of every link. The result
  must explicitly mark skipped and unsupported checks so users can see which
  links were not verified.
- Login-dialog/effective-user detection may be contour-specific. The offline
  implementation should keep stable result codes and leave live proof as a
  retained provider gap when no Windows host is present.
- Proxy-side bearer auth may live outside this repository in the suite proxy.
  qa-mcp can still report whether the expected bearer env var is present and
  document the distinction without changing proxy internals.

## Non-Goals

- No COM write/query expansion beyond the existing COM doctor.
- No live data mutation, posting, deployment, or debug instrumentation.
- No raw large captures or Windows screenshots committed to git.

## 1. Lifecycle Environment And Diagnostics

- [x] 1.1 Add lifecycle helpers that resolve `QA_MCP_TESTCLIENT_LIBGCC_PRELOAD`, autodetect supported system libgcc paths, and build a child environment without mutating `os.environ`.
- [x] 1.2 Apply the resolved child environment to both owned-display and `xvfb-run` launch paths and expose preload metadata in process status.
- [x] 1.3 Add bounded failed-launch diagnostics that include output directory, port, timeout, return code when available, and log tails from `client.out` / `testclient.out`.

## 2. Attach-To-Running Endpoint

- [x] 2.1 Add an attach handle for already-listening TestClient endpoints with `attached=true`, `owns_process=false`, and no external process termination.
- [x] 2.2 Expose the attach path through the MCP server and package exports while preserving existing launch/status/stop behavior.

## 3. Offline Tests

- [x] 3.1 Add lifecycle unit tests for libgcc autodetect, opt-out, override, and prepend behavior.
- [x] 3.2 Add lifecycle unit tests for timeout diagnostics and attach ownership semantics.
- [x] 3.3 Run focused offline verification: `uv run pytest tests/test_lifecycle.py tests/test_mcp_server.py`.

## 4. Runtime Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `launch_test_client` native Linux process lifecycle | Run Linux runtime preflight, then launch with managed cleanup when preflight passes | `source_preflight`, pytest summary, retained launch status/log summary | `.artifacts/openspec/testclient-launcher-libgcc-and-attach/20260626-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Preflight may report lab contention before a 1C process starts. |
| QA/TestClient UI automation | attach/session protocol drive through `TestClientSession` | Run read-only active-window or descriptor probe against launched or attached TPort | `qa_testclient_scenario`, `active_window` or `form_tree`, bounded run log | `.artifacts/openspec/testclient-launcher-libgcc-and-attach/20260626-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Verifies lifecycle/session access, not new frame semantics. |
| Business data mutation | object writes, posting, delete/fill/import/export | no business mutation is part of this lifecycle change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This change only launches or attaches to TestClient and runs read-only probes. | Residual risk is limited to process/runtime availability. |
| Windows-native verification | Windows launcher or host-agent path | no Windows process launcher is changed by this Linux lifecycle card | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change is Linux-native `1cv8` process env and attach-handle behavior; Windows host-launch work is tracked separately. | Windows users still rely on existing external host launch / remote-client flow. |

- [x] 4.1 Run OpenSpec validation and `git diff --check`.
- [x] 4.2 Run Linux runtime preflight before any live launch/probe; record a `runtime_gap` if it fails before starting 1C.
- [x] 4.3 When preflight passes, run `tools/protocol-research/run_lifecycle_test.sh` or an equivalent read-only launch/status/probe/stop sequence and retain bounded evidence.
- [x] 4.4 Confirm no evidence-index update is needed because the change makes no new protocol frame claim; retain runtime artifacts under ignored paths only.

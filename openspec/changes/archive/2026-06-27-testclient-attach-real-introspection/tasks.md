## 1. Attached Session Route

- [x] 1.1 Add an in-process attached endpoint context for `attach_test_client` that preserves external ownership
      and exposes non-secret active endpoint status.
- [x] 1.2 Add a central MCP session resolver/factory that prefers the active attached endpoint when no explicit
      host/port override is supplied and fails closed when the attached endpoint is unavailable.
- [x] 1.3 Route descriptor, value-read, scenario and replay-backed write session creation through the resolver
      without changing the low-level `TestClientSession` API.
- [x] 1.4 Add attach/bootstrap/open/descriptor diagnostic fields so attached descriptor failures do not collapse
      to an unexplained empty `{opened:null, fields:{}}` result.

## 2. Offline Tests

- [x] 2.1 Add lifecycle/MCP tests proving `attach_test_client` records an active non-owned endpoint and cleanup
      still refuses to kill it.
- [x] 2.2 Add descriptor tests proving attached endpoint routing is used by default and explicit host/port
      parameters override it.
- [x] 2.3 Add write/scenario factory tests proving replay-backed write tools can resolve the attached endpoint
      route while preserving existing write/action safety results.
- [x] 2.4 Run focused offline verification:
      `uv run pytest tests/test_lifecycle.py tests/test_mcp_server.py tests/test_form_descriptor.py`.

## 3. Runtime Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Out-of-band TestClient attach feeding `read_form_descriptor` and value-read/write session factories | Attach a listening endpoint, then run descriptor through the attached context; offline tests prove write/session factory routing | `qa_testclient_scenario`, `form_tree` or descriptor summary, bounded run log, pytest summary | `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live preflight may report lab contention before starting or attaching 1C. |
| Delivery or runtime apply | Linux runtime preflight and externally owned TestClient cleanup boundary | Run preflight before any live attach/probe; stop only owned processes from the proof harness | `source_preflight`, retained cleanup summary | `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | External clients are intentionally not killed by qa-mcp cleanup. |
| Business data mutation | Create/fill/save proof through an attached endpoint | Keep live mutation behind existing safe write/recovery policy; verify route offline unless a reviewed mutation manifest exists | offline pytest for route; optional `qa_testclient_bundle` with cleanup evidence if executed | `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | The card unblocks the route; live mutation remains higher risk without recovery evidence. |
| Windows-native verification | Windows host or COM launch path | No Windows launcher or host-agent behavior changes | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This Linux-native attach/session change does not modify Windows process launch or host-agent code. | Windows out-of-band clients still rely on explicit host/port or future host-agent evidence. |

- [x] 3.1 Run matrix preflight before implementation and retain `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/matrix-preflight.json`.
- [x] 3.2 Run Linux runtime preflight before any live attach/probe; record `runtime_gap` if it fails before starting
      or attaching a 1C process.
- [x] 3.3 When preflight passes, start a TestClient out-of-band, call `attach_test_client`, then run
      `read_form_descriptor(open_link=..., enumerate_live=true)` through the attached route and retain a bounded
      descriptor summary.
- [x] 3.4 Run matrix archive gate and retain `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/matrix-archive-gate.json`.

## 4. OpenSpec And Evidence

- [x] 4.1 Run `openspec validate testclient-attach-real-introspection --strict`.
- [x] 4.2 Run `git diff --check`.
- [x] 4.3 Sync the delta spec into `openspec/specs/qa-mcp-protocol-lab/spec.md`.
- [x] 4.4 Confirm no evidence-index update is needed unless implementation discovers a new protocol frame claim.

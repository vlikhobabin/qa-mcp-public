## Context

`attach_test_client` stores an attached endpoint, but only a subset of tools call `_resolve_testclient_endpoint`. Tools that omit this helper silently use their default host/port values. The same boilerplate also repeats capture resolution, attach-error shaping and `attached_endpoint` annotation across many tools.

## Design

Add a small decorator near `_local_only_tool` in `src/qa_mcp/mcp_server.py`:

- Use `functools.wraps` so FastMCP keeps the wrapped function metadata.
- Resolve `host`, `port` and the attachment snapshot through `_resolve_testclient_endpoint`.
- Optionally resolve a `capture` argument to `capture_dir` via `resolve_capture_dir(capture, _repo_root())`.
- Convert attach resolution errors, invalid captures and invalid arguments into the existing structured result envelope.
- Annotate dict results with `attached_endpoint` when an attachment was used.
- Compose local-only and local-boot guard behavior for tools such as `measure_scenario`.
- Pass through already-structured write/replay outcomes, including `retarget_failed` and `send_timeout`, without replacing them with a generic error.

The decorator should pass resolved values into the tool body by keyword, for example `_host`, `_port`, `_capture_dir`, and `_attachment`, so registered MCP arguments remain unchanged. Tool bodies that are also called internally should have the shared work extracted to a plain helper before being decorated, to avoid internal calls unexpectedly going through remote-mode guards.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation tool surface | Endpoint-touching tools in `src/qa_mcp/mcp_server.py`, including replay/action/list/dialog/report/window tools | Offline monkeypatched connector tests and registry scan; no live UI action execution | `qa_testclient_scenario` as offline contract-test summary, `junit_report` or pytest output | `.artifacts/openspec/testclient-tool-decorator/<run-id>/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | No 1C metadata/runtime apply, deployment, or live infobase mutation | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | Change is Python MCP server behavior only and is offline-testable. | Live runtime regressions remain possible but are outside this low-risk tool-contract fix. |

## Notes

The implementation should reduce endpoint boilerplate, but behavioral correctness is more important than forcing every one-line helper through the decorator in the first pass. Any endpoint-touching tool left undecorated must be covered by the follow-up contract test or called out explicitly.

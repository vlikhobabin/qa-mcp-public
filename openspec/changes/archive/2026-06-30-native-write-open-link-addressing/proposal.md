## Why

`read_form_descriptor(open_link=...)` can open and inspect arbitrary managed forms without a per-form capture, but `write_form_value` and `write_form_values` still replay fixture setup frames before retargeting field leaves. That blocks UI writes against a new configuration object such as the `demo10413` contract catalog create form.

## What Changes

- Add an `open_link` write-session setup path that opens and resolves the target form before write blocks run.
- Let MCP write tools report the opened form/nav-link together with field write results.
- Keep capture-backed fixture setup as the default when `open_link` is omitted.
- Add offline tests for open-link setup selection and field-addressing behavior.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: native write tools can address fields on arbitrary forms opened by nav-link, with evidence requirements for live protocol claims.

## Impact

- Touches Python manager code under `src/qa_mcp/protocol/` and `src/qa_mcp/mcp_server.py`.
- Touches MCP tool behavior for native write helpers.
- Requires offline Python tests first, then Linux-native TestClient live evidence before claiming runtime completion.
- Does not depend on Vanessa MCP, EDT/meta snapshots, or raw capture commits.

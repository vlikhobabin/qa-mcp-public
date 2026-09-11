## Why

The public `open_list` tool defaults to a historical development capture name
that is absent from released runtimes, so a correctly attached live TestClient
can fail before navigation begins. The shipped endpoint must instead use a
versioned bundled navigation path and report unavailable assets before any
protocol write.

## What Changes

- Make omitted `capture` select the supported bundled live-navigation path
  rather than a development capture or `/work/traffic.jsonl`.
- Preserve an explicit bundled-capture compatibility path for callers that
  still select a concrete navigation template.
- Return a typed capability diagnostic when an optional navigation asset is
  unavailable, before opening or writing to the TestClient socket.
- Add focused MCP endpoint tests for omitted capture, explicit bundled
  template, missing assets, and attached-endpoint routing.
- Retain bounded live TestClient evidence because the change affects the real
  remote navigation path; no new capture, Vanessa MCP, EDT/meta snapshot, MCP
  provider setup, OpenSpec workflow, or runtime-lab configuration is required.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: Define capture-free `open_list` defaults,
  explicit bundled-template compatibility, and pre-write asset diagnostics.

## Impact

- Python MCP endpoint and protocol navigation helpers under `src/qa_mcp/`.
- Focused endpoint/protocol tests under `tests/`.
- The public `open_list` tool schema changes its `capture` default from a
  historical string to an omitted/optional compatibility selector.
- Runtime behavior remains read-only/safe-navigation and reuses already shipped
  versioned protocol assets.

# Design

The migration changes only the MCP framework boundary:

- import `FastMCP` from standalone `fastmcp`;
- keep the same module-level `mcp = FastMCP("qa-native-manager")` registration
  surface;
- replace the SDK-bundled `streamable_http_app()`/`mcp.settings` path with
  FastMCP 3 `http_app(path="/mcp", transport="streamable-http")` and explicit
  uvicorn host/port settings from qa-mcp configuration;
- keep stdio as the default transport with `show_banner=False`;
- normalize registered FastMCP 3 tool schema metadata so `tools/list` preserves
  the pre-migration titles, descriptions, open input-object shape and output
  schema titles captured in before evidence.

The compatibility normalizer is intentionally local to qa-mcp because this
provider has the largest public tool surface and already promises no schema
drift for this final migration. It does not wrap domain handlers or change
runtime protocol behavior.

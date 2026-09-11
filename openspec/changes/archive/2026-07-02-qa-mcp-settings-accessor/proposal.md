## Why

`QA_MCP_*` environment variables are read in scattered locations, with some
values frozen at import time and others parsed per call. A single settings
accessor makes environment policy observable and avoids duplicated boolean and
ODATA default parsing.

## What Changes

- Add `qa_mcp.config.Settings.from_env()` documenting and parsing the supported
  `QA_MCP_*` variables in one place.
- Route remote-client truth parsing, ODATA defaults and version-injection
  helpers through the shared settings/accessor path.
- Migrate call sites incrementally without changing the public CLI, MCP
  arguments or default values.
- Keep this as Python manager/runtime configuration code only. It does not
  change OpenSpec workflow or 1C metadata.

## Capabilities

### New Capabilities

- `qa-mcp-runtime-configuration`: centralized runtime configuration parsing for
  qa-mcp environment variables and defaults.

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: remote-client local-only gating continues to
  use the same truth semantics after moving to the settings accessor.

## Impact

- Affected code: `src/qa_mcp/config.py`, modules reading `QA_MCP_*`, OData
  defaults and remote-client guards.
- Affected tests: configuration/unit tests, endpoint local-only tests and full
  `uv run pytest -q`.
- Live 1C runtime is not required; this change is verified offline with
  environment-isolated tests.

## Why

Protocol modules currently import `active_version_key()` lazily from
`regression.versioning` to avoid a dependency cycle. Version selection is shared
runtime policy and should live in a leaf module that protocol code can import
normally.

## What Changes

- Add a leaf `qa_mcp.versioning` module for active platform-family selection and
  live platform detection helpers.
- Re-export the moved helpers from `regression.versioning` for compatibility.
- Replace protocol-side lazy imports and cycle comments with normal top-level
  imports from the leaf module.
- Preserve `_bundled/<family>/` selection behavior, accepted
  `QA_MCP_PLATFORM_VERSION` values and fail-closed unsupported-version behavior.
- Keep this as Python manager/protocol code only. It does not change MCP
  provider setup, OpenSpec workflow, runtime lab configuration or 1C metadata.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: protocol version-family selection is importable from a
  cycle-free leaf module while preserving existing platform selection behavior.

## Impact

- Affected code: `src/qa_mcp/versioning.py`,
  `src/qa_mcp/regression/versioning.py` and protocol modules that select bundled
  captures/assets.
- Affected tests: versioning tests, protocol bootstrap/evidence tests and full
  `uv run pytest -q`.
- Live 1C runtime is not required unless existing live-regression is available
  for an optional unchanged-behavior proof.

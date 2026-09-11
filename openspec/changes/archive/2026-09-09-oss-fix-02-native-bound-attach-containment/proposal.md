## Why

Project-bound attach can promote endpoint reachability or a remote PID/port
check into trusted target provenance without observing the actual infobase.
Contain that path before continuing the product corrections following OSS-FIX-01.

## What Changes

- Reject non-owned bound attach when current target/generation observation is
  absent, mismatched or stale, before admitting a session or sending UI commands.
- Preserve validated owned launch and explicit standalone attach.
- Document that general non-owned bound attach remains unavailable until an
  independently reviewed observer can prove identity; do not invent an observer.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-target-bound-testclient-lifecycle`: require observed target provenance
  before admitting a non-owned project-bound attachment.

## Impact

The existing `src/qa_mcp/mcp_server.py` and `src/qa_mcp/core/runtime_target.py`
boundaries, their lifecycle/MCP regression tests, and lifecycle documentation.
Verification is offline with synthetic endpoints; Linux/Windows runtime
qualification remains separately owned by OSS-FIX-11/12. This change depends on
the final reviewed OSS-FIX-01 product baseline and does not finalize its old run.

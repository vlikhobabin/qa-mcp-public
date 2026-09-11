## Why

On published FIX-07, the shared executor promotes a pre-existing unrelated file
inside the admitted root, with a false well-formed digest, as current evidence.
The receipt is minted from result data after execution, without trusted production.

## What Changes

- Bind receipts to actual trusted screenshot production in the current application
  operation; raw executor artifact claims cannot create authority.
- Verify owned destination, content hash and current file identity before success,
  retaining sanitized metadata after removal of only the owned raw capture.
- Preserve exact refusal taxonomy, concurrent scope isolation, public privacy and
  useful deliberately unbound standalone screenshot behavior.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `qa-mcp-positive-core-operation-boundary`: trusted production and content-bound artifact receipts.
- `qa-mcp-positive-operation-boundary-public-integration`: real shared default capture producer and concurrent isolation.
- `qa-mcp-target-bound-evidence-cleanup`: cleanup only current owned screenshot production.

## Impact

core/boundary.py, core/operations.py, mcp_server.py, core/contracts.py only if needed;
focused trusted-artifact tests and affected screenshot/boundary/public consumers;
consumer documentation and three canonical specs. No live I/O, protocol change,
ChangeRail work, storage service, signing system or general producer registry.

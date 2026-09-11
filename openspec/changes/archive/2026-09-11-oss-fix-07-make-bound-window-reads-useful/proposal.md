## Why

The real ActiveWindowContext result contains no fields admitted by the current
read_active_window success schema, so a bound read becomes success/value={};
ScenarioRunner then evaluates expectations against that redacted empty payload.
A real matching window predicate consequently fails on the published baseline.

## What Changes

- Define a bounded operation-specific active-window observation with safe state
  and count fields derived from the actual DTO, preserving missing/ambiguous states.
- Evaluate an explicitly requested expected-window predicate against the internal
  window reference/markers before public normalization; publish only safe outcome.
- Keep malformed/oversized executor data, provenance, artifact receipt and positive
  reconstruction protections while separating generic scalar-class tests from the
  production active-window schema.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-shared-core-extension`: useful private-safe active-window reads and
  assertions through the actual default handler and shared operation.
- `qa-mcp-positive-core-operation-boundary`: operation-specific safe active-window
  fields with unchanged positive class, size, provenance and receipt protections.
- `qa-mcp-positive-operation-boundary-public-integration`: ScenarioRunner evaluates
  the requested window predicate before sanitized public result serialization.

## Impact

src/qa_mcp/core/boundary.py, core/operations.py, mcp_server.py and scenario/runner.py;
focused active-window acceptance and directly affected boundary/scenario tests;
consumer docs and the three governing specs. No new query, native protocol claim,
live action, artifact authority redesign or default single-session BDD delivery
(the latter remains FIX-09A).

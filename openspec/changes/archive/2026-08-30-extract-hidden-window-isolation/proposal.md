## Why

The published hidden worker lifecycle owns an exact Windows worker, job and
TPort listener, but later direct-execute stages still lack a reusable,
independently reviewable proof that run-owned windows stay off the operator
desktop and that one exact class/owner surface can be selected fail-closed.

## What Changes

- Add a dormant, read-only hidden/default desktop window inventory.
- Add exact PID/job/class/owner admission with hostile ambiguity refusal.
- Add sanitized isolation receipts and source/runtime proof of zero global
  input or desktop switching.
- Add portable hostile tests and exact-source Windows synthetic and real 1C
  TestClient verification without activating a public route or UI action.

## Capabilities

### New Capabilities
- `qa-mcp-hidden-window-isolation`: Exact hidden/default Win32 window inventory,
  fail-closed window identity selection and sanitized zero-input receipts.

### Modified Capabilities
- none.

## Impact

Only four new dormant Go source/test files, one new capability spec, OpenSpec
artifacts and ignored sanitized evidence are affected. No protocol tool,
Python manager, MCP provider/profile, wire schema or runtime lab configuration
changes. Offline tests cover policy and hostile inputs; exact Windows proof
requires the trusted host, platform `8.3.27.2214` and declared
`vanessa_client`, but sends no 1C UI action and requires no Vanessa/EDT/meta
provider.

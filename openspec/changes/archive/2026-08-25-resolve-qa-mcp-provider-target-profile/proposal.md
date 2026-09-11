## Why

The public contract is not useful until qa-mcp can reconcile the frozen project
handoff with exactly one ignored provider profile. Resolution must be typed,
closed and non-mutating before later application or lifecycle integration.

## What Changes

- Parse the closed provider profile from an allowlisted regular local file.
- Reconcile logical target, kind, fingerprint, principal, receipt, generation
  and binding reference with the frozen handoff.
- Enforce `sanitized` and explicitly approved `full_local` evidence policies.
- Return secret-safe typed failures for partial, malformed, stale or mismatched
  input without starting runtime resources.

## Capabilities

### New Capabilities
- `qa-mcp-runtime-target-adapter`: Standalone resolution of the frozen project
  handoff into one provider-local target binding.

### Modified Capabilities
- None.

## Impact

Python adapter code and offline tests change. There is no dependency on
`agent-core`, admin-mcp or live-mcp packages; only their frozen wire values are
consumed. No protocol mapping or live 1C execution is required.

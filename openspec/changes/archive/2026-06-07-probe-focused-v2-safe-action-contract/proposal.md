## Why

The V2 safety contract forbids promoting a safe-action row from frame join alone.
The first focused proof must attempt replay, direct Python-manager probe or
typed contract validation and record whether the row is accepted or remains
candidate.

## What Changes

- Choose the feasible proof route for each focused row after frame isolation:
  replay, direct Python-manager probe or typed contract validation.
- Retain compact proof artifacts with normalized hash, dynamic fields, operation
  token, request/response sizes and action result markers where available.
- Keep rows non-accepted when proof is infeasible, incomplete or fails.
- Preserve raw replay/probe payloads under ignored runtime paths.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: The first focused V2 safe-action proof records an
  explicit replay/probe or typed-contract proof decision before accepted status
  is used.

## Impact

- Existing replay/probe tooling, Python manager proof paths or typed contract
  evidence summaries.
- Compact evidence under
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/` and
  `.artifacts/openspec/probe-focused-v2-safe-action-contract/<run-id>/`.
- May require a live TestClient or replay environment depending on proof route;
  no business-data mutation is allowed.

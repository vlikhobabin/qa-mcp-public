## Why

After the manager V2 runner can execute and recover safe actions, the project
needs compact candidate evidence that downstream focused proof can review
without committing raw captures. Publication must keep candidate and accepted
states separate.

## What Changes

- Publish compact manager fixture V2 safe-action candidate evidence from live
  or reviewed runs.
- Link action, background and recovery ranges, normalized hash fields, result
  markers and replay/probe or typed-contract status where available.
- Keep rows non-accepted unless all V2 acceptance gates are satisfied.
- Update docs/evidence index or runner docs so the first focused proof can
  consume the candidate set.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: Manager fixture V2 safe-action candidate evidence is
  published with explicit non-accepted or accepted status and compact proof
  links.

## Impact

- Protocol research evidence docs and V2 reporter outputs.
- Potential focused tests for reporter/comparison behavior.
- Raw captures, platform logs and generated replay payloads remain ignored.

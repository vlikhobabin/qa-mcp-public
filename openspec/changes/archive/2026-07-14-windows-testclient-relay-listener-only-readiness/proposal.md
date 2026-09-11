## Why

The authenticated relay has one fixed single-manager target. The generic
`port_is_listening` probe currently uses the authenticated connector, so status
and readiness tools can open and discard that target before a real protocol
session. Independent ChangeRail review classified this as a publication
blocker.

## What Changes

- Make generic lifecycle probes use TCP-only reachability for the exact
  configured relay listener.
- Preserve authenticated relay access for real TestClient protocol sessions.
- Add regressions for lifecycle and public status/info/state paths.

## Capabilities

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: relay readiness and status probes do not
  consume the single-manager target.

## Impact

This change is confined to `qa-mcp` lifecycle probing, focused Python tests,
the synced endpoint contract and this card. It performs no runtime mutation;
live proof is owned by the subsequent root T4 rerun.

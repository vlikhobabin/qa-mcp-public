## Why

The V2 safe-action surface is only useful if every allowed action can be
recovered back to the V1 baseline. The fixture therefore needs a recovery
verification change that proves reset and frame-range isolation after each
safe action.

## What Changes

- Add recovery verification criteria for each safe-action case.
- Require before, action, post and recovery markers plus reset result
  evidence.
- Separate candidate action frame ranges from bootstrap, refresh and cleanup
  traffic.
- Keep recovery local to the fixture and fail closed if the baseline cannot be
  restored.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V2 fixture recovery evidence and capture isolation are
  now explicit planning requirements.

## Impact

- Protocol research evidence bundles and compact review notes.
- Future capture and runner work that consumes the recovered fixture surface.
- Requires live 1C runtime evidence for verification.

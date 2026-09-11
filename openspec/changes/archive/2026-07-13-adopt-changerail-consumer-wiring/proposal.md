# Change: Adopt canonical ChangeRail consumer wiring

## Why

The qa-mcp repository still exposes obsolete OPSX links and broken `/opt/opsx`
OpenSpec skill targets. Canonical ChangeRail workflows therefore cannot be
discovered reliably from this component, and the fail-closed consumer verifier
passes only 9 of 43 checks.

## What Changes

- Replace generic Claude/Codex workflow links with canonical ChangeRail,
  `chrl`, and OpenSpec links from `/opt/changerail`.
- Add canonical OpenSpec, verdict, and verifier helpers under `bin/`.
- Preserve the ownership boundary for AI1C domain overlays and qa-mcp project
  skills instead of treating them as ChangeRail-owned content.
- Align component instructions, board flow, runtime/auth ignore policy, and
  local generated MCP profiles with the verifier contract.

## Capabilities

### New Capabilities
- `changerail-consumer-wiring`: Defines how qa-mcp discovers and verifies the
  suite-shared ChangeRail lifecycle without publishing local provider state.

### Modified Capabilities
- None.

## Impact

- Public-safe repository wiring, agent guidance, board documentation, and
  OpenSpec artifacts are committable.
- Local ignored `.mcp.json` and `.codex/config.toml` receive only the filesystem
  scope needed by the verifier and remain outside publication.
- No qa-mcp runtime, host-agent source, protocol behavior, or live 1C state is
  changed.

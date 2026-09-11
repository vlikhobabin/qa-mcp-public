## Why

qa-mcp currently registers one unconditional MCP surface around import-time
settings and mixes shared protocol behavior with product-specific transports.
The new public-upstream/private-downstream model needs one stable extension
boundary so standalone and AI for 1C can evolve without a source fork.

## What Changes

- Add an application factory that composes settings, executor, tool profile and
  optional integrations.
- Define public executor, target/session, result/error and artifact contracts.
- Register tools through explicit standalone and research profiles.
- Adapt existing local and Windows-bridge paths to the shared contracts without
  changing supported operation semantics.
- Add downstream contract fixtures and an upstream-first extension policy.
- Provide the generic immutable target/session model seam required by the
  follow-up runtime-target binding card without implementing project-descriptor
  binding in this change.

## Capabilities

### New Capabilities
- `qa-mcp-shared-core-extension`: Public composition, executor and profile
  contracts shared by standalone qa-mcp and downstream products.

### Modified Capabilities
- none.

## Impact

Touches Python manager code, MCP provider setup, tests and architecture docs.
It does not change protocol frame claims and needs offline contract evidence;
live Linux/Windows regression is required before release because executor
routing changes. Vanessa MCP and EDT/meta snapshots are not required.
The separate runtime-target binding story starts after this foundation and the
shared descriptor contract are ready.

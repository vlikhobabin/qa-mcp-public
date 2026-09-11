## Context

qa-mcp combines repository-specific protocol/runtime guidance, AI1C domain
skills, and generic development workflow tooling. Only the generic workflow is
owned by `/opt/changerail`; the other layers must not be deleted or copied into
ChangeRail.

The component's full-provider MCP profiles are generated local development
state and are intentionally ignored. They contain machine-specific suite paths,
so adoption must satisfy local verification without turning them into release
payload.

## Goals / Non-Goals

**Goals:**
- expose every canonical ChangeRail/`chrl`/OpenSpec discovery surface;
- remove obsolete generic OPSX wiring;
- preserve project/domain ownership boundaries;
- pass the canonical 43-check verifier;
- keep local provider profiles and auth/runtime state uncommitted.

**Non-Goals:**
- modify host-agent, MCP provider, protocol, or 1C runtime behavior;
- deliver the separate display-bridge version-forward-compat story;
- rewrite historical done/archive evidence.

## Decisions

### Canonical generic workflow links

Claude uses `/opt/changerail/skills` plus the `changerail` and `chrl` command
directories. Codex receives individual `changerail-*`, `chrl-*`, and
`openspec-*` links. Obsolete `opsx-*` and `/opt/opsx` links are removed.

### Narrow `.codex` tracking exceptions

The existing broad `.codex/` ignore remains the default for local config and
auth state. `.gitignore` permits only canonical generic skill links to appear
as committable paths; project/domain skill material remains under its existing
owner and is not swept into this migration.

### Local profile verification without publication

The ignored full-provider profiles receive an exact-pinned filesystem MCP
entry scoped to the qa-mcp root. This satisfies the local consumer gate while
preserving the component's machine-specific profile policy.

## Risks / Trade-offs

- A fresh checkout must render its normal component-local provider profile
  before running the full verifier. This is already the qa-mcp profile model.
- Absolute links depend on the documented Linux suite layout at
  `/opt/changerail`.

## Verification

The canonical project verifier must pass 43/43, strict OpenSpec validation must
pass, both ignored profiles must parse, and an alternate Git index must prove
whitespace cleanliness for every committable manifest path without changing
the real index.

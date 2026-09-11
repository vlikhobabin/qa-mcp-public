## Context

The existing protocol lab already separates wire evidence from semantic
metadata. `docs/protocol-research/corpus-evidence-contract.md` permits
`help-mcp`, `meta-mcp` and `edt-mcp` as semantic enrichment, and the main
`qa-mcp-protocol-lab` spec states that semantic metadata does not replace
capture, normalization or replay evidence.

The missing piece is an operator-facing inventory of approved source locations
and provider boundaries for the demo lab. The current infrastructure evidence
names the `demo10413` metadata build and the available MCP providers, but it
does not define where EDT workspaces or metadata snapshots belong, how their
readiness is recorded, or how provider gaps should be routed.

## Goals / Non-Goals

**Goals:**

- Define one compact document for semantic source inventory and provider
  boundary policy under `docs/protocol-research/`.
- Record approved external locations for EDT workspaces, metadata snapshots and
  generated fixture outputs without committing those generated artifacts.
- Preserve provider readiness evidence as compact summaries linked from the
  evidence index.
- Make provider unavailability explicit with owner and residual risk instead
  of blocking raw protocol capture or replay.

**Non-Goals:**

- Do not change the MCP profile, provider implementations or local credentials.
- Do not require live TestClient, Vanessa MCP or 1C TestManager execution.
- Do not treat metadata, help or EDT data as protocol proof.
- Do not commit EDT workspaces, full infobase exports, Qdrant/Postgres
  snapshots, raw captures or provider payload dumps.

## Decisions

- Keep the inventory in protocol research docs, not runtime config. This keeps
  the reviewed policy committable while external workspace paths and raw
  provider output stay outside git. Alternative: store the inventory in a
  runtime JSON file. That would make it easy to regenerate but poor for
  review.
- Link to compact evidence rather than embedding provider responses. The
  source inventory should name provider id, owner, configuration/build and
  intended use, but full metadata/help results belong in ignored runtime paths
  or provider stores. Alternative: paste source extracts into the doc. That
  would risk stale or oversized evidence.
- Treat provider failures as semantic-source gaps. Raw capture,
  normalization, replay and direct Python-manager probing must still run when
  the optional semantic layer is unavailable. Alternative: make provider
  readiness mandatory before corpus capture. That would violate the current
  source-of-truth boundary.

## Risks / Trade-offs

- Source paths can become machine-specific. Mitigation: record lab baseline
  locations separately from the policy and allow unresolved path rows with
  residual risk.
- Provider readiness can drift after evidence is recorded. Mitigation: require
  each readiness summary to include run id, provider id and build/version when
  available.
- Semantic labels can be overtrusted. Mitigation: repeat the primary-wire
  evidence rule in the source inventory and keep acceptance requirements tied
  to capture/replay/probe evidence.

## Migration Plan

No runtime migration is required. Implementation should add the source
inventory, link compact readiness or skipped-provider evidence from the
evidence index, and leave existing corpus rows unchanged unless later changes
add semantic mapping references.

## Open Questions

- The exact EDT workspace path may be unresolved during implementation. If so,
  record it as a provider/local-lab gap with owner and residual risk rather
  than inventing a path.

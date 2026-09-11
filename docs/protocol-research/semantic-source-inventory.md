# Semantic Source Inventory

This inventory defines which optional semantic and support sources may label,
select or contextualize protocol corpus cases in the qa-mcp lab. These sources
can explain 1C object model terms, forms, element families, controlled source
changes, diagnostics, platform command evidence and read-only side-channel
checks, but they do not prove native TestManager/TestClient protocol behavior.

Primary protocol evidence remains:

- captured manager-to-client and client-to-manager frames;
- normalized dynamic fields and normalized request hashes;
- response markers;
- replay or direct Python-manager probe status.

Raw TCP capture, normalization, replay and direct Python-manager probing must
remain usable when every semantic provider below is unavailable.

## Reviewed Readiness Evidence

Current profile wiring:
`.mcp.json`, `.codex/config.toml` and `AGENTS.md`.

Historical compact readiness summary:
`docs/protocol-research/evidence/semantic-sources/20260603-opsx-do-semantic-sources/source_readiness.md`.

Earlier infrastructure evidence:
`docs/protocol-research/evidence/infrastructure-checks/20260602-161326/infra_check.md`.

## Source Inventory

| Provider | Owner route | Current source/build | Allowed use | External boundary | Readiness evidence |
| --- | --- | --- | --- | --- | --- |
| `help-mcp` | `/opt/ai-dev-suite-for-1c/help-mcp` | Platform help default version `8.5.1.1343` in `.mcp.json` | Label tested object-model terms and select candidate API families | Help collections, Qdrant data and provider payloads stay outside reviewed git changes | `.mcp.json`; historical summary `docs/protocol-research/evidence/semantic-sources/20260603-opsx-do-semantic-sources/source_readiness.md` |
| `meta-mcp` | `/opt/ai-dev-suite-for-1c/meta-mcp` | Configuration id `qa_mcp`; metadata store rooted under `/opt/ai-dev-suite-for-1c/meta-mcp/data` | Inspect form, element and configuration metadata for corpus semantic mapping | Metadata store snapshots, Postgres/Qdrant data and raw provider payloads stay outside reviewed git changes | `.mcp.json`; `AGENTS.md` |
| `config-mcp` | `/opt/ai-dev-suite-for-1c/config-mcp` | Component-local controlled source authoring provider | Controlled fixture/source authoring, import planning and structural validation summaries | Source dumps, generated projects, import artifacts and raw provider payloads stay outside reviewed git changes unless a compact summary is curated | `.mcp.json`; `AGENTS.md` |
| `bsl-mcp` | `/opt/ai-dev-suite-for-1c/bsl-mcp` | Read-only BSL diagnostics provider | Diagnostics and changed-file analysis for BSL touched by fixture/source changes | Diagnostic caches and raw provider payloads stay outside reviewed git changes | `.mcp.json`; `AGENTS.md` |
| `admin-mcp` | `/opt/ai-dev-suite-for-1c/admin-mcp` | Platform command planning/execution provider | Platform command planning, validation and retained command evidence when a workflow needs it | Command logs, platform output, infobase exports and local runtime output stay outside reviewed git changes unless curated as compact evidence | `.mcp.json`; `AGENTS.md` |
| `live-mcp` | `/opt/ai-dev-suite-for-1c/live-mcp` | Read-only `vanessa_client` access via OData and HTTP-service | Read-only side-channel data checks and DCS/query evidence; not a protocol proof substitute | Live connection env, credentials, raw payloads and large result sets stay outside reviewed git changes | `.mcp.json`; `AGENTS.md` |

## Generated Output Policy

Reviewed changes may include compact Markdown or JSON summaries under
`docs/protocol-research/evidence/`. They must not include:

- full EDT workspaces;
- full infobase exports;
- raw provider payload dumps;
- Qdrant, Postgres or metadata-store snapshots;
- raw protocol captures or generated replay payloads;
- local credentials, target env contents or platform logs.

Generated or local runtime output belongs under ignored paths such as
`runtime/`, `.runtime/`, `.ai1c/` or provider-owned stores outside this
repository.

## Provider Gap Policy

When a semantic source is unavailable, record a compact provider gap with:

- provider id and owner route;
- affected semantic use;
- missing capability or failure mode;
- current workaround;
- impact on the current protocol delivery;
- sanitized evidence path;
- residual risk.

The gap does not block raw protocol capture, normalization, replay or direct
Python-manager probing unless the current change explicitly requires that
semantic source for fixture authoring or mapping.

## Use By Protocol Artifacts

Corpus rows may use the existing optional `semantic_sources` field to point at
help, metadata, source-authoring, BSL diagnostic, platform-admin or read-only
runtime references. Semantic mapping artifacts may also link this inventory and
the compact readiness evidence. In both cases, the row or mapping must still
link the primary wire evidence path that supports any protocol claim. Legacy
`edt-mcp` references are retained only in dated evidence and roadmap material.

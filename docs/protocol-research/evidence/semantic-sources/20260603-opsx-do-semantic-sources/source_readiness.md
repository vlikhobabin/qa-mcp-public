# Semantic Source Readiness 20260603-opsx-do-semantic-sources

Date: 2026-06-03.

This compact summary records the semantic-source readiness used while applying
`document-edt-meta-semantic-sources`. No live provider calls were made during
this delivery step; the summary reuses the curated infrastructure check from
2026-06-02 and the current project profile preflight.

## Inputs

- Existing readiness evidence:
  `docs/protocol-research/evidence/infrastructure-checks/20260602-161326/infra_check.md`.
- Current AI1C profile manifest:
  `.ai1c/profile-manifest.json`.
- OPSX trace id:
  `trc_087918945ede462bad9eaf42b7884651`.

## Provider Summary

| Provider | Owner route | Status | Evidence | Notes |
| --- | --- | --- | --- | --- |
| `help-mcp` | `/opt/finshtab-1c` | referenced-ready | 2026-06-02 infrastructure check | Default local platform help version was `8.3.27.1786`. |
| `meta-mcp` | `/opt/finshtab-1c` | referenced-ready | 2026-06-02 infrastructure check | Runtime status was `ready` for configuration `demo10413`, build `2026-05-24T000000Z-demo10413-edt`. |
| `edt-mcp` | `/opt/edt-lab` | referenced-ready | 2026-06-02 infrastructure check | Listed local infobases including `vanessa_manager`; use remains limited to controlled fixture authoring and validation. |
| `vanessa-mcp` | `/opt/vanessa-mcp-stack` | telemetry-gap | current profile preflight | Active provider is unproxied; this is expected while Vanessa proxying is unsupported and does not affect this docs-only source inventory. |

The current profile manifest has `proxy_mcp: false` and an empty
`proxied_providers` list. OPSX trace preflight recorded unproxied active
providers as degraded telemetry. This delivery did not require live provider
calls, UI actions, runtime apply or direct TestClient execution.

## Boundaries

- No raw provider payloads were captured or committed.
- No EDT workspace, generated fixture output, infobase export, Qdrant snapshot
  or Postgres snapshot was committed.
- Protocol capture, normalization, replay and direct Python-manager probing
  remain independent from these semantic providers.

## Residual Risk

- Readiness can drift after the 2026-06-02 infrastructure check. Future mapping
  or fixture work should record a fresh compact provider summary when it uses
  live provider results.
- The exact external EDT workspace path may remain machine-specific; fixture
  changes must record a provider/local-lab gap when that path is unavailable.

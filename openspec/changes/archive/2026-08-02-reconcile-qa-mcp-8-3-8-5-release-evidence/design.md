## Context

Epic 112 made platform identity and protocol-data identity deliberately
independent. A live 8.5 session declares `8.5.1.1343` in synthesized,
foreground, and captured-replay frames while capture-backed operations resolve
through the validated `_bundled/8.3` data. Existing Linux-native grid evidence
proves that protocol decision, and existing Windows model-B evidence proves an
8.3 release path, but the card still needs a release-equivalent HTTP/MCP proof
for both baselines and consistent active guidance.

This is delivery/evidence reconciliation, not protocol research. Historical
OpenSpec archives, canceled cards, and retained historical evidence remain an
audit trail and are not rewritten.

## Goals / Non-Goals

**Goals:**

- Retain or link one 8.3 and one 8.5 release-equivalent Agent/MCP HTTP
  attach/read run, explicitly naming Windows model-B or Linux host-platform
  model-A.
- Prove that the shipped path receives the full live platform version while
  8.5 continues to use validated 8.3 protocol data.
- Make active delivery docs use `/mcp` and describe supported baselines plus the
  validate-first rule consistently.
- Leave enough command/outcome and cleanup evidence for independent review.
- Close release-path defects exposed by the smoke with narrow regression tests,
  without changing TestClient protocol behavior.

**Non-Goals:**

- Populate `_bundled/8.5`, recapture the protocol, or change protocol behavior
  while validate-first remains green.
- Rewrite historical cards, archived changes, or historical evidence that used
  the former `/mcp/` route or earlier delivery assumptions.
- Exercise business writes, 1C metadata changes, BSL changes, or COM flows.

## Decisions

### Reuse evidence only when it meets the release-equivalent floor

An existing run is reusable only when it identifies the delivery model and
full platform build, reaches qa-mcp through HTTP/MCP, proves attach plus a
read-only operation, records the observed outcome, and includes cleanup or a
clear retained-runtime disposition. Linux-native direct protocol grid evidence
is supporting evidence but does not replace the HTTP/MCP release proof.

Alternative considered: treat any live 8.5 replay as release proof. Rejected
because it would not test the Agent/MCP HTTP and packaging/configuration path
named by the card.

### Prefer the smallest safe runtime route

Inventory retained evidence first. If one baseline is missing, run exactly one
bounded read-only release-equivalent smoke for that baseline. Windows model-B
is acceptable; Linux host-platform model-A is also acceptable when the runtime
preflight passes. A Linux model-A run additionally records `ldd` missing-library
status for `/opt/1cv8/x86_64/8.5.1.1343/1cv8`.

Alternative considered: always rerun both platforms on both delivery models.
Rejected because the card asks for evidence reconciliation and exactly one
new 8.5 smoke when needed, not a new delivery matrix campaign.

### Keep platform identity visible in the evidence

The runtime transcript records `PLATFORM_ROOT` and/or
`QA_MCP_PLATFORM_VERSION` as a sanitized full `x.y.z.w` value, the selected
protocol-data family, the canonical `/mcp` endpoint, attach result, read result,
and cleanup. Secrets, raw infobase data, large platform logs, and credentials
remain outside tracked artifacts.

### Fail closed on a red validate-first smoke

If 8.5 attach/read fails because of protocol behavior, delivery stops and the
failure is classified for a separate protocol/capture card. This card does not
self-authorize recapture or a populated 8.5 corpus.

### Repair release-path blockers in the owning layer

The first current-image smoke returned HTTP 200 but starved the Streamable HTTP
event because the UTF-8 middleware synthesized endless empty ASGI request
messages after replaying the validated body. The middleware now replays the
body once and forwards subsequent receives to the original channel. A focused
test records the failing and corrected lifecycle.

The same smoke also showed that a wheel/container launch writes its ownership
marker below the writable `QA_MCP_HOME`, while stateless cleanup defaulted to a
source-tree-relative root beside site-packages. Ownership-root resolution now
prefers the explicit override, then `QA_MCP_HOME`, then the source checkout
default. This keeps cleanup identity-checked and does not authorize stopping an
unowned process.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Active self-hosted/Docker delivery docs and full-version environment handoff | Diff inventory plus focused documentation contract checks for supported builds, `/mcp`, and version variables | exact test/scan commands and observed outcomes | `.artifacts/openspec/reconcile-qa-mcp-8-3-8-5-release-evidence/<run-id>/docs/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Text contract tests cannot prove a live container received the value. |
| Delivery or runtime apply | Streamable HTTP UTF-8 gate and container ownership-marker lookup | Focused middleware/lifecycle RED-to-GREEN tests plus both final live teardowns | unit results, marker-present launch status, non-refused owned cleanup | `tests/test_mcp_server.py`, `tests/test_lifecycle.py`, curated runtime evidence | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Unit tests do not replace the final image smoke; the live teardown supplies that evidence. |
| QA/TestClient runtime | 8.3 release-equivalent Agent/MCP HTTP attach/read | Reusable-evidence audit or one bounded read-only smoke naming model and full build | runtime preflight, endpoint/attach/read summary, cleanup or retained-runtime disposition | `.artifacts/openspec/reconcile-qa-mcp-8-3-8-5-release-evidence/<run-id>/8-3-release-smoke/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Reused evidence can predate the current commit; its artifact identity must be recorded. |
| QA/TestClient runtime | 8.5 release-equivalent Agent/MCP HTTP attach/read through validated 8.3 protocol data | One bounded read-only smoke if no qualifying evidence exists | runtime preflight, full-version and protocol-data-family proof, endpoint/attach/read summary, cleanup | `.artifacts/openspec/reconcile-qa-mcp-8-3-8-5-release-evidence/<run-id>/8-5-release-smoke/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | A red protocol capability blocks this card and routes to separate capture research. |
| Delivery or runtime apply | 8.5 Linux model-A binary dependencies, only when that model is selected | `ldd` missing-library inventory for the selected binary | command, count, and sanitized missing-library list or zero result | `.artifacts/openspec/reconcile-qa-mcp-8-3-8-5-release-evidence/<run-id>/8-5-ldd/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Row becomes N/A with rationale if Windows model-B supplies the 8.5 proof. |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | No BSL or configuration source is edited. | None. |
| New or changed metadata object | 1C metadata | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/config-mcp` | No 1C metadata or source import is changed. | None. |

## Risks / Trade-offs

- **Existing 8.3 evidence may not match the current alpha artifact** -> record
  the release/artifact identity and run one bounded current smoke if equivalence
  cannot be established.
- **Linux model-A contends with Apache for the file infobase** -> run the local
  runtime preflight and use only the project-owned launch/cleanup path that
  manages Apache; never terminate unrelated 1C sessions.
- **A live transcript can expose credentials or business rows** -> retain only
  sanitized platform, endpoint, tool status, row-count/shape, and cleanup
  summaries.

## Migration Plan

1. Audit existing evidence and active docs.
2. Run only the missing bounded release smoke after runtime preflight.
3. Update active docs/tests and record the reconciled evidence index in the
   card/manifest.
4. Roll back by reverting docs/spec changes; runtime smokes are read-only and
   cleanup only processes/resources explicitly owned by the run.

## Open Questions

- Whether existing 8.3 release evidence is current-artifact equivalent is
  resolved during implementation by inspecting its recorded image/release
  identity; it is not assumed from the filename alone.

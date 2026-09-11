## Context

The thin container exposes MCP through the suite proxy at `/mcp`. A printed URL
with `/mcp/` leads to a `not_found` response for some clients and sends the
operator down a false troubleshooting path. The runbooks need to match the
actual proxy path and preserve Windows-specific setup advice without requiring
the operator to infer shell encoding or empty-password semantics.

## Goals / Non-Goals

**Goals:**

- Make `bootstrap.ps1` print `http://127.0.0.1:<port>/mcp`.
- Update delivery docs to use `/mcp`, not `/mcp/`.
- Document that blank 1C passwords omit `-Password`.
- Keep Docker Desktop readiness checks and manual PowerShell UTF-8 byte guidance
  close to the commands operators copy.

**Non-Goals:**

- Do not change the suite proxy routing contract to accept every path variant.
- Do not add new deployment infrastructure or release-server behavior.
- Do not run a data-changing Windows bootstrap in this Linux delivery.

## Decisions

- **Prefer slashless URL over route broadening.** The server already has a
  canonical `/mcp` route; fixing generated config avoids widening routing
  behavior late in release delivery.
- **Keep password semantics in docs and generated examples.** The bootstrap
  already treats a non-empty password as optional input. The docs must tell
  operators not to pass an empty string argument.
- **Use UTF-8 byte examples for manual requests.** Manual PowerShell calls with
  Cyrillic payloads should construct UTF-8 bytes explicitly, matching the
  tester feedback and avoiding console-code-page surprises.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `delivery/bootstrap.ps1` printed MCP URL and operator guidance | Static script/doc assertions and diff review | pytest or grep-based focused test output, diff-check output | `.artifacts/openspec/bootstrap-mcp-path-and-runbook/<run-id>/delivery-docs.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Real Windows bootstrap run | Operator-owned Windows bootstrap smoke with Docker Desktop and host-agent | Retained bootstrap transcript and MCP `/mcp` tools/list result | `.artifacts/openspec/bootstrap-mcp-path-and-runbook/<run-id>/windows-bootstrap-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, Docker Desktop, PowerShell runtime, or licensed 1C TestClient is available inside this Linux workspace. | The next release install run must retain a bootstrap transcript using the slashless MCP URL. |

## Risks / Trade-offs

- **Some old docs may still mention `/mcp/`.** Mitigate with focused search and
  targeted updates to active delivery docs.
- **Windows-only install behavior is not executed locally.** Mitigate with
  script tests/static assertions and a retained Windows smoke checklist.

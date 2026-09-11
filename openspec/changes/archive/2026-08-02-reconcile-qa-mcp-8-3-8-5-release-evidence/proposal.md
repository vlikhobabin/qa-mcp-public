## Why

qa-mcp already supports 1C 8.5 through the epic-112 validate-first decision, but
the active delivery guidance and retained release evidence do not yet present one
coherent 8.3/8.5 story. Before the next public alpha, the reviewed release
contract must show that the shipped HTTP/MCP path passes the live full platform
version and can attach/read on both supported baselines without requiring a
pre-populated 8.5 corpus.

## What Changes

- Reconcile retained 8.3 and 8.5 delivery evidence and retain a release-equivalent
  HTTP/MCP attach/read transcript for either baseline when the existing evidence
  does not meet that floor.
- Update active delivery and release guidance to name `8.3.27.2130` and
  `8.5.1.1343`, state the validate-first 8.5-to-8.3 protocol-data fallback, and
  reserve `_bundled/8.5` population for a red capability.
- Make active MCP endpoint examples consistently use the canonical `/mcp` path
  and remove stale `/mcp/` instructions in the touched delivery docs.
- Record the live full-version injection path through
  `QA_MCP_PLATFORM_VERSION` / `PLATFORM_ROOT` and keep the evidence model
  (Windows model-B or Linux host-platform model-A) explicit.
- Fix the two delivery-path blockers exposed by the current-image smoke: the
  UTF-8 request gate must preserve the downstream ASGI disconnect flow, and
  stateless TestClient cleanup in an installed/container runtime must discover
  ownership markers below `QA_MCP_HOME`.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `qa-mcp-self-hosted-release`: supported-platform delivery evidence must cover
  both declared baseline builds over the shipped HTTP/MCP attach/read path and
  must preserve the live full platform version while using validate-first
  protocol data.

## Impact

- Touches active release/delivery documentation, focused documentation and
  runtime contract tests, the HTTP UTF-8 middleware, TestClient ownership-root
  resolution, retained runtime evidence, the card, and OpenSpec artifacts.
- Does not change native protocol semantics, MCP tool schemas, provider setup,
  1C metadata/BSL, or persistent runtime lab configuration.
- Requires live 1C release-equivalent evidence and the project runtime preflight;
  it does not require Vanessa MCP, EDT/meta snapshots, or a new protocol capture.

## Why

I4 cannot be independently compiled, hostile-verified or scoped-published from
clean published HEAD because its required private fenced S4 seam exists only
inside the protected dirty S4-R1 candidate. A bounded offline decision is
required before any further implementation card can proceed safely.

## What Changes

- Reconstruct the exact source and dependency boundary between clean HEAD and
  the dirty candidate without modifying either payload.
- Publish exactly one decision: authorize one minimal separately reviewable
  private seam extraction/composition with exact limits, or require
  architectural redesign and supersession of I4.
- Curate a privacy-safe findings report and sync the resulting decision as an
  OpenSpec capability.
- Grant no seam, classifier, runtime correction, test, live, target, Windows,
  public-route or S7 implementation authority.

## Capabilities

### New Capabilities
- `qa-mcp-private-fenced-seam-publication-decision`: Defines the offline,
  fail-closed decision contract for whether the private fenced S4 seam can be
  extracted and composed as a separately reviewable dependency of later I4.

### Modified Capabilities
- None.

## Impact

This change touches only OpenSpec workflow artifacts, the I5 board card and a
curated protocol-research decision document. It changes no protocol tool,
Python manager code, MCP provider setup, runtime lab configuration, production
or test source. It requires only published artifacts, local source/diff
analysis and retained privacy-safe I4 composition evidence; it requires no
live 1C runtime, Vanessa MCP, EDT/meta snapshot, endpoint or target access.

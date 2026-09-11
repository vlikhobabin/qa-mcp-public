## Why

Rejected/unpublished I4 and its rejected/unpublished I9 replacement repeated
the same invariant failure: a classifier that is not exactly equivalent to the
unchanged main-window admission can turn invalid predicate or inventory state
into a successful absence cause. ChangeRail therefore requires a published
investigation/design boundary before another implementation attempt.

## What Changes

- Publish the complete expected-predicate, inventory-row, match-cardinality and
  ordering contract for the unchanged first and second exact-main admissions.
- Define a call-neutral admission-result or pure-replay design that cannot add
  membership/Windows calls and cannot synthesize success for invalid state.
- Define exact predecessor call, fence, poll, sleep, UIA, outcome, privacy and
  zero-action invariants plus connected RED/GREEN matrices for every mismatch.
- Decide the five-path/301-production-LOC envelope and publish a
  machine-readable decision with exact fail-closed successor/authorization
  handoff when the evidence supports it.
- Prepare documentation/OpenSpec/board artifacts only; no protocol tool,
  Python manager, MCP provider, host-agent product/test or runtime-lab code is
  changed.

## Capabilities

### New Capabilities

- `qa-mcp-main-predicate-equivalence-decision`: Defines the closed offline
  equivalence contract and bounded authorization handoff required before a
  successor may classify hidden main-inventory outcomes.

### Modified Capabilities

- None.

## Impact

The change affects only OpenSpec workflow, curated protocol-research decision
documentation, board metadata and successor planning. It changes no public API,
route, wire field, product/test/runtime behavior or authority and preserves
Apache-2.0 unchanged. It uses only offline Linux source and retained evidence;
live 1C, Vanessa MCP, EDT/meta snapshots, Windows/PowerShell, endpoints, SSH,
S5/S7 and action surfaces are neither required nor authorized.

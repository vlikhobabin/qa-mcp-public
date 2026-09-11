## Why

Legal files, manifests and documentation are insufficient unless an isolated
source snapshot can build and run the documented offline gates without ignored
workspace state, credentials or private services.

## What Changes

- Add regression tests for the license/policy, standard public docs,
  provenance completeness, documentation links and I2 prerequisite.
- Add an isolated source-snapshot verifier that copies only Git-visible public
  inputs into owned temporary state, builds the package and runs focused
  public-readiness smoke checks.
- Execute the complete offline pytest floor, source/wheel build, public audit,
  provenance check, I2 hostile-mutation oracle, strict OpenSpec validation and
  tracked/untracked whitespace checks.
- Retain raw evidence only under ignored ChangeRail runtime state.

## Capabilities

### New Capabilities

- `qa-mcp-public-clone-readiness`: Defines the isolated public-source snapshot,
  dependency/build and offline verification behavior required before public
  repository publication.

### Modified Capabilities

- none.

## Impact

This affects offline tests, a bounded repository-readiness verifier, docs and
OpenSpec lifecycle state. It does not change the Python manager/MCP runtime,
protocol wire behavior, release automation or lab configuration. Public
package dependencies may be resolved from the existing lock/cache, but no
credentials, Windows, SSH, 1C, TestClient, Vanessa, EDT/meta, live service or
private network are required.

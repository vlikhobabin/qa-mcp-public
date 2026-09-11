## Why

The self-hosted publish helper can leave a partial server-side version directory
after an interrupted activation, then permanently block retries because the
final `versions/<version>` path already exists. The same release surface also
lets ignored environment files override explicit CLI arguments, stamps unchecked
image tags into manifests, and omits durable delivery docs from generated
manifests.

This change touches qa-mcp release tooling, tests and release documentation. It
does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots, or protocol
capture evidence; verification is offline shell/Python evidence plus operator
release-server smoke where activation is exercised.

## What Changes

- Copy server activations into a temporary sibling directory, then atomically
  rename it into `versions/<version>` only after the copy completes.
- Make activated version directories immutable to normal write paths with
  `chmod -R a-w` after successful activation.
- Source `.ai/release.env` or legacy `.ai1c/release.env` before argument parsing
  so explicit CLI flags win.
- Validate that a supplied `--image-archive` contains the manifest image tag
  before staging when `--skip-build` is used.
- Make public-link cleanup robust under `set -e` when non-symlink files are
  present.
- Stage durable delivery docs, including `agent-install-runbook.md`, through
  tooling and include them in `manifest.json`.
- Keep the saved-archive protected-image scanner owned by the active
  `protect-thin-image-saved-archive` change; this change consumes that gate
  when present rather than redefining it.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-self-hosted-release`: publish activation is atomic and immutable,
  explicit CLI values have precedence over ignored release env defaults, staged
  image archives are checked against the manifest tag, and delivery docs are
  generated through the manifest path.

## Impact

- Release script: `tools/release/publish_self_hosted.sh`.
- Release docs: `delivery/agent-install-runbook.md`,
  `docs/self-hosted-release-delivery-plan.md`,
  `docs/release-and-e2e-plan.md` if publish steps change.
- Tests: `tests/test_self_hosted_release_scripts.py` and focused offline
  release-helper tests.
- Existing active dependency/overlap: `protect-thin-image-saved-archive` already
  modifies the publish helper and its tests for archive scanner gating.

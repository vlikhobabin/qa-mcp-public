## Why

Independent review proved that `publish_self_hosted.sh --skip-gates` can stage an unverified supplied executable and that bare executable verification accepts missing VCS metadata. A public release must consume a complete source-bound bundle regardless of whether expensive test gates are skipped.

## What Changes

- Always verify a supplied host-agent artifact before staging, independently of `--skip-gates`.
- Require the supplied executable to come from a bundle with provenance manifest and sha sidecar matching current source.
- Require exact VCS revision and modified-state metadata instead of accepting missing values.
- Add negative release and verifier tests for missing sidecars, missing VCS metadata and source mismatch.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-self-hosted-release`: Supplied Windows host-agent release assets are always source-bound and fail closed before staging.

## Impact

This affects the Linux release helper, Windows artifact verifier, focused release tests and delivery documentation. It performs no publication, installation, Windows execution or live 1C mutation during this change.

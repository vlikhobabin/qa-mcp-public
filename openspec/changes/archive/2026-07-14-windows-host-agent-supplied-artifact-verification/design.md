## Context

The publisher currently treats `--skip-gates` as permission to skip supplied executable verification, even though release staging is a separate trust boundary from expensive tests. Bare executable verification also accepts absent VCS settings, so it cannot prove source identity.

## Goals / Non-Goals

**Goals:**

- Verify every supplied release executable before staging.
- Require the source-bound bundle manifest and sha sidecar for supplied assets.
- Reject missing or mismatched VCS metadata.

**Non-Goals:**

- Publish or sign a release in this delivery.
- Add Authenticode or replace the existing detached component-manifest signature.

## Decisions

- `--skip-gates` skips Python/Go regression suites only; artifact trust verification is unconditional.
- A supplied executable is verified through its containing bundle directory. The executable must use the stable bundle name and the adjacent provenance/sha files must match current source and bytes.
- `_validate_vcs` requires an exact `vcs.revision` and an explicit `vcs.modified` value consistent with the recorded clean/dirty state.
- Focused tests use a once-built real bundle for successful staging and retain lightweight malformed bundles for negative paths.

## Risks / Trade-offs

- [Legacy operators supply only an `.exe`] → The release fails with an actionable missing-manifest diagnostic; they must use the documented builder or signed bootstrap.
- [Dirty local staging uses a source-bound bundle] → `--allow-dirty` remains explicit and the manifest fingerprint/dirty state must match the current tree.

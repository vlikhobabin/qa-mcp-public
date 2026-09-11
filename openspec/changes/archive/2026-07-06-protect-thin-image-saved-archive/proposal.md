## Why

The current protected thin image removes readable protocol source and encrypts
bundled protocol data only in later final-stage layers, so `docker save` still
ships earlier layer blobs containing plaintext source/data. The same build also
passes the real bundled-data key as a build arg, leaving avoidable key exposure
in build history/cache surfaces.

This change affects qa-mcp Docker/release tooling and automated verification.
It does not touch live 1C runtime behavior, BSL, metadata, or TestClient
capture/replay semantics.

## What Changes

- Rework the thin-image protected build so plaintext `src/`, readable gate
  modules, and unencrypted `_bundled` data never land in any final-image layer.
- Extend `docker/verify_protected_image.py` with a host-side saved-archive scan
  that inspects every layer tar and image config/history, not only the merged
  runtime filesystem.
- Switch bundled-data key injection from `ARG BUNDLED_DATA_KEY` to a BuildKit
  secret mount, and fail closed when the secret is missing.
- Update `tools/release/publish_self_hosted.sh` to pass the key as a secret,
  reject the committed development key for release staging, save the image, and
  run the archive-layer scanner before copying the image archive into a release
  directory.
- Keep the in-container protected-image verifier as a runtime/import/decrypt
  smoke while making the archive scanner the publishable-asset gate.
- Record that v0.2.3 must be republished by the operator after this fix is
  merged and the image gate passes.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protected-release-assets`: protected release image archives must be
  verified at the saved-layer level and must not contain protected plaintext or
  bundled-data keys in any layer/config/history.
- `qa-mcp-protocol-lab`: the protected build injects the bundled-data encryption
  key through BuildKit secrets instead of Docker build args or committed
  defaults, while preserving a documented local secret-based build path.

## Impact

- Docker/release code: `docker/Dockerfile.thin`,
  `docker/verify_protected_image.py`, `tools/release/publish_self_hosted.sh`.
- Tests: focused offline tests for the archive scanner and publish helper
  script behavior, plus image/archive checks when Docker is available.
- Operational: published v0.2.3 is known bad and needs a republish after this
  change; the code change records the assignment but does not itself activate a
  production release.

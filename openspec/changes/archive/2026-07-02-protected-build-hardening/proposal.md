## Why

The protected image and release workflow claim to hide internal protocol prose and ship a hardened delivery artifact, but the compile scripts keep docstrings, the standalone verifier under-proves the claim, and the images/workflow still use weak packaging defaults.

## What Changes

- Compile protected modules without docstrings and scan compiled protocol modules for leaked protocol prose.
- Strengthen `docker/verify_protected_image.py` so it proves the gate/loader invariant, protocol-string absence and bundled-data decrypt path, not only file absence and tool count.
- Run containers as a non-root user and define healthchecks in both image variants.
- Pin base images by digest and make release actions immutable by pinning to commit SHAs.
- Align the workflow's pre-publish verification with the stronger verifier.

## Capabilities

### New Capabilities
- `qa-mcp-container-delivery-hardening`: qa-mcp container images and release workflow use non-root runtime defaults, healthchecks and immutable external inputs.

### Modified Capabilities
- `qa-mcp-comment-free-image`: protected-image verification now covers docstring removal, compiled-module leakage and decryptability invariants.

## Impact

Touches Dockerfiles, protected-image compile/verify scripts and release workflow configuration. This does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots or protocol capture evidence; verification is Docker build, protected-image verification, static release workflow checks and existing offline tests.

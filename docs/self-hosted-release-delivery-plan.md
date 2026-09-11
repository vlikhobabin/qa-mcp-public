# qa-mcp self-hosted component staging

This document describes the current component-owned staging helper. OSS-08
owns the later public GitHub/GHCR release train; this file does not claim that
the final public release workflow is complete.

## Artifact contract

`tools/release/publish_self_hosted.sh` stages one immutable version under:

```text
<staging-root>/versions/<version>/
```

The directory contains the Docker archive, Windows host-agent executable,
installer, rendered bootstrap, solo runbook, checksum sidecars, signed
`manifest.json` and its detached signature. The root product publisher owns
copying that complete version directory to the authenticated product origin.

The Docker archive contains the ordinary source-visible qa-mcp package:

- readable Python modules;
- reviewed plaintext curated JSON/JSONL assets under `qa_mcp/_bundled`;
- normal locked runtime dependencies;
- no data-key input or alternate cloud-only package.

`docker/verify_open_image.py` checks both an installed image and a saved Docker
archive. It requires the expected modules and curated assets, parses every
distributable JSON/JSONL asset, rejects the retired encrypted representation
and reconciles the artifact with the component manifest.

## Security controls that remain

Open source delivery does not relax runtime security:

- `manifest.json.minisig` is verified before artifact hashes are trusted;
- MCP HTTP stays behind bearer authentication and host loopback publication;
- portal and 1C passwords are kept out of tracked defaults and logs;
- the Windows host agent retains token authentication, source identity and
  owned-process cleanup;
- lifecycle/display handlers share a bounded authenticated execution limit,
  display selectors cannot override the owned lifecycle PID/TPort, and the
  container protocol path uses the token-authenticated fixed-target relay;
- default uninstall removes both exact host-agent and persisted relay firewall
  rules before deleting owned install state;
- only reviewed curated non-customer assets may enter the package.

## Local staging

Run the offline Python and Windows host-agent gates, then stage a version with
an existing minisign key or detached signature:

```bash
tools/release/publish_self_hosted.sh \
  --version vX.Y.Z \
  --manifest-signing-key /secure/path/to/minisign.key
```

Useful local-only inputs include `--staging-root`, `--image-archive`,
`--host-agent-exe`, `--skip-build` and `--allow-dirty`.
They do not authorize remote publication or change the immutable version-path
contract.

Before staging, the helper:

1. runs the non-live Python suite and Windows host-agent Go tests unless gates
   are explicitly skipped for a bounded local smoke;
2. builds the source-visible model-B image from `docker/Dockerfile.thin` or
   verifies the supplied uncompressed Docker archive; the build uses the
   documented public uv/Python base pinned by digest (optionally overridden by
   `QA_MCP_PUBLIC_BASE_IMAGE`) and installs the `uv.lock` resolution with hash
   checking;
3. records the exact readable-module and curated-asset inventory, then checks
   installed files and the saved archive against that inventory, image digest,
   tag and source revision in the component manifest before publication;
4. verifies the source-bound Windows host-agent artifact;
5. renders a key-free standalone bootstrap;
6. writes and validates the component manifest;
7. signs the manifest and writes checksum sidecars;
8. atomically moves the complete staging directory into the version path.

No existing version directory is overwritten. Release credentials, signing
keys, raw logs and temporary build directories remain outside Git.

## Downstream boundary

This repository exports one public package/artifact contract suitable for both
standalone and AI for 1C consumption. OSS-09 owns changing private downstream
dependency pins and proving the final cutover. OSS-08 owns the public release
train and exact published artifact evidence.

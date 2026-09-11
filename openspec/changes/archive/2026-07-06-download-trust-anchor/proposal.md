## Why

The Windows bootstrap currently trusts `manifest.json`, sidecars and scripts
only through TLS and same-origin downloads, and it accepts plain `http://`
release bases. A compromised release host or downgraded link can therefore turn
the bootstrap path into arbitrary code execution on tester machines.

This change touches the qa-mcp Windows bootstrap, publish tooling, docs and
offline tests. It does not require live 1C runtime, Vanessa MCP, EDT/meta
snapshots, or protocol capture evidence; verification is script/test evidence
plus a retained signature verification smoke.

## What Changes

- Reject non-HTTPS `ReleaseBase` values before downloading release metadata.
- Publish and verify a detached signature for `manifest.json` before trusting
  manifest asset hashes.
- Require the manifest verification public key to come from an out-of-band
  bootstrap parameter or locally trusted configuration, not from the release
  directory being verified.
- Stop before executing `install-windows-host-agent.ps1`, loading Docker
  archives, or running downloaded executables when the manifest signature is
  missing or invalid.
- Document the trusted-key handoff for operators and CI release staging.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-self-hosted-release`: bootstrap requires HTTPS release bases and a
  detached manifest trust anchor before consuming downloaded assets.

## Impact

- Bootstrap script: `delivery/bootstrap.ps1`.
- Publish script/signing docs: `tools/release/publish_self_hosted.sh`,
  `delivery/README.md`, `delivery/windows-agent-runbook.md`,
  `docs/self-hosted-release-delivery-plan.md`.
- Tests: `tests/test_self_hosted_release_scripts.py` and focused signature-path
  fixtures.

## Context

The active delivery compiles Python through Nuitka, strips readable material,
encrypts curated `_bundled` data with AES-GCM and verifies saved image layers.
The new product decision makes all qa-mcp source and distributable data open in
standalone and AI for 1C cloud deployments. Maintaining a second protected path
would recreate divergence and key-management cost.

No protocol capture, frame range, normalization or replay rule changes. Existing
curated assets become ordinary package data. Raw lab captures remain ignored and
runtime cleanup policy is unchanged.

## Known Active Retirement Surface

- Runtime/package: `pyproject.toml`, `uv.lock`,
  `src/qa_mcp/protocol/_bundled_crypto.py` and its loader/settings callers.
- Container/release: `docker/Dockerfile.thin`, the compile/strip/encrypt and
  protected-image verifier helpers, `.github/workflows/release.yml`, component
  manifest/self-hosted release helpers and their protection-only tests.
- Standalone delivery: `delivery/bootstrap.ps1`, its renderer/verifier and the
  active standalone, Docker and Windows runbooks. Existing entrypoints may be
  made key-free; this change adds no new PowerShell, `.cmd` or `.bat` workflow.
- Governance: all eight active protection-related main specs, including the CI
  and standalone-release requirements covered by the newly added deltas.
  Active planning/docs are updated or superseded; archived/canceled history is
  not.

Generic security uses of protected ACL files, authenticated downloads, host
authentication and secret-free logging are not confidentiality-stack residue
and must remain where functionally required.

## Goals / Non-Goals

**Goals:**
- Delete every active confidentiality/obfuscation build and runtime path.
- Install readable Python and plaintext curated assets from one normal package.
- Preserve integrity, import, tool-surface and asset-load verification.
- Make the same package consumable by standalone and AI for 1C.

**Non-Goals:**
- Remove HTTP/host authentication, target binding or mutation safeguards.
- Publish unreviewed raw captures, credentials or customer data.
- Rewrite archived ChangeRail history documenting retired decisions.
- Rebuild the independent Docker or GitHub release pipeline in this change.
- Change AI for 1C dependency pins or perform the downstream cutover owned by
  OSS-09.
- Deliver the independent Windows host bridge owned by OSS-05 or the final
  public release artifacts owned by OSS-08.

## Decisions

1. Delete the protected path instead of retaining a feature flag. One package
   and one asset representation prevents cloud/standalone drift.
2. Remove `_bundled_crypto` and read curated JSON/JSONL directly through normal
   package resources. Encrypted legacy artifacts are not supported inputs after
   migration; source assets are canonical.
3. Replace secrecy scanners with integrity checks: wheel contents, expected
   package modules/assets, parsability, deterministic hashes and import/tool
   smoke.
4. Remove `cryptography` only after dependency inspection proves it has no
   remaining functional use.
5. Keep archived specs/cards unchanged; delta specs explicitly supersede every
   active confidentiality requirement. After sync, fully retired protection
   capability files with no remaining requirements are removed from the active
   main spec set while their archived history remains intact.
6. Define one readable public package contract that both standalone and AI for
   1C can consume. This repository removes every protected variant; OSS-09 owns
   changing downstream dependency pins and proving the eventual cutover.
7. Verify the current standalone Windows bootstrap is syntactically valid and
   key-free, then run an owned native read smoke when its authorized target is
   available. OSS-05 owns the independent open host bridge and OSS-08 owns
   verification of the later exact public release artifact.
8. Scope the protection regression scan deterministically. Active runtime,
   build, CI, release and documentation inputs are scanned; archived/canceled
   ChangeRail history and this active change's explicit migration text are the
   only allowed historical references before archive.

## Risks / Trade-offs

- [Risk] Asset loaders assume encrypted magic or runtime keys. → Add plaintext
  wheel/image tests before deleting crypto code.
- [Risk] Removing compile stages changes imports or omitted modules. → Compare
  the package and tool surface against the source checkout.
- [Risk] Historical protection strings make a naive scan appear incomplete. →
  Use an explicit path/term allowlist for migration history, scan every active
  delivery surface and preserve archives as audit.
- [Risk] Plain assets expose sensitive captured data. → Complete the publication
  provenance/privacy review before GitHub release; do not add raw captures.
- [Risk] Treating a downstream consumption statement as an OSS-02 cutover can
  expand scope into the private product. → Prove the single-artifact contract
  here and defer the actual AI for 1C pin/adoption evidence to OSS-09.

## Migration Plan

1. Add plaintext loader/package tests and invert protection-only expectations.
2. Remove runtime crypto/key configuration and migrate callers to direct reads.
3. Replace the protected Docker stages with normal package installation.
4. Delete compile/strip/encrypt/verifier helpers and protection-only tests.
5. Remove unused dependencies and active CI/release/bootstrap/documentation key
   inputs; sync the replacement requirements and retire empty active protection
   capability specs.
6. Run full offline, wheel and container smokes from a clean checkout, plus the
   bounded current Windows configuration check.

Rollback is a source revert before publication. No encrypted release is treated
as an upgrade input; operators move to a fresh open image and preserve only
normal runtime/evidence volumes.

## Open Questions

- None. The product decision retires protection for both products.

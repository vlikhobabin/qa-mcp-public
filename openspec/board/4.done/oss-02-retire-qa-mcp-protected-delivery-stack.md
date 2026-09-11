# Retire qa-mcp protected delivery stack

## Status
4.done

## Owner
unassigned

## Series
oss-02

## Order Index
401

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Summary
Remove Nuitka compilation, source stripping, bundled-data encryption and every
protection-only build/runtime path from qa-mcp as a whole. The same readable
public package is used by standalone deployments and by server-side AI for 1C.

## Acceptance
- Active source, dependencies, build scripts, Dockerfiles, tests and docs have
  no Nuitka, strip-source, bundled-data encryption/key or protected-image path.
- Readable Python modules and plaintext curated JSON/JSONL assets are present
  and loadable in wheels and runtime images without a data key.
- Protection-only dependencies and tests are removed; integrity and
  reproducible source-build checks replace secrecy assertions.
- qa-mcp exposes one unprotected public package contract for standalone and
  downstream AI for 1C use; no cloud-only protected variant remains. Actual
  downstream pinning and cutover are owned by OSS-09.
- Active main specs no longer require protected delivery; fully retired
  protection capabilities are removed from the active spec set.
- Archived ChangeRail history remains unchanged as an audit trail.

## Change Set
1. `retire-qa-mcp-protected-delivery-stack` -
   `openspec/changes/archive/2026-08-24-retire-qa-mcp-protected-delivery-stack/`

## Change 1: `retire-qa-mcp-protected-delivery-stack`

### Why
The protected build, encrypted bundled-data and runtime-key paths conflict with
the decision to publish one readable qa-mcp package for every consumer.

### Goal
Retire the complete active confidentiality/obfuscation stack while preserving
ordinary integrity, privacy, authentication and runtime-safety controls.

### Scope
- Replace compiled/stripped delivery with readable Python packaging.
- Replace encrypted curated assets with reviewed plaintext package data.
- Remove protection-only dependencies, helpers, settings, release inputs,
  Docker stages, tests and active documentation.
- Replace secrecy assertions with package, asset, import, manifest and clean
  source-build checks.
- Supersede conflicting active OpenSpec requirements without rewriting archived
  history.

### Acceptance
- Same as the card Acceptance section and the change delta specifications.
- No protocol mapping, target-binding, authentication or mutation-safety
  semantics change as part of this retirement.

### Depends On
- `openspec/board/4.done/oss-01-establish-qa-mcp-shared-core-boundary.md`

### Related
- `openspec/changes/archive/2026-08-24-retire-qa-mcp-protected-delivery-stack/`

## Dependencies
- `openspec/board/4.done/oss-01-establish-qa-mcp-shared-core-boundary.md`

## Verify
- Initial focused package/delivery/core/runtime suite: 310 passed; rescue-focused
  delivery suite: 29 passed.
- Exact post-rescue non-live CI suite: 943 passed, coverage 72.94%.
- Clean wheel and sdist contain readable modules and 16 plaintext curated
  assets; source-visible image build, installed verifier, saved-layer verifier,
  68-tool smoke and healthcheck passed.
- Windows PowerShell parse and Docker Desktop source-visible image smoke passed
  without a bundled-data key; the public `WindowsHostQAExecutor` read returned
  `OperationVerdict.SUCCESS` with three windows and no business mutation.
- Owned Windows TestClient, task, firewall rules, ports, staging, container and
  image were removed; pre-existing task and 16 suite containers were untouched.
- Python compilation, release-shell syntax, deterministic protection scan,
  `git diff --check`, synced main-spec validation and strict change validation
  passed.
- Sanitized runtime evidence: `.runtime/changerail/evidence/oss-02-retire-qa-mcp-protected-delivery-stack/`.

## Archive
- `openspec/changes/archive/2026-08-24-retire-qa-mcp-protected-delivery-stack/`

## Related
- `openspec/board/4.done/122-2026-06-27-protect-protocol-ip-nuitka.md`
- `openspec/board/4.done/remove-product-license-gate-for-free-qa-mcp.md`

## Result
- Removed the active compile/strip/encrypt/decrypt stack, its helpers and
  confidentiality-only tests; normal package reads now load curated plaintext
  JSON/JSONL assets.
- Replaced the thin image and release gates with a source-visible package,
  clean build/import/tool/asset checks and saved-image integrity verification.
- Bound the exact readable-module/asset inventory to the component manifest,
  OCI source revision, image tag and archive digest before any push; missing,
  undeclared, private or hash/provenance-drifted artifacts now fail closed.
- Pinned the mandatory suite base by digest, installed runtime and build
  dependencies from frozen `uv.lock` hashes, and proved dependency-layer cache
  reuse across a source-only rebuild.
- Removed the direct `cryptography` dependency; it remains only through current
  authentication/JWT dependency chains in the lock file.
- Synced seven retained capabilities, added the open-runtime-assets capability,
  and removed the two fully retired protection capabilities from active specs.
- No protocol mapping changed, so no capture or evidence-index update was
  required. Downstream pin/cutover remains explicitly owned by OSS-09.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-24 child card extracted from the open-source roadmap; its OpenSpec
  change is apply-ready.
- 2026-08-24 targeted fast-forward refresh reconciled the card with completed
  OSS-01, added the missing CI/release-spec deltas, made the change section
  do-parseable and bounded downstream, Windows and later release ownership.
- 2026-08-24 ChangeRail delivery started on `main`; the preflight confirmed the
  remote push target and isolated the pre-existing planning diff to OSS-02.
- 2026-08-24 implementation, Linux package/container verification and the
  authorized Windows-native key-free delivery/read smoke completed with exact
  owned cleanup.
- 2026-08-24 delta specs were synced, the two retired protection capabilities
  were removed from active specs, and the completed change was archived.
- 2026-08-24 independent review cycle 1 returned NO-GO: the saved-image
  verifier was not exact/manifest-bound, the package evidence had reused stale
  `build/lib`, and the thin image still used a mutable base with no retained
  two-build cache proof.
- 2026-08-24 bounded rescue closed all three findings with an exact 78-file
  manifest-bound inventory, isolated 16-asset wheel/sdist builds, a digest-pinned
  base, frozen hash-checked dependencies and observed BuildKit cache reuse.
  The current image and bootstrap were rechecked on the authorized Windows host,
  then the owned image/staging were removed with 16 unrelated containers intact.
- 2026-08-24 independent review cycle 2 returned GO: all six acceptance
  criteria passed, cycle-1 findings R1-R3 were closed, and no findings remained.
- 2026-08-24T15:22:16Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

# Optimize QA protected-image dependency layers

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Root `upd-10-vendor-forgejo-registry` layer audit (2026-07-15).
- Root report: `../deploy/docker/release/image-layer-audit.json`.

## Problem
`docker/Dockerfile.thin` correctly isolates and sanitizes protected artifacts,
but the `protected-package` stage copies all `src` before `pip install .`.
Any code-only change therefore rebuilds the complete stable Python dependency
prefix before the compiled/encrypted artifacts are substituted.

## Goal
Separate stable dependency installation from mutable protected source without
weakening the saved-layer, external runtime-key, compilation, archive scanner
or no-readable-protected-source invariants. Product license enforcement is no
longer an invariant for qa-mcp and is handled by
`remove-product-license-gate-for-free-qa-mcp.md`.

## Acceptance
- Stable Python dependencies are materialized before mutable QA source in the
  protected-package flow; a code-only edit reuses them.
- BuildKit cache or registry-manifest evidence demonstrates the improvement.
- Every final/saved layer remains free of readable protected source and key
  material; compilation, encrypted bundled data, 68-tool import and archive
  scanner checks remain green.

## Related
- Root card: `openspec/board/3.inprogress/upd-10-vendor-forgejo-registry.md`.
- Root audit finding: `ai-suite-qa`.
- Existing security card: `openspec/board/3.inprogress/audit-qa-thin-layer-leak.md`.
- Archived change:
  `openspec/changes/archive/2026-08-01-split-qa-mcp-protected-container-dependency-layers/`.

## Change Set
1. `split-qa-mcp-protected-container-dependency-layers`

## Change 1: `split-qa-mcp-protected-container-dependency-layers`

### Scope
- Reorder the normal and protected image flows so dependency metadata is
  materialized before mutable QA source.
- Preserve the final-stage sanitized-prefix pattern and saved-archive scanner.
- Keep bundled protocol data encrypted and the runtime key outside image layers.
- Do not reintroduce product-license enforcement while touching the protected
  build.

### Acceptance
- A code-only edit reuses the Python dependency layer, with BuildKit
  plain-progress or registry cache evidence retained under ignored
  runtime/evidence.
- Saved image/archive inspection still proves no readable protected source,
  plaintext bundled data or runtime key material in any final shipped layer.
- Existing protected-image import/smoke tests stay green.

### Depends On
- none

## Verify
- Test-first cache-boundary regression: expected RED before implementation and
  GREEN afterward; protected release/archive modules passed 21 tests in 7.54s.
- Cold `--no-cache` and source-edited warm protected builds passed. Warm
  plain-progress output shows dependency step `#13 CACHED`, while `COPY src`
  and the dependency-free project install executed again.
- Protected-package and final-stage smokes each loaded 68 tools. The in-image
  verifier reported 16 bundled files encrypted and decryptable with the
  external key; the 116 MB saved archive passed every-layer/config/history
  scanning with no readable protected source, plaintext bundled data, or key.
- Windows-native PowerShell check passed on `HISTORICAL-LAB-HOST`; Dockerfile
  hashes matched the local payload and owned temporary files were removed.
- New capability and all 21 post-archive OpenSpec items validate strictly;
  `git diff --check`, evidence-index validation, and delivery-manifest scope
  reconciliation are green. Evidence index:
  `.runtime/changerail/evidence/optimize-container-dependency-layers/index.json`.

## Archive
- `openspec/changes/archive/2026-08-01-split-qa-mcp-protected-container-dependency-layers/`

## Result
- Normal and protected Dockerfiles now materialize metadata-declared build and
  runtime dependencies before mutable QA source, then install the project with
  dependency/build isolation disabled. Protected release invariants remain
  green under a real source-edited rebuild and saved-layer scan.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01 alpha-release triage: still current release image hygiene; moved
  to `2.todo`. Acceptance was updated for the new qa-mcp no-license decision.
- 2026-08-01T22:28:36Z fast-forwarded
  `split-qa-mcp-protected-container-dependency-layers` to complete, strictly
  valid apply-ready artifacts; remote-push preflight passed for `origin/main`.
- 2026-08-01T22:31:14Z delivery started; card moved to `3.inprogress` and
  ignored delivery manifest initialized.
- 2026-08-01T23:37:47Z implementation, Linux/Windows verification, capability
  sync, strict validation, and archive completed; card remains
  `3.inprogress` pending independent review and review-gated publication.
- 2026-08-01T23:47:16Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

# Publish qa-mcp GitHub and GHCR release train

## Status
1.backlog

## Owner
qa-mcp

## Series
oss-08

## Order Index
407

## OpenSpec Stage
story

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Summary
Create public GitHub Actions and a tag-driven release train that publishes the
Python distribution, GHCR image and Windows bridge artifacts from one source
revision. This card may first publish a clearly pre-stable release candidate.

## Acceptance
- Pull requests run offline Python/Go tests, OpenSpec validation, package/image
  build checks and the required security/supply-chain gates.
- One tag and commit produce the Python artifact, public GHCR image, Windows
  executable and installer with consistent semantic versions.
- Release assets include checksums, SBOM/provenance, compatibility metadata,
  release notes and an immutable digest/commit manifest.
- Workflows use only documented GitHub permissions and public dependencies;
  they contain no private portal, package source or AI for 1C release secret.
- An anonymous clean environment pulls the exact image/artifacts and completes
  the documented authenticated HTTP and Windows bridge smoke.
- Rollback and release-candidate promotion are documented and reproducible.

## Depends On
- `openspec/board/4.done/oss-03-make-qa-mcp-standalone-http-runtime-independent.md`
- `openspec/board/4.done/oss-05-extract-independent-open-windows-host-bridge.md`
- `openspec/board/4.done/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`
- `openspec/board/1.backlog/oss-fix-10-scan-decoded-json-credential-assignments.md`
- `openspec/board/1.backlog/oss-fix-11-verify-corrected-linux-runtime.md`
- `openspec/board/1.backlog/oss-fix-12-verify-corrected-windows-runtime.md`

## Change Set
- none yet

## Verify
- GitHub Actions workflow validation and least-privilege review.
- Exact-tag Python/GHCR/Windows artifact consistency checks.
- Anonymous pull/download/install/runtime smoke.
- Release manifest, checksum, SBOM and provenance verification.

## Archive
- not started

## Related
- Historical final-NO-GO source:
  `openspec/board/3.inprogress/oss-07-prepare-qa-mcp-public-repository-readiness.md`.
- `openspec/board/1.backlog/oss-09-cut-over-qa-mcp-public-stable-and-downstream.md`

## Result
not started

## Next
- Corrective publication gate: the 2026-09-05 review reproduced ten defects
  despite a green offline floor. FIX-10 and both final source-bound runtime
  qualification cards now gate artifact publication; the qualification cards
  transitively depend on FIX-01–03, FIX-04A/B/C, FIX-05–08 and FIX-09A/B/C.
  Superseded FIX-04/FIX-09 are not done prerequisites. Release planning may
  continue, but the former published prerequisites alone no longer prove
  readiness to publish a candidate.
- Published prerequisites 402, 404 and OSS-07-R1 are complete; the replacement
  publication is commit `8e94a21`. This is the next release-sequence planning
  story, not an accepted delivery card.
- Refine bounded board-only plans with Delivery Budget and explicit artifact,
  account and runtime verification boundaries before delivery. The six
  acceptance groups and combined Python/GHCR/Windows scope exceed current
  single-card admission. No release or runtime execution starts from this
  inventory update.

## Log
- 2026-09-05T08:38:59Z Named all FIX-04/FIX-09 successors in the inherited corrective publication gate; no release or admission.
- 2026-09-05T08:11:47Z Added operator-requested corrective disclosure and
  runtime qualification dependencies; no artifact release or native execution.
- 2026-08-24 extracted from the former all-in-one publication change so CI and
  artifact publication can be delivered independently of the stable cutover.
- 2026-09-03 blocked behind linked OSS-07-R1 after final OSS-07 review cycle 3
  returned `NO-GO` with its same-card rescue budget exhausted at `2/2`.
- 2026-09-05 board inventory reconciled published dependencies and removed the
  exhausted OSS-07 source from mandatory delivery prerequisites; its lineage
  remains Related. No implementation or release was started.

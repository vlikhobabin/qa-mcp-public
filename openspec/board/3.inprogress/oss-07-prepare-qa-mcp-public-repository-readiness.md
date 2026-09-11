# Prepare qa-mcp public repository readiness

## Status
3.inprogress

## Owner
qa-mcp

## Series
oss-07

## Order Index
406

## OpenSpec Stage
implemented, synced and archived; awaiting independent review

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
- Card-405 stable-profile omission decision after published I15.
- Operator-approved SPDX license choice: `Apache-2.0`.
- Published OSS-07-I2 fail-closed public-safety matrix at commit `61b8d90`;
  I2 is a completed design/investigation prerequisite, not a replacement for
  this parent delivery.

## Summary
Prepare a legally and operationally publishable GitHub source repository after
the product boundaries settle. This card owns disclosure, provenance,
licensing, governance and public documentation, not release automation.

## Acceptance
- Current tree and publishable history are reviewed for secrets, credentials,
  personal/customer data, private endpoints and internal-only artifacts.
- Every curated protocol asset and evidence file has an explicit
  redistribution/provenance decision; non-publishable material is absent.
- The approved OSI license, NOTICE/trademark attribution, SECURITY,
  CONTRIBUTING, governance, support and code-of-conduct documents are present;
  the first future change binds operator-approved `Apache-2.0` to the exact
  repository publication policy, while I16 creates no license files.
- Public architecture, installation, authentication, Windows bridge,
  development and upstream-first contribution docs match the final source.
- A fresh unauthenticated clone can install dependencies, build the package and
  run the documented offline checks using public inputs only.
- Archived planning history retained in the public snapshot contains no secret
  or customer material and is clearly historical rather than active guidance.
- The published I2 matrix, freeze record, verifier and evidence floor remain
  byte/semantics fail-closed: the unchanged control and all 23 hostile
  mutations pass their expected outcomes before this card may publish.

## Dependencies
- Cards 400-404 define the source and product surface to be audited.
- Card 405 is not required when its tool is explicitly omitted from the
  standalone profile and public support matrix.
- Published OSS-07-I2 closes only the exhausted I1 false-PASS design class.
  Its five-file successor surface and archived capability are retained; the
  failed I1 nine-path payload remains unavailable and must not be restored,
  copied or reconstructed.

## Change Set
- `oss-07-bind-apache2-publication-policy`
- `oss-07-audit-public-assets-and-evidence`
- `oss-07-publish-public-repository-guides`
- `oss-07-prove-clean-clone-readiness`

## Verify
- Full-tree and selected-history secret/privacy/provenance scan.
- Public-document link and terminology checks.
- Anonymous clean-clone package build and offline test smoke.
- Strict OpenSpec validation.

## Archive
- `openspec/changes/archive/2026-09-02-oss-07-bind-apache2-publication-policy/`
- `openspec/changes/archive/2026-09-02-oss-07-audit-public-assets-and-evidence/`
- `openspec/changes/archive/2026-09-02-oss-07-publish-public-repository-guides/`
- `openspec/changes/archive/2026-09-02-oss-07-prove-clean-clone-readiness/`

## Related
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`
- `openspec/board/4.done/oss-07-i2-freeze-fail-closed-public-safety-matrix.md`
- `openspec/changes/archive/2026-09-02-freeze-fail-closed-public-safety-matrix/`

## Result
All four ordered changes are implemented, synced and archived. The payload
binds exact SPDX `Apache-2.0`, adds the public legal/governance/documentation
surface, admits 649 Git-visible asset/evidence files through a deterministic
provenance ledger, and proves an ignored-state-free source snapshot excludes
all 34 external ChangeRail symlinks, performs locked offline install/import and
focused audit/provenance/docs/I2 tests, then builds one wheel and one sdist with
inspected Apache-2.0 metadata, LICENSE and NOTICE.

The authoritative `uv run pytest -q -m "not live"` gate passes with 1598
tests and 4 expected skips, including the Linux-safe Windows host-agent
cross-build and self-hosted release-script tests. The nested-worktree Go build
now binds VCS stamping to the exact delivery worktree, preserving revision,
modified-state and byte-identical rebuild checks. Public audit, provenance,
12-document link checks, strict OpenSpec and whitespace gates pass. The audit
now covers every Git-visible file, symlink target and path name plus decoded
structured Base64/UTF-16 protocol payloads. Case-insensitive credential suffixes
such as `TEST_CLIENT_PASSWORD` are detected in any directory, malformed
JSON/JSONL and invalid declared Base64 fail closed, and fixture allowances bind
exact category/path/source/value/count tuples rather than directories or whole
files. Fifteen focused tests cover credential, RFC1918, machine/customer,
encoded disclosure, parse/decode, symlink, occurrence-count, provenance-gate
and unsupported-extension classes. Provenance admission itself now requires a
clean policy/disclosure scan and unchanged I2. The two affected protocol assets
are sanitized length-preservingly and re-hashed.
Published I2 remains byte-unchanged: the `46/14/5/D14` control and all 23
hostile mutations return their reviewed outcomes. The real 4+6 lab corpus gate
is retained through fail-loud identity-free discovery, while the unsafe retired
broad-kill XTEST prototype is removed. No Windows, SSH, 1C, TestClient or live
service was run, and OSS-08/09 remain unstarted.

## Next
- Run fresh independent review cycle 3:

  ```text
  $changerail-review openspec/board/3.inprogress/oss-07-prepare-qa-mcp-public-repository-readiness.md --cycle 3
  ```

- Publish the reviewed scoped payload to `origin/main` only on GO.

## Change 1: `oss-07-bind-apache2-publication-policy`

### Why
The operator-approved license and exact public history boundary must be fixed
before any wider repository-readiness payload can make legal or disclosure
claims.

### Goal
Bind SPDX `Apache-2.0` in package metadata and canonical legal files, define
the reviewed-tree and publishable-history policy, and make published I2 an
immutable fail-closed prerequisite.

### Scope
- Add the canonical Apache License 2.0 text, NOTICE/trademark attribution and
  machine-readable package license metadata.
- Define one public publication policy with public contacts, history strategy,
  excluded internal history/material and explicit OSS-08/09 boundary.
- Preserve all published I2 bytes and require its 23-mutation verifier in the
  publication gate; never restore or recreate I1.

### Acceptance
- License choice is exactly SPDX `Apache-2.0` everywhere this change adds a
  choice, and policy contacts expose no personal address.
- Publication/history policy is deterministic, public-safe and fail-closed on
  unresolved secret, privacy, provenance or I2 findings.

### Depends On
- Published OSS-07-I2 at `61b8d90`.

### Related
- `openspec/changes/archive/2026-09-02-oss-07-bind-apache2-publication-policy/`

## Change 2: `oss-07-audit-public-assets-and-evidence`

### Why
The source tree contains hundreds of curated protocol/evidence files and
historical lab reports; public distribution needs an exact per-path decision
and repeatable privacy/secret checks rather than prose assurance.

### Goal
Create a deterministic offline public-readiness audit and a hash-bound
per-file redistribution/provenance manifest, then remove or sanitize material
that the policy does not admit.

### Scope
- Cover every tracked bundled protocol asset, protocol UI asset and curated
  evidence file with an explicit path, digest, provenance class and decision.
- Detect high-confidence secrets, personal/customer markers, private lab
  endpoints, unsupported binaries and manifest drift without printing values.
- Sanitize historical evidence narrowly and remove only exact non-admitted
  packaged artifacts; keep historical claims and I2 semantics intact.

### Acceptance
- Current-tree and selected-history audit passes under the policy with only
  bounded, classified excluded-history counts.
- Provenance check proves every in-scope path is present once, digest-matched
  and explicitly redistributable; no non-publishable in-scope file remains.

### Depends On
- `oss-07-bind-apache2-publication-policy`

### Related
- `openspec/changes/archive/2026-09-02-oss-07-audit-public-assets-and-evidence/`

## Change 3: `oss-07-publish-public-repository-guides`

### Why
The current README and delivery notes mix research-lab and private staging
language with public usage, and the repository lacks standard security,
contribution, governance, support and conduct documents.

### Goal
Make the public source boundary, architecture, installation, authentication,
Windows bridge, development and upstream-first contribution routes clear and
consistent with the actual source without inventing an OSS-08 release train.

### Scope
- Add SECURITY, CONTRIBUTING, GOVERNANCE, SUPPORT and CODE_OF_CONDUCT policies.
- Replace public entry-point guidance with source-clone/package/Docker flows
  and public-safe authentication/Windows bridge instructions.
- Label retained planning/research documents as historical where necessary and
  verify local documentation links/terminology.

### Acceptance
- A new contributor can find architecture, install, auth, bridge, development,
  support, security and upstream-first guidance from README.
- Public docs contain no credential values, customer identity or claim that
  OSS-08/09 release/cutover work is complete.

### Depends On
- `oss-07-audit-public-assets-and-evidence`

### Related
- `openspec/changes/archive/2026-09-02-oss-07-publish-public-repository-guides/`

## Change 4: `oss-07-prove-clean-clone-readiness`

### Why
Repository-readiness requires an executable source-snapshot proof, not only a
documentation and scanner review.

### Goal
Verify an isolated Git-export-equivalent snapshot uses public inputs only,
installs/builds without repository-local secrets and runs the documented
offline readiness gates.

### Scope
- Add regression tests for policy, provenance, standard docs and public links.
- Add an isolated snapshot build/smoke command using ignored temporary state.
- Run the complete offline suite, package build, I2 mutation oracle, public
  audit/provenance checks, strict OpenSpec and whitespace gates.

### Acceptance
- Isolated snapshot package build and focused public-readiness smoke pass with
  no ignored/local runtime input copied into the snapshot.
- The complete mandatory offline floor passes and retained evidence stays only
  under ignored `.runtime/changerail/` state.

### Depends On
- `oss-07-publish-public-repository-guides`

### Related
- `openspec/changes/archive/2026-09-02-oss-07-prove-clean-clone-readiness/`

## Log
- 2026-08-24 extracted from the former all-in-one publication change so it can
  be planned and reviewed independently.
- 2026-09-02 I16 handoff confirms this remains an unplanned `1.backlog` story
  with no OpenSpec artifacts; it is the next separate card after omission
  publication, with `Apache-2.0` operator-approved.
- 2026-09-02 published OSS-07-I2 at `61b8d90` freezes the exact fail-closed
  public-safety matrix after I1 exhausted its rescue budget. Parent delivery
  must preserve I2 and its offline evidence floor without restoring I1; OSS-08
  and OSS-09 remain blocked and out of scope.
- 2026-09-02 accepted into `2.todo` with four ordered offline public-readiness
  changes. Change 1 binds exact SPDX `Apache-2.0`; later changes audit
  provenance/disclosure, publish public docs and prove an isolated clean source
  snapshot. No OSS-08/09 or live/Windows work is authorized.
- 2026-09-02 delivery started from clean published commit `61b8d90`; scope is
  the four OSS-07 changes plus reconciled parent/roadmap/OSS-08 dependency
  metadata. Runtime/live/Windows work remains not applicable.
- 2026-09-02 restored every tested delivery guidance contract and fixed Go VCS
  stamping to use the exact nested delivery worktree. The mandatory full
  non-live suite then passed with 1586 tests and 4 skips; the earlier failed
  attempt and diagnostic partial run remain ignored evidence, with the latter
  classified supplemental rather than acceptance.
- 2026-09-02 synced four new public-readiness capability specs and archived all
  four completed changes. Strict all-spec validation reports 71 active/main
  items green; fresh independent review is the remaining publication gate.
- 2026-09-02 independent review cycle 1 returned NO-GO on four connected
  public-readiness oracle defects: encoded payload disclosure was invisible,
  hostile scanner tests were absent, snapshot checks still resolved external
  symlinks and did not install/test in isolation, and broad privacy substitution
  changed historical/runtime meaning.
- 2026-09-02 bounded same-card rescue 1 added RED-first hostile disclosure
  tests, decoded Base64/UTF-16 scanning, sanitized 18 machine-id occurrences in
  two protocol assets, made the snapshot standalone, restored the fail-loud
  4+6 corpus contract without publishing its private identity, removed the
  unsafe prototype, and replaced fictitious product/path claims with explicit
  redaction semantics. Full non-live suite is 1592 passed/4 skipped; fresh
  independent review cycle 2 is next.
- 2026-09-02 independent review cycle 2 returned NO-GO on one remaining
  disclosure-oracle blocker: lowercase credentials and Git-visible findings
  under `tests/` bypassed directory/file-wide exemptions.
- 2026-09-03 final same-card rescue 2 removed those exemptions and added
  RED-first lowercase/test-tree cases. A separate semantic audit then closed
  the connected prefixed-credential, malformed payload, symlink-target,
  global example-email, unbounded occurrence and provenance-admission bypasses
  before handoff. Final focused readiness is 15 passed, full non-live is 1598
  passed/4 skipped, provenance covers 649 files, I2 remains byte-unchanged and
  all offline gates are green. Rescue budget is exhausted at 2/2; independent
  review cycle 3 is the only next review step.

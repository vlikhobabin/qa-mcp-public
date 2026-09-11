# qa-mcp standalone product release

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source

- Root ChangeRail card
  `qa-mcp-standalone-product-release-track-v1`.
- Linked root change `qa-mcp-standalone-release-surface`.

## Summary

Make the component-owned release helper stage immutable, signed standalone
`qa-mcp` product bytes for the root authenticated product publisher. Retire
active secret-link activation and ship solo-only product guidance.

The pre-existing active change `license-activation-bootstrap` continues to own
the source `delivery/bootstrap.ps1` activation flow and
`delivery/windows-agent-runbook.md`. This card does not rewrite or archive that
change. It changes only the staged bootstrap substitution, adds a separate
standalone product runbook, and records the dependency explicitly.

## Change 1: `qa-mcp-standalone-product-release`

### Scope

- Make `publish_self_hosted.sh` stage product-version paths below the
  authenticated `/qa-mcp/download/versions/` route.
- Remove component-side public-link/server activation from the supported CLI.
- Stage current solo-only guidance with no active legacy distribution link.
- Preserve the signed frozen component manifest and exact asset identities for
  the root publisher.
- Add offline contract and staging tests.

### Verification

- `uv run --with pytest pytest -q tests/test_self_hosted_release_scripts.py tests/test_component_manifest.py`
- `uv run --with pytest pytest -q tests/test_verify_protected_image_archive.py`
- `sh -n tools/release/publish_self_hosted.sh`
- Render and parse `bootstrap.ps1` with Windows PowerShell on
  `HISTORICAL-LAB-HOST` at the explicitly supplied current endpoint.
- `openspec validate qa-mcp-standalone-product-release --strict`
- `openspec validate --all --strict`
- `git diff --check`

## Dependencies

- The root publisher consumes the staged `versions/<version>/` directory.
- `license-activation-bootstrap` remains the owner of the source activation
  code until independently completed; standalone product licensing is wired by
  the root track and a later explicitly linked component change.

## Progress Log

- 2026-07-26: linked component card and OpenSpec change created.
- 2026-07-26: isolated product staging implementation started.
- 2026-07-26: focused release/manifest tests passed (15); shell syntax,
  strict change/all validation and diff checks passed.
- 2026-07-26: staged bootstrap selects product `qa-mcp` and strips the legacy
  shared license/decryption defaults without editing the active source change.
- 2026-07-26: independent review cycle 1 returned NO-GO for plain bootstrap
  secret parameters, missing Windows-native verification, and an outdated
  vendored broker.
- 2026-07-26: rescue replaced plain secret parameters with ACL-protected input
  files, refreshed the broker from root commit `23fa56d`, pinned it into the
  final image, and expanded archive/runtime contract tests.
- 2026-07-26: Windows PowerShell on `HISTORICAL-LAB-HOST` parsed and checked the
  rendered bootstrap successfully; exact owned path
  `C:\Users\User\AppData\Local\qa-mcp-e2e\bootstrap-review` was removed.
- 2026-07-26: independent review cycle 2 returned NO-GO because supplied image
  archives could carry arbitrary non-executable broker bytes, one diagnostic
  was stale, and the broker build carried a dirty VCS stamp.
- 2026-07-26: rescue now requires executable broker mode plus the exact pinned
  digest in every supplied archive, builds with `-buildvcs=false`, reproduces
  byte-for-byte from root commit `23fa56d`, and passes 24 focused tests.
- 2026-07-26: the updated rendered artifact was rechecked by Windows
  PowerShell on `HISTORICAL-LAB-HOST`; exact temporary cleanup passed again.
- 2026-07-26: independent review cycle 3 returned NO-GO because a later image
  layer could replace the pinned broker path with a symlink after the digest
  check.
- 2026-07-26: rescue now models exact-path and ancestor replacements, direct
  and ancestor whiteouts, and opaque whiteouts across image layers; lower-layer
  broker plus upper-layer symlink/opaque/whiteout attacks are rejected (26
  focused tests passed).

## Next
- done

## Result
Published reviewed payload as `08e72e53efa119ec548dd95bd4478fc64aaaf49b`; push status `pending` on `main`/`origin`.

## Log
- 2026-07-26T14:49:38Z publish finalized card into `4.done` with commit `08e72e53efa119ec548dd95bd4478fc64aaaf49b` and push status `pending`.

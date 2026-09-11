# Define The Public Runtime Target Contract

## Status
4.done

## Owner
unassigned

## Series
oss-04a

## Order Index
4031

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Goal
Add the generic immutable runtime-target data contract and closed public profile
schema without yet consuming the suite handoff or changing TestClient behavior.

## Acceptance
- Public immutable types represent fingerprint, target binding, provider
  observation, profile and evidence policy without importing suite providers.
- A packaged closed JSON schema rejects unknown or incomplete profile fields.
- Existing `TargetIdentity` remains the shared-core identity primitive.
- The payload stays at or below `300` added production LOC.

## Change Set
1. `define-qa-mcp-runtime-target-contract` -
   `openspec/changes/define-qa-mcp-runtime-target-contract/`

## Dependencies
- [OSS-01](../4.done/oss-01-establish-qa-mcp-shared-core-boundary.md).

## Verify
- Contract immutability, fingerprint, enum and JSON-schema tests.
- Packaging/archive inventory tests for the schema asset.
- Focused core/package tests, full non-live suite, compilation, strict OpenSpec
  and deterministic review preflight with production LOC at or below `300`.

## Result
Implementation, verification, spec sync and archive are complete. The payload
adds the immutable provider-neutral target values and closed packaged schema
without resolver, application or lifecycle authority. Independent review cycle
3 returned `GO` with `0` findings and the scoped publish was finalized.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-25 created by the OSS-04 complexity investigation as payload A.
- 2026-08-25 moved to `3.inprogress`; replayed the public immutable contract
  and packaged schema from the preserved payload.
- 2026-08-25 Windows contract smoke passed on the authorized
  `HISTORICAL-LAB-HOST\\User` role at `192.0.2.203`; the isolated staging path
  was removed and no TestClient, Docker or host-agent state was changed.
- 2026-08-25 focused package/core verification passed (`30 passed`); exact
  non-live suite passed (`958 passed`, `73.21%` coverage); Python compilation,
  `git diff --check` and strict OpenSpec validation passed (`30` objects).
- 2026-08-25 synced `qa-mcp-runtime-target-contract` and archived the change at
  `openspec/changes/archive/2026-08-25-define-qa-mcp-runtime-target-contract/`.
- 2026-08-25 independent review cycle 1 returned `NO-GO`: the payload exposed
  a premature readiness status, the manifest mislinked full-suite evidence,
  and nested closed-schema cases needed direct coverage. The bounded rescue
  removed readiness/resolution behavior from A, corrected the manifest link
  and added nested unknown/incomplete schema tests.
- 2026-08-25 rescue verification passed: focused `30 passed`, exact non-live
  `958 passed` with `73.19%` coverage, compilation, diff and strict OpenSpec
  validation green; ready for fresh cycle-2 review.
- 2026-08-25 independent review cycle 2 returned `NO-GO`: the retained Windows
  smoke was bound to the pre-rescue wheel. The second bounded rescue refreshes
  Windows evidence from the exact final tree and expands tracked nested-schema
  rejection coverage to the reviewer's twelve-case boundary matrix.
- 2026-08-25T06:44:49Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

# Publish Hidden Direct-Execute Investigation Decision

## Status
4.done

## Owner
unassigned

## Series
oss-06-i2

## Order Index
405.2

## OpenSpec Stage
archived

## Source
- Deterministic review preflight for OSS-06-I1 returned
  `investigation-required` before semantic review.
- Retained hidden-desktop, direct-`/Execute`, prompt and cleanup evidence from
  OSS-06-I1.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Publish the already completed hidden-desktop/direct-`/Execute` engineering
decision as a clean, documentation-only investigation result. This card does
not publish the combined production candidate and does not admit
`open_external_processor`.

## Acceptance
- The decision binds the exact retained Windows platform, target, source,
  executable, wheel, prompt and cleanup lineage without exposing sensitive UI
  or credentials.
- It records that the chooser route is non-admitting and that the hidden
  direct-`/Execute` architecture is the only eligible production direction.
- It records the canonical ChangeRail constraint: production successors are
  independently published in bounded units, with the final wire/public unit
  no larger than `500` LOC and covered by a separate published authorization.
- The card contains no production-code change and leaves stable tool admission
  unchanged.

## Blocks
- `oss-06-s7-admit-hidden-direct-execute-public-route`

## Change Set
1. `publish-hidden-direct-execute-investigation-decision` -
   `openspec/changes/archive/2026-08-30-publish-hidden-direct-execute-investigation-decision/`

## Verify
- `openspec validate publish-hidden-direct-execute-investigation-decision --strict`
- `openspec validate --all --strict`
- `git diff --check` plus explicit whitespace validation for untracked files.
- Delivery manifest scope-check proving that all OSS-06 production payload is
  excluded as preexisting successor work.

## Archive
- `openspec/changes/archive/2026-08-30-publish-hidden-direct-execute-investigation-decision/`

## Related
- `openspec/changes/publish-hidden-direct-execute-investigation-decision/`
- `.runtime/changerail/evidence/oss-06-i1-investigate-hidden-windows-desktop-automation/production-route-final/index.json`

## Result
The clean documentation-only decision is implemented, synced and archived.
It retains sanitized chooser `PARTIAL`, hidden lifecycle `FEASIBLE` and direct
candidate lineage without publishing production code or admitting the tool.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `publish-hidden-direct-execute-investigation-decision`

### Why
ChangeRail requires a clean published investigation before a bounded successor
may receive an authorization exception.

### Goal
Publish an exact, privacy-safe and non-admitting decision from the completed
OSS-06-I1 evidence.

### Scope
- Decision/spec/card documentation only.
- Exact retained evidence references and typed limitations.
- No production source, public capability or runtime mutation.

### Acceptance
- Decision is reproducible from retained evidence and names the exact final
  successor it blocks.
- Production candidate and unrelated `.codex/config.toml` remain excluded.

### Depends On
- none

### Related
- `openspec/changes/publish-hidden-direct-execute-investigation-decision/`

## Log
- 2026-08-30 retained native lineage audit passed, the new decision capability
  was synchronized, and the change was archived. Manifest scope excludes the
  complete production/A2/S1-S7 payload and `.codex/config.toml`; review is next.
- 2026-08-30 card created after operator authorized bounded decomposition.
- 2026-08-30T06:36:30Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

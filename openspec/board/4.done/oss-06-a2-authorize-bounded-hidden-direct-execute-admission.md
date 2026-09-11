# Authorize Bounded Hidden Direct-Execute Admission

## Status
4.done

## Owner
unassigned

## Series
oss-06-a2

## Order Index
405.3

## OpenSpec Stage
archived

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/oss-06-i2-publish-hidden-direct-execute-investigation-decision.md","investigation_id":"oss-06-i2-publish-hidden-direct-execute-investigation-decision","successor_card":"openspec/board/3.inprogress/oss-06-s7-admit-hidden-direct-execute-public-route.md","successor_id":"oss-06-s7-admit-hidden-direct-execute-public-route","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Summary
After the investigation decision is published, authorize exactly one final
successor to integrate and admit the hidden direct-`/Execute` route. The
authorization is capped at `500` production LOC and does not cover any other
card, route or authority.

## Acceptance
- The inline authorization binds one exact published investigation and one
  exact final successor path/id.
- `production_loc_ceiling` is `500` and protocol allowance is `true` only for
  the final reviewed capability integration.
- Foundation cards remain independently limited to `300` production LOC and
  cannot use this authorization.
- This card changes no production code, runtime behavior or stable tool
  profile.

## Depends On
- `oss-06-i2-publish-hidden-direct-execute-investigation-decision`

## Change Set
1. `authorize-bounded-hidden-direct-execute-admission`

## Verify
- Strict change/all OpenSpec validation.
- Exact investigation/successor relation checks.
- `git diff --check` and manifest scope-check with production payload excluded.

## Archive
- `openspec/changes/archive/2026-08-30-authorize-bounded-hidden-direct-execute-admission/`

## Related
- `openspec/changes/authorize-bounded-hidden-direct-execute-admission/`

## Result
The exact documentation-only authorization is synchronized and archived. It
binds only published I2 to final successor S7, caps the exception at `500`
production LOC and grants no runtime or stable-tool authority.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-hidden-direct-execute-admission`

### Why
The final successor introduces a backward-compatible bridge capability and is
larger than the ordinary `300`-LOC ceiling.

### Goal
Publish the exact bounded authorization required by deterministic preflight.

### Scope
- Authorization contract and relationship documentation only.
- No implementation, runtime action or stable admission.

### Acceptance
- Authorization validates only after the investigation is a clean tracked
  `4.done` artifact.
- Any path/id, ceiling or protocol mismatch fails closed.

### Depends On
- `oss-06-i2-publish-hidden-direct-execute-investigation-decision`

### Related
- `openspec/changes/authorize-bounded-hidden-direct-execute-admission/`

## Log
- 2026-08-30 review cycle 1 found the successor lane and retained negative
  fixture matrix incomplete; same-card rescue now binds S7 at its canonical
  `3.inprogress` review path and retains all required fail-closed mutations.
- 2026-08-30 exact tracked I2/S7 binding and the shared fail-closed preflight
  matrix passed; authorization spec was synchronized and the change archived.
- 2026-08-30 card created as the single authorization source for final S7.
- 2026-08-30T07:18:39Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

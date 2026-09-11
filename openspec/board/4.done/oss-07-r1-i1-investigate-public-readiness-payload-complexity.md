# Investigate OSS-07-R1 public-readiness payload complexity

## Status
4.done

## Owner
unassigned

## Series
oss-07-r1-i1

## Order Index
406.11

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Source
- Deterministic OSS-07-R1 review preflight returned
  `investigation-required` because the complete unpublished public-readiness
  payload measured approximately `313` added production LOC against the
  default `300` limit.
- The measurement arose after review-cycle-1 fixes for globally absent
  allowlist paths/sources and camelCase credential keys. Removing blank lines
  can lower the raw-line counter but is not accepted as a complexity decision.
- Successor:
  `openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`.

## Goal
Publish a bounded, reviewable decision on the smallest honest production-LOC
ceiling needed by the existing OSS-07-R1 public-readiness payload, without
changing its capability, authority, runtime or network scope.

## Acceptance
- The investigation records the exact successor id/path and explains why the
  complete replacement payload crosses the default `300` raw-added-line gate.
- The decision rejects whitespace deletion, source reclassification and scope
  exclusion as ways to evade the guard.
- The approved ceiling is no greater than `350` added production LOC and is
  limited to the current disclosure/provenance implementation already owned by
  OSS-07-R1.
- The decision sets `allow_new_authority_or_wire_protocol` to `false` and
  grants no live, SSH, Windows, 1C, release, credential or mutation authority.
- OSS-07-I2 remains byte-identical; OSS-07-I1 is not restored; exact SPDX
  `Apache-2.0` remains unchanged.
- The payload is metadata-only and passes strict OpenSpec, scope, whitespace
  and fresh independent review before publication.

## Scope
- Investigation/OpenSpec/board metadata only.
- No implementation, fixture, evidence payload, runtime or external action.

## Investigation Decision
The exact and only conditionally eligible successor is
`oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity` at
authorization-time path
`openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`.
The retained deterministic trigger is approximately `313` added production
lines for the complete unpublished payload against the default `300` limit.
This investigation does not import that payload, remeasure it, or certify its
current bytes; exact complete measurement remains a future admission
condition.

The maximum permitted future envelope is `production_loc_ceiling: 350`. This
is a hard ceiling for the current disclosure/provenance implementation already
owned by exact OSS-07-R1, not a target, expansion budget, global limit change,
or reusable waiver. A later fresh session must measure every successor-owned
production path at no more than `350` under stable classification and scope.
Above that ceiling, or if the exact successor identity/scope changes, delivery
must split or investigate again.

Whitespace deletion, production-source reclassification and owned-scope
exclusion are rejected as complexity-gate workarounds. They change accounting
without reducing the complete payload's review complexity. No future count may
pass by deleting blank lines for the gate, relabeling production paths as
tests/fixtures/docs/generated content/metadata, or omitting owned paths from
the manifest or measurement.

`allow_new_authority_or_wire_protocol` is `false`. The decision grants no new
public or wire contract and no live, SSH, Windows, 1C, TestClient, Apache,
release, credential, mutation, network or external-action authority. Any such
addition invalidates this decision and requires new scope.

Exact SPDX `Apache-2.0` remains unchanged. Published OSS-07-I2 remains
byte-identical, OSS-07-I1 remains absent, and OSS-08/OSS-09 implementation is
not part of this payload.

## Prepared Authorization Source Data
After this investigation is independently reviewed and published unchanged in
`4.done`, a later separate metadata-only authorization source may carry
exactly:

```json
{"investigation_card":"openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md","investigation_id":"oss-07-r1-i1-investigate-public-readiness-payload-complexity","successor_card":"openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md","successor_id":"oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity","production_loc_ceiling":350,"allow_new_authority_or_wire_protocol":false}
```

That separate source must depend on this investigation. Before using the
ceiling, the successor must depend on this investigation and reference only
the exact unchanged tracked `4.done` authorization source. This investigation
creates neither the source nor the successor reference. Missing, additional,
stale, untracked or mismatched fields/relations remain fail-closed.

## Change Set
1. `investigate-oss-07-r1-public-readiness-payload-complexity` -
   `openspec/changes/archive/2026-09-03-investigate-oss-07-r1-public-readiness-payload-complexity/`

## Depends On
- Published OSS-07-I2 safety matrix and immutable OSS-07 final-NO-GO lineage.

## Blocks
- `oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity` at
  `openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`

## Verify
- `bin/openspec validate
  investigate-oss-07-r1-public-readiness-payload-complexity --strict`,
  `bin/openspec validate
  qa-mcp-public-readiness-payload-complexity-decision --strict`, and pre-archive
  `bin/openspec validate --all --strict` passed (`69/69`).
- Agent-driven spec sync produced requirements identical to the delta; archive
  used `--skip-specs` only after that equality check. Post-archive
  `bin/openspec validate --all --strict` passed (`68/68`).
- Focused literal audit found the exact investigation/successor paths and ids,
  exact six-field object in the card and design, ceiling `350`, boolean
  authority/wire flag `false`, exact `Blocks` relation, separate-source rule,
  and all three prohibited accounting workarounds.
- Delivery-manifest working-tree scope reconciliation passed with only this
  card, the five-file archived change, and the new synced capability; OSS-07-I2
  matched `HEAD`, OSS-07-I1 remained absent, and no successor, license,
  OSS-08/09, product, test, fixture, evidence-payload or runtime path changed.
- `git diff --check`, explicit untracked trailing-whitespace scan and focused
  public-safety scan passed with zero findings. This repository has no local
  `scripts/public-surface-scan.py`, so that optional project scanner was
  recorded unavailable rather than claimed as executed.
- Test-first and Windows-native verification are not applicable to this
  metadata-only investigation. No live, SSH, Windows, 1C, TestClient, Apache-
  service, network, credential, mutation or release operation ran.

## Archive
- `openspec/changes/archive/2026-09-03-investigate-oss-07-r1-public-readiness-payload-complexity/`

## Related
- `openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`
- `openspec/board/4.done/oss-07-i2-freeze-fail-closed-public-safety-matrix.md`
- `openspec/changes/archive/2026-09-03-investigate-oss-07-r1-public-readiness-payload-complexity/`

## Result
Metadata-only investigation decision completed, synced and archived. Exact
OSS-07-R1 is the only conditionally eligible successor; the future maximum
production envelope is `350`, accounting workarounds are prohibited, and new
authority/wire protocol remains false. The investigation makes no current
successor size, byte, test or publication certification and creates no direct
authorization source. The card remains in `3.inprogress` for fresh independent
review and review-gated publication.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-oss-07-r1-public-readiness-payload-complexity`

### Why
The deterministic complexity gate must be resolved by a published decision,
not by mechanically reducing whitespace in an otherwise unchanged payload.

### Goal
Define one bounded, non-reusable ceiling for the exact OSS-07-R1 successor.

### Scope
- Exact successor identity, production-LOC ceiling and explicit non-authority
  metadata.
- No source implementation or runtime evidence changes.

### Acceptance
- The decision permits at most `350` production LOC only for the named
  successor and cannot authorize another card or a new protocol/authority.
- Any changed successor, ceiling or authority flag requires a new published
  investigation.

### Depends On
- Published OSS-07-I2 safety matrix and immutable OSS-07 final-NO-GO lineage.

### Related
- `openspec/changes/investigate-oss-07-r1-public-readiness-payload-complexity/`

## Log
- 2026-09-03 created after deterministic preflight measured the complete
  OSS-07-R1 payload above the default `300` production-LOC gate. The prior
  whitespace-only reduction was discarded; the verified implementation and
  Apache-2.0/I2 boundaries are retained unchanged in its isolated workspace.
- 2026-09-03 fast-forwarded one metadata-only decision change with exact
  successor identity, maximum ceiling `350`, closed authority/wire flag,
  prohibited accounting workarounds, and no successor implementation import.
- 2026-09-03 completed the bounded decision, synced its new capability, proved
  exact object/lineage/scope/whitespace/public-safety boundaries, and archived
  the fully completed change. The card remains in `3.inprogress` for fresh
  independent ordinary-risk review; no runtime or external operation ran.
- 2026-09-03T02:30:46Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

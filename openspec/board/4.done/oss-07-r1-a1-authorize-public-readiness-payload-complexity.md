# Authorize OSS-07-R1 public-readiness payload complexity

## Status
4.done

## Owner
unassigned

## Series
oss-07-r1-a1

## Order Index
406.12

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md","investigation_id":"oss-07-r1-i1-investigate-public-readiness-payload-complexity","successor_card":"openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md","successor_id":"oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity","production_loc_ceiling":350,"allow_new_authority_or_wire_protocol":false}`

## Source
- Published investigation:
  `openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md`.
- Exact successor prepared in its isolated delivery workspace:
  `openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`.
- The investigation requires a distinct, unchanged tracked `4.done`
  authorization source before the successor may use the bounded ceiling.

## Goal
Publish the exact non-reusable authorization source that binds the published
I1 investigation to the existing OSS-07-R1 successor with a maximum complete
production envelope of `350` and no new authority or wire protocol.

## Acceptance
- The card contains exactly the six-field `Investigation authorization`
  object required by ChangeRail and byte-for-byte matches the object prepared
  by published I1.
- The object binds only the published I1 path/id and exact OSS-07-R1
  authorization-time path/id, with integer `production_loc_ceiling: 350` and
  boolean `allow_new_authority_or_wire_protocol: false`.
- `Depends On` references I1 and the card explains that the successor must
  separately depend on I1 and reference this exact unchanged tracked `4.done`
  source before deterministic admission.
- The authorization grants no new public/wire contract, credential, mutation,
  live, SSH, Windows, 1C, TestClient, Apache, network, release or other external
  authority.
- Whitespace deletion, production-source reclassification and owned-scope
  exclusion remain prohibited as complexity-gate workarounds.
- Exact SPDX `Apache-2.0` and published OSS-07-I2 remain unchanged; OSS-07-I1
  remains absent; no OSS-07-R1 implementation or OSS-08/09 work is imported.
- The metadata-only payload passes strict OpenSpec, exact-object, dependency,
  scope, whitespace, public-safety and fresh independent review gates before
  scoped publication to `origin/main`.

## Scope
- This board card and its OpenSpec authorization metadata only.
- No implementation, test, fixture, evidence payload, license file, runtime,
  service, network or external action.

## Authorization Boundary
This source authorizes only later deterministic review admission of the exact
named successor when its complete honest production scope measures no more
than `350` lines. It is not a reusable waiver, implementation budget, global
limit change, payload certification or publication approval.

The successor must still carry reciprocal dependency metadata, reference this
exact unchanged tracked `4.done` source under its Review section, pass
deterministic preflight, retain its full verified evidence and obtain a fresh
independent semantic review. Any changed path/id, payload above `350`, new
authority/wire behavior or accounting workaround invalidates this source.

## Change Set
1. `authorize-oss-07-r1-public-readiness-payload-complexity` -
   `openspec/changes/archive/2026-09-03-authorize-oss-07-r1-public-readiness-payload-complexity/`

## Depends On
- `oss-07-r1-i1-investigate-public-readiness-payload-complexity` at
  `openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md`

## Blocks
- `oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity` at
  `openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`

## Verify
- Exact-object audit parsed the card JSON and proved byte equality with the one
  prepared object in published I1: six exact ordered fields, integer ceiling
  `350`, boolean authority/wire flag `false`, exact I1 and successor paths/ids,
  sole I1 dependency, future reciprocal-reference contract and all three
  prohibited accounting workarounds.
- `bin/openspec validate
  authorize-oss-07-r1-public-readiness-payload-complexity --strict`,
  `bin/openspec validate
  qa-mcp-public-readiness-payload-complexity-authorization --strict` and
  pre-archive `bin/openspec validate --all --strict` passed (`70/70`).
  Agent-driven sync produced requirements identical to the delta; archive used
  `--skip-specs` only after that equality check. Post-archive strict validation
  passed (`69/69`).
- Delivery-manifest working-tree reconciliation passed with only this card,
  the five-file archived change and the new synced capability. Published I1
  and OSS-07-I2 matched `HEAD`; the successor and OSS-07-I1 remained absent;
  no implementation, test, fixture, evidence payload, license, runtime,
  service, OSS-08/09 or unrelated active-change path entered scope.
- `git diff --check` and an isolated temporary-index `git diff --cached
  --check` covered tracked and untracked paths and passed. The focused
  public-safety scan found zero private-key, access-key, credential-URL, email,
  Windows-user-path or lab-path findings. This repository has no local
  `scripts/public-surface-scan.py`, so that optional scanner was recorded
  unavailable rather than claimed as executed.
- Test-first, live, SSH, Windows-native, 1C, TestClient, Apache-service,
  credential, mutation, network and release verification are prohibited and
  not applicable to this metadata-only authorization. No such payload or
  service operation ran; only ChangeRail's required Git remote preflight and
  eventual scoped push use publication transport.

## Archive
- `openspec/changes/archive/2026-09-03-authorize-oss-07-r1-public-readiness-payload-complexity/`

## Related
- `openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md`
- `openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`
- `openspec/board/4.done/oss-07-i2-freeze-fail-closed-public-safety-matrix.md`
- `openspec/changes/archive/2026-09-03-authorize-oss-07-r1-public-readiness-payload-complexity/`

## Result
Metadata-only authorization source completed, synced and archived. It binds
published I1 to exact OSS-07-R1 with the byte-identical six-field object,
ceiling `350`, closed authority/wire flag and prohibited accounting
workarounds. The successor payload remains absent and uncertified; this card
remains in `3.inprogress` for fresh independent review and review-gated
publication.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-oss-07-r1-public-readiness-payload-complexity`

### Why
The published investigation is intentionally not direct authorization; the
ChangeRail complexity guard requires a separate tracked authorization source
that binds the exact investigation, successor, ceiling and authority flag.

### Goal
Create the one exact, non-reusable metadata source consumed by later
OSS-07-R1 deterministic preflight.

### Scope
- Authorization card, OpenSpec artifacts, synced capability and archive
  metadata only.
- No successor payload or runtime action.

### Acceptance
- The six-field object, I1 dependency and fail-closed successor conditions are
  explicit and independently reviewable.
- Publication leaves the authorization card unchanged and tracked in
  `4.done` for exact later reference.

### Depends On
- `oss-07-r1-i1-investigate-public-readiness-payload-complexity`

### Related
- `openspec/changes/archive/2026-09-03-authorize-oss-07-r1-public-readiness-payload-complexity/`

## Log
- 2026-09-03 created after I1 was independently reviewed, published to
  `origin/main` at commit `63f104fe62db5b4c339b4076acc7482718271fc2`,
  and resolved in `4.done`. The authorization remains metadata-only and grants
  no new authority or wire protocol.
- 2026-09-03 fast-forwarded one metadata-only authorization change with the
  exact I1-prepared object, hard `350` ceiling, closed authority/wire flag,
  prohibited accounting workarounds and no successor payload import.
- 2026-09-03 completed the exact authorization source, synced its new
  capability, proved object/lineage/scope/whitespace/public-safety boundaries,
  and archived the fully completed change. The card remains in `3.inprogress`
  for fresh independent ordinary-risk review; no runtime or external operation
  ran beyond required Git publication transport.
- 2026-09-03T02:52:23Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

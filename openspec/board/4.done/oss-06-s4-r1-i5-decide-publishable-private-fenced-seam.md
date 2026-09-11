# Decide Publishable Private Fenced Seam

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i5

## Order Index
405.1019

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Investigation classification: `mandatory offline investigation/design decision after the I4 composition stop; not another implementation attempt`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Decision payload type: `investigation/design only; zero production or test implementation`
- Published decision lineage:
  `openspec/board/4.done/oss-06-s4-r1-i3-decide-hidden-desktop-inventory-observation-boundary.md`
  at `8f2bce4f4f49b6c80b565bec0ce15b61a38e14fa`

## Summary
Reconstruct the exact clean-HEAD versus dirty-candidate dependency boundary
that blocked I4, then publish one privacy-safe offline decision: either
authorize one minimal separately reviewable private fenced-seam extraction and
composition relative to clean HEAD, or conclude that no bounded extraction is
valid and require architectural redesign/supersession of I4.

## Source Lineage
- Published I3 decision:
  `openspec/board/4.done/oss-06-s4-r1-i3-decide-hidden-desktop-inventory-observation-boundary.md`
  at `8f2bce4f4f49b6c80b565bec0ce15b61a38e14fa`.
- Blocked I4 card:
  `openspec/board/3.inprogress/oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause.md`.
- Retained privacy-safe I4 composition evidence and ignored delivery manifest
  under `.runtime/changerail/` are evidence only and remain unpublished.
- I4 stopped before implementation because clean published HEAD lacks the
  private fenced S4 sample/pre-receipt diagnostic seam: a wired classifier
  would absorb prohibited unreviewed S4-R1 predecessor bytes, while a
  standalone classifier would be dormant and not independently verifiable.

## Acceptance
- Remain offline and local: use only published artifacts, current source/diff
  analysis, retained privacy-safe I4 composition evidence and safe no-1C
  analysis. Do not launch or connect to 1C, retry or confirm live behavior,
  access a target, mutate real Windows configuration, perform S7 work, use
  `User@192.*`, or access the retained evidence-only
  `historical-user@192.0.2.201` identity.
- Preserve every pre-existing dirty S4-R1, S7, fixture, OSS-07 and OSS-08 byte.
  The required immutable baselines are S4 source diff
  `01bf8f777ac6b15cca81cca6d23157ae4af8530b508cece835ba5b799e71f3c8`,
  S7 diff
  `504320daebf74e7b7e581f0a5ff7f8d6b2908fae5fe526fc0dfa5da765965709`,
  fixture tree
  `5a1e42727b845d641705dfa07904de505220866d877e0f2a5d26a3883248e629`,
  OSS-07/08 diff
  `7cec4fcc3a24c62bc8c75e447365bedca75efefd1fe1c662352c40912e6f8010`,
  and OSS-07 untracked changes
  `c8c734758f14a2a31722ff3ae287c1ac51f16e79fcdfa804c7b2f3b543b369d8`.
- Reconstruct the exact dependency boundary between clean published HEAD and
  the dirty candidate: enumerate the required private seam predicates,
  ownership/call relationships and compile/verification dependencies; identify
  which bytes are absent from HEAD, which dirty predecessor regions supply
  them, and why dormant or partial composition is invalid.
- Publish exactly one outcome. Outcome A may authorize one minimal separately
  reviewable private seam extraction/composition relative to clean HEAD only
  if it defines exact owned paths or source predicates, a dependency ceiling,
  hostile verification floor, rollback, and a fail-closed staging rule that
  makes a later I4 independently compilable and publishable. Outcome B must
  state that no such bounded extraction is valid and require architectural
  redesign/supersession of I4.
- The decision grants no seam or classifier implementation, runtime correction,
  test payload, source change, live confirmation, retry, target, Windows
  mutation, public route or S7 authority. Any authorized extraction and any
  later I4 work require separate accepted cards and fresh independent review.
- Publish only this card, its OpenSpec artifacts, curated privacy-safe findings,
  synced decision specification and the minimum linkage metadata required by
  the final handoff. Preserve I4 and its artifacts otherwise unchanged.
- Pass strict change/all OpenSpec validation, focused privacy and forbidden-
  endpoint checks, untracked-aware whitespace checks, immutable-baseline
  comparison, delivery-manifest scope reconciliation and `git diff --check`
  before a fresh independent review and explicit-path scoped publication.

## Change Set
1. `decide-publishable-private-fenced-seam`

## Verify
- Retained I4 evidence and bounded local predicates reproduced all eight
  clean-HEAD-absent dependency families, three core candidate paths, five
  transferred-observer integration paths and zero staging.
- Strict change/capability/all OpenSpec validation, focused privacy/forbidden-
  endpoint checks, untracked-aware whitespace, manifest scope and
  `git diff --check` passed before archive.
- S4, S7, fixture and OSS-07 untracked hashes matched their supplied
  baselines; the supplied OSS-07/08 aggregate remained retained with both card
  files additionally bound to unchanged per-file hashes.
- The explicit staging plan contains only I5 documentation/OpenSpec paths and
  zero production/test paths. Windows-native, 1C, endpoint, target, live and
  S7 execution were prohibited, not applicable and not run.
- Review-rescue evidence retained current `main`/`origin/main` remote
  reachability and the explicit eight-path I5 versus 67-path protected
  ownership partition. No historical pre-edit remote receipt is claimed.
- The supplied protected hashes remain exact. Because no delivery-start digest
  exists for every individual untracked S7/I4 file, no retroactive full-set
  hash comparison is claimed; review cycle 1 established protected aggregate
  `956de29464466db81ca8625f29814c9fc45a96d10991568c855b51deb3d4603e`
  and I4 tree
  `df7eb9df2e6ac8b1f8de47b5fdf779c877b38b9080c1d3ceca5d98edc8eb51b4`
  for rescue/re-review/publish preservation.

## Archive
- `openspec/changes/archive/2026-09-01-decide-publishable-private-fenced-seam/`

## Related
- `openspec/changes/archive/2026-09-01-decide-publishable-private-fenced-seam/`
- `docs/protocol-research/evidence/private-fenced-seam-publication-decision-2026-09-01/findings.md`
- `openspec/board/4.done/oss-06-s4-r1-i3-decide-hidden-desktop-inventory-observation-boundary.md`
- `openspec/board/3.inprogress/oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause.md`
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Result
Outcome A selected: exactly one later separately accepted clean-base seam card
may own the seven allowlisted fenced liveness/diagnostic paths and predicates,
replace exactly the two existing clean-HEAD worker inventory call sites, and
pass the connected hostile floor on its exact staged tree. Its dependency/LOC,
rollback and fail-closed staging ceilings are published in the curated
findings. I5 implements no seam/source/test payload; current I4 remains blocked
until that seam is independently reviewed/published and I4 is replanned
against it.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-publishable-private-fenced-seam`

### Why
I4 cannot be compiled, hostile-verified and scoped-published from clean HEAD:
its required private fenced seam exists only inside the protected dirty S4-R1
candidate. Another implementation attempt would repeat the prohibited
composition failure rather than decide whether an independently publishable
dependency can exist.

### Goal
Publish one offline dependency-boundary decision that either authorizes exactly
one bounded private seam extraction/composition for a later card or requires
architectural redesign/supersession of I4.

### Scope
- Published lineage, clean-HEAD source, dirty-candidate diff and retained
  privacy-safe I4 composition evidence.
- Documentation and one OpenSpec decision capability only.
- No production/test source, runtime, target, Windows or S7 action.

### Acceptance
- The clean-versus-dirty boundary is exact enough for an independent reviewer
  to reproduce without accessing a live target.
- Exactly one Outcome A or Outcome B is published, with no implied
  implementation or live authority.

### Depends On
- Published I3 decision at
  `8f2bce4f4f49b6c80b565bec0ce15b61a38e14fa`.
- I4 composition safety stop and retained privacy-safe evidence.

### Related
- `openspec/changes/decide-publishable-private-fenced-seam/`

## Log
- 2026-09-01 materialized as exactly one linked offline investigation/design
  decision after I4's mandatory composition stop; it is not a repeated
  implementation and grants no source, runtime, live, target, Windows, public
  route or S7 authority.
- 2026-09-01 fast-forwarded one documentation/OpenSpec-only decision change;
  its first gate preserves all supplied baselines and its binary outcome rule
  cannot authorize implementation, runtime access or dirty predecessor
  publication.
- 2026-09-01 offline analysis selected Outcome B: a pure seam unit has no
  clean-HEAD consumer, while the actual worker/diagnostic consumer closes over
  protected S4-R1 transfer, checkpoint and marker-derivation predicates. I4
  requires architectural redesign/supersession; no I4 or source/test path was
  edited.
- 2026-09-01 completed the documentation-only decision, synced its capability
  and archived the change. Strict OpenSpec, privacy/endpoint, protected-byte,
  scope and whitespace gates passed; no Windows, 1C, endpoint, target, live or
  S7 action ran. Card remains in `3.inprogress` for fresh independent review.
- 2026-09-01 review cycle 1 returned `NO-GO`: Outcome B had not refuted the
  existing two-call-site clean-HEAD composition, remote/ownership evidence was
  incomplete and full-set protected hashing was over-claimed. Same-card rescue
  attempt 1 changed only decision/evidence claims: selected bounded Outcome A,
  retained current remote/ownership evidence, stated the historical hash limit
  and bound all 67 protected records from cycle 1 onward. No source/test,
  runtime, endpoint, Windows, target or S7 action ran.
- 2026-09-01T19:17:41Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

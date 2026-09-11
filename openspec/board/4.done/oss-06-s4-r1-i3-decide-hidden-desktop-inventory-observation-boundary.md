# Decide Hidden-Desktop Inventory Observation Boundary

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i3

## Order Index
405.1017

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published predecessor decision:
  `4285a3d154c784f28625ade51b59297bf6ad2679`

## Summary
Use only the consumed-confirmation evidence and offline source analysis to
explain why the exact hidden-desktop inventory still retains
`first_window_inventory/first_window_inventory_failed` after the published
exact child/listener/job/TPort liveness fence, then decide whether one minimal
testable successor can be authorized or the boundary requires architectural
redesign.

## Source Lineage
- Blocked source card:
  `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`.
- Published predecessor decision:
  `4285a3d154c784f28625ade51b59297bf6ad2679`.
- Consumed confirmation evidence:
  `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/live-confirmation-20260901t1711z/`.
- Repeated blocker: the exact first tracked S4 row retained
  `first_window_inventory/first_window_inventory_failed` despite the sole
  authorized liveness-fenced inventory correction.

## Acceptance
- Remain offline: no 1C launch or connection, live retry, new confirmation,
  target substitution, real Windows configuration mutation, S7 work, or use
  of any endpoint other than the already-retained exact
  `historical-user@192.0.2.201` evidence identity; no alternate principal or address
  is permitted.
- Preserve the blocked S4-R1 production/test/change payload and every S7,
  fixture, OSS-07 and OSS-08 path byte-for-byte. Publish only this card's
  OpenSpec artifacts, curated privacy-safe findings, synced decision spec and
  minimum board metadata.
- Reconstruct the exact first-inventory call boundary from retained evidence
  and source: desktop handle provenance and lifetime, observation-thread
  desktop binding, child/listener/job/TPort fence semantics, enumeration API
  result and error propagation, and the cleanup/zero-action boundary.
- Explain which invariant the published fence proves and which required
  inventory invariant remains unobserved; do not infer API-level cause from a
  typed failure alone or collapse inventory error into successful empty.
- Publish exactly one decision: either authorize one minimal later-session
  successor correction inside the existing private S4 seam, with one explicit
  hostile verification target and fail-closed ceiling, or state that no
  bounded correction is justified and architectural redesign is required.
- Grant no successor implementation, live confirmation, retry, target or S7
  authority. Any authorized successor must be delivered by a separate card
  after publication and fresh independent review of this decision.
- Pass strict change/all OpenSpec validation, focused privacy and forbidden-
  endpoint checks, protected-path byte comparison, manifest scope
  reconciliation and `git diff --check` before fresh independent review.

## Change Set
1. `decide-hidden-desktop-inventory-observation-boundary`

## Verify
- Consumed confirmation JSON parsing and exact typed-value inspection passed;
  no new runtime evidence or probe was created.
- Strict capability/change validation passed before archive; all 58 current
  OpenSpec items passed after archive.
- Focused privacy/endpoint and untracked-aware whitespace checks passed. The
  project public-surface scanner is absent and is not claimed.
- The aggregate protected-path SHA-256 evidence remained byte-identical at
  `d38323700eac2bbface51a2d918cb4eb100d699f27bab784ccbd09d373af698a`;
  manifest scope reconciliation passed for the explicit decision paths.
- Windows-native execution is not applicable to this docs/OpenSpec-only
  payload and was prohibited by the card; no Windows, SSH or 1C command ran.

## Archive
- `openspec/changes/archive/2026-09-01-decide-hidden-desktop-inventory-observation-boundary/`

## Related
- `openspec/changes/archive/2026-09-01-decide-hidden-desktop-inventory-observation-boundary/`
- `docs/protocol-research/evidence/hidden-desktop-inventory-observation-boundary-decision-2026-09-01/findings.md`
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`
- `openspec/board/4.done/oss-06-s4-r1-i2-decide-observation-liveness-boundary.md`

## Result
The consumed failure is `inventory_boundary_unresolved`: the retained outer
pair collapses pre-fence liveness refusal, composite inventory error and
post-fence lifecycle change, while the inventory composite further collapses
hidden, operator and isolation-validation sources. The admitted candidate
contains the exact liveness fence, but the retained row does not prove the
fence passed or identify a desktop API failure.

The decision authorizes exactly one later, separately accepted successor: a
behavior-neutral closed-vocabulary cause classifier at the private S4
inventory/diagnostic seam, bound to one injected hostile RED/GREEN matrix.
It authorizes no implementation, behavioral correction, live confirmation,
retry, target access or S7 work. Failure to preserve behavior/call counts, or
evidence that ownership/binding must change, requires architectural redesign.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-hidden-desktop-inventory-observation-boundary`

### Why
The published liveness fence observed the exact child and listener around the
inventory call, but the consumed confirmation retained the same first-
inventory failure. The remaining desktop/enumeration boundary must be decided
before another correction can be justified.

### Goal
Publish one privacy-safe, source-grounded inventory-boundary decision and
either one minimal successor authorization with hostile verification or an
architectural-redesign requirement.

### Scope
- Retained consumed-confirmation evidence and offline source analysis.
- Documentation and one OpenSpec decision capability only.
- At most safe disposable no-1C local probes if source reasoning is otherwise
  insufficient.
- No production/test implementation, remote execution, real configuration,
  live authority or public S7 route.

### Acceptance
- The decision distinguishes proven liveness from unproven desktop-call
  usability and binds every claim to retained evidence or an exact source
  predicate.
- Any sole successor authorization names one seam, one hostile verification
  oracle and a fail-closed stop; otherwise the decision explicitly requires
  redesign.

### Depends On
- none

### Related
- `openspec/changes/decide-hidden-desktop-inventory-observation-boundary/`

## Log
- 2026-09-01 materialized as the required offline investigation/design
  successor after the published liveness fence retained the same first-window
  inventory refusal; no implementation or live authority is included.
- 2026-09-01 fast-forwarded one documentation/OpenSpec-only decision change;
  its apply-ready artifacts authorize only a behavior-neutral private cause
  classifier with one hostile oracle, not implementation or runtime access.
- 2026-09-01 offline delivery published the curated boundary findings, synced
  the new capability and archived the change. Strict OpenSpec, retained-JSON,
  privacy/endpoint, protected-byte and whitespace gates passed without 1C,
  SSH, Windows execution, live retry, target mutation or S7 work.
- 2026-09-01T17:55:04Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

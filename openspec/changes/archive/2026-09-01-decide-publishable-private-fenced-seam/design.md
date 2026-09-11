## Context

Published HEAD at I3 commit
`8f2bce4f4f49b6c80b565bec0ce15b61a38e14fa` authorizes one later
behavior-neutral cause classifier at a private fenced inventory/diagnostic
seam. I4's mandatory composition gate established that this seam is absent
from published HEAD and exists only inside the protected uncommitted S4-R1
candidate. Wiring the classifier would therefore absorb unreviewed predecessor
bytes; isolating it as a dormant unit would not prove integration behavior.

I5 is the mandatory investigation/design break in that implementation
staircase. It uses no live runtime or target. Its evidence sources are the
published I3 artifacts, the I4 card and artifacts, the ignored privacy-safe I4
manifest/composition evidence, and local clean-HEAD/current-diff analysis.

## Goals / Non-Goals

**Goals:**

- Reproduce the exact clean-HEAD versus dirty-candidate seam boundary using
  bounded source predicates and dependency relationships.
- Decide whether one minimal separately reviewable private seam extraction can
  be authorized for a future card.
- If authorization is valid, define its exact ownership ceiling, hostile
  verification floor, rollback and fail-closed staging rule.
- Otherwise require architectural redesign/supersession of I4.
- Preserve all protected payload baselines and publish only privacy-safe I5
  decision material.

**Non-Goals:**

- Implementing or editing any seam, classifier, runtime correction, test
  payload, production source or test source.
- Launching or connecting to 1C, performing a live retry/confirmation,
  accessing any target, or mutating real Windows configuration.
- Granting public route, wire, live admission, S7 or source-change authority.
- Restoring, staging, committing or publishing any dirty predecessor payload.

## Decisions

### Reconstruct two source views without manufacturing a clean worktree

Use `git show`/`git grep` against published HEAD for the clean view and
read-only local source/diff inspection for the candidate view. Record exact
symbols or source predicates, owning files and call edges rather than copying
large source excerpts. This keeps the protected dirty tree in place and avoids
a substitute worktree, checkout or restoration operation.

Alternative considered: reset or isolate the candidate in another worktree.
Rejected because I4 already identified composition as the blocker and the
operator requires the current dirty payload to remain byte-identical.

### Apply a fail-closed binary decision rule

Authorize Outcome A only when the boundary demonstrates all of the following:

1. a behavior-neutral private seam has exact owned paths or syntactic source
   predicates separable from every protected predecessor behavior;
2. its dependency ceiling includes only clean-HEAD facilities and explicit
   new private seam-owned units, with no S4-R1, S7, fixture, OSS-07 or OSS-08
   byte;
3. it can compile and pass a hostile injected verification floor independently
   before any later I4 classifier is added;
4. explicit-path staging can be mechanically rejected if a protected path or
   non-owned hunk appears; and
5. rollback is deletion/reversion of only the future seam-owned payload,
   leaving clean HEAD and all protected dirty bytes unchanged.

If any condition is not source-proven, publish Outcome B and require
architectural redesign/supersession of I4. Absence of proof is not treated as
permission.

Alternative considered: authorize a partial or dormant seam skeleton and let
I4 prove it later. Rejected because that repeats the exact composition defect
and cannot independently verify the integration boundary.

### Separate decision authority from future implementation authority

Even Outcome A is only design authority for one new linked card. That future
card must independently materialize, compile, hostile-verify, review and
publish the seam before I4 can be reconsidered. I5 itself owns documentation,
OpenSpec artifacts and at most minimum lineage metadata; it owns no `.go`,
Python or test path.

### Retain only curated offline evidence

The publishable finding records hashes, paths, symbol/source predicates and
dependency conclusions. Raw ignored I4 evidence, machine/UI dynamic values and
endpoint data remain excluded. No capture source or frame range exists for
this decision because no protocol capture or replay occurs. Runtime cleanup is
not applicable because no runtime process or external resource is started.

## Risks / Trade-offs

- **[Risk] Source predicates could accidentally describe protected candidate
  behavior too broadly.** → Require clean-HEAD absence/presence evidence,
  bounded symbol ownership and an explicit dependency ceiling; otherwise
  choose Outcome B.
- **[Risk] Outcome A could be mistaken for implementation or live authority.**
  → Repeat the no-authority clause in findings, spec, card result and successor
  handoff.
- **[Risk] Unrelated dirty changes could enter publication.** → Preserve the
  supplied baseline hashes, reconcile an explicit delivery manifest and use
  explicit-path staging only after independent GO.
- **[Trade-off] Documentation-only analysis cannot prove runtime behavior.** →
  Make no runtime claim; require a future seam card's offline hostile floor and
  fresh review before any later I4 composition.

## Migration Plan

1. Produce and review the curated binary decision without source changes.
2. If Outcome A is selected, create one separate accepted seam-extraction card
   owning only the exact bounded scope in the decision. I4 remains blocked
   until that card is independently published.
3. If Outcome B is selected, supersede I4 with an architectural redesign card;
   do not resume its classifier change.

Rollback of I5 is removal of only its published decision artifacts and linkage
metadata. No runtime or source rollback is needed. Rollback of any future
Outcome-A implementation must remove only its exact seam-owned paths/hunks and
must leave all protected payload baselines unchanged.

## Open Questions

- Resolved: clean HEAD already contains the real worker consumer with exactly
  two direct inventory call sites. The pure fenced sample and Windows wrapper
  are independent of transferred-observer, diagnostic and marker-derivation
  predicates, so one bounded clean-base composition remains valid.
- Resolved: the complete publishable seam must own its exact private
  liveness/diagnostic closure in seven allowlisted paths and prove the actual
  two consumer call sites through a standalone hostile oracle. It must not
  extract or stage dirty whole-file bytes.

## Published Outcome

Outcome A is selected. One later separately accepted seam card may compose the
private fenced sample, exact liveness/diagnostic ownership closure and exactly
two clean-HEAD worker call-site substitutions in the seven paths enumerated by
the curated findings. Its ceiling is three non-test plus four test Go paths,
250 added non-test Go lines, no new dependency/package/public/wire surface and
no marker derivation or unrelated S4/S7 bytes. It must pass the connected
offline hostile floor on its exact staged clean-base tree before review.

This design authorizes only that future card. It implements no seam or source
change. Current I4 remains blocked until the seam is independently published
and I4 is replanned against that published commit.

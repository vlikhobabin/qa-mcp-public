## Context

Published I15 commit `1be1829ee71b96f8c1c690c9fa55c2e8e14c1425`
is the current `origin/main` head. Its one authorized original-route canary
produced no typed Session-1 receipt, candidate invocation remained zero, no
S4/I13 row ran, exact cleanup passed and topology attribution remained
`NOT-VERIFIABLE`. I13 therefore remains active, unarchived and uncertified;
S4-R1 and S7 remain incomplete.

The card-405 roadmap gate already allows stable release to proceed when
`open_external_processor` is explicitly omitted. The tracked roadmap and
handoff cards, however, still contain stale I15 paths/counts and claim OSS-07
is fast-forward planned in `2.todo`, while the actual card is a story with no
OpenSpec artifacts in `1.backlog`.

This is an offline evidence/docs/spec/board-only decision. There are no capture
sources, frame ranges, dynamic protocol fields or replay strategy because it
adds no protocol claim. Runtime cleanup is not applicable because no live
contour, 1C process, candidate action or runtime state is created.

## Goals / Non-Goals

**Goals:**

- Bind the stable omission to the exact published-I15 fail-closed outcome.
- Make the stable standalone support claim unambiguous without deleting or
  changing dormant implementation, tests, tracked EPFs or foundations.
- Reconcile the exact affected board and public documentation with current
  paths, counts and OpenSpec state.
- Make OSS-07 the next separate card and record operator-approved
  `Apache-2.0` for its future first change.

**Non-Goals:**

- Retrying, authorizing, certifying or archiving I13/S4-R1/S7.
- Running a live contour, Windows/historical-user/1C/SSH command, `/Execute`, canary,
  S4/S5/S7 row or candidate action.
- Editing product/test/fixture/EPF/runtime source or license files.
- Creating OSS-07 OpenSpec artifacts or implementing OSS-07.

## Decisions

### 1. Published I15 and actual `origin/main` state are the evidence baseline

The decision records I15's exact outcome and commit, then checks current board
paths and active OpenSpec state directly. It does not reinterpret the failed
canary or create new runtime evidence. Treating the roadmap's stale prose as
the baseline was rejected because it incorrectly says OSS-07 is already
planned and points at pre-publication I15 paths.

### 2. Omission changes support status, not implementation ownership

The public README/tool reference will classify `open_external_processor` as
dormant/pre-stable and omit it from the declared stable release support
profile/matrix. The unchanged code-level `standalone` catalog remains a
64-tool pre-stable runtime inventory and is not a stable-support claim; the
declared stable support allowlist has 63 tools. Source, tests, Gherkin
vocabulary, tracked EPFs, published foundations and historical evidence remain
present. Removing those assets or changing source catalog membership was
rejected because this evidence/docs/spec/board-only card records a release
decision, not capability destruction or runtime implementation.

The later release/cutover work must enforce the 63-tool allowlist before
stable promotion. This does not implement OSS-07 or authorize a qualification
retry.

### 3. Incomplete certification lineage remains explicit

I13 stays in `3.inprogress` with its active change unarchived, while S4-R1 and
S7 stay in `2.todo` and incomplete. Parent and handoff prose may acknowledge
the stable omission, but MUST NOT mark those cards done, certified, superseded
or authorized for another attempt.

### 4. OSS-07 remains a separate story-stage card

This change corrects roadmap links/state to the actual
`1.backlog/oss-07-prepare-qa-mcp-public-repository-readiness.md`, records it as
the next card after publication, and carries the operator-approved
`Apache-2.0` choice into its handoff. It creates no OSS-07 change slug or
artifact. Folding OSS-07 planning into this payload was rejected because it
would widen scope beyond the omission decision.

### 5. Verification is entirely offline and scope-oriented

The proof floor is strict OpenSpec validation, deterministic board/dependency
assertions, JSON checks, public-surface/privacy scanning, Apache-2.0 path
assertions, tracked-plus-untracked whitespace checks, manifest scope and fresh
ordinary-risk review. Windows-native/live verification required for protocol
or behavior changes is explicitly not applicable because no such surface is
changed; running it would violate the card boundary.

## Risks / Trade-offs

- [Readers confuse dormant availability with stable support] -> label the
  public support matrix and README explicitly and retain the future
  qualification condition.
- [Historical foundations are mistaken for certification] -> state that I14
  and I15 are non-certifying and keep I13/S4-R1/S7 statuses unchanged.
- [Roadmap sequencing drifts again] -> assert exact board paths and absence of
  OSS-07 active/archive artifacts before review.
- [Scope accidentally reaches product or license files] -> derive a manifest,
  assert allowed paths and fail on source/test/EPF/license-path changes.

## Migration Plan

1. Retain a bounded I16 decision/findings pair derived only from published I15.
2. Reconcile the exact affected public docs and board cards.
3. Run offline verification, sync the decision spec and archive this change.
4. Obtain a fresh independent ordinary-risk review, publish the scoped payload
   and finalize only this card into `4.done`.

Rollback is a scoped revert of this decision payload; dormant implementation
requires no rollback because it is never modified.

## Open Questions

None. Future qualification and OSS-07 planning require separate cards.

# Record Stable-Profile Omission After I15

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i16

## Order Index
405.10199

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/2.todo/oss-06-stabilize-external-processor-open-flow.md`

## Source
- Published I15 commit `1be1829ee71b96f8c1c690c9fa55c2e8e14c1425`.
- `docs/protocol-research/evidence/i15-session1-admission-and-s4-isolation-2026-09-02/decision.json`.
- The parent roadmap release gate permits card 405 to be explicitly omitted
  from the stable standalone profile when target-bound certification remains
  incomplete.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Record the release-scope decision that `open_external_processor` remains
omitted from the stable standalone profile and public support matrix after I15
failed closed without a Session-1 receipt or candidate invocation. Preserve the
implemented foundations and incomplete I13/S4-R1/S7 lineage for a future,
separately authorized qualification effort, while unblocking OSS-07 repository
readiness and the downstream release sequence.

## Acceptance
- Bind the decision to published I15 and retain its exact outcome: one
  authorized canary, no typed Session-1 receipt, zero candidate invocation, no
  S4/I13 row and no further retry authority.
- Explicitly satisfy the roadmap's card-405 delivered-or-omitted release gate
  by omitting `open_external_processor` from the declared stable release
  support profile and public support matrix until a separately reviewed future
  qualification publishes. The unchanged code-level `standalone` catalog is
  pre-stable runtime inventory, not stable admission.
- Preserve OSS-06 product/test source, tracked EPFs, runtime authority and all
  published foundations plus source profile membership unchanged; omission is
  a support/profile decision, not source deletion, runtime implementation or
  certification. Stable cutover must enforce the declared 63-tool allowlist.
- Leave I13 active, unarchived and uncertified; leave S4-R1 and S7 incomplete
  and do not represent I14 or I15 as certification.
- Update the OSS-06 parent, S4-R1 parent, I13, S7, roadmap and OSS-07 handoff so
  they agree on omission, actual board state and the next executable card.
- Correct stale post-I15 roadmap/card paths and counts encountered inside the
  owned documentation scope, including the published I15 `4.done` path and
  nine-entry evidence count.
- Admit no live contour action, no historical-user/1C execution, no retry, no product or
  test change and no license-path change.
- Pass strict OpenSpec, exact board/dependency assertions, scoped public-surface
  and privacy checks, Apache-2.0 path checks, tracked-plus-untracked whitespace,
  manifest scope and fresh independent review before publication.

## Non-Goals
- Retrying I13, S4-R1, S7 or any Session-1 admission route.
- Removing dormant implementation or fixture source.
- Adding a new stable capability, public API or wire behavior.
- Implementing OSS-07, OSS-08 or OSS-09 in this card.

## Change Set
1. `record-stable-profile-omission-after-i15`

## Verify
- `bin/openspec validate record-stable-profile-omission-after-i15 --strict`,
  `bin/openspec validate qa-mcp-stable-profile-omission-after-i15 --strict` and
  `bin/openspec validate --all --strict` passed.
- Exact Git/board/dependency/JQ assertions passed for published I15, active and
  unarchived I13, incomplete S4-R1/S7 and story-stage OSS-07 with no artifacts.
- Scoped ChangeRail public-surface scan, README changed-line privacy,
  Apache-2.0 path, tracked-plus-untracked whitespace and `git diff --check`
  passed. Five pre-existing README `/opt` findings are outside changed lines.
- Delivery-manifest working-tree scope passed with no missing, extra or
  mismatched paths; retained ignored evidence index validates with eight entries.
- Offline catalog/matrix assertions prove 68 research inventory tools, 64
  unchanged pre-stable `standalone` catalog tools, 63 declared stable support
  tools and five explicitly non-stable inventory entries.
- Windows/live verification is not applicable because this decision changes no
  executable behavior and all such actions are explicitly forbidden.

## Archive
- `openspec/changes/archive/2026-09-02-record-stable-profile-omission-after-i15/`

## Related
- `openspec/board/4.done/oss-06-s4-r1-i15-retry-i13-s4-isolation-after-session1-admission-restoration.md`
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`
- `openspec/board/2.todo/oss-06-stabilize-external-processor-open-flow.md`
- `openspec/board/1.backlog/oss-07-prepare-qa-mcp-public-repository-readiness.md`
- `openspec/changes/archive/2026-09-02-record-stable-profile-omission-after-i15/`

## Result
Implemented and verified as one evidence/docs/spec/board-only omission
decision. `open_external_processor` is omitted only from stable standalone
release support/public matrix; the unchanged code-level `standalone` catalog
remains pre-stable inventory, and dormant source/tests/EPFs/authority/
foundations remain.
I13 remains active/unarchived/uncertified, S4-R1/S7 remain incomplete and
OSS-07 remains the next separate unplanned backlog story. No live contour,
retry, candidate action, product/test/license change or OSS-07 implementation
occurred.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `record-stable-profile-omission-after-i15`

### Why
Published I15 exhausted the sole authorized canary without a typed Session-1
receipt or candidate invocation, while the stable release gate requires either
card-405 delivery or an explicit omission.

### Goal
Publish the bounded omission decision, reconcile post-I15 documentation with
actual board state and hand OSS-07 off as the next separate backlog card.

### Scope
- Bounded public-safe decision evidence and a new decision capability.
- Exact affected OSS-06/I13/S4-R1/S7/I15/roadmap/OSS-07 board surfaces and the
  public support matrix.
- Offline OpenSpec, board, JSON, privacy/public-surface, Apache-2.0,
  whitespace, scope and independent-review gates only.

### Acceptance
- The decision preserves I15's exact fail-closed outcome and grants no retry.
- Only stable profile/support claims change; dormant source, tests, EPFs,
  authority and foundations remain intact.
- I13 remains active/unarchived/uncertified, S4-R1 and S7 remain incomplete,
  and OSS-07 remains an unplanned backlog story until a later separate card.

### Depends On
- Published I15 commit `1be1829ee71b96f8c1c690c9fa55c2e8e14c1425`.

### Related
- `openspec/changes/record-stable-profile-omission-after-i15/`

## Log
- 2026-09-02 created after published I15 exhausted its one authorized canary
  without typed admission or candidate invocation; the roadmap fallback is an
  explicit stable-profile omission before OSS-07.
- 2026-09-02T10:37:09Z accepted and fast-forwarded as one
  evidence/docs/spec/board-only decision change; no runtime or implementation
  action was admitted.
- 2026-09-02T10:55:07Z bounded decision evidence, stable-support docs and exact
  post-I15 board/OSS-07 handoff were reconciled. Six-entry retained evidence,
  strict OpenSpec, JSON/state, public/privacy, Apache-2.0, whitespace and
  manifest scope gates passed; Windows/live verification is not applicable.
  The decision capability was synced and archived while I13 and unrelated
  active changes remained untouched.
- 2026-09-02 review cycle 1 returned `NO-GO`: two I16 links used stale
  `2.todo` paths, and docs did not distinguish the unchanged 64-tool pre-stable
  code catalog from the declared 63-tool stable support profile. Same-card
  rescue attempt 1 corrects both within the existing docs/spec/board-only
  authority; no source/profile implementation is added.
- 2026-09-02 review cycle 2 returned `NO-GO`: the public matrix enumerated 59
  rather than all 63 declared stable tools, and retained evidence still named
  the old `2.todo` card path. Final bounded same-card rescue attempt 2 adds the
  four missing stable rows (`write_form_date`, `query_com`,
  `assert_com_count`, `com_connector_doctor`), proves exact set equality and
  refreshes the current-card 18-file public-surface evidence. No source/profile
  implementation or runtime action is added.
- 2026-09-02T11:51:05Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

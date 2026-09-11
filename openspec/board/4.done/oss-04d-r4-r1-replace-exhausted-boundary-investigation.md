# Replace Exhausted Operation Boundary Investigation

## Status
4.done

## Owner
unassigned

## Series
oss-04d-r4-r1

## Order Index
4034.855

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Replaces
- Unpublished exhausted design investigation
  `oss-04d-r4-investigate-operation-boundary-concurrency-and-bounds`.

## Source Lineage
- Latest safe published baseline:
  `af74de482bd32dd1190ea860aac54103422210a3`.
- OSS-04D-R4 cycle 3 ended with fresh `NO-GO` at tree
  `d09f7b834e415d08b43e6be3da1ed63edfe0109c` and fingerprint
  `sha256:05aa7a5edd265d08330c9ddec5830ec32bb40297e590a126d03954264e608be8`.
- Named stash `oss04d-r4-exhausted-review-payload-20260825` independently
  reconstructs that exact tree/fingerprint. It and the older R3 stash are
  evidence only and MUST NOT be published or restored wholesale.
- R4 review history records cycles 1–3 and rescue budget `2/2`, remaining `0`,
  exhausted `true`. The final R4 verdict has one blocker: exact credential and
  userinfo depths 1–5 plus paired safe controls were not carried consistently
  through archived design, synced spec and R6 public-path verification.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Goal
Publish the otherwise accepted R4 concurrency/bounds design as a clean linked
replacement with one exact, consistent userinfo/credential URL matrix across
design, spec and both real public execution paths.

## Acceptance
- Exact R3 and R4 lineage, recovery mappings, final findings, accepted
  invariants and retained evidence hashes are durable and secret-free.
- The replacement preserves context-local evidence authority, all six
  field-specific provenance grammars, actual canonical JSON byte/structure
  bounds, fixed-point URL handling and seven stable matrix rows.
- URL hostiles enumerate credential assignment and userinfo hidden at every
  exact encoding depth 1, 2, 3, 4 and 5; paired benign encoded-path and
  non-userinfo authority controls are explicit at every admitted depth.
- R6 verification requires every hostile and paired control through both real
  MCP and ScenarioRunner with identical absence/preservation outcomes.
- The ordered A2 → R5 → A3 → R6 handoff is recreated with one-to-one future
  `3.inprogress` authorization paths, machine ceilings 301, stricter runtime
  caps 300 and no new authority or wire protocol; only R6 unblocks OSS-04E.
- Payload is design-only: no `src/`, tests, runtime adapter, Windows, Docker,
  TestClient, live 1C or external action, and neither failed stash is restored.

## Scope
- Durable investigation/design documentation, OpenSpec artifacts and board
  lineage reconstructed from accepted reviewed R4 decisions.
- Read-only audit of retained R3/R4 verdicts, histories, evidence and exact
  named stashes.
- No production/runtime implementation or external mutation.

## Change Set
1. `replace-exhausted-qa-mcp-operation-boundary-investigation` -
   `openspec/changes/archive/2026-08-25-replace-exhausted-qa-mcp-operation-boundary-investigation/`

## Dependencies
- [OSS-04C](../4.done/oss-04c-compose-project-target-readiness.md) is published.
- OSS-04D-R3 and OSS-04D-R4 have fresh retained exhausted `NO-GO` histories.

## Blocks
- [OSS-04D-A2](oss-04d-a2-authorize-core-operation-boundary-replacement.md)
- [OSS-04D-R5](oss-04d-r5-implement-core-operation-boundary.md)
- [OSS-04D-A3](oss-04d-a3-authorize-operation-boundary-integration.md)
- [OSS-04D-R6](oss-04d-r6-integrate-operation-boundary-public-paths.md)
- `oss-04d-a2-authorize-core-operation-boundary-replacement`
- `oss-04d-r5-implement-core-operation-boundary`
- `oss-04d-a3-authorize-operation-boundary-integration`
- `oss-04d-r6-integrate-operation-boundary-public-paths`
- [OSS-04E lifecycle admission](oss-04e-bind-testclient-lifecycle-admission.md)

## Verify
- Exact lineage recovery: passed. Isolated worktrees reconstructed R3 tree
  `2fb0ad5...`/fingerprint `e75d981...` and R4 tree
  `d09f7b8...`/fingerprint `05aa7a5...` from their named stashes.
- Evidence/hash audit: passed (`2` exhausted lineages, cycle/rescue/final
  finding hashes, `10` decisions, `7` stable rows).
- URL matrix audit: passed after rescue 1 (exactly
  `40 = 5 × (3 hostile + 1 control) × 2 paths` cells; every hostile cell asserts
  no original/decoded fragment; depths 1–4 canonical control preservation,
  depth 5 non-fixed bounded rejection).
- Successor audit: passed (`A2 → R5 → A3 → R6`, two one-to-one future exact
  `3.inprogress` sources, ceilings `301`, runtime caps `300`, authority/wire
  false, only R6 unblocks OSS-04E).
- Design-only scope audit: passed (`0` production/test/runtime paths).
- Evidence index:
  `.runtime/changerail/evidence/oss-04d-r4-r1-replace-exhausted-boundary-investigation/index.json`.
- `bin/openspec validate qa-mcp-operation-boundary-concurrency-bounds-design --strict`:
  passed.
- `bin/openspec validate --all --strict`: `34 passed, 0 failed` before archive;
  `33 passed, 0 failed` after archive.
- Delivery manifest working-tree scope and `git diff --check`: passed.
- Test-first, Windows-native, live-runtime and external-action verification:
  not applicable; no SSH, Windows, TestClient, Docker, host-agent or runtime
  action was performed.
- Fresh independent ChangeRail design review cycle 2: `GO` (`6/6`
  acceptance, zero findings).

## Result
The full accepted R4 architecture is re-materialized from published `main`
without restoring either failed stash. The final missing oracle is now an exact
depth 1–5 credential/userinfo/control table repeated consistently in durable
docs, archived design, synced spec and R6 acceptance/verification for both real
MCP and ScenarioRunner. A2/R5/A3/R6 are recreated with one-to-one future review
paths and bounded caps. The design capability is synced and the change is
archived at
`openspec/changes/archive/2026-08-25-replace-exhausted-qa-mcp-operation-boundary-investigation/`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- Deliver
  [OSS-04D-A2](../2.todo/oss-04d-a2-authorize-core-operation-boundary-replacement.md)
  as the next sequential card.

## Change 1: `replace-exhausted-qa-mcp-operation-boundary-investigation`

### Why
The accepted R4 design was not publishable because its final exact
userinfo/control depth matrix was inconsistent across its handoff artifacts.

### Goal
Recreate the full accepted design from clean published main and close the one
remaining matrix oracle without restoring the exhausted payload.

### Scope
- Exact R3/R4 lineage and accepted invariant reconstruction.
- Complete depth 1–5 credential/userinfo/control table across design/spec/R6.
- Reciprocal A2 → R5 → A3 → R6 board handoff.
- No production/runtime or external action.

### Acceptance
- Every card criterion is explicit and independently auditable.
- Design/spec/successor wording uses the same exact table and outcomes.
- Strict OpenSpec/design-only scope gates pass before fresh review.

### Depends On
- Exhausted R3 and R4 retained verdict/history/stash evidence.

### Related
- `openspec/changes/replace-exhausted-qa-mcp-operation-boundary-investigation/`

## Log
- 2026-08-25 created by ChangeRail escalation after R4 review cycle 3 returned
  one matrix-exactness blocker at rescue budget `2/2`.
- 2026-08-25 exact failed R4 payload was preserved as
  `oss04d-r4-exhausted-review-payload-20260825`; isolated recovery reproduced
  the reviewed tree/fingerprint while `main` returned clean.
- 2026-08-25 fast-forward produced one design-only apply-ready replacement
  with the full accepted architecture, seven stable rows and an explicit
  credential/userinfo/control table at exact depths 1–5 through both public
  paths.
- 2026-08-25 completed `14/14` tasks, verified both exact stashes, recreated
  A2/R5/A3/R6, synced the design capability, passed strict/scope/hash/diff
  gates and archived the change. Card remains `3.inprogress` for fresh review.
- 2026-08-25 review cycle 1 returned `NO-GO` because R6 made fragment absence
  explicit only at depth 5; matrix count wording was also ambiguous. Rescue 1
  made every hostile depth 1–5/path assert no original or decoded fragment and
  fixed the exact public matrix count at 40 cells.
- 2026-08-25 review cycle 2 returned `GO` with `6/6` acceptance and zero
  findings; OSS-04D-A2 is the next sequential card.
- 2026-08-25T19:58:26Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

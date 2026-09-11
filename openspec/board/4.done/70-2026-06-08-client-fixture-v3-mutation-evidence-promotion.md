# 03B. Client Fixture Processor V3: Mutation Evidence And Promotion

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
75

## Source
- 2026-06-08 split from `03. Client Fixture Processor V3: Mutation Sandbox`
- `openspec/board/4.done/03-2026-06-04-client-fixture-v3-mutation-sandbox-surface.md`
- `docs/protocol-research/client-fixture-processor-roadmap.md`
- Closed V2 safe-action tooling, runner and focused proof cards

## Summary
Use the V3 mutation sandbox surface to define recovery proof, fail-closed
mutation rows and compact evidence publication. This card covers capture
review, frame isolation and candidate/accepted promotion decisions, using the
archived fixture-local surface as the prerequisite.

## Expected Scope
- Define the before, action, post and recovery evidence sequence for V3
  mutation cases.
- Select the initial reviewed row set from the closed V3 surface: text, number,
  date, checkbox toggle and inert button marker flows.
- Require deterministic reset or recovery proof for each mutation row.
- Keep candidate action frame ranges separate from bootstrap, background and
  cleanup traffic.
- Define the mutation-manifest shape for `target_marker`,
  `mutation_family`, `pre_state`, `action`, `post_state`,
  `recovery_expectation`, `mutates_business_data=false` and
  `expected_action_result_markers`.
- Publish compact reviewed evidence links and summaries without raw captures in
  git.
- Classify mutation rows as candidate, accepted, rejected, blocked, partial or
  timeout according to available proof.
- Promote mutation protocol mappings only when replay, direct probe or typed
  contract evidence supports the row.

## Change Set
- `openspec/changes/archive/2026-06-09-mutation-reset-recovery-verification/`
- `openspec/changes/archive/2026-06-09-mutation-corpus-manifest-updates/`

## Out Of Scope
- Implementing fixture-local state fields or form handlers; those belong to the
  sandbox surface card.
- Creating, editing or posting documents.
- Writing catalogs, registers, settings storage or external files.
- Network, COM, HTTP, mail, crypto or filesystem side effects.
- Reusing the V2 safe-action allowlist as a shortcut for mutation scenarios.
- Treating a mutation row as accepted from marker or capture evidence alone.

## Acceptance
- Every reviewed mutation row has deterministic pre-state, post-state and reset
  evidence.
- Re-running the same mutation case after reset produces the same observable
  markers.
- Failure during a mutation scenario leaves a documented recovery path.
- The action frame range is isolated from bootstrap, refresh and recovery
  traffic before any row is promoted.
- Manifest validation fails closed when required fields are missing or unsafe.
- Rows remain candidate unless replay/probe or typed contract proof supports
  accepted status.
- No V3 scenario depends on current demo business data.

## Delivery Gate
- Run this card only after the fixture-local surface delivery remains archived
  at
  `openspec/board/4.done/03-2026-06-04-client-fixture-v3-mutation-sandbox-surface.md`.
- Treat the V2 safe-action tooling, runner and focused proof prerequisites as
  already satisfied by the related `4.done` cards; they are not remaining
  delivery blockers for this card.
- Do not promote accepted mutation protocol mappings unless same-action replay,
  direct Python-manager probe or typed contract proof is available. If that
  proof is missing, publish candidate evidence only.

## Verify
- `bin\openspec.cmd validate mutation-reset-recovery-verification --strict` passed before archive
- `bin\openspec.cmd validate mutation-corpus-manifest-updates --strict` passed before archive
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict` passed after spec sync
- `bin\openspec.cmd validate --all` passed after both archives
- `git diff --check` passed with CRLF warnings only

## Archive
- `openspec/changes/archive/2026-06-09-mutation-reset-recovery-verification/`
- `openspec/changes/archive/2026-06-09-mutation-corpus-manifest-updates/`

## Related
- `openspec/board/4.done/03-2026-06-04-client-fixture-v3-mutation-sandbox-surface.md`
- `openspec/board/4.done/01-2026-06-04-client-fixture-v1-control-surface.md`
- `openspec/board/4.done/02-2026-06-04-client-fixture-v2-safe-actions.md`
- `openspec/board/4.done/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`
- `openspec/board/4.done/10-2026-06-07-v2-readiness-docs-and-safety-contract.md`
- `openspec/board/4.done/40-2026-06-07-v2-safe-action-tooling-pipeline.md`
- `openspec/board/4.done/50-2026-06-07-v2-first-focused-safe-action-proof.md`
- `openspec/changes/archive/2026-06-09-mutation-reset-recovery-verification/`
- `openspec/changes/archive/2026-06-09-mutation-corpus-manifest-updates/`
- `docs/protocol-research/safe-ui-action-scope.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/evidence/client-fixture-v3-mutation/20260609-recovery-proof/`
- `docs/protocol-research/evidence/client-fixture-v3-mutation/20260609-manifest-contract/`
- `docs/protocol-research/evidence/accepted-mappings/client-fixture-v3-mutation-20260609/`

## Result
published; V3 mutation recovery proof and fail-closed manifest publication are
documented as candidate-only evidence, main specs are synced, accepted mapping
output remains empty until replay/probe or typed contract proof exists, and
the scoped publish commit is ready

## Next
- none

## Change Plan Notes
Change order:
1. `mutation-reset-recovery-verification`
2. `mutation-corpus-manifest-updates`

## Change 1: `mutation-reset-recovery-verification`

### Why
Mutation rows are not trustworthy unless reset and recovery behavior is
reviewed separately from the handler implementation.

### Goal
Define and retain before/action/post/reset evidence for each V3 mutation case,
with action frames separated from background and cleanup traffic.

### Scope
- Define the evidence sequence.
- Retain reset and rerun proof for every selected row.
- Record candidate action frame ranges separately from bootstrap, refresh and
  recovery traffic.
- Keep rows candidate when proof is incomplete.

### Acceptance
- Every selected row has a documented recovery expectation.
- Candidate frame ranges are reviewable and separate from cleanup traffic.

### Depends On
- V3 mutation sandbox surface delivery.

### Related
- `openspec/changes/archive/2026-06-09-mutation-reset-recovery-verification/`

## Change 2: `mutation-corpus-manifest-updates`

### Why
Mutation evidence needs a fail-closed manifest and compact publication contract
before rows can be captured, reviewed or promoted.

### Goal
Define the V3 mutation row shape, evidence-link fields and promotion boundary.

### Scope
- Define required mutation manifest fields.
- Document rejected/incomplete row behavior.
- Update compact evidence publication expectations.
- Preserve candidate status until replay/probe or typed contract proof exists.

### Acceptance
- Incomplete or unsafe rows fail closed.
- Compact reviewed evidence links are sufficient for candidate publication.
- Accepted promotion remains proof-gated.

### Depends On
- `mutation-reset-recovery-verification`

### Related
- `openspec/changes/archive/2026-06-09-mutation-corpus-manifest-updates/`

## Log
- 2026-06-08T00:00:00Z card split from the broader V3 mutation sandbox card
- 2026-06-09T00:00:00Z prerequisite surface card archived in `4.done`
- 2026-06-09T00:00:00Z refreshed gate wording after the V2 proof and V3
  surface prerequisites were closed; remaining promotion proof is
  mutation-specific
- 2026-06-09T04:22:34Z moved to `2.todo` with apply-ready OpenSpec artifacts
- 2026-06-09T04:50:38Z archived both planned changes, synced
  `qa-mcp-protocol-lab`, and moved card to `4.done`
- 2026-06-09T05:02:46Z finalized publish card state for scoped commit

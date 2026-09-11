## Context

Cards 60 and 70 show the repository's preferred publication pattern: compact
evidence, explicit non-accepted states and empty accepted outputs when proof is
missing. Card 61 needs the same shape for real-demo mutations, with extra care
for cleanup or documented residue.

## Goals / Non-Goals

**Goals:**

- Publish selected, executed, rejected and blocked real-demo mutation outcomes.
- Link compact target, manifest, runtime, recovery and frame-isolation evidence.
- Keep accepted output proof-gated and empty when proof is missing.
- Record residual demo data, owner and risk when cleanup is incomplete or not
  applicable.

**Non-Goals:**

- Executing new runtime actions during publication.
- Committing raw captures, full UI dumps, platform logs or generated replay
  payloads.
- Retroactively treating candidate runtime evidence as accepted protocol
  knowledge.
- Claiming the demo mutation layer is safe for customer or production bases.

## Decisions

- Publish every selected or attempted row, including rejected and blocked rows,
  so gaps remain reviewable.
- Use the same status names as the manifest contract to avoid translation
  drift.
- Keep accepted-mapping output empty by default and add rows only when the
  accepted proof route is retained.
- Make residual demo data visible with owner and residual risk instead of
  hiding cleanup limitations.

## Risks / Trade-offs

- [Risk] Candidate evidence may be read as accepted. Mitigation: status and
  proof route are mandatory in the publication summary and accepted output is
  separate.
- [Risk] Publication may expose too much local runtime detail. Mitigation: link
  compact sanitized evidence and keep raw output ignored.
- [Risk] A blocked pilot may feel incomplete. Mitigation: blocked with precise
  no-execution reason is an acceptable outcome for this pilot.

## Migration Plan

- Gather compact evidence from target selection, manifest contract, guarded
  execution and frame isolation.
- Write the publication summary and evidence-index updates.
- Update accepted-output or candidate-output summaries according to proof.
- Hand the completed card to `$opsx-pub` after `$opsx-do` verifies evidence.

## Open Questions

- Should the first publication use a dedicated
  `docs/protocol-research/evidence/demo-real-mutation-corpus/<run-id>/`
  directory or extend the existing mutation evidence tree?
- Which row, if any, will have accepted proof during the pilot rather than
  candidate-only or blocked status?

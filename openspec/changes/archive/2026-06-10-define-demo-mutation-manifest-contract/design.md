## Context

V2 safe-action rows fail closed when `mutates_business_data` is true. This card
does not weaken that rule; it creates a separate real-demo mutation layer for a
disposable demo configuration, where mutation is allowed only when explicit,
reviewed and recoverable.

## Goals / Non-Goals

**Goals:**

- Define the row fields required before any real-demo mutation can be executed.
- Make `mutates_business_data=true` an explicit reviewed field rather than an
  accidental side effect.
- Preserve row status and accepted-proof gates for publication.
- Keep the contract compatible with compact evidence and ignored runtime paths.

**Non-Goals:**

- Implementing a runner or executing a live row.
- Approving unbounded save, post, delete, fill, import, export or external
  side-effect operations.
- Replacing V2 safe-action acceptance gates.
- Treating manifest completeness as accepted protocol proof.

## Decisions

- Require a row to declare both the intended mutation and the recovery
  expectation. A row with only one of those fields is not executable.
- Keep the status taxonomy aligned with existing corpus publication language:
  `accepted`, `candidate`, `rejected`, `blocked`, `partial` and `timeout`.
- Require `target_id` and target marker to be stable across pre-state and
  recovery checks so frame evidence can be joined back to the manifest row.
- Fail closed for external side effects and for save/post/delete/fill/import/
  export actions unless the row has pre-approved cleanup or recovery details.

## Risks / Trade-offs

- [Risk] A permissive mutation contract could be mistaken for production
  safety. Mitigation: the manifest names demo10413 as disposable lab scope and
  records residual risk for every row.
- [Risk] Recovery may be described too vaguely to verify. Mitigation: require
  expected post-state and recovery markers or classify the row as blocked.
- [Risk] Accepted output can drift from proof. Mitigation: accepted status
  requires same-action replay, direct Python-manager probe or accepted typed
  contract proof, not visual success alone.

## Migration Plan

- Draft the manifest field contract and compact evidence expectations.
- Update the downstream guarded pilot to load only complete reviewed rows.
- Roll back by marking all real-demo mutation rows `blocked` until the contract
  is reviewable.

## Open Questions

- Should the first pilot manifest live only under `.artifacts/openspec/` until
  execution, or should a compact reviewed sample be promoted to
  `docs/protocol-research/evidence/` during `$opsx-do`?
- Which proof route can first support accepted status for a real-demo mutation:
  replay, direct Python-manager probe or typed contract proof?

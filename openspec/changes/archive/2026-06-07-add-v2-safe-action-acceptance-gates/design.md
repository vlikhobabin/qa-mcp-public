## Context

The evidence contract already states that safe-action rows are not accepted
until action-frame evidence, result markers and replay/probe or typed contract
proof align. This change makes that policy explicit in comparison and
accepted-mapping tooling.

## Goals / Non-Goals

**Goals:**

- Gate accepted V2 action mappings on stable hashes and action proof.
- Keep non-accepted safe-action rows visible with explicit status and reason.
- Preserve compact proof links for replay, probe or typed contract evidence.
- Keep accepted-mapping output free of unresolved candidate rows.

**Non-Goals:**

- Add capture scenario wiring.
- Add reporter output fields.
- Implement V3 mutation acceptance or rollback behavior.
- Promote real demo business-button actions.

## Decisions

- Treat joined action-frame evidence as necessary but not sufficient for
  acceptance. It must be paired with action result markers and accepted
  replay/probe or typed contract evidence.
- Keep non-accepted rows in comparison output rather than dropping them. This
  preserves follow-up work and avoids hidden coverage gaps.
- Keep raw replay and probe payloads out of reviewed git; accepted rows link
  compact summaries only.

## Risks / Trade-offs

- [Risk] Acceptance criteria may be stricter than early exploratory evidence.
  [Mitigation] Preserve candidate and partial rows with reason fields so they
  remain useful without being promoted.
- [Risk] Typed side-channel evidence may be mistaken for direct wire proof.
  [Mitigation] Require the row to name the contract kind and evidence source.
- [Risk] Existing read-only comparison output could regress.
  [Mitigation] Run focused comparison checks for read-only and safe-action
  rows.

## Context

The V1 manager fixture reporter accepts read-only rows only when replay or
probe evidence matches the joined case. V2 safe-action reporting needs to keep
that acceptance discipline while adding action-specific frame ranges and
result markers.

## Goals / Non-Goals

**Goals:**

- Add a V2 reporter for safe-action frame joins and compact evidence.
- Keep action, background and recovery ranges separate.
- Emit reviewed JSON and Markdown summaries suitable for the evidence index.
- Preserve non-accepted action rows with explicit status and reason.

**Non-Goals:**

- Implement capture scenario wiring.
- Define the manifest contract.
- Accept protocol mappings without replay/probe or typed contract evidence.
- Replace or regress V1 read-only reporting.

## Decisions

- Keep V2 reporting separate from the V1 reporter so V1 read-only acceptance
  remains stable.
- Publish compact evidence rows and summaries under
  `docs/protocol-research/evidence/` while keeping raw payloads in ignored
  runtime paths.
- Treat action-frame joins as candidate evidence until acceptance gates attach
  replay, probe or typed contract proof.

## Risks / Trade-offs

- [Risk] Joined action frames may include unrelated refresh traffic.
  [Mitigation] Require separated `background_frame_ranges` and
  `recovery_frame_range` in reporter output.
- [Risk] Report output may look accepted before proof exists.
  [Mitigation] Emit explicit status and reason values for every non-accepted
  row.
- [Risk] V2 reporter changes may accidentally affect V1 evidence.
  [Mitigation] Keep V1 reporter entrypoints and fixtures stable, and verify
  existing V1 reporting still validates.

## Context

The V2 tooling pipeline can publish safe-action rows with action, background
and recovery ranges. The first focused proof needs a strict review pass over a
small live capture so that action frames are isolated without promoting the row
to accepted status by correlation alone.

## Goals / Non-Goals

**Goals:**

- Join focused phase events to candidate action frame ranges.
- Keep bootstrap, background refresh and recovery traffic separate.
- Preserve request/response sizes, dynamic fields, normalized hash candidates
  and action result markers.
- Mark ambiguous or incomplete joins with explicit non-accepted status.

**Non-Goals:**

- Running new live actions.
- Replaying or probing requests.
- Publishing accepted mappings.
- Modifying V1 read-only reporting semantics.

## Decisions

- Use the existing V2 reporter output shape so downstream comparison and
  accepted-mapping gates stay consistent with archived tooling changes.
- Treat missing action frame ranges as a blocker for acceptance, but still
  retain the row if the failure explains a provider or runtime gap.
- Keep normalized hash candidates and dynamic fields in compact summaries; raw
  packet payloads remain under ignored runtime paths.
- Do not merge recovery traffic into action frames. Recovery is useful proof
  context, not the action protocol shape.

## Risks / Trade-offs

- [Risk] Side-channel event timestamps can be too coarse to isolate frames.
  [Mitigation] Keep row status candidate/partial/timeout and record the
  ambiguous frame window separately.
- [Risk] Background refresh can look like action traffic. [Mitigation] Require
  explicit background ranges or non-accepted reason.
- [Risk] Reporter fixes can regress previous V1/V2 outputs. [Mitigation] Run
  focused reporter checks and preserve V1 read-only compatibility.

## Migration Plan

- Consume the live capture run id and phase event summaries.
- Generate the focused safe-action report and comparison row.
- Pass candidate rows and non-accepted reasons to
  `probe-focused-v2-safe-action-contract`.

## Open Questions

- Which normalized hash should be treated as the stable candidate when request
  and response fields both contain dynamic values?
- Should ambiguous background ranges be retained in docs or only in
  `.artifacts` when no accepted proof is possible?

## Context

Earlier V2 changes produced tooling and candidate dry-run output, but no accepted
safe-action mapping. The first focused proof card closes the first live proof
loop by publishing a compact accepted-or-candidate decision that other cards can
cite without reading raw runtime output.

## Goals / Non-Goals

**Goals:**

- Publish a compact first focused proof report.
- Update docs and evidence indexes with the selected rows, frame ranges, proof
  route, final status and residual risk.
- Update accepted-mapping output only when replay/probe or typed contract proof
  satisfies the V2 gates.
- Keep candidate rows visible and clearly non-accepted.

**Non-Goals:**

- Running additional live actions.
- Reopening the V2 manifest, runner or tooling design.
- Starting demo real-button pilots.
- Publishing raw captures, platform logs or generated replay payloads.

## Decisions

- Use the existing manager fixture V2 safe-action evidence directory family for
  the proof report so readers can compare it with the candidate dry-run output.
- Include both human-readable and machine-readable compact outputs where the
  existing evidence pattern supports them.
- Update accepted-mapping output only if the proof gate change produced accepted
  status. Otherwise publish candidate status and leave accepted output empty or
  unchanged with an explicit reason.
- Record downstream readiness language carefully: a first accepted fixture row
  can unblock later pilots only for the proven action family, while candidate
  status keeps later pilots gated.

## Risks / Trade-offs

- [Risk] Docs can overstate a candidate row. [Mitigation] Put status and
  non-accepted reason next to every evidence link.
- [Risk] Accepted mapping output can drift from the proof report. [Mitigation]
  cross-check accepted/candidate counts and normalized hashes before archive.
- [Risk] Runtime paths can leak sensitive local context. [Mitigation] publish
  sanitized summaries and keep raw outputs ignored.

## Migration Plan

- Consume final row decisions from `probe-focused-v2-safe-action-contract`.
- Publish compact docs/evidence updates and accepted/candidate outputs.
- Update this card's result and handoff language during `$opsx-do`/archive.

## Open Questions

- If the first row remains candidate, should downstream V3/V4 gates require a
  later accepted V2 row or only reviewed candidate evidence?
- Should the evidence index use a dated proof id or a stable
  `first-focused-proof` alias in addition to dated paths?

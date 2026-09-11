## Context

The V2 safety contract already names the manifest fields needed for safe
action rows. This change turns that policy into a tooling-facing manifest
shape that the capture scenario, reporter and acceptance gates can all share.

## Goals / Non-Goals

**Goals:**

- Define required safe-action manifest fields for tooling.
- Keep row validation fail-closed before capture or reporting.
- Map manifest rows to fixture target maps and corpus row fields.
- Preserve explicit unsupported, blocked and pending statuses.

**Non-Goals:**

- Add capture scenario wiring.
- Implement reporter output.
- Accept action protocol mappings.
- Expand the V2 allowlist or include V3 mutation families.

## Decisions

- Use the existing V2 safety fields as the required manifest baseline rather
  than inventing a second row shape. This keeps docs, runner and reporter
  semantics aligned.
- Keep `mutates_business_data=false` mandatory and literal. Any missing or
  non-false value rejects the row before capture.
- Preserve incomplete target rows as explicit `blocked`, `unsupported` or
  `pending` records when useful for coverage review, but do not execute them.

## Risks / Trade-offs

- [Risk] Schema and documentation may drift.
  [Mitigation] Update the docs and tooling contract in the same change and
  validate with representative accepted and rejected rows.
- [Risk] Fail-closed validation may block useful exploratory captures.
  [Mitigation] Keep coverage rows as non-executable statuses with provider
  owner and residual risk fields.
- [Risk] Manifest rows may imply acceptance before evidence exists.
  [Mitigation] State that a valid manifest row is only permission to capture or
  report, not accepted protocol knowledge.

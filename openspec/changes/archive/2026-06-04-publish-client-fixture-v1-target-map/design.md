## Context

The fixture processor and V1 controls produce a stable UI surface, but protocol
research needs a machine-reviewable bridge from fixture elements to corpus
cases. Previous fixture evidence recorded gaps because the runner could not
reliably target the intended form/families. This change closes the planning
gap by publishing target paths and marker coverage.

## Goals / Non-Goals

Goals:

- Produce a compact target map for V1 `PF_*` elements.
- Link targets to element families, expected states and read-only case ids.
- Preserve provider and runtime gaps explicitly.
- Prepare corpus manifest inputs for later Windows-native capture runs.

Non-goals:

- Do not generate accepted protocol mappings.
- Do not embed raw TCP payloads, screenshots or platform logs in reviewed
  evidence.
- Do not implement the manager harness.
- Do not execute action or mutation cases.

## Decisions

- Keep the target map under reviewed protocol evidence, for example
  `docs/protocol-research/evidence/fixture-target-maps/<run-id>/target_map.json`.
  This keeps source-of-truth evidence near corpus artifacts without committing
  raw runtime output.
- Include both human-readable summary and machine-readable JSON. The JSON feeds
  future runner/manifest work; the Markdown summary supports review.
- Record `availability` per target. A target can be `supported`, `pending`,
  `partial` or `blocked` without blocking unrelated families.
- Treat EDT/meta/Vanessa labels as semantic support. Native protocol evidence
  still requires capture and replay/probe proof under the corpus evidence
  contract.

## Target Map Shape

Each row should include at least:

- `marker`
- `element_family`
- `target_path`
- `form`
- `expected_state`
- `expected_response_markers`
- `case_ids`
- `availability`
- `semantic_sources`
- `evidence_path`
- `notes`

## Capture And Replay Strategy

This change prepares capture inputs and does not claim frame ranges. Later
capture changes will use the map to mark cases, extract frame ranges and
classify normalized hashes. If direct Python-manager probes are run during
verification, they remain readiness evidence unless they are linked to reviewed
corpus rows.

## Risks / Trade-offs

- Target paths may shift if EDT generated form IDs change. Mitigation: base
  rows on stable markers and names, not numeric element IDs alone.
- Some provider evidence may be unavailable. Mitigation: record provider gaps
  and keep target availability non-accepted.
- The map could drift from the actual form. Mitigation: require read-only form
  analysis evidence in the same delivery.

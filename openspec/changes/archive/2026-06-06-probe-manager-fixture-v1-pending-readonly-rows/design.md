## Context

The cleanup replay summaries already proved eight rows. Additional pending
rows need evidence that is tied to the cleanup run, not only older
repeatability or marker probes. Some rows may replay transport-level
successfully while still missing the declared semantic marker.

## Goals / Non-Goals

**Goals:**

- Attempt focused read-only replay/direct probes for rows selected by the
  classification output.
- Record dynamic adaptations, response markers, normalized hashes, negative
  controls and validation mismatches.
- Produce retained summaries that the reporter can fold into the cleanup
  live-join report.

**Non-Goals:**

- No global relaxation of random-block adaptation rules.
- No acceptance from older evidence unless reconciled with the current cleanup
  run.
- No safe action, mutation, text input, click or page-switch semantics.

## Decisions

1. Probe by row family instead of using one broad replay as proof for all
   rows.
   Different endpoint families have different dynamic-field behavior and
   marker expectations.

2. Require current-run identity for accepted summaries.
   The summary must name the current run id, case id, frame range and
   normalized hash that the reporter will validate.

3. Retain negative controls.
   Transport success without the expected marker is protocol evidence, but it
   must remain non-accepted with the mismatch preserved.

## Risks / Trade-offs

- Some rows may need new dynamic adaptation rules. Mitigation: add only
  range-scoped adaptations with negative controls.
- Live TestClient startup may be provider-gapped. Mitigation: record the
  provider gap and keep rows pending instead of accepting them.

## Verification Matrix

Detailed rows are in `tasks.md`.

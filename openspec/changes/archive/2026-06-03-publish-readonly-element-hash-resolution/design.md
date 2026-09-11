## Context

The current package descriptor boundary intentionally exposes only
`active-window-context` and `active-form-context` as accepted mappings.
`form-element-details` and `typed-input-field-readonly` are available as useful
direct Python-manager paths but remain unresolved. This publication change is
the gate that either promotes those rows from reviewed evidence or preserves a
clear unresolved status.

## Goals / Non-Goals

**Goals:**

- Consume the classification output from
  `refine-readonly-element-gap-classification`.
- Publish accepted mapping evidence when both stable reviewed hashes and
  accepted replay/probe proof are present.
- Preserve descriptor status as non-accepted when the evidence remains
  incomplete, with reasons specific enough for future work.
- Update docs, evidence index and focused tests to match the final status.

**Non-Goals:**

- Do not re-run capture/classification in this change except for a final smoke
  or verification command.
- Do not promote rows from direct-probe output alone.
- Do not introduce action/write operations or broaden protocol coverage beyond
  these two read-only rows.
- Do not archive or sync unrelated OpenSpec changes.

## Decisions

### Publication Is Outcome-Gated

There are two valid publication paths:

- Accepted path: write accepted-mapping evidence and update descriptors with
  accepted status, normalized hash, source capture ids and evidence paths.
- Unresolved path: write a resolution report, keep descriptors
  `incomplete_hash` or another non-accepted status, and expose the precise
  unresolved reason in docs/tests.

The delivery should not mix these paths. If one row is accepted and the other
remains unresolved, publish both outcomes explicitly in one report.

### Descriptors Follow Reviewed Evidence Only

`src/qa_mcp/protocol/` descriptors can change only when reviewed evidence
satisfies the accepted mapping contract. If the final status remains
unresolved, tests should assert that descriptors still expose non-accepted
status for the two rows.

### Docs Name The Next Delivery Boundary

The evidence index and protocol package docs should state whether safe-action
capture remains blocked by read-only element hash gaps. This card still does
not implement safe-action behavior.

## Risks / Trade-offs

- A partial promotion could confuse downstream users; mitigate by publishing a
  per-row table with accepted/unresolved status and evidence paths.
- Descriptor updates can drift from evidence docs; mitigate with focused tests
  that compare descriptor status to expected publication status.
- A final live smoke may be unavailable; mitigate by allowing the already
  retained compact evidence to be the delivery proof and recording runtime
  unavailability as residual risk.

## Migration Plan

No runtime migration is required. If descriptors become accepted, downstream
code can consume the new evidence status through existing package APIs. If
descriptors remain unresolved, future work continues from the published
resolution report and precise reason taxonomy.

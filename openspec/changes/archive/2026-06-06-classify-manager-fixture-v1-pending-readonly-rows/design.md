## Context

The status report for 2026-06-06 identifies eight accepted rows and nine
pending rows in the manager fixture V1 cleanup run. Joined frame evidence
alone is intentionally insufficient: accepted proof must match the current
`case_id`, manager frame range and `normalized_hash`.

## Goals / Non-Goals

**Goals:**

- Produce one classification record for every pending row.
- Distinguish wrong expected marker, wrong endpoint, missing replay/probe
  evidence, ambiguous frame range and retained pending status.
- Identify candidate manifest corrections without applying them prematurely.

**Non-Goals:**

- No accepted mapping promotion.
- No replay/probe implementation.
- No V2 safe action, input, click, page-switch or mutation semantics.

## Decisions

1. Use the 20260606 cleanup run as the current source of truth.
   Older accepted mappings can be supporting context, but they do not promote
   a row unless reconciled with the current run.

2. Keep classifications machine-readable.
   The follow-up probe and publish changes need stable values rather than
   prose-only notes.

3. Treat marker mismatches as candidates, not fixes.
   A row with an observed marker but missing expected marker needs an explicit
   decision about whether the expected marker was wrong or the endpoint is
   wrong.

## Risks / Trade-offs

- A row may have multiple plausible blockers. Mitigation: store a primary
  classification plus supporting observations.
- Classification may reveal missing report fields. Mitigation: update tooling
  narrowly and verify against retained cleanup artifacts.

## Verification Matrix

Detailed rows are in `tasks.md`.

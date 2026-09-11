## Context

The expanded read-only matrix produced two comparable corpus runs:
`20260602-193802` and `20260602-195407`. Active-window and active-form rows
normalize to stable request hashes after dynamic replacement, but comparison
classification remains `non_accepted` because the rows still carry only
`pending` replay status. Separately, direct Python-manager probing confirmed
the supported `EditField`/typed input family without a 1C TestManager
instance, but the Vanessa-only corpus rows for element details still have
incomplete request hashes.

## Goals / Non-Goals

**Goals:**

- Let corpus generation or comparison attach compact direct-probe evidence to
  relevant read-only rows.
- Promote stable repeated active-window and active-form mappings only when the
  attached probe/replay status is accepted.
- Preserve explicit unresolved classifications for element-detail and
  typed-input rows when request-frame evidence is incomplete.
- Generate reviewed comparison/evidence output that names accepted mappings
  separately from unsupported fixture gaps.
- Add offline tests for status promotion and gap preservation.

**Non-Goals:**

- Do not implement safe UI actions, clicks, text input or business-data writes.
- Do not promote mappings solely from metadata/help labels.
- Do not require EDT/meta services for byte-level acceptance.
- Do not commit raw capture streams or full probe output.

## Decisions

### Probe Evidence Joins By Case Identity And Operation Shape

The implementation should avoid broad "any probe succeeded" promotion. Probe
evidence should match a corpus row by case id, query/family, expected response
markers or another explicit reviewed mapping. If the join is ambiguous, the
row remains non-accepted and records the ambiguity.

### Accepted Classification Is Conservative

Comparison can classify a row as stable accepted only when every comparison
input contains a non-null stable normalized hash and the row has accepted
probe/replay status. Unsupported fixture-gap rows and incomplete-hash rows
stay visible.

### Evidence Output Is Compact And Regenerable

Reviewed outputs should include accepted case ids, source capture ids,
probe-evidence paths, status counts and unresolved reasons. Raw outputs remain
under `runtime/protocol-research/` and should not be required for reviewing
the committed evidence.

## Risks / Trade-offs

- Direct probe evidence may not cover exactly the same frame slice as a
  Vanessa capture; mitigate with explicit join criteria and unresolved
  reasons.
- Promotion logic can accidentally accept stale evidence; mitigate by storing
  evidence paths and source capture/probe identifiers in generated reports.
- Live 1C regeneration can be slow or environment-sensitive; prefer existing
  compact evidence for tests and require live runs only for fresh evidence.

## Migration Plan

Existing reviewed corpus rows remain valid. The delivery may regenerate
comparison and normalizer evidence for the two expanded read-only captures,
and may add new compact accepted-mapping evidence. Old non-accepted reports
should remain historically accurate unless a new report id explicitly
supersedes them.

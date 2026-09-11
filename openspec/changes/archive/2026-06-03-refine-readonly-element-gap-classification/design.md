## Context

Previous comparison work intentionally kept element-detail and typed-input rows
as `incomplete_hash` when useful direct-probe output existed without reviewed
request hashes. This card now needs a sharper status boundary so future work
can tell whether it should collect frames, fix operation joins, adjust fixture
state or extend normalizer coverage.

## Goals / Non-Goals

**Goals:**

- Consume the audit and request-hash evidence produced by the preceding
  changes.
- Emit precise unresolved reasons for both target rows.
- Preserve accepted mapping rules that require stable non-null normalized
  hashes plus accepted replay or direct-probe evidence for the same operation.
- Add offline tests and compact classification evidence.

**Non-Goals:**

- Do not run fresh live capture in this change unless a focused verification
  command already depends on retained compact evidence.
- Do not update `qa_mcp.protocol` descriptors.
- Do not rewrite historical evidence directories in place.
- Do not treat metadata/help semantic labels as sufficient byte-level
  acceptance.

## Decisions

### Keep Classification Reasons Machine-Readable

Tool output should expose a stable reason field or list alongside the existing
classification. The expected reason values for this card are:

- `missing_request_frames`
- `ambiguous_operation_join`
- `unsupported_fixture_state`
- `incomplete_normalizer_coverage`
- `accepted_reviewed_hash`
- `runtime_unavailable`

Reports can keep human-readable notes, but tests should assert the stable
reason values.

### Accepted Still Requires Stable Wire Evidence

The classification may mark a row accepted only when every compared input has
a non-null stable normalized hash and the row has accepted replay or direct
Python-manager proof for the same operation markers. Probe-only success
without request hashes remains non-accepted.

### Provider Gaps Stay Explicit

If a missing reason depends on Vanessa/TestClient harness behavior rather than
project tooling, the classification evidence should name the provider owner and
impact. For this repo, runtime UI/capture gaps route to
`/opt/vanessa-mcp-stack`; protocol tool gaps stay with `project:qa-mcp`.

## Risks / Trade-offs

- Adding more reason values can fragment reports; mitigate by keeping a small
  controlled taxonomy and mapping unknown cases to a reviewed note.
- Classification can accidentally change historical evidence expectations;
  mitigate by generating a new comparison evidence id instead of editing old
  reports.
- A reason may depend on both missing frames and normalizer coverage; mitigate
  by recording a primary reason plus secondary notes.

## Migration Plan

Existing reports remain historical. New comparison or classification output
may include the reason taxonomy. The publication change consumes the new
classification and updates docs/descriptors only after the accepted-or-
unresolved outcome is clear.

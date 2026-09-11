## Context

The first corpus runner can write normalized rows for one capture. For a
protocol dictionary, one accepted row is not enough: the same case must be
captured repeatedly so the lab can confirm whether `normalized_hash` is stable
and whether any remaining byte differences represent unhandled dynamic fields.

## Goals / Non-Goals

**Goals:**

- Compare two or more corpus runs for the same case set.
- Group rows by `case_id` and compare normalized hashes, request/response
  sizes, operation tokens, response markers and dynamic field lists.
- Produce compact repeatability reports with capture ids and case ids.
- Flag suspected dynamic ranges for the normalizer follow-up.

**Non-Goals:**

- Do not change the corpus row contract unless a missing field is proven.
- Do not require live 1C runtime for offline comparison of already retained
  captures.
- Do not treat metadata/help labels as proof of protocol stability.

## Decisions

### Compare Reviewed Rows First

The comparison should start from `corpus_cases.jsonl` reviewed rows and only
fall back to raw runtime captures for suspected dynamic-range investigation.

Alternative considered: compare raw `traffic.jsonl` first. Raw byte comparison
is useful, but reviewed rows provide stable case ids and reduce the chance of
mixing unrelated background traffic into a repeatability report.

### Use Capture Ids As Evidence Boundaries

Every comparison report should name the capture ids, case ids and evidence
paths it compares. If a run is missing a case, the report should record a
matrix gap instead of silently comparing the remaining subset.

## Risks / Trade-offs

- Different background refresh timing can create missing or shifted frame
  ranges - mitigate by comparing side-channel case events and recording gaps.
- A stable hash may still hide over-broad normalization - mitigate by carrying
  dynamic-field replacement summaries into the comparison report.
- Repeated live captures are slower - mitigate by supporting offline
  comparison after captures have been generated.

## Migration Plan

No migration is required. Existing corpus evidence can be used as one input
set, and new repeated captures add additional evidence folders.

# Readonly Element Hash Gap Audit

- Generated at: `2026-06-03T10:18:00+03:00`
- Change: `audit-readonly-element-hash-evidence`
- Scope: `form-element-details` and `typed-input-field-readonly`
- Safety: read-only evidence review only; no live TestClient run was started

## Summary

Both target rows are still non-accepted in package descriptors because the
current repeated expanded comparison over captures `20260602-193802` and
`20260602-195407` has no reviewed request bytes or normalized hashes for the
rows. The direct Python-manager probe returned useful element data, and older
compact corpus rows include extractable reviewed request-frame evidence for the
same `101..106` element-detail schedule.

This audit does not promote either row. It records the source evidence and
routes the next change to extract or recapture request-hash evidence, then let
classification decide whether the row can be accepted.

## Current Descriptor Status

| Row | Descriptor status | Descriptor reason | Descriptor source |
| --- | --- | --- | --- |
| `form-element-details` | `incomplete_hash` | `accepted_probe_without_reviewed_request_hash` | `src/qa_mcp/protocol/evidence.py` |
| `typed-input-field-readonly` | `incomplete_hash` | `accepted_probe_without_reviewed_request_hash` | `src/qa_mcp/protocol/evidence.py` |

## Reviewed Evidence Sources

| Evidence | Path | Relevant facts |
| --- | --- | --- |
| Current repeated comparison | `docs/protocol-research/evidence/corpus-comparison/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/` | Both target rows are `incomplete_hash`; probe status is effectively accepted, but request bytes, response bytes and hashes are zero/null in the compared rows. |
| Direct Python-manager probe | `docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/python_manager_probe_result.json` | Probe status is `ok`; frame mode is `short`; frames `101..106` returned two `EditField` element detail groups without TestManager. |
| Expanded corpus with reviewed element rows | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/` | Both target rows have manager frames `101..106`, request size `1200`, response size `972`, normalized hash `b56da7520da52418f0941530becea763233f5affc658a7bb3da9c1c3162e630a`, replay `accepted` and one response marker. |
| Readonly smoke corpus `20260602-172319` | `docs/protocol-research/evidence/corpus/20260602-172319-readonly-smoke/` | `form-element-details` has manager frames `101..106`, request size `1200`, response size `972`, normalized hash prefix `606a57c6f2554e93` and replay `accepted`. |
| Readonly smoke corpus `20260602-084433` | `docs/protocol-research/evidence/corpus/20260602-084433-readonly-smoke/` | `form-element-details` has manager frames `101..106`, request size `2100`, response size `1910`, normalized hash prefix `6cd987cb4294867c` and replay `accepted`. |

## Contract Field Audit

| Row | Current comparison captures | Current request/hash state | Extractable compact row | Dynamic fields seen | Operation token | Response markers | Direct probe status | Audit outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `form-element-details` | `20260602-193802`, `20260602-195407` | frame range `101..106` is named, but request size `0`, response size `0`, normalized hash `null` | `20260602-172319-expanded-readonly` has request size `1200`, response size `972`, normalized hash `b56da7520da52418f0941530becea763233f5affc658a7bb3da9c1c3162e630a` | `ack_guid_uuid_le`, `sequence_uint16_le`, `nonce`, `ascii_guid` | preserved at offset `51` in the expanded reviewed row | managed form marker retained in compact row; probe frames return two `EditField` element groups | `ok`, short frame mode, frames `101..106` | `extractable_existing_capture` |
| `typed-input-field-readonly` | `20260602-193802`, `20260602-195407` | frame range `101..106` is named, but request size `0`, response size `0`, normalized hash `null` | `20260602-172319-expanded-readonly` has request size `1200`, response size `972`, normalized hash `b56da7520da52418f0941530becea763233f5affc658a7bb3da9c1c3162e630a` | `ack_guid_uuid_le`, `sequence_uint16_le`, `nonce`, `ascii_guid` | preserved at offset `51` in the expanded reviewed row | managed form marker retained in compact row; row semantically reuses the `EditField` element-detail operation | `ok`, through `form-element-details` query | `extractable_existing_capture` with operation-join review required |

## Findings

- The current repeated comparison correctly keeps both target rows out of
  accepted mappings because the compared inputs contain no request bytes and
  no normalized hashes for the rows.
- The direct probe confirms useful read-only element data, but probe success
  alone is not accepted wire evidence.
- `20260602-172319-expanded-readonly` is the best compact extraction source:
  it contains reviewed request fields for both target rows in the expanded
  matrix shape.
- `typed-input-field-readonly` needs an explicit join check because it reuses
  the same `EditField` element-detail request/hash shape as
  `form-element-details`.
- No evidence in this audit justifies changing `qa_mcp.protocol` descriptors
  yet.

## Next Action

Use `capture-readonly-element-request-hashes` to either:

- extract the reviewed row fields from `20260602-172319-expanded-readonly` and
  generate a current resolution evidence bundle; or
- run a fresh read-only probe/capture if the extraction cannot prove the
  current descriptor rows.

If extraction or capture cannot prove the rows, preserve the precise blocker:
`missing_request_frames`, `ambiguous_operation_join`,
`unsupported_fixture_state`, `incomplete_normalizer_coverage` or
`runtime_unavailable`.

## Raw Evidence Boundary

Raw captures, PID files, platform logs and generated probe output remain under
ignored `runtime/protocol-research/`. This report references compact reviewed
artifacts only and does not copy raw TCP payloads.

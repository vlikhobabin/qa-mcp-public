# Readonly Element Hash Resolution Classification

- Generated at: `2026-06-03T10:43:00+03:00`
- Change: `refine-readonly-element-gap-classification`
- Comparison inputs:
  - `docs/protocol-research/evidence/corpus/20260602-193802-expanded-readonly/corpus_cases.jsonl`
  - `docs/protocol-research/evidence/corpus/20260602-195407-expanded-readonly/corpus_cases.jsonl`
- Direct probe evidence:
  `docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/python_manager_probe_result.json`
- Request-hash evidence:
  `docs/protocol-research/evidence/readonly-element-request-hashes/20260602-172319-expanded-extracted/request_hashes.json`

## Summary

The current repeated expanded comparison remains conservative:

- `active-window-context` and `active-form-context` are stable accepted rows.
- `form-element-details` and `typed-input-field-readonly` remain
  `incomplete_hash` because the current repeated inputs still have zero
  request/response bytes and no normalized hashes for the target rows.
- The extracted `20260602-172319` request-hash evidence is present and
  reviewable, but it does not by itself make the current repeated comparison
  stable.

## Target Rows

| Row | Classification | Precise reasons | Provider owners | Request-hash evidence | Decision |
| --- | --- | --- | --- | --- | --- |
| `form-element-details` | `incomplete_hash` | `accepted_reviewed_hash`, `missing_request_frames` | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | `docs/protocol-research/evidence/readonly-element-request-hashes/20260602-172319-expanded-extracted/request_hashes.json` | Keep non-accepted; publication should preserve `incomplete_hash` with sharper reasons. |
| `typed-input-field-readonly` | `incomplete_hash` | `accepted_reviewed_hash`, `ambiguous_operation_join`, `missing_request_frames` | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | `docs/protocol-research/evidence/readonly-element-request-hashes/20260602-172319-expanded-extracted/request_hashes.json` | Keep non-accepted; publication should name the shared element-detail request shape and operation-join caveat. |

## Provider Routing

- `missing_request_frames` is routed to `/opt/vanessa-mcp-stack` because the
  current repeated Vanessa/TestClient capture rows lack captured request
  payloads for the element rows.
- `accepted_reviewed_hash` is routed to `project:qa-mcp` because the extracted
  compact row is reviewed project evidence.
- `ambiguous_operation_join` is routed to `project:qa-mcp` because the
  protocol classification layer must decide whether the typed-input row can
  share the element-detail operation shape.

## Verification Notes

- No live runtime was used by this classification change.
- Existing accepted, stable, unsupported and pending classifications were
  preserved for unaffected rows.
- Raw captures and full probe output remain under ignored runtime paths.

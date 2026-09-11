# Readonly Element Hash Resolution

- Generated at: `2026-06-03T10:55:00+03:00`
- Change: `publish-readonly-element-hash-resolution`
- Outcome: unresolved; no package descriptor was promoted
- Safety: read-only evidence publication only

## Summary

`form-element-details` and `typed-input-field-readonly` remain
`incomplete_hash` protocol descriptors. The delivery found and published
reviewed request-hash evidence from `20260602-172319-expanded-readonly`, but
the current repeated expanded comparison over `20260602-193802` and
`20260602-195407` still has zero request/response bytes and no normalized hash
for both target rows.

The conservative outcome is to keep the descriptors non-accepted and publish
the sharper reasons for future work.

## Row Outcomes

| Row | Published status | Precise reasons | Descriptor action | Next blocker |
| --- | --- | --- | --- | --- |
| `form-element-details` | `incomplete_hash` | `accepted_reviewed_hash`, `missing_request_frames` | Preserved non-accepted descriptor status | Produce repeated current comparison inputs with non-zero request bytes and stable hash, or explicitly accept a different evidence policy for the extracted `20260602-172319` row. |
| `typed-input-field-readonly` | `incomplete_hash` | `accepted_reviewed_hash`, `ambiguous_operation_join`, `missing_request_frames` | Preserved non-accepted descriptor status | Resolve whether the typed-input row can share the element-detail operation shape, then produce repeated current comparison inputs with non-zero request bytes and stable hash. |

## Evidence Chain

- Audit:
  `docs/protocol-research/evidence/readonly-element-hash-audit/current-element-hash-gaps/audit_summary.md`
- Extracted request hashes:
  `docs/protocol-research/evidence/readonly-element-request-hashes/20260602-172319-expanded-extracted/request_hashes.json`
- Classification:
  `docs/protocol-research/evidence/corpus-comparison/readonly-element-hash-resolution-20260603-extracted/classification_summary.md`
- Package descriptors:
  `src/qa_mcp/protocol/evidence.py`

## Descriptor Decision

Descriptors remain unchanged because accepted evidence did not satisfy the
repeated stable mapping contract:

- accepted mappings remain limited to `active-window-context` and
  `active-form-context`;
- `form-element-details` remains `incomplete_hash`;
- `typed-input-field-readonly` remains `incomplete_hash`;
- no accepted mapping evidence directory is produced for these two rows.

## Safe-Action Boundary

This card does not unblock safe UI actions. Clicks, text input, command
execution and business-data mutation still require a separate safe-action
capture/recovery card after read-only descriptor evidence is accepted.

## Files

- `resolution_summary.md`
- `resolution.json`

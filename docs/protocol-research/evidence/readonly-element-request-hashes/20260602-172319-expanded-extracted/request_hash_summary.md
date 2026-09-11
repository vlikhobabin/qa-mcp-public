# Readonly Element Request Hash Extraction

- Generated at: `2026-06-03T10:29:00+03:00`
- Change: `capture-readonly-element-request-hashes`
- Source compact corpus:
  `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/`
- Extraction mode: existing reviewed compact evidence; no live 1C runtime was
  started
- Raw source boundary: raw capture remains under
  `runtime/protocol-research/captures/20260602-172319/`

## Summary

The audit identified `20260602-172319-expanded-readonly` as the best committed
compact extraction source for the two useful element rows. This evidence bundle
copies the review-critical request-hash facts from that source into a focused
resolution input for later classification.

The extracted rows share the same read-only `EditField` request shape:

- manager-to-client frames: `101..106`
- client-to-manager frames: `102..107`
- request size: `1200`
- response size: `972`
- normalized hash:
  `b56da7520da52418f0941530becea763233f5affc658a7bb3da9c1c3162e630a`
- replay status: `accepted`
- operation token: preserved semantic token at offset `51` on frames
  `101..106`

This bundle does not promote either descriptor. It provides reviewed request
evidence for the classification step, which still must decide whether the
shared element-detail request shape is sufficient for
`typed-input-field-readonly`.

## Extracted Rows

| Row | Capture | Frames | Request bytes | Response bytes | Normalized hash | Dynamic fields | Operation token | Response markers | Replay |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `form-element-details` | `20260602-172319` | manager `101..106`, client `102..107` | `1200` | `972` | `b56da7520da52418f0941530becea763233f5affc658a7bb3da9c1c3162e630a` | `ack_guid_uuid_le`, `sequence_uint16_le`, `nonce`, `ascii_guid` | preserved at offset `51`; constant `0a102bc90b462c40b5aeb6e2329a7234` in this row | managed form marker and expected `EditField` family | `accepted` |
| `typed-input-field-readonly` | `20260602-172319` | manager `101..106`, client `102..107` | `1200` | `972` | `b56da7520da52418f0941530becea763233f5affc658a7bb3da9c1c3162e630a` | `ack_guid_uuid_le`, `sequence_uint16_le`, `nonce`, `ascii_guid` | preserved at offset `51`; constant `0a102bc90b462c40b5aeb6e2329a7234` in this row | managed form marker and expected `EditField` family | `accepted` |

## Dynamic Field Groups

The source rows record replacements for every manager frame in the range:

| Field | Direction | Frames | Offset | Length | Role |
| --- | --- | --- | --- | --- | --- |
| `ack_guid_uuid_le` | manager-to-client | `101..106` | `2` | `16` | replaced dynamic ACK GUID |
| `sequence_uint16_le` | manager-to-client | `101..106` | `19` | `2` | replaced sequence counter |
| `nonce` | manager-to-client | `101..106` | `68` | `16` | replaced nonce |
| `ascii_guid` | manager-to-client | `101..106` | `95`, `145` | `36` | replaced managed-form related GUIDs |
| `operation_token` | manager-to-client | `101..106` | `51` | `16` | preserved semantic token in normalized hash |

## Classification Input

Recommended classification inputs:

- Treat `form-element-details` as having reviewed request-hash evidence from
  `20260602-172319-expanded-readonly`.
- Treat `typed-input-field-readonly` as having reviewed request-hash evidence
  from the same source, with an explicit operation-join review because it
  shares the element-detail request/hash shape.
- Do not use the `20260602-193802` versus `20260602-195407` comparison alone
  for promotion; those two current comparison inputs still have zero
  request/response bytes and no normalized hashes for the target rows.

## Files

- `request_hash_summary.md`
- `request_hashes.json`

## Safety

No TestClient or TestManager process was started by this extraction. No raw TCP
payload, PID file, platform log, local credentials or infobase data is copied
into this reviewed evidence bundle.

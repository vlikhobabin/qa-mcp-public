# Protocol Normalizer Evidence

- Generated at: `2026-06-02T17:19:14Z`
- Accepted replacements: `["ack_guid_uuid_le", "ascii_guid", "nonce", "sequence_uint16_le"]`
- Preserved fields: `["operation_token"]`
- Ambiguous fields: `[]`
- Normalizer investigation cases: `[]`

## Cases

| case | classification | before hash count | after hash count | before prefixes | after prefixes | accepted replacements | preserved fields | ambiguous fields |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| active-form-context | non_accepted | 2 | 1 | ["a80b3b8e82bb10b7", "c63209d269d87024"] | ["e43ce48cedae7b6d"] | ["ack_guid_uuid_le", "ascii_guid", "nonce", "sequence_uint16_le"] | ["operation_token"] | [] |
| active-window-context | non_accepted | 2 | 1 | ["5193c81c798e0de0", "af7098e700c1c522"] | ["62e03d159d511173"] | ["ack_guid_uuid_le", "nonce", "sequence_uint16_le"] | ["operation_token"] | [] |
| button-family-readonly-gap | unsupported_gap | 0 | 0 | [] | [] | [] | [] | [] |
| checkbox-family-readonly-gap | unsupported_gap | 0 | 0 | [] | [] | [] | [] | [] |
| commandbar-family-readonly-gap | unsupported_gap | 0 | 0 | [] | [] | [] | [] | [] |
| form-element-details | incomplete_hash | 0 | 0 | [] | [] | [] | [] | [] |
| label-family-readonly-gap | unsupported_gap | 0 | 0 | [] | [] | [] | [] | [] |
| page-family-readonly-gap | unsupported_gap | 0 | 0 | [] | [] | [] | [] | [] |
| table-family-readonly-gap | unsupported_gap | 0 | 0 | [] | [] | [] | [] | [] |
| typed-input-field-readonly | incomplete_hash | 0 | 0 | [] | [] | [] | [] | [] |

## Notes

- `before_hashes` are calculated after tail stripping and before dynamic replacements.
- `after_hashes` are the normal corpus `normalized_hash` values.
- `operation_token` is preserved as a semantic token and is not replaced by the current normalizer.

# Protocol Normalizer Evidence

- Generated at: `2026-06-05T11:50:30Z`
- Accepted replacements: `["binary_frame_dynamic_bytes", "binary_frame_without_semantic_token", "polling_frame_repeat_dedup"]`
- Preserved fields: `["semantic_payload_token"]`
- Ambiguous fields: `[]`
- Normalizer investigation cases: `[]`

## Cases

| case | classification | before hash count | after hash count | before prefixes | after prefixes | accepted replacements | preserved fields | ambiguous fields |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-form | stable | 2 | 1 | ["2a92e0e66ca73618", "df58d4117839a7a1"] | ["484507fd5b4399e3"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |
| tm-v1-active-window | non_accepted | 2 | 1 | ["611b3bc7fc825303", "fc0e7a0dcf65bc5b"] | ["8405686654272190"] | ["binary_frame_dynamic_bytes", "binary_frame_without_semantic_token"] | ["semantic_payload_token"] | [] |
| tm-v1-button-inert | non_accepted | 2 | 1 | ["679d96078cbd2fcb", "d05201ceb1d16e2b"] | ["338c9594036d6108"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |
| tm-v1-checkbox-true | stable | 2 | 1 | ["3c9114dcd08f601a", "9aa9d26837d0d114"] | ["7a6b4ee6ce323d54"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |
| tm-v1-commandbar-main | non_accepted | 2 | 1 | ["a80e22794f83b07e", "ad30b0493b452e87"] | ["d53667875717aa2a"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |
| tm-v1-field-string | non_accepted | 2 | 1 | ["4fce5d04088a0595", "ab9b526c274c0765"] | ["125f5761a5508acc"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |
| tm-v1-field-version | non_accepted | 2 | 1 | ["477100ea44575801", "b53276b13970da27"] | ["ced131ff5e070b8b"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |
| tm-v1-form-summary | non_accepted | 2 | 1 | ["9e612e5afa35c98a", "cde2720d1dfaeee0"] | ["484507fd5b4399e3"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |
| tm-v1-group-main | non_accepted | 2 | 1 | ["2c1b2c8f30425467", "aa9c5dec81ee646c"] | ["20e49acc1255b6f4"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |
| tm-v1-pages-main | non_accepted | 2 | 1 | ["582e7088cf2f81cf", "7c46b963ea756fc1"] | ["f5ebb93e628a09a4"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |
| tm-v1-table-items | non_accepted | 2 | 1 | ["0806e391ac8594cc", "57e7c5e57f437655"] | ["cde75cf79d2a25d4"] | ["binary_frame_dynamic_bytes", "polling_frame_repeat_dedup"] | ["semantic_payload_token"] | [] |

## Notes

- `before_hashes` are calculated after tail stripping and before dynamic replacements.
- `after_hashes` are the normal corpus `normalized_hash` values.
- `operation_token` is preserved as a semantic token and is not replaced by the current normalizer.

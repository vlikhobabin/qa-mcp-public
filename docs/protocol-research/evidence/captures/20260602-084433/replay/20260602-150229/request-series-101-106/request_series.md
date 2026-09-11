# Protocol Request Series

- Generated at: `2026-06-02T12:18:08Z`
- Input kind: `replay`
- Input dir: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\vanessa-mcp\runtime\protocol-research\captures\20260602-084433\replay\20260602-150229`
- Frames: `101..106`
- Normalized request shape SHA-256: ``
- Canonical request shape SHA-256: ``

## Summary

- `frame_count`: `6`
- `request_body_lengths`: `{347: 3, 345: 3}`
- `response_byte_counts`: `{'332': 1, '313': 2, '330': 1, '311': 2}`
- `request_semantic_counts`: `{'form_element_summary_request': 6}`
- `response_semantic_counts`: `{'form_element_summary': 6}`
- `sequence_le_at_19_values`: `[5563, 5564, 5565, 5566, 5567, 5568]`
- `unique_ack_guids_at_2`: `['78ee31e9-55d4-4680-87a1-0d962999c2c9']`
- `unique_managed_form_guids`: `['16f14cb6-6c7b-41d8-85ec-a154745da6ac']`
- `variable_range_count`: `1`

## Frames

| frame | request body | seq@19 | op token@51 | request semantic | element names | response bytes | expected bytes | same size | response semantic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | 347 | 5563 | 2603cee9c164de47ab5ba07142ceaf79 | form_element_summary_request | ['ДиаграммаПоПериодам'] | 332 | 332 | True | form_element_summary |
| 102 | 347 | 5564 | 23c842fb38ad0a40a81b02d5c7822a18 | form_element_summary_request | ['ДиаграммаПоПериодам'] | 313 | 313 | True | form_element_summary |
| 103 | 347 | 5565 | b2c3815e482c61428e8e621adcf59922 | form_element_summary_request | ['ДиаграммаПоПериодам'] | 313 | 313 | True | form_element_summary |
| 104 | 345 | 5566 | 2603cee9c164de47ab5ba07142ceaf79 | form_element_summary_request | ['ДиаграммаПоТоварам'] | 330 | 330 | True | form_element_summary |
| 105 | 345 | 5567 | 23c842fb38ad0a40a81b02d5c7822a18 | form_element_summary_request | ['ДиаграммаПоТоварам'] | 311 | 311 | True | form_element_summary |
| 106 | 345 | 5568 | b2c3815e482c61428e8e621adcf59922 | form_element_summary_request | ['ДиаграммаПоТоварам'] | 311 | 311 | True | form_element_summary |

## Variable Request Ranges

| start | end | length | reason | values by frame |
| --- | --- | --- | --- | --- |
| 0 | 347 | 347 | request_body_lengths_differ | [] |

## Known Dynamic Request Ranges

| name | start | end | length | values by frame |
| --- | --- | --- | --- | --- |
| ack_guid_uuid_le | 2 | 18 | 16 | [{'frame_index': 101, 'hex': 'e931ee78d455804687a10d962999c2c9'}, {'frame_index': 102, 'hex': 'e931ee78d455804687a10d962999c2c9'}, {'frame_index': 103, 'hex': 'e931ee78d455804687a10d962999c2c9'}, {'frame_index': 104, 'hex': 'e931ee78d455804687a10d962999c2c9'}, {'frame_index': 105, 'hex': 'e931ee78d455804687a10d962999c2c9'}, {'frame_index': 106, 'hex': 'e931ee78d455804687a10d962999c2c9'}] |
| sequence_uint16_le | 19 | 21 | 2 | [{'frame_index': 101, 'hex': 'bb15'}, {'frame_index': 102, 'hex': 'bc15'}, {'frame_index': 103, 'hex': 'bd15'}, {'frame_index': 104, 'hex': 'be15'}, {'frame_index': 105, 'hex': 'bf15'}, {'frame_index': 106, 'hex': 'c015'}] |
| nonce | 68 | 84 | 16 | [{'frame_index': 101, 'hex': 'a322ed558a8d1c7d24ee6aff1521ac1f'}, {'frame_index': 102, 'hex': '95885c7408b5cbe71e53988d067cceaa'}, {'frame_index': 103, 'hex': '582bace93f69564c60728515b21409ae'}, {'frame_index': 104, 'hex': '0a435624dc77a7a87d7494b81b8ba8c0'}, {'frame_index': 105, 'hex': 'bb1bfccff360efa42fafe87d632115e1'}, {'frame_index': 106, 'hex': '682050b614dce2699bf2b14d42a674d5'}] |
| managed_form_guid_utf16le | 204 | 276 | 72 | [{'frame_index': 101, 'hex': '310036006600310034006300620036002d0036006300370062002d0034003100640038002d0038003500650063002d00610031003500340037003400350064006100360061006300'}, {'frame_index': 102, 'hex': '310036006600310034006300620036002d0036006300370062002d0034003100640038002d0038003500650063002d00610031003500340037003400350064006100360061006300'}, {'frame_index': 103, 'hex': '310036006600310034006300620036002d0036006300370062002d0034003100640038002d0038003500650063002d00610031003500340037003400350064006100360061006300'}, {'frame_index': 104, 'hex': '310036006600310034006300620036002d0036006300370062002d0034003100640038002d0038003500650063002d00610031003500340037003400350064006100360061006300'}, {'frame_index': 105, 'hex': '310036006600310034006300620036002d0036006300370062002d0034003100640038002d0038003500650063002d00610031003500340037003400350064006100360061006300'}, {'frame_index': 106, 'hex': '310036006600310034006300620036002d0036006300370062002d0034003100640038002d0038003500650063002d00610031003500340037003400350064006100360061006300'}] |

## Shape Groups

| request body | frames | normalized shape SHA-256 | canonical shape SHA-256 | known dynamics |
| --- | --- | --- | --- | --- |
| 345 | [104, 105, 106] | 668029ddff1cbcb791f4c0a868941c535dff56e7f8ca4567f05bda19796c0cd5 | e54dd8f7525b379100da3483d64ec45decd41b9a05a8f91809a760c2b9cfaa52 | ['ack_guid_uuid_le@2:16', 'sequence_uint16_le@19:2', 'nonce@68:16', 'managed_form_guid_utf16le@204:72'] |
| 347 | [101, 102, 103] | 28e4fea4b1a8d5e94176045175dd4057b59c668061e76b563fc678f973493a6f | 9bc0d3a58101f3b5e4a445833623b1b8c14fd7c7d6b7cc3ce46e43d7c71dac97 | ['ack_guid_uuid_le@2:16', 'sequence_uint16_le@19:2', 'nonce@68:16', 'managed_form_guid_utf16le@204:72'] |

## Operation Token Groups

| op | label | token@51 | frames | elements | response bytes | extra response identifiers | token echo positions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | editfield_detail_op_1_caption_or_value | 2603cee9c164de47ab5ba07142ceaf79 | [101, 104] | ['ДиаграммаПоПериодам', 'ДиаграммаПоТоварам'] | [332, 330] | ['Диаграмма'] | [{'frame_index': 101, 'positions': [13]}, {'frame_index': 104, 'positions': [13]}] |
| 2 | editfield_detail_op_2_reference_only | 23c842fb38ad0a40a81b02d5c7822a18 | [102, 105] | ['ДиаграммаПоПериодам', 'ДиаграммаПоТоварам'] | [313, 311] | [] | [{'frame_index': 102, 'positions': [13]}, {'frame_index': 105, 'positions': [13]}] |
| 3 | editfield_detail_op_3_reference_only | b2c3815e482c61428e8e621adcf59922 | [103, 106] | ['ДиаграммаПоПериодам', 'ДиаграммаПоТоварам'] | [313, 311] | [] | [{'frame_index': 103, 'positions': [13]}, {'frame_index': 106, 'positions': [13]}] |

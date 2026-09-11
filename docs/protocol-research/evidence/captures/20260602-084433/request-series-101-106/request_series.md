# Protocol Request Series

- Generated at: `2026-06-02T12:18:08Z`
- Input kind: `capture`
- Input dir: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\vanessa-mcp\runtime\protocol-research\captures\20260602-084433`
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
- `unique_ack_guids_at_2`: `['92b71ecf-cd35-4052-abbd-48afc9134f7a']`
- `unique_managed_form_guids`: `['5d68a8e5-a712-4fc2-8543-9717300ad965']`
- `variable_range_count`: `1`

## Frames

| frame | request body | seq@19 | op token@51 | request semantic | element names | response bytes | expected bytes | same size | response semantic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | 347 | 5563 | 2603cee9c164de47ab5ba07142ceaf79 | form_element_summary_request | ['ДиаграммаПоПериодам'] | 332 | None | False | form_element_summary |
| 102 | 347 | 5564 | 23c842fb38ad0a40a81b02d5c7822a18 | form_element_summary_request | ['ДиаграммаПоПериодам'] | 313 | None | False | form_element_summary |
| 103 | 347 | 5565 | b2c3815e482c61428e8e621adcf59922 | form_element_summary_request | ['ДиаграммаПоПериодам'] | 313 | None | False | form_element_summary |
| 104 | 345 | 5566 | 2603cee9c164de47ab5ba07142ceaf79 | form_element_summary_request | ['ДиаграммаПоТоварам'] | 330 | None | False | form_element_summary |
| 105 | 345 | 5567 | 23c842fb38ad0a40a81b02d5c7822a18 | form_element_summary_request | ['ДиаграммаПоТоварам'] | 311 | None | False | form_element_summary |
| 106 | 345 | 5568 | b2c3815e482c61428e8e621adcf59922 | form_element_summary_request | ['ДиаграммаПоТоварам'] | 311 | None | False | form_element_summary |

## Variable Request Ranges

| start | end | length | reason | values by frame |
| --- | --- | --- | --- | --- |
| 0 | 347 | 347 | request_body_lengths_differ | [] |

## Known Dynamic Request Ranges

| name | start | end | length | values by frame |
| --- | --- | --- | --- | --- |
| ack_guid_uuid_le | 2 | 18 | 16 | [{'frame_index': 101, 'hex': 'cf1eb79235cd5240abbd48afc9134f7a'}, {'frame_index': 102, 'hex': 'cf1eb79235cd5240abbd48afc9134f7a'}, {'frame_index': 103, 'hex': 'cf1eb79235cd5240abbd48afc9134f7a'}, {'frame_index': 104, 'hex': 'cf1eb79235cd5240abbd48afc9134f7a'}, {'frame_index': 105, 'hex': 'cf1eb79235cd5240abbd48afc9134f7a'}, {'frame_index': 106, 'hex': 'cf1eb79235cd5240abbd48afc9134f7a'}] |
| sequence_uint16_le | 19 | 21 | 2 | [{'frame_index': 101, 'hex': 'bb15'}, {'frame_index': 102, 'hex': 'bc15'}, {'frame_index': 103, 'hex': 'bd15'}, {'frame_index': 104, 'hex': 'be15'}, {'frame_index': 105, 'hex': 'bf15'}, {'frame_index': 106, 'hex': 'c015'}] |
| nonce | 68 | 84 | 16 | [{'frame_index': 101, 'hex': '2c1b5a119fea87469d8dcb312c59fea3'}, {'frame_index': 102, 'hex': 'fbe884bbf0a2f141b831ef2e8e91021e'}, {'frame_index': 103, 'hex': '35e0dd26ac5cf443997da2079bb21fa9'}, {'frame_index': 104, 'hex': '54746c061ec6da4b9d6b1acbd1483c59'}, {'frame_index': 105, 'hex': '98e95ccc76133a458f08fb33427cd35a'}, {'frame_index': 106, 'hex': 'cb91ae513c30244f95f116d6a8693f37'}] |
| managed_form_guid_utf16le | 204 | 276 | 72 | [{'frame_index': 101, 'hex': '350064003600380061003800650035002d0061003700310032002d0034006600630032002d0038003500340033002d00390037003100370033003000300061006400390036003500'}, {'frame_index': 102, 'hex': '350064003600380061003800650035002d0061003700310032002d0034006600630032002d0038003500340033002d00390037003100370033003000300061006400390036003500'}, {'frame_index': 103, 'hex': '350064003600380061003800650035002d0061003700310032002d0034006600630032002d0038003500340033002d00390037003100370033003000300061006400390036003500'}, {'frame_index': 104, 'hex': '350064003600380061003800650035002d0061003700310032002d0034006600630032002d0038003500340033002d00390037003100370033003000300061006400390036003500'}, {'frame_index': 105, 'hex': '350064003600380061003800650035002d0061003700310032002d0034006600630032002d0038003500340033002d00390037003100370033003000300061006400390036003500'}, {'frame_index': 106, 'hex': '350064003600380061003800650035002d0061003700310032002d0034006600630032002d0038003500340033002d00390037003100370033003000300061006400390036003500'}] |

## Shape Groups

| request body | frames | normalized shape SHA-256 | canonical shape SHA-256 | known dynamics |
| --- | --- | --- | --- | --- |
| 345 | [104, 105, 106] | 1a9b8fc37a8e5fb7747cf00b71212c7ac22a2b397490a9d5786443f20e2f423e | e54dd8f7525b379100da3483d64ec45decd41b9a05a8f91809a760c2b9cfaa52 | ['ack_guid_uuid_le@2:16', 'sequence_uint16_le@19:2', 'nonce@68:16', 'managed_form_guid_utf16le@204:72'] |
| 347 | [101, 102, 103] | c45aff31df5083393e6b4a6cd3e941e0964294e5af1c33e4d407159f4342bb84 | 9bc0d3a58101f3b5e4a445833623b1b8c14fd7c7d6b7cc3ce46e43d7c71dac97 | ['ack_guid_uuid_le@2:16', 'sequence_uint16_le@19:2', 'nonce@68:16', 'managed_form_guid_utf16le@204:72'] |

## Operation Token Groups

| op | label | token@51 | frames | elements | response bytes | extra response identifiers | token echo positions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | editfield_detail_op_1_caption_or_value | 2603cee9c164de47ab5ba07142ceaf79 | [101, 104] | ['ДиаграммаПоПериодам', 'ДиаграммаПоТоварам'] | [332, 330] | ['Диаграмма'] | [{'frame_index': 101, 'positions': [13]}, {'frame_index': 104, 'positions': [13]}] |
| 2 | editfield_detail_op_2_reference_only | 23c842fb38ad0a40a81b02d5c7822a18 | [102, 105] | ['ДиаграммаПоПериодам', 'ДиаграммаПоТоварам'] | [313, 311] | [] | [{'frame_index': 102, 'positions': [13]}, {'frame_index': 105, 'positions': [13]}] |
| 3 | editfield_detail_op_3_reference_only | b2c3815e482c61428e8e621adcf59922 | [103, 106] | ['ДиаграммаПоПериодам', 'ДиаграммаПоТоварам'] | [313, 311] | [] | [{'frame_index': 103, 'positions': [13]}, {'frame_index': 106, 'positions': [13]}] |

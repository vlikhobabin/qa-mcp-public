# Protocol Capture Analysis

- Generated at: `2026-06-02T06:47:05Z`
- Capture dir: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\vanessa-mcp\runtime\protocol-research\captures\20260602-084433`
- Frames file: `frames.jsonl`
- Scenario: `all`
- TestClient port: `15381`
- Proxy port: `15382`
- MCP port: `19874`

## Summary

```json
{
  "chunk_count_by_direction": {
    "client_to_manager": 107,
    "manager_to_client": 106
  },
  "bytes_by_direction": {
    "client_to_manager": 20433,
    "manager_to_client": 22049
  },
  "class_counts": {
    "binary": 204,
    "utf8-bom-text": 8,
    "utf-16-le-text": 1
  },
  "tail_marker_counts": {
    "false": 1,
    "true": 212
  },
  "header_sides": {
    "manager_to_client:0": 4,
    "client_to_manager:1": 4
  },
  "header_kinds": {
    "manager_to_client:4": 3,
    "manager_to_client:1": 1
  },
  "first_sequence_values": {
    "manager_to_client": [
      "5463",
      "5464",
      "5465",
      "5466"
    ],
    "client_to_manager": [
      "1",
      "1",
      "1",
      "1"
    ]
  },
  "top_guids": [
    [
      "6ca75e50-62a3-4842-b6cd-b429f7591ef2",
      186
    ],
    [
      "5d68a8e5-a712-4fc2-8543-9717300ad965",
      169
    ],
    [
      "ae135932-4f94-44df-92c1-c91f15a92848",
      6
    ],
    [
      "671507fd-50a9-4b63-b70e-58b3d364f48f",
      6
    ],
    [
      "e23134a2-14ff-4160-ba5f-ccef04e3786f",
      3
    ],
    [
      "7f58f27d-5ad8-43a1-aa1e-c982f41bed5c",
      3
    ],
    [
      "d450256e-76cf-4404-b8ae-056edd642053",
      3
    ],
    [
      "00000000-0000-0000-0000-000000000000",
      3
    ],
    [
      "92b71ecf-cd35-4052-abbd-48afc9134f7a",
      2
    ],
    [
      "3ace6d91-51bb-4344-9388-c8105ad4ad11",
      1
    ],
    [
      "ba5edc33-8936-4212-9ed2-485e759203aa",
      1
    ],
    [
      "102301e1-f311-4cbb-acb2-9dbfa0aeb4bd",
      1
    ]
  ]
}
```

## Non-Chunk Events

| ts | event | connection | direction |
| --- | --- | --- | --- |
| 2026-06-02T05:44:36.896604Z | proxy_listening |  |  |
| 2026-06-02T05:44:59.313214Z | connection_open | 1 |  |
| 2026-06-02T05:45:00.162113Z | direction_error | 1 | manager_to_client |
| 2026-06-02T05:45:00.162433Z | direction_eof | 1 | client_to_manager |
| 2026-06-02T05:45:00.162541Z | connection_closed | 1 |  |

## First Frames

| chunk | direction | bytes | class | bom | tail | header | head hex | excerpt |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | client_to_manager | 5 | binary | False | False | [] | 53f5c61a7b |  |
| 1 | manager_to_client | 547 | utf8-bom-text | True | True | ['0', 'e23134a2-14ff-4160-ba5f-ccef04e3786f', '5463', '4'] | efbbbf7b302c65323331333461322d313466662d343136302d626135662d6363 | {0,e23134a2-14ff-4160-ba5f-ccef04e3786f,5463,4,7f58f27d-5ad8-43a1-aa1e-c982f41bed5c,0,1,11,0,\r\n{"S","TestClient:TestClient"},0,\r\n{"#",ae135932-4f94-44df-92c1-c91f15a92848,\r\n{1,d450256e-76cf-4404-b8ae-056edd642053}\r\n},0,\r\n{"S","Tes... |
| 2 | client_to_manager | 210 | utf8-bom-text | True | True | ['1', '1636514399', '1'] | efbbbf7b312c313633363531343339392c312c0d0a7b2255227d2c31312c302c | {1,1636514399,1,\r\n{"U"},11,0,0,0,0,2,\r\n{"#",671507fd-50a9-4b63-b70e-58b3d364f48f,\r\n{VjhJbnRyb1RpY2tldEFjawAWREVTS1RPUC1LVThIVTYyXExlbm92bwAJTmVnb3RpYXRl}\r\n},1,\r\n{"B",0},0,0,0,0,1,\r\n{"U"},1,"RHostRoot"},0 |
| 2 | manager_to_client | 579 | utf8-bom-text | True | True | ['0', 'e23134a2-14ff-4160-ba5f-ccef04e3786f', '5464', '4'] | efbbbf7b302c65323331333461322d313466662d343136302d626135662d6363 | {0,e23134a2-14ff-4160-ba5f-ccef04e3786f,5464,4,7f58f27d-5ad8-43a1-aa1e-c982f41bed5c,0,1,11,0,\r\n{"S","TestClient:TestClient"},0,\r\n{"#",ae135932-4f94-44df-92c1-c91f15a92848,\r\n{1,d450256e-76cf-4404-b8ae-056edd642053}\r\n},0,\r\n{"S","Tes... |
| 3 | client_to_manager | 450 | utf8-bom-text | True | True | ['1', '1636514400', '1'] | efbbbf7b312c313633363531343430302c312c0d0a7b2255227d2c31312c302c | {1,1636514400,1,\r\n{"U"},11,0,0,0,0,2,\r\n{"#",671507fd-50a9-4b63-b70e-58b3d364f48f,\r\n{TlRMTVNTUAACAAAAHgAeADgAAAA1worimyyRQnvdI0LCAAEAAAAAAJgAmABWAAAACgD0ZQAAAA9EAEUAUwBLAFQATwBQAC0ASwBVADgASABVADYAMgACAB4ARABFAFMASwBUAE8AUAAtAEsAVQA4AE... |
| 3 | manager_to_client | 611 | utf8-bom-text | True | True | ['0', 'e23134a2-14ff-4160-ba5f-ccef04e3786f', '5465', '4'] | efbbbf7b302c65323331333461322d313466662d343136302d626135662d6363 | {0,e23134a2-14ff-4160-ba5f-ccef04e3786f,5465,4,7f58f27d-5ad8-43a1-aa1e-c982f41bed5c,0,1,11,0,\r\n{"S","TestClient:TestClient"},0,\r\n{"#",ae135932-4f94-44df-92c1-c91f15a92848,\r\n{1,d450256e-76cf-4404-b8ae-056edd642053}\r\n},0,\r\n{"S","Tes... |
| 4 | client_to_manager | 262 | utf8-bom-text | True | True | ['1', '1636514401', '1'] | efbbbf7b312c313633363531343430312c312c0d0a7b2223222c336163653664 | {1,1636514401,1,\r\n{"#",3ace6d91-51bb-4344-9388-c8105ad4ad11,\r\n{92b71ecf-cd35-4052-abbd-48afc9134f7a}\r\n},11,0,0,0,0,2,\r\n{"#",671507fd-50a9-4b63-b70e-58b3d364f48f,\r\n{}\r\n},1,\r\n{"B",1},0,0,0,0,1,\r\n{"#",ba5edc33-8936-4212-9ed2-48... |
| 4 | manager_to_client | 91 | utf8-bom-text | True | True | ['0', '92b71ecf-cd35-4052-abbd-48afc9134f7a', '5466', '1'] | efbbbf7b302c39326237316563662d636433352d343035322d616262642d3438 | {0,92b71ecf-cd35-4052-abbd-48afc9134f7a,5466,1,102301e1-f311-4cbb-acb2-9dbfa0aeb4bd} |
| 5 | client_to_manager | 23 | utf8-bom-text | True | True | ['1', '2732362971', '1'] | efbbbf7b312c323733323336323937312c317d6653b2a6 | {1,2732362971,1} |
| 5 | manager_to_client | 113 | binary | False | True | [] | 4195cf1eb79235cd5240abbd48afc9134f7a8d5b158595e101231011f3bb4cac |    fS |
| 6 | client_to_manager | 76 | binary | False | True | [] | 428fdf8cdca284838183cb23953e7ce4bebd3626498daf71e22243feb0d5373a |  |
| 6 | manager_to_client | 104 | binary | False | True | [] | 4195cf1eb79235cd5240abbd48afc9134f7a8d5c15818595e101231011f3bb4c |    fS |

## First Binary Manager Frames

| chunk | bytes | uuid_le_at_2 | seq_le_at_19 | block_67_or_68 | block_88 | head hex |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 113 | 92b71ecf-cd35-4052-abbd-48afc9134f7a | 5467 | 373ab725d4798244b15e94082e4688e2 | 56925ef05101e84e9069bfc76324f58e | 4195cf1eb79235cd5240abbd48afc9134f7a8d5b158595e101231011f3bb4cac |
| 6 | 104 | 92b71ecf-cd35-4052-abbd-48afc9134f7a | 5468 | 3ffa8bfa190a3a429a2a3d88f3b24010 |  | 4195cf1eb79235cd5240abbd48afc9134f7a8d5c15818595e101231011f3bb4c |
| 7 | 103 | 92b71ecf-cd35-4052-abbd-48afc9134f7a | 5469 | f195bf36c5c4ea4982a09336f4e0bcad |  | 4195cf1eb79235cd5240abbd48afc9134f7a8d5d15818595e101231011f3bb4c |
| 8 | 99 | 92b71ecf-cd35-4052-abbd-48afc9134f7a | 5470 | ffd632d233998342ac06e4f703278067 |  | 4195cf1eb79235cd5240abbd48afc9134f7a8d5e15818595e101231011f3bb4c |
| 9 | 103 | 92b71ecf-cd35-4052-abbd-48afc9134f7a | 5471 | 97cb223acb93fc46b475e54166e11b32 |  | 4195cf1eb79235cd5240abbd48afc9134f7a8d5f15818595e101231011f3bb4c |
| 10 | 99 | 92b71ecf-cd35-4052-abbd-48afc9134f7a | 5472 | 3a3f06eebbc7d242b6db84477b326781 |  | 4195cf1eb79235cd5240abbd48afc9134f7a8d6015818595e101231011f3bb4c |
| 11 | 99 | 92b71ecf-cd35-4052-abbd-48afc9134f7a | 5473 | 0d6f48b8192a19498b77195d6564b5c7 |  | 4195cf1eb79235cd5240abbd48afc9134f7a8d6115818595e101231011f3bb4c |
| 12 | 150 | 92b71ecf-cd35-4052-abbd-48afc9134f7a | 5474 | d5a526a520e4a6f34dba088ccb4b3a61 | 6d65506167655b36636137356535302d | 4195cf1eb79235cd5240abbd48afc9134f7a8d6215818595e101231011f3bb4c |

## MCP Results

| file | status | id | excerpt |
| --- | --- | --- | --- |
| mcp_active_form_name.json | ok | 112 | Отчет.ДашбордПродажи.Форма.ФормаОтчета |
| mcp_active_window_caption.json | ok | 111 | Начальная страница |
| mcp_attach_running.json | ok | 100 | Шаг выполнен успешно |
| mcp_form_analysis_gherkin.json | ok | 120 | # Анализ текущей формы\n\n## Gherkin-состояние формы\n```gherkin\n	Тогда элемент формы с именем 'ДиаграммаПоПериодам' стал равен "ДиаграммаПоПериодам"\n	И у элемента формы с именем... |
| mcp_tools.json | ok | None |  |
| mcp_window_list_testclient.json | ok | 110 | В клиенте тестирования найдено 2 окон:\n   -Демонстрационное приложение\n   -Начальная страница |

## Initial Protocol Hypotheses

- Many text-like chunks start with UTF-8 BOM `EF BB BF` and end with marker `66 53 B2 A6`.
- The first TestClient-to-manager chunk is a 5-byte preface before the text-like frame exchange.
- Text-like chunks use a brace/comma structure rather than strict JSON; first-line header fields are captured in `header_fields`.
- Later chunks can be binary even when they still end with the same tail marker.
- Repeated GUIDs and sequence/header fields should be correlated across multiple captures before implementing replay.

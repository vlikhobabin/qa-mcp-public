# Demo Real Mutation — Protocol Capture (Warehouse "Не использовать" toggle)

Run id: `mut-warehouse-donotuse-20260610`

## Decision

The real, recoverable business-data mutation proven earlier
(`20260610-warehouse-donotuse-real-mutation`) was re-executed **through the
qa-mcp capture pipeline** so its TestClient protocol frames are captured. The
mutation and its recovery are database-confirmed and the write traffic is
isolated to a small, named frame range. This is the first protocol-level
evidence of a real business-data mutation in qa-mcp.

| Field | Value |
| --- | --- |
| Object | `Справочник.Склады`, element `Средний` |
| Field | `НеИспользовать` (boolean) |
| Operation family | `catalog_boolean_attribute_toggle` |
| `mutates_business_data` | `true` |
| Pre / Post / Recovery | `Нет` → `Да` → `Нет` (DB-confirmed via `Перечитать`) |
| Result status | `mutation_and_recovery_confirmed` |
| Total captured frames | 1723 (~400 KB) |
| Isolated action-write frames | **28 frames / 7512 bytes** |

## How it was captured

The capture pipeline (`tools\protocol-research\run_protocol_capture.ps1`,
new `-Scenario demo-catalog-mutation`) launches its own TestClient
(`/TESTCLIENT` on `vanessa_client`), a recording proxy (15382 → 15381) and a
Vanessa TestManager (MCP 19874). The manager attaches to the TestClient
**through the proxy**, then drives the proven toggle sequence via
`execute_step_from_text` / `get_form_analysis`:

1. `bootstrap_open_card` — open `Склады` list, go to row `Средний`, press `Изменить`.
2. `pre_read` — `get_form_analysis` → `НеИспользовать = Нет`.
3. `action_write` — set the flag, press `Записать` (**the mutation write**).
4. `post_read` — press `Перечитать`, `get_form_analysis` → `НеИспользовать = Да`.
5. `recovery` — clear the flag, `Записать`, `Перечитать` → `НеИспользовать = Нет`.

Every TestClient API call flows through the proxy, so all frames land in
`traffic.jsonl`. The runner records a UTC `phaseTimeline`, so frames are
attributed to phases by timestamp.

## Frame isolation

| Phase | Frames | Bytes | Flag after |
| --- | ---: | ---: | --- |
| bootstrap_open_card | 50 | 14865 | |
| pre_read | 478 | 111688 | Нет |
| **action_write** | **28** | **7512** | |
| post_read | 548 | 125893 | Да |
| recovery | 588 | 135649 | Нет |

The mutation write is cleanly separated from bootstrap, read and recovery
traffic. Compact per-frame metadata (direction, size, sha256, normalized
header/GUID fields, text excerpt — **no raw payload**) for the 28 action-write
frames is in `frame_isolation.json`.

## Proof class and honest limitation

Proof class: `isolated_action_frames_with_db_confirmed_mutation_and_recovery`.

What is proven: a real business-data write happened, its frames are isolated,
and the value was confirmed in the database before and after both the mutation
and the recovery.

What is **not** yet proven: the decoding of the write opcode and field binding
to a named TestClient API call. `accepted_protocol_mapping` stays `false`. The
next step promotes this to an accepted mapping by comparing the isolated
action-write frames against a **same-action vanessa-mcp reference** run (the
automatic comparison oracle), and against a repeat capture to confirm the
normalized hash is stable across runs.

## Raw output policy

Raw streams and full parsed frames stay under ignored
`runtime/protocol-research/captures/mut-warehouse-donotuse-20260610/`
(`client_to_manager.bin`, `manager_to_client.bin`, `traffic.jsonl`,
`frames.jsonl`, `analysis.md`). Only compact metadata is in reviewed git.

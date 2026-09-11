# 1C Test Protocol Research Plan

## Goal

Investigate the native 1C TestManager/TestClient TCP protocol enough to build a
Python manager that can talk directly to a `/TESTCLIENT` process without
starting a second 1C instance as `/TestManager`.

The first research target is local Windows file bases:

- TestClient base: `C:\1C_BASES\vanessa_client`
- TestManager base: `C:\1C_BASES\vanessa_manager`
- Fixed platform for both sides: `C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe`

`C:\1C_BASES\vanessa_manager` must be used as the manager base. Because the
current copy is an empty file infobase and did not start Vanessa MCP during
preflight, it must be prepared by recreating it from the stack manager template
before a capture run:

```powershell
scripts\protocol-research\run_protocol_capture.ps1 -RecreateManagerFromTemplate
```

The script deletes and replaces only `C:\1C_BASES\vanessa_manager`, and refuses
to recreate arbitrary custom manager paths.

## Current Evidence

Preflight on 2026-06-02 established:

- `vanessa_client` and `vanessa_manager` both exist and contain `1Cv8.1CD`.
- `vanessa_client` starts in `/TESTCLIENT` mode and opens a TCP listener when
  launched with `-TPort`.
- `vanessa_client` starts cleanly with `/NАдминистратор` and an empty password.
- The Vanessa lazy backend starts successfully on platform `8.3.27.2130` and
  exposes the full MCP tool surface.
- The empty `vanessa_manager` did not open the Vanessa MCP port when started
  directly with the Vanessa EPF, while the prepared stack template did.
- Python 3.13.1 is available.
- Wireshark/tshark/dumpcap are not installed; Windows `pktmon` is available.

## Script Smoke Results

`C:\1C_BASES\vanessa_manager` was recreated from `infobases\manager` on
2026-06-02 and then used as the direct Vanessa TestManager base.

The orchestration script was smoke-tested with:

```powershell
scripts\protocol-research\run_protocol_capture.ps1 -Scenario connect-only
scripts\protocol-research\run_protocol_capture.ps1 -Scenario all
```

Both runs returned `status=ok` and stopped the created TestClient, proxy and
TestManager PIDs. The latest full read-only capture was written to:

```text
runtime\protocol-research\captures\20260602-084433\
```

That capture includes a successful active window read (`Начальная страница`),
active form name read (`Отчет.ДашбордПродажи.Форма.ФормаОтчета`), form analysis
Gherkin output, and non-empty raw protocol streams in both directions.

The first analyzer pass is available as:

```powershell
python scripts\protocol-research\analyze_capture.py runtime\protocol-research\captures\20260602-084433
```

It writes:

- `analysis.md` - human-readable protocol summary.
- `frames.jsonl` - one machine-readable record per captured chunk.

Initial analyzer observations from `20260602-084433`:

- 213 captured chunks: 107 client-to-manager, 106 manager-to-client.
- 20,433 bytes client-to-manager and 22,049 bytes manager-to-client.
- The first client-to-manager payload is a 5-byte preface: `53 F5 C6 1A 7B`.
- 212 of 213 chunks end with marker `66 53 B2 A6`.
- The handshake begins with UTF-8 BOM text-like frames.
- Manager handshake frame headers start with side `0`, stable message GUID
  `e23134a2-14ff-4160-ba5f-ccef04e3786f`, and sequence values such as
  `5463`, `5464`, `5465`, `5466`.
- Client handshake frame headers start with side `1` and numeric message IDs
  such as `1636514399`, `1636514400`.
- Later frames are mostly binary and need a second-level frame decoder before
  replay.

## Replay Probe Results

The first direct replay probe is available as:

```powershell
python scripts\protocol-research\replay_probe.py runtime\protocol-research\captures\20260602-084433 --port 15381 --send-count 1
```

The probe expects a separately running `/TESTCLIENT`; it does not start or stop
1C itself. It writes replay evidence under:

```text
runtime\protocol-research\captures\<capture>\replay\<timestamp>\
```

Smoke runs on 2026-06-02 used a temporary `vanessa_client` TestClient process
on port `15381`, then stopped only that created PID.

Replay evidence:

- `send-count 1` wrote replay `20260602-090816`.
- The initial 5-byte TestClient preface matched the capture exactly:
  `53 F5 C6 1A 7B`.
- The TestClient response after the first captured manager frame matched the
  capture byte-for-byte.
- `send-count 4` wrote replay `20260602-091027`.
- Responses after manager frames 2 and 3 kept the same frame shape and length,
  but differed in dynamic NTLM/session payload bytes.
- Response after manager frame 4 diverged: instead of the captured 23-byte ACK,
  TestClient returned a text error frame containing
  `Сеанс работы завершен администратором.`
- `send-count 4 --adapt-frame4-guid` wrote replay `20260602-091441`.
- The adaptive probe extracted live GUID
  `e1fa1386-dc57-4a61-b774-d4ab2f87446e` from the response after manager
  frame 3 and replaced the captured manager frame 4 header GUID
  `92b71ecf-cd35-4052-abbd-48afc9134f7a`.
- Response after the adapted manager frame 4 became a 23-byte ACK:
  `{1,4062157521,1}`.
- The ACK differs from the captured ACK only in the dynamic numeric id
  (`4062157521` vs `2732362971`). The session-close error disappeared.
- `send-count 5 --adapt-frame4-guid` wrote replay `20260602-094008`.
  Manager binary frame 5 still contained captured GUID
  `92b71ecf-cd35-4052-abbd-48afc9134f7a` in UUID little-endian form at
  offset 2. TestClient returned a 665-byte error frame containing
  `Сеанс работы завершен администратором.`
- `send-count 5 --adapt-frame4-guid --adapt-frame5-guid` wrote replay
  `20260602-094228`. The probe replaced that UUID_LE value with the live GUID
  `3b5c342d-32ca-495e-945b-2abf5debe5ee` at offset 2. TestClient no longer
  returned the session-close error, but returned an 826-byte error frame:
  `Ошибка подключения к клиенту тестирования. Отсутствует подходящий клиент тестирования.`
- A second real connect-only capture was written to
  `runtime\protocol-research\captures\20260602-094336\`.
- Two more real connect-only captures were written to
  `runtime\protocol-research\captures\20260602-095544\` and
  `runtime\protocol-research\captures\20260602-095648\`.
- Comparing real captures `20260602-084433` and `20260602-094336` showed that
  manager binary frame 5 differs at offsets `2..17` (dynamic ACK GUID in
  UUID_LE form), `19..20` (little-endian sequence: text frame 4 sequence + 1),
  `67..82` and `88..103` (two 16-byte session/auth blocks). Those two
  16-byte blocks are echoed by client response 6 at offsets `30..45` and
  `51..66`.
- `compare_captures.py` wrote comparison evidence to
  `runtime\protocol-research\comparisons\20260602-095920\`. Across four real
  captures, frame 5 always has:
  - UUID_LE at offset `2` equal to the frame 4/client ACK GUID.
  - `uint16_le` at offset `19` equal to frame 4 sequence + 1.
  - Two variable 16-byte blocks at offsets `67` and `88`, echoed by client
    response 6 at offsets `30` and `51`.
- The analyzer now writes a `First Binary Manager Frames` section and
  `binary_probe` fields in `frames.jsonl` so these binary offsets are visible
  without ad-hoc scripts.
- `send-count 5 --adapt-frame4-guid --adapt-frame5-guid --adapt-frame5-random-blocks`
  wrote replay `20260602-100101`. The probe replaced frame 5 blocks at offsets
  `67` and `88` with random 16-byte values. TestClient returned the normal
  76-byte response and echoed the random blocks at response offsets `30` and
  `51`.
- `send-count 7 --adapt-frame4-guid --adapt-frame5-guid --adapt-frame5-random-blocks --adapt-frame6-7`
  wrote replay `20260602-100435`. The probe adapted frames 6 and 7 by replacing
  the ACK GUID in UUID_LE form at offset `2` and replacing the 16-byte block at
  offset `68` with random bytes. TestClient returned normal responses with the
  captured sizes: 360 bytes after frame 6 and 359 bytes after frame 7. In both
  responses the random block was echoed at offset `30`.
- `send-count 8 --adapt-frame4-guid --adapt-frame5-guid --adapt-frame5-random-blocks --adapt-binary-single-block-through 8`
  wrote replay `20260602-101110`. Frame 8 follows the same single-block binary
  template: ACK GUID in UUID_LE form at offset `2`, captured sequence at offset
  `19`, and one arbitrary 16-byte block at offset `68`. TestClient returned
  the expected 212-byte response and echoed the random frame 8 block at
  response offset `30`. That response contains the first useful UI payload
  observed in replay, including `HomePage` / `Начальная страница`.
- `send-count 10 --adapt-frame4-guid --adapt-frame5-guid --adapt-frame5-random-blocks --adapt-binary-single-block-through 10`
  wrote replay `20260602-101735`. Frames 9 and 10 also follow the same
  single-block binary template. TestClient returned captured-size responses:
  359 bytes after frame 9 and 212 bytes after frame 10. The random frame 9/10
  blocks were echoed at response offset `30`.
- Response after frame 9 contains stable UI identifiers:
  `MainFrame`, `HomePage`, and `e1cib/navigationpoint/startpage`.
- Response after frame 10 contains `HomePage` and
  `e1cib/navigationpoint/startpage`.
- `extract_payloads.py` wrote systematic payload reports for frames 8..10:
  - Capture report:
    `runtime\protocol-research\captures\20260602-084433\payload_extract.md`.
  - Replay report:
    `runtime\protocol-research\captures\20260602-084433\replay\20260602-101735\payload_extract.md`.
- The extractor records response sizes, nonce echo positions, ASCII strings,
  UTF-16LE strings and a first `semantic_guess`. For both capture and replay:
  - Frame 8: `home_page_navigation_point`, 212-byte response, nonce
    `68->[30]`, identifiers `HomePage`, `e1cib/navigationpoint/startpage`,
    `Начальная страница`.
  - Frame 9: `main_frame_with_home_page`, 359-byte response, nonce
    `68->[30]`, identifiers `MainFrame`, `HomePage`,
    `e1cib/navigationpoint/startpage`, `Демонстрационное приложение`,
    `Начальная страница`.
  - Frame 10: `home_page_navigation_point`, 212-byte response, nonce
    `68->[30]`, identifiers `HomePage`, `e1cib/navigationpoint/startpage`,
    `Начальная страница`.
- `extract_manager_templates.py` wrote manager frame templates for frames 8..10
  to `runtime\protocol-research\templates\20260602-104132\`. Each template
  separates stable byte ranges from generated fields:
  - ACK GUID as UUID_LE at offset `2`.
  - Sequence as `uint16_le` at offset `19`, calculated as frame 4 sequence +
    delta.
  - Random 16-byte nonce at offset `68`.
- `send-count 10` with `--manager-templates` wrote replay
  `20260602-104203`. Frames 8..10 were rendered from
  `manager_frame_templates.json`, not patched from captured frame bytes.
  TestClient returned the expected response sizes and payload semantics:
  `home_page_navigation_point`, `main_frame_with_home_page`,
  `home_page_navigation_point`.
- `python_manager_probe.py` wrote the first minimal Python TestManager
  prototype evidence to
  `runtime\protocol-research\python-manager-probe\20260602-105024\`. The probe
  connected directly to a running `/TESTCLIENT`, sent captured bootstrap frames
  1..3, adapted frame 4 from the live ACK GUID, generated frames 5..7 from
  protocol rules, rendered frames 8..10 from `manager_frame_templates.json`,
  and extracted structured UI identifiers from responses.
- The prototype result was `status=ok` with ACK GUID
  `a392f0c0-7438-4abc-8c7d-06e54f1f89c5`, frame 4 sequence `5466`, 2,449 bytes
  sent and 2,528 bytes received. It returned:
  - Frame 8: `home_page_navigation_point`, 212-byte response, `HomePage`,
    `e1cib/navigationpoint/startpage`, `Начальная страница`.
  - Frame 9: `main_frame_with_home_page`, 359-byte response, `MainFrame`,
    `HomePage`, `Демонстрационное приложение`, `Начальная страница`.
  - Frame 10: `home_page_navigation_point`, 212-byte response, `HomePage`,
    `e1cib/navigationpoint/startpage`, `Начальная страница`.

- `python_manager_client.py` now contains the reusable Python-manager runtime
  classes: `CaptureBootstrap`, `ProtocolTemplates`, `TestClientSession` and
  `TestClientSession.get_initial_ui_context()`. `python_manager_probe.py` is
  now a thin CLI wrapper around those classes.
- The refactored Python manager was live-tested against a temporary
  `/TESTCLIENT` on port `15381` and wrote evidence to
  `runtime\protocol-research\python-manager-probe\20260602-110237\`. The
  result was `status=ok`, ACK GUID
  `847c3fd9-9b3b-4201-aec0-50d9493ef158`, frame 4 sequence `5466`, 2,449 bytes
  sent and 2,528 bytes received. It returned the same confirmed UI semantics:
  frame 8 `home_page_navigation_point`, frame 9
  `main_frame_with_home_page`, frame 10 `home_page_navigation_point`.
- Payload extraction for frames 8..30 was written to
  `runtime\protocol-research\captures\20260602-084433\payload-frames-08-30\`.
  Frame 12 is the first compact response that contains the active managed form
  descriptor: caption `Продажи`, form name
  `Отчет.ДашбордПродажи.Форма.ФормаОтчета`, and a dynamic
  `HomePage.ManagedForm[...]` reference.
- `extract_manager_templates.py` generated templates for frames 8..12 under
  `runtime\protocol-research\templates\20260602-frames08-12\`. Frames 11 and
  12 use the same dynamic field rule as frames 8..10: live ACK GUID at offset
  `2`, sequence at offset `19`, and a random 16-byte nonce at offset `68`.
- Replay `runtime\protocol-research\captures\20260602-084433\replay\20260602-113014\`
  confirmed that frames 8..12 can be rendered from template JSON. Frame 12
  returned the same 339-byte response shape and active form descriptor with a
  live `ManagedForm[...]` GUID.
- `TestClientSession.get_active_form_context()` was added as the next typed
  Python-manager method. A live run wrote evidence to
  `runtime\protocol-research\python-manager-probe\20260602-113219\` and
  returned `status=ok`, `active_form_name =
  Отчет.ДашбордПродажи.Форма.ФормаОтчета`, `active_form_caption = Продажи`,
  and frame 12 semantic `active_form_descriptor`.

- Templates for frames 8..17 were generated under
  `runtime\protocol-research\templates\20260602-frames08-17-managedform\`.
  Frame 17 has a fourth dynamic field:
  `managed_form_guid@145:36:managed_form_guid_ascii`. This field must be
  rendered from the latest live `ManagedForm[...]` GUID returned by the
  TestClient, not from the captured template bytes.
- Replay `runtime\protocol-research\captures\20260602-084433\replay\20260602-113453\`
  showed the failure mode when frame 17 keeps the captured managed-form GUID:
  the TestClient returned only a 162-byte managed-form reference response
  instead of the expected 876-byte element payload.
- Replay `runtime\protocol-research\captures\20260602-084433\replay\20260602-114034\`
  confirmed the fix. After patching `managed_form_guid_ascii` from the live
  frame 12 response, frame 17 returned 876 bytes with semantic
  `form_element_summary`.
- `TestClientSession.get_form_summary()` was added as the next typed
  Python-manager method. A live run wrote evidence to
  `runtime\protocol-research\python-manager-probe\20260602-114124\` and
  returned `status=ok`, `element_count = 2`, with two `EditField` elements:
  `ДиаграммаПоПериодам` and `ДиаграммаПоТоварам`.

- Templates for frames 8..30 were generated under
  `runtime\protocol-research\templates\20260602-frames08-30-firstpass\`.
  Replay
  `runtime\protocol-research\captures\20260602-084433\replay\20260602-144755\`
  completed with `status=ok` through frame 30. Frames 18..30 all returned
  162-byte `managed_form_ref` responses matching expected replay sizes.
- `analyze_request_series.py` was added to classify manager request series.
  Reports were written for the original capture and replay:
  `runtime\protocol-research\captures\20260602-084433\request-series-18-30\`
  and
  `runtime\protocol-research\captures\20260602-084433\replay\20260602-144755\request-series-18-30\`.
  Both runs show frames 18..30 as 196-byte `managed_form_ref_request`
  bodies with the same canonical request shape SHA-256
  `cc023bcdf5b7f3204b977cf104783966eec7a580226a01972b6e52d1d6e5352e`.
  The known dynamic fields are ACK GUID UUID_LE at `2..18`,
  `sequence_uint16_le` at `19..21`, nonce at `68..84`, and live
  `managed_form_guid_ascii` at `145..181`. Inside each series, only the low
  sequence byte and nonce differ.
- Payload extraction for frames 31..106 showed that frames 31..100 continue
  the same 200-byte request / 162-byte `managed_form_ref` response pattern.
  Frames 101..106 are the next semantic boundary: generated EditField requests
  that return `form_element_summary` responses for the two dashboard chart
  fields.
- `extract_manager_templates.py`, `replay_probe.py` and
  `python_manager_client.py` now support `managed_form_guid_utf16le`.
  This is required for frames 101..106 because the live `ManagedForm[...]`
  GUID is embedded in a UTF-16LE
  `HomePage.ManagedForm.EditField[...]` request string.
- Templates for frames 8..106 were regenerated under
  `runtime\protocol-research\templates\20260602-frames08-106-utf16-managedform\`.
  Live replay
  `runtime\protocol-research\captures\20260602-084433\replay\20260602-150229\`
  completed with `status=ok` through frame 106. Frames 101..106 matched the
  expected response sizes: `332`, `313`, `313`, `330`, `311`, `311`, all with
  semantic `form_element_summary`.
- `analyze_request_series.py` now reports per-body-length shape groups for
  mixed request series. For frames 101..106, capture and replay have matching
  canonical request shapes:
  `9bc0d3a58101f3b5e4a445833623b1b8c14fd7c7d6b7cc3ce46e43d7c71dac97` for
  body length `347` / frames 101..103, and
  `e54dd8f7525b379100da3483d64ec45decd41b9a05a8f91809a760c2b9cfaa52` for
  body length `345` / frames 104..106.
- `python_manager_client.py` now has
  `TestClientSession.get_form_element_details()`, exposed by
  `python_manager_probe.py --query form-element-details`. The method supports
  `--element-frame-mode full` (`1..106`) and `short` (`1..17,101..106`).
  Live short-mode evidence was written to
  `runtime\protocol-research\python-manager-probe\short-element-details-20260602-151206\`.
  The TestClient accepted the sequence jump from frame 17 to frame 101 and
  returned the same element-detail response sizes: `332`, `313`, `313`, `330`,
  `311`, `311`.
- `analyze_request_series.py` now classifies `operation_token@51:16` for
  frames 101..106 and records where that token is echoed in the response. The
  three tokens are identical in capture and replay:
  `2603cee9c164de47ab5ba07142ceaf79` for frames 101/104
  (`editfield_detail_op_1_caption_or_value`, response token echo at offset
  `13`, response includes caption/value `Диаграмма`),
  `23c842fb38ad0a40a81b02d5c7822a18` for frames 102/105
  (`editfield_detail_op_2_reference_only`), and
  `b2c3815e482c61428e8e621adcf59922` for frames 103/106
  (`editfield_detail_op_3_reference_only`). The second and third operations
  echo the token at response offset `13` and return only the element reference.

Confirmed replay findings:

- The first manager frame is static enough to replay directly.
- The NTLM/session challenge response includes dynamic bytes but keeps stable
  framing.
- The fourth manager text frame must acknowledge a dynamic GUID from the third
  TestClient response. Replaying the captured GUID closes the session, while
  replacing it with the live GUID produces the expected short ACK.
- The first binary manager frame can be synthesized with:
  - ACK GUID in UUID_LE form at offset `2`.
  - Sequence `frame4_sequence + 1` as `uint16_le` at offset `19`.
  - Two arbitrary manager-generated 16-byte blocks at offsets `67` and `88`.
- Binary manager frames 6 and 7 can be synthesized with ACK GUID at offset `2`,
  their captured incremented `uint16_le` sequence at offset `19`, and a fresh
  arbitrary 16-byte block at offset `68`.
- Binary manager frame 8 follows the same single-block template and returns the
  first replayed command-specific UI payload.
- Binary manager frames 9 and 10 follow the same single-block template.
- The first replayed UI response payloads expose stable ASCII identifiers such
  as `MainFrame`, `HomePage`, and `e1cib/navigationpoint/startpage`; the next
  extractor maps frames 8 and 10 to `home_page_navigation_point` and frame 9
  to `main_frame_with_home_page`.
- Frames 8..10 can now be generated from `manager_frame_templates.json` plus
  live ACK GUID, frame 4 sequence and fresh nonces. This is the first
  transition from captured-byte replay to protocol message generation.
- `python_manager_probe.py` is the first working TCP-only Python manager
  prototype for this session. It still uses captured bootstrap frames 1..3, but
  no longer needs a running 1C TestManager for the confirmed UI queries.
- `python_manager_client.py` turns that prototype into reusable
  handshake/session/query classes. The current typed query method is
  `TestClientSession.get_initial_ui_context()`.
- `TestClientSession.get_active_form_context()` now maps the next read-only
  Vanessa-style fact from generated frames 11..12: active form caption and
  active form metadata name.
- Frame 17 needs one additional dynamic field beyond the common ACK GUID,
  sequence and nonce fields: the live managed-form GUID obtained from a
  previous active-form descriptor response.
- `TestClientSession.get_form_summary()` now maps the first larger read-only
  form-element payload and returns a typed initial element summary.
- Frames 18..30 are repeated managed-form reference refresh/control requests,
  not new element-property payloads. The generated Python replay and the
  original 1C TestManager capture have the same canonical request shape after
  normalizing ACK GUID, sequence, nonce and ManagedForm GUID.
- Frames 31..100 continue that refresh/control pattern.
- Frames 101..106 are generated EditField request templates. They require
  replacing the live ManagedForm GUID in UTF-16LE at offset `204` and return
  `form_element_summary` payloads for `ДиаграммаПоПериодам` and
  `ДиаграммаПоТоварам`.
- The TestClient accepts a short schedule `1..17,101..106`; frames 31..100 can
  be skipped for this read-only element-detail query.
- The three requests sent per `EditField` are classified by
  `operation_token@51:16`. Operation 1 returns the element reference plus
  caption/value `Диаграмма`; operations 2 and 3 return only the element
  reference. All three operation tokens are echoed in the response at offset
  `13`.
- The next protocol step should test whether one operation can be omitted or
  reordered, starting with a short schedule that sends only operation 1 for
  each `EditField` (`1..17,101,104`).

## Capture Topology

Use an application-level TCP proxy as the primary capture tool:

```text
1C TestManager / Vanessa
        |
        | connects to proxy port
        v
Python TCP proxy 127.0.0.1:15382
        |
        | forwards to real TestClient port
        v
1C TestClient 127.0.0.1:15381
```

This gives deterministic application bytes without requiring loopback packet
capture drivers. `pktmon` can be added later as independent transport evidence.

## Capture Artifacts

Each run writes to:

```text
runtime\protocol-research\captures\<timestamp>\
```

Expected files:

- `capture_manifest.json` - launch parameters and selected paths.
- `capture_summary.json` - outcome, created PIDs, cleanup status.
- `testclient.out` - 1C TestClient `/Out` log.
- `testmanager.out` - 1C TestManager `/Out` log.
- `proxy.out` / `proxy.err` - proxy process logs.
- `traffic.jsonl` - timestamped proxy events and chunk metadata.
- `manager_to_client.bin` - raw aggregate stream from manager to client.
- `client_to_manager.bin` - raw aggregate stream from client to manager.
- `connections\connection_0001_manager_to_client.bin` - per-connection stream.
- `connections\connection_0001_client_to_manager.bin` - per-connection stream.
- `mcp_*.json` - Vanessa MCP requests/results for the scripted scenario.

Runtime captures are local evidence and must not be committed by default.

## First Scenario

The first run should be read-only and minimal:

1. Start `vanessa_client` as `/TESTCLIENT` on the real port.
2. Start the TCP proxy on the proxy port.
3. Start `C:\1C_BASES\vanessa_manager` as `/TestManager` with Vanessa EPF.
4. Wait for Vanessa MCP tools to include `execute_step_from_text`.
5. Execute the Vanessa attach-running step against the proxy port.
6. Run read-only Vanessa MCP tools:
   - `get_window_list_testclient`
   - `get_active_window_data` with `window_caption`
   - `get_active_window_data` with `form_name`
   - `get_form_analysis` with `gherkin`

The first useful protocol boundary is:

```text
connect-only -> active-window -> form-analysis
```

If the connect-only run fails, the captured handshake is still useful evidence.

## Analysis Path

After each capture:

1. Compare `traffic.jsonl` with the Vanessa MCP action timeline.
2. Identify framing: fixed header, length prefix, delimiters, compression, or
   serialized 1C value blocks.
3. Split handshake frames from command/response frames.
4. Repeat with one extra API call at a time to isolate command IDs and response
   shapes.
5. Build a Python replay probe that connects directly to the TestClient and
   sends only the smallest confirmed handshake bytes.
6. Only after handshake replay works, implement typed Python methods for
   read-only calls such as active window and form tree.

## Safety

- Always stop only the PIDs created by the capture script.
- Do not delete `C:\1C_BASES\vanessa_manager` unless
  `-RecreateManagerFromTemplate` is explicitly passed.
- Do not mutate `vanessa_client` beyond normal 1C session service files.
- Keep capture output under `runtime\`.
- Prefer read-only Vanessa calls until the protocol framing is understood.

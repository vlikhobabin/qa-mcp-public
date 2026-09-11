# Linux native capture wrapper — Milestone 1 proven (2026-06-15)

Operator chose to build the recording proxy on Linux (card-80 option B) so new protocol flows
(checkbox / number / date / catalog edit) can be captured here and replayed/tested systematically,
removing the Windows dependency. This records Milestone 1: the capture PIPELINE works end-to-end on
Linux. The genuine-manager driver is Milestone 2.

## Architecture

`driver → protocol_proxy.py(:15382) → TestClient(:15381, Xvfb)` — the proxy records both directions
to `runtime/.../captures/<name>/traffic.jsonl` in the exact `read_capture_chunks` format. `protocol_proxy.py`
is fully portable (asyncio/stdlib, zero changes). The OS-specific part is the launcher
`tools/protocol-research/capture_session.sh` (boots the thin client under `xvfb-run`, starts the proxy,
runs a driver against the proxy, cleans up on exit).

## Milestone 1 — PROVEN

Driver = our own Python manager (`native_openform_probe.py`) pointed at the PROXY port, to prove the
pipeline without yet needing the genuine 1C TestManager:

- Driver through the proxy: `driver-exit=0`, `secondary_frame_opened=true`, `value_mode_on=true`,
  value `PF_EDIT_STRING_VALUE` — the full open-form + value-read flow traversed the proxy.
- Proxy recorded a clean session: **21 manager→client + 22 client→manager** frames, one connection,
  clean EOF both directions, `proxy_stopped`.
- `read_capture_chunks` (the replay pipeline's own loader) parses it: total=43, mgr=21, cli=22; 2
  client frames carry `PF_EDIT_STRING_VALUE` (real protocol content). So a Linux-captured `traffic.jsonl`
  is directly consumable by the existing decode/replay tooling.
- Clean teardown (no leftover 1cv8 / proxy / Xvfb; ports free).

## Two gotchas solved (baked into capture_session.sh)

1. **Proxy readiness via the ready-file, NOT a TCP probe.** A `/dev/tcp` probe of the proxy port is
   forwarded all the way to the TestClient, which accepts ONE manager connection — the spurious
   connect+close consumes the slot and the real driver is then reset. Wait on `proxy.ready.json`.
   (Client listener is checked with `ss`, which does not open a connection.)
2. **File-infobase platform-version contention.** vanessa_client is a FILE base; it can be held by
   only one platform version at a time. The Apache OData publication holds it at **8.3.27.1936**
   (`wsap24.so`), so a TestClient from **8.3.27.2130** opens the port then exits with «активные сеансы …
   другой версии … 8.3.27.1936». Capture and OData-verify are SEQUENTIAL: `sudo systemctl stop apache2`
   to free the base for capture, `start` afterwards to restore OData. (See memory
   linux-native-testclient-xvfb / ibsrv-odata-vs-httpservice.)

## Milestone 2 (next) — genuine manager driver

To capture GENUINE reference frames for new WRITE flows, the real 1C TestManager must drive the client
through the proxy. The manager harness already exists:
`vanessa_manager` → `DataProcessor.ProtocolFixtureTestManager.Form.ManagerHarness` →
`TM_RUN_FROM_CAPTURE_RUNNER_V1(RunID, ProxyPort, ManifestPath, OutputDir)` (connects
`Новый ТестируемоеПриложение("127.0.0.1", ProxyPort, "")`, reads a manifest, runs each command).
Remaining work:
- **Invoke that method Vanessa-free on Linux.** No `ПараметрЗапуска` startup hook exists in the manager
  config today. Add one (`ПередНачаломРаботыСистемы` reads a launch param → opens the harness form →
  calls `TM_RUN_FROM_CAPTURE_RUNNER_V1` → exits) so the manager can be booted headless under Xvfb with
  `1cv8 ENTERPRISE … /C "<capture-run directive>"`. (1C config edit via edt-mcp/designer.) Alternative:
  get vanessa-mcp working on Linux (the Windows path injects the call via execute_step_from_text).
- **Add WRITE command kinds to the harness** (`ВыполнитьReadOnlyКомандуV1` is read-only today): set a
  checkbox, edit a field, set+save a catalog flag.
- **Manifests** for the new write flows + capture them → then replay through `native_action_scenario`
  and verify the effect (OData read-back), answering card 80's "do checkbox/click writes commit on
  replay?" on real objects.
- Manager + client must both run at 8.3.27.2130 (protocol parity) with apache2 stopped (base free).

## Artifacts
- `tools/protocol-research/capture_session.sh` (the launcher), `protocol_proxy.py` (portable proxy).
- Capture: `runtime/protocol-research/captures/linux-proxy-smoke-4/` (gitignored).
</content>

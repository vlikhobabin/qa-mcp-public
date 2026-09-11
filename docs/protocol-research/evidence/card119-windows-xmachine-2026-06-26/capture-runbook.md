# Card 119 — Windows handshake capture: continuation runbook (2026-06-26)

Goal: capture a **genuine** 1C TestManager↔TestClient handshake against the **Windows** client, so qa-mcp can
derive **platform-keyed** bootstrap + manager-frame templates (the OS-axis analogue of epic-112's version keys).
Chosen mechanism (user decision): a **custom minimal `.epf` manager** (deterministic, no Vanessa dependency).

## What is already done
- **Lab proven ready:** `pktmon` present; the qa-mcp checkout + `.venv` Python is on Windows at
  `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp` (branch `main`); the proxy script
  `tools/protocol-research/protocol_proxy.py` supports `--target-host`; the client launches + binds
  `0.0.0.0:15381` in session 1; inbound 15381 firewall rule added.
- **1C testing API resolved:** manager process must run with **`/TESTMANAGER`**; constructor
  `Новый ТестируемоеПриложение(<ИмяКомпьютера>, <Порт>, <ИдентификаторКлиента>)` then `.УстановитьСоединение()`;
  reads `.ПолучитьПодчиненныеОбъекты()` / `.ПолучитьАктивноеОкно()`; client `/TESTCLIENT -TPort<N>` (default 1538).
- **Manager `.epf` SOURCE authored + EDT-exported** (the BSL is correct and verified):
  EDT project `qa_xmachine_mgr` at
  `/opt/ai-dev-suite-for-1c/edt-mcp/.workspaces/infobases/qa_xmachine_mgr`; the form module's `ПриОткрытии`
  connects to `127.0.0.1:15382` (the proxy), reads child objects + active window, logs to
  `C:\Users\historical-user\TEMP\qa_mgr.log`, then `ЗавершитьРаботуСистемы(Ложь, Ложь)`. Designer-format XML export
  (all-Latin form name `MgrForm`) staged + transferred to Windows `C:\Users\historical-user\TEMP\qa_mgr_src2.tgz`.

## Remaining blockers (both bounded)
1. **`.epf` will not build yet.**
   - Linux `export_rebuild_external_data_processor` fails: the Linux 1cv8 Designer crashes with
     `libgcc_s.so.1: version GCC_12.0.0/GCC_13.0.0 not found (required by libhwy.so.1)` — 1C's bundled libgcc is
     older than what the system `libhwy` needs. (Possible fix: make 1C use the system libgcc, e.g.
     `LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libgcc_s.so.1`, or move 1C's bundled `libgcc_s.so.1` aside.)
   - So build on **Windows Designer** instead (`1cv8 DESIGNER /F<scratch_ib> /LoadExternalDataProcessorOrReportFromFiles
     <xml> <out.epf>`). Fixed: Cyrillic form name → Latin `MgrForm` (Windows `tar` mojibake'd the Cyrillic
     filename). **Still failing:** `Исключение XDTO ... Form.xml` — the hand-authored minimal `Form.form`
     (autoCommandBar + OnOpen handler + main `Объект` attribute) does not produce a valid managed-form XDTO.
   - **Recommended next fix:** seed a valid form instead of hand-authoring — either
     `create_external_data_processor(seed_epf=<a real .epf>)` (e.g. copy a vanessa_client `.epf` to Linux as a
     seed and swap only the form-module BSL), or add the missing form elements (likely `<ChildItems/>` + a
     proper `<Title>`/window props) so the XDTO reader accepts it. Then re-export → rebuild on Windows.
2. **The capture run itself is unproven** — once the `.epf` builds, validate the 3-process run (below). Open
   risk: whether `/TESTMANAGER /Execute <epf>` actually fires the form `ПриОткрытии` (if not, drive the connect
   from a startup that runs without a visible form, or confirm Vanessa's documented `/TESTMANAGER` launch).

## The capture run (once the `.epf` is built → `C:\Users\historical-user\TEMP\qa_xmachine_mgr.epf`)
All on the Windows box (session 1):
1. **Client:** `1cv8 ENTERPRISE /IBConnectionString File="C:\1C_BASES\vanessa_client"; /NАдминистратор
   /TESTCLIENT -TPort 15381 /DisableStartupDialogs /DisableStartupMessages` (use the proven `schtasks /RU historical-user
   /IT` launcher `C:\Users\historical-user\TEMP\qatc_launch.ps1` — keeps it in session 1).
2. **Proxy:** from the Windows qa-mcp checkout `.venv`:
   `python tools/protocol-research/protocol_proxy.py --listen-port 15382 --target-port 15381
   --capture-dir C:\Users\historical-user\TEMP\wincap --ready-file C:\Users\historical-user\TEMP\wincap\ready.json`
   (proxy writes `traffic.jsonl` in the `{event,direction,payload_b64}` format the extractor expects).
3. **Manager:** `1cv8 ENTERPRISE /IBConnectionString File="C:\1C_BASES\vanessa_manager"; /TESTMANAGER
   /Execute C:\Users\historical-user\TEMP\qa_xmachine_mgr.epf /DisableStartupDialogs /DisableStartupMessages`
   (vanessa_manager = no user/no pw). It connects to `127.0.0.1:15382` → proxy → client, reads, logs, exits.
4. Check `C:\Users\historical-user\TEMP\qa_mgr.log` (expect `connected` / `child_objects=N` / `done_ok`) and that
   `wincap\traffic.jsonl` recorded a rich handshake (client frame-1 reply ~210 B, like the Linux genuine
   capture — NOT the 4-byte `66 53 b2 a6` + EOF the synth got).

## Extract + integrate
- Copy `traffic.jsonl` to Linux. Diff its manager frames 1..N + the client responses against the bundled
  Linux genuine capture `src/qa_mcp/_bundled/8.3/captures/tm-v1-ro-batchQ3/traffic.jsonl` — the divergence at
  frame 3 (Windows reset point) is the field(s) to fix.
- Run `tools/protocol-research/extract_manager_templates.py` on the Windows capture → Windows
  `manager_frame_templates.json` + a Windows `bootstrap_frames_1to3.json`.
- Add a **platform key** beside the version keys: bundle under e.g. `src/qa_mcp/_bundled/windows/…` (or
  `8.3-windows/`), and make the bootstrap/template selection platform-aware (mirror `active_version_key()` /
  `bootstrap_synth.SYNTH_TEMPLATE_VERSION` injection — but on the OS axis). The remote-client mode (task #2's
  original scope) selects the windows bundle when driving a Windows client.
- **Verify:** re-run the 3 `ui` checks cross-machine
  (`scratchpad/xmachine_smoke.py` equivalent, `host=192.0.2.202 port=15381`) → expect GREEN.

## Lab artifacts currently on the Windows box (kept for continuation)
- `C:\Users\historical-user\TEMP\qa_mgr_src2.tgz` (all-Latin Designer XML export of the manager), `…\qa_mgr_xml2\` (extracted),
  `…\scratch_ib\` (scratch infobase for the Designer build), `…\qatc_launch.ps1` (client launcher),
  `designer_build2.log`. Firewall rule `qa-mcp TestClient 15381` is in place. No 1cv8 left running.
- EDT project on Linux: `/opt/ai-dev-suite-for-1c/edt-mcp/.workspaces/infobases/qa_xmachine_mgr` (edit
  `…/Forms/Форма/Module.bsl` + `Form.form`, re-export, rebuild on Windows).

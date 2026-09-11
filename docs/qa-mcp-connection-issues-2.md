# QA-MCP connection issues report

Date: 2026-07-07  
Environment: Windows host, Docker container `qa-mcp`, 1C platform `8.3.27.2130`  
Target infobase: `File="C:\Users\User\Documents\private-lab-infobase"`

## Summary

The QA-MCP container itself was running and healthy, and the final connection to the Windows 1C test client succeeded. However, the connection check exposed several integration and diagnostics issues that made the setup harder to verify and could cause false negative failures.

Update 2026-07-07: qa-mcp now includes `qa_mcp_doctor` (MCP tool) and
`qa-mcp-doctor` (CLI). The doctor returns one secret-safe pass/fail/skipped
chain for bearer-token env presence, host-agent HTTP reachability,
container-to-host route, platform discovery, TestClient TPort reachability, an
open-link-free TestClient smoke, login/access-dialog evidence, effective-user
evidence when available, and the COMConnector doctor when configured.

Final known-good state:

- Docker container `qa-mcp`: running, healthy.
- MCP endpoint: `http://127.0.0.1:8000/mcp`.
- MCP server responded successfully as `qa-native-manager 1.28.1`.
- Windows host-agent responded on `http://127.0.0.1:8001/health`.
- 1C Windows client was launched manually with `/TESTCLIENT -TPort 15381`.
- QA-MCP successfully attached to `host.docker.internal:15381`.

## Problems encountered

### 1. MCP tools were not exposed directly in Codex tool list

The configured MCP server existed in `codex mcp list`:

```text
qa-mcp  http://127.0.0.1:8000/mcp  enabled  Bearer token
```

But the current Codex session did not expose callable `qa-mcp` tools as native tools. I had to call the MCP endpoint manually through JSON-RPC over HTTP.

Impact:

- The server can be configured and healthy, but still not practically usable from the assistant tool surface.
- Diagnostics become manual and error-prone.

Suggested fix:

- Ensure streamable HTTP MCP servers configured in Codex are loaded into the active tool registry.
- If loading fails, surface a clear tool-loading error in the UI/session instead of silently omitting the tools.

### 2. Bearer token was not visible in the current process environment

The QA-MCP configuration uses:

```text
bearer_token_env_var: QA_MCP_BEARER_TOKEN
```

The token existed in the Windows user environment and matched the container's
project-owned `QA_MCP_BEARER_TOKEN`. However, in the normal shell process
environment, `$env:QA_MCP_BEARER_TOKEN` was absent.

This caused manual MCP requests to fail with:

```json
{"error": "unauthorized"}
```

When the request was rerun outside the sandbox and the Windows user environment was read explicitly, the same endpoint returned `200 OK`.

Impact:

- A valid configured MCP server can appear unauthorized if Codex or its subprocesses do not inherit the user environment.
- The error message does not distinguish between "bad token" and "token env var missing in current process".

Suggested fix:

- Codex should either read `bearer_token_env_var` from the same environment scope where it was configured, or clearly report that the variable is missing from the active process.
- Improve the authorization error to include a non-secret diagnostic such as `token_env_present=false`.

### 3. `launch_test_client` cannot launch a client in `remote-client` mode

Calling `launch_test_client` returned:

```json
{
  "ok": false,
  "error": "local-boot-disabled-remote-client",
  "mode": "remote-client"
}
```

The message explains that in model-B remote-client mode the 1C client must be started on the Windows host manually:

```text
1cv8 ENTERPRISE /TESTCLIENT -TPort <port>
```

Impact:

- The tool name suggests it will launch the client, but in this mode it cannot.
- Users may treat this as a connection failure even though it is a mode limitation.

Suggested fix:

- Rename or split behavior in remote-client mode, or return a stronger actionable hint with the exact Windows command that should be run.
- Consider adding a host-agent mediated launch path for Windows clients, since the host-agent is already present and has platform path information.

### 4. `host-agent` health reports missing `ai-com-worker.exe`

The host-agent itself was running and `/health` returned `ok: true`, but the health payload included:

```json
"com_worker": {
  "available": false,
  "error": "com-worker-not-found",
  "path": "C:\\Users\\User\\AppData\\Local\\qa-mcp-host-agent\\ai-com-worker.exe"
}
```

Impact:

- It is unclear whether this missing component is optional or required for specific QA-MCP features.
- The agent reports `ok: true`, while one named subsystem is missing.

Suggested fix:

- Document whether `ai-com-worker.exe` is optional.
- If optional, classify it as a warning with feature impact.
- If required for common flows, make the installation check fail earlier or include remediation steps.

### 5. Port checks were confusing because host-agent listens on IPv6 wildcard

The host-agent log showed:

```text
listening on [::]:8001
```

Initial `Get-NetTCPConnection -LocalPort 8001 -State Listen` checks did not reliably show the listener in the constrained environment, which made it look like port `8001` was not listening.

Direct HTTP checks later proved the agent was reachable on both:

```text
http://127.0.0.1:8001/health
http://[::1]:8001/health
```

Impact:

- Port-level diagnostics may produce false negatives.
- Users may investigate firewall or Docker networking unnecessarily.

Suggested fix:

- Provide an official `qa-mcp doctor` command or health endpoint check that validates actual HTTP reachability instead of relying on raw port enumeration.

### 6. Container-to-host route worked, but required manual verification

The container had:

```text
QA_MCP_HOST_AGENT=host.docker.internal:8001
QA_MCP_CLIENT_HOST=host.docker.internal
QA_MCP_CLIENT_PORT=15381
```

The route from container to Windows host-agent worked when manually tested:

```text
http://host.docker.internal:8001/health -> 200
```

Impact:

- This is a critical dependency but not clearly summarized by the MCP server until tools are invoked.

Suggested fix:

- Include container-to-host-agent connectivity in an MCP health or diagnostics tool.
- Expose a single command/result showing:
  - MCP proxy auth status.
  - Host-agent reachability.
  - 1C platform discovery.
  - Test-client reachability.

### 7. `get_window_list_testclient` required `open_link`

After successful attachment, calling `get_window_list_testclient` failed with:

```json
{
  "ok": false,
  "error": "open-link-required",
  "detail": "cannot infer current ManagedForm GUID; pass open_link"
}
```

Impact:

- This looks like a failure after connection, but it is actually a missing operation parameter.
- The tool name implies it can list current windows, but it cannot infer the current managed form in this state.

Suggested fix:

- Clarify the tool description and error wording.
- If possible, provide a separate low-level connection smoke test that does not require `open_link`.
- Add an example `open_link`, such as `e1cib/list/<metadata>`, to the tool schema description.

## Successful manual connection sequence

The following sequence eventually worked:

1. Confirm container was running:

   ```text
   qa-mcp: Up, healthy, 127.0.0.1:8000->8080/tcp
   ```

2. Confirm MCP endpoint with bearer token:

   ```json
   {
     "serverInfo": {
       "name": "qa-native-manager",
       "version": "1.28.1"
     }
   }
   ```

3. Confirm infobase info:

   ```json
   {
     "target": "File=\"C:\\Users\\User\\Documents\\private-lab-infobase\"",
     "user": "Администратор",
     "client_bin": "/opt/1cv8/x86_64/8.3.27.2130/1cv8"
   }
   ```

4. Start Windows 1C manually:

   ```text
   "C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe" ENTERPRISE /F"C:\Users\User\Documents\private-lab-infobase" /N"Администратор" /TESTCLIENT -TPort 15381
   ```

5. Attach QA-MCP:

   ```json
   {
     "attached": true,
     "listening": true,
     "host": "host.docker.internal",
     "port": 15381
   }
   ```

## Additional issues found while reading `Справочник.Валюты`

After the basic connection was confirmed, we tried to use QA-MCP to open and read the currency catalog in the same file infobase:

```text
File="C:\Users\User\Documents\private-lab-infobase"
```

Target navigation link:

```text
e1cib/list/Справочник.Валюты
```

### 8. Wrong user caused the 1C client to stop at the access dialog

The first test-client launches used user `Администратор`. The 1C client opened the "Доступ к информационной базе" dialog and did not reach the application workspace.

Correct credentials for this infobase were:

```text
User: Админ
Password: empty
```

The working launch command was:

```text
"C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe" ENTERPRISE /F"C:\Users\User\Documents\private-lab-infobase" /N"Админ" /P"" /TESTCLIENT -TPort 15383
```

Impact:

- QA-MCP attach checks can fail or hang at a higher level if the Windows client is waiting on the login dialog.
- The QA-MCP `attach_test_client` result later reported user `Администратор` even though the client had been launched with `Админ`, which can confuse diagnostics.

Suggested fix:

- Include the effective infobase user in test-client status if it can be queried.
- Detect login/access dialogs as a separate diagnostic state.

### 9. Cyrillic navigation link was corrupted without explicit UTF-8 request body

The first manual JSON-RPC call to `read_list_grid` used PowerShell defaults. The intended link:

```text
e1cib/list/Справочник.Валюты
```

arrived at QA-MCP / 1C as:

```text
e1cib/list/??????????.??????
```

1C then displayed:

```text
Не удалось перейти по навигационной ссылке
```

When the JSON body was sent as UTF-8 bytes with `Content-Type: application/json; charset=utf-8`, the same link was accepted. QA-MCP then resolved the form:

```json
{
  "opened": "Валюты",
  "available_tables": ["Валюты"]
}
```

Impact:

- This produces a false impression that the navigation link itself is invalid.
- The failure is especially easy to hit from PowerShell-based diagnostics on Windows.

Suggested fix:

- Ensure QA-MCP diagnostics/examples force UTF-8 for JSON-RPC bodies.
- Consider rejecting non-UTF-8 request bodies with a clear error instead of forwarding corrupted text.
- Add a link echo/validation diagnostic that shows the exact received `open_link`.

### 10. `read_list_grid` opened the form but returned `row_count: 0`

After the UTF-8 issue was fixed, `read_list_grid` successfully opened the currency catalog and identified the table:

```json
{
  "table": "Валюты",
  "nav_link": "e1cib/list/Справочник.Валюты",
  "table_resolution": {
    "source": "descriptor",
    "opened": "Валюты",
    "available_tables": ["Валюты"]
  }
}
```

However, the tool returned:

```json
{
  "row_count": 0,
  "rows": []
}
```

with this diagnostic:

```json
{
  "error": "window-not-found",
  "tool": "force_list_refresh",
  "detail": "target window not found",
  "mode": "remote-client",
  "status": 422
}
```

Running with `refresh=false` still returned `0` and reported a similar `cold_state_sweep` failure.

Impact:

- `row_count: 0` is ambiguous. It can mean either an empty list or a failure to refresh/read the live list.
- In this case, the list was not empty; the UI showed one visible currency row.
- The tool result includes the warning, but callers may still consume `row_count: 0` as factual data.

Suggested fix:

- Do not return a normal-looking `row_count: 0` when refresh/sweep fails.
- Add an explicit top-level status such as `ok: false` or `data_confidence: "unknown"` for this case.
- Provide a remote-client compatible list-read path that does not depend on locating the host window by display/window handle.

### 11. Remote-client window discovery does not match the visible Windows 1C window

QA-MCP could attach to the test client on `host.docker.internal:15383`:

```json
{
  "attached": true,
  "listening": true
}
```

It could also resolve the opened managed form descriptor. But refresh/sweep failed with `window-not-found`.

Manual Windows UI Automation showed that the real visible top-level 1C window existed:

```text
Class: V8TopLevelFrameSDI
Title: Бухгалтерия предприятия, редакция 3.0
Form: Валюты
```

Impact:

- Protocol-level attachment and form descriptor access work, while window-level refresh/read fails.
- This split makes the problem difficult to diagnose from the QA-MCP response alone.

Suggested fix:

- In remote-client mode, surface the exact window identity being searched for.
- Add a diagnostic that lists discovered Windows-side 1C windows, handles, classes, and process IDs.
- Avoid returning table data unless the tool can confirm it read from the intended live window/form.

### 12. UI Automation confirmed one visible currency row

Because `read_list_grid` returned an ambiguous `0`, the visible 1C window was inspected via Windows UI Automation. It showed the opened `Валюты` form and one visible row:

```text
Российский рубль
643
руб.
1
```

The UIA custom cells found were:

```json
[
  "Российский рубль Наименование валюты",
  "643 Цифр. код",
  "руб. Симв. код",
  "1 Курс",
  "Кратность"
]
```

Impact:

- QA-MCP list reading reported no rows, while the actual UI had at least one row.
- This confirms the problem is not the navigation link and not an empty catalog.

Suggested fix:

- Add an official fallback/debug tool for reading visible list cells through the Windows host-agent/UIA bridge.
- Include screenshot or UIA evidence in diagnostics when list-read returns `0` after refresh failure.

### 13. COMConnector fallback was blocked by missing TypeLib registration

Status update: resolved locally after elevated 64-bit registration.

As a fallback, a read-only 1C query was attempted through `V83.COMConnector`:

```1c
ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК Количество
ИЗ Справочник.Валюты
```

The COM ProgID existed:

```text
V83.COMConnector
```

The COM class pointed to the expected 64-bit platform DLL:

```text
C:\Program Files\1cv8\8.3.27.2130\bin\comcntr.dll
```

But object creation failed with:

```text
Library not registered. (Exception from HRESULT: 0x8002801D / TYPE_E_LIBNOTREGISTERED)
```

The class registration referenced TypeLib:

```text
{98AC3B5B-5323-418F-8F07-E32F231D2393}
```

but this TypeLib key was not present under `HKEY_CLASSES_ROOT\TypeLib`.

Attempts made:

- Verified PowerShell process was 64-bit.
- Ran 64-bit `C:\Windows\System32\regsvr32.exe` against `comcntr.dll`.
- Tried `oleaut32.dll!LoadTypeLibEx(..., REGKIND_REGISTER, ...)`.

These attempts were first run from a non-admin process and the COMConnector error remained.

The successful fix was to run 64-bit `regsvr32.exe` elevated through UAC:

```powershell
Start-Process `
  -FilePath "C:\Windows\System32\regsvr32.exe" `
  -ArgumentList '/s "C:\Program Files\1cv8\8.3.27.2130\bin\comcntr.dll"' `
  -Verb RunAs `
  -Wait
```

After this, the expected TypeLib key appeared:

```text
HKEY_CLASSES_ROOT\TypeLib\{98AC3B5B-5323-418F-8F07-E32F231D2393}\1.0\0\win64
    C:\Program Files\1cv8\8.3.27.2130\bin\comcntr.dll
```

The COMConnector then connected successfully. A read-only query through 64-bit `cscript.exe` returned:

```text
Count=1
```

PowerShell `New-Object -ComObject V83.COMConnector` also created the connector and executed the query after registration, but reading fields from the 1C query result through PowerShell/.NET COM binding still returned `null`. The 64-bit WSH/JScript late-binding path returned the value correctly.

Impact:

- Direct read-only database query fallback was unavailable until COMConnector registration was repaired.
- Non-admin registration attempts can look successful but leave the TypeLib missing.
- PowerShell/.NET COM binding may still be less reliable than WSH late binding for reading 1C query result fields.

Suggested fix:

- Document the exact supported 64-bit COMConnector registration procedure for this environment.
- Add installer/doctor validation for 64-bit `V83.COMConnector`, `InprocServer32`, TypeLib key presence, and a successful test query against a file infobase.
- Explicitly check whether registration was run elevated.
- Include a WSH/JScript late-binding smoke test as a fallback validation path.

### 14. A Designer metadata dump attempt can hang and leave extra 1C processes

An attempt to use Designer mode to dump metadata for resolving the catalog name was started:

```text
DESIGNER /F"C:\Users\User\Documents\private-lab-infobase" /N"Админ" /P"" /DumpConfigToFiles ...
```

The command timed out and left an extra `1cv8.exe DESIGNER ...` process running. It had to be stopped manually.

Impact:

- Metadata-dump diagnostics can leave the infobase in a more confusing state.
- Extra 1C processes make it harder to identify the active test client.

Suggested fix:

- Avoid Designer metadata dump in ordinary connection diagnostics.
- If such a tool is used, add timeout cleanup and clear reporting of spawned process IDs.

### 15. No QA-MCP tool currently exposes COM-based data queries

After fixing the local 64-bit `V83.COMConnector` registration, we checked the full QA-MCP tool list. The server exposed 63 tools.

The data-related tools were:

```text
assert_data
assert_data_count
role_data_matrix
```

However, their schemas are OData-oriented. For example, `assert_data_count` accepts:

```text
base_url, entity_set, expected, filter, op, password, user
```

Calling it for the currency catalog without OData configuration returned:

```text
OData base_url not configured (set QA_MCP_ODATA_URL or pass base_url=)
```

The host-agent health also showed:

```json
{
  "com_worker": {
    "available": false,
    "error": "com-worker-not-found",
    "path": "C:\\Users\\User\\AppData\\Local\\qa-mcp-host-agent\\ai-com-worker.exe"
  }
}
```

At the same time, direct 64-bit COMConnector access from Windows was working after elevated registration. A read-only query via `cscript.exe` returned:

```text
Count=1
```

for:

```1c
ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК Qty
ИЗ Справочник.Валюты
```

Impact:

- QA-MCP has UI/protocol tools and OData data assertion tools, but no currently available tool for COM-based reads from a file infobase.
- For local file infobases without OData publishing, QA-MCP cannot reliably answer simple data questions such as "how many currencies are in `Справочник.Валюты`" through its own tool surface.
- Users must fall back to external scripts even though host-side COMConnector is available.

Suggested fix:

- Add a QA-MCP tool for COM-based read-only queries, for example `query_com` or `assert_com_count`.
- The tool should run on the Windows host side through the host-agent, not inside the Linux container.
- Suggested minimal input schema:

  ```json
  {
    "infobase_path": "C:\\Users\\User\\Documents\\private-lab-infobase",
    "user": "Админ",
    "password": "",
    "query": "ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК Qty ИЗ Справочник.Валюты",
    "timeout_sec": 60
  }
  ```

- Suggested output:

  ```json
  {
    "ok": true,
    "rows": [
      { "Qty": 1 }
    ],
    "transport": "com",
    "platform": "8.3.27.2130",
    "bitness": "x64"
  }
  ```

- Provide a count-specific helper for common checks:

  ```json
  {
    "tool": "assert_com_count",
    "object": "Справочник.Валюты",
    "expected": 1
  }
  ```

- Keep the tool read-only by default and reject queries with obvious write operations unless explicitly enabled.

### 16. QA-MCP should include a Windows 11 x64 COMConnector doctor

The COMConnector issue was caused by incomplete registration from a non-admin process. Before the fix:

- `V83.COMConnector` ProgID existed.
- `InprocServer32` pointed to `C:\Program Files\1cv8\8.3.27.2130\bin\comcntr.dll`.
- The process was 64-bit.
- But `HKEY_CLASSES_ROOT\TypeLib\{98AC3B5B-5323-418F-8F07-E32F231D2393}` was missing.
- Calls failed with `0x8002801D / TYPE_E_LIBNOTREGISTERED`.

The successful fix was elevated 64-bit registration:

```powershell
Start-Process `
  -FilePath "C:\Windows\System32\regsvr32.exe" `
  -ArgumentList '/s "C:\Program Files\1cv8\8.3.27.2130\bin\comcntr.dll"' `
  -Verb RunAs `
  -Wait
```

After that, the TypeLib key appeared under:

```text
HKEY_CLASSES_ROOT\TypeLib\{98AC3B5B-5323-418F-8F07-E32F231D2393}\1.0\0\win64
```

Impact:

- A partial COM registration can look valid because `V83.COMConnector` and `InprocServer32` exist.
- The actual failure only appears when calling methods such as `Connect`.
- Non-admin `regsvr32`/TypeLib registration attempts are misleading.

Suggested fix:

- Add a `com_connector_doctor` diagnostic in QA-MCP or host-agent.
- It should check:
  - process bitness;
  - admin/elevation status;
  - installed 1C platform roots;
  - `V83.COMConnector` ProgID;
  - CLSID;
  - `InprocServer32`;
  - TypeLib GUID;
  - `win64` TypeLib path;
  - a real `CreateObject("V83.COMConnector")`;
  - a real `Connect(...)` to a supplied file infobase;
  - a small read-only query.
- If TypeLib is missing, it should recommend elevated 64-bit registration using `C:\Windows\System32\regsvr32.exe`, not `SysWOW64`.
- The diagnostic should explicitly warn that PowerShell/.NET COM binding may create the connector but still be awkward for reading 1C query result fields; WSH/JScript late binding worked reliably in this test.

## Recommended developer-facing improvements

- Use the delivered single end-to-end diagnostics command/MCP tool:
  `qa-mcp-doctor` / `qa_mcp_doctor`.
- Keep token/env-var diagnostics explicit without exposing secrets.
- Surface MCP tool loading failures in Codex instead of silently hiding the configured server.
- Improve remote-client mode UX: either launch through host-agent or provide a generated host command.
- Distinguish optional and required host-agent components in `/health`.
- Use the `qa_mcp_doctor` `testclient_smoke` link for "MCP connected to test client"
  proof that does not require `open_link`.
- Force UTF-8 in all Windows/PowerShell JSON-RPC examples and diagnostics.
- Make `read_list_grid` fail loudly when refresh/sweep fails instead of returning a plausible `row_count: 0`.
- Add remote-client diagnostics for Windows-side window discovery and UIA-visible list cells.
- Use the delivered COMConnector doctor link for 64-bit 1C registration checks.
- Add a host-side COM data query tool for local file infobases where OData is not configured.
- Add a Windows 11 x64 COMConnector doctor that verifies TypeLib registration and can guide elevated `regsvr32` repair.

## Resolution — 2026-07-08 real-base runtime acceptance

The six hardening cards above were delivered on 2026-07-07 and their runtime
acceptance was executed on 2026-07-08 by driving qa-mcp HEAD against the real
[redacted third-party configuration] file base (User@192.0.2.205, 1С 8.3.27.2130, user `Админ`).

Proven live: `query_com`/`assert_com_count` → `Qty=1` for `Справочник.Валюты`,
`com_connector_doctor` green, the `qa_mcp_doctor` ordered chain (including the
`open_link`-free `testclient_smoke`), the remote `launch_test_client` command,
the `read_list_grid` fail-loud guarantee (never a fabricated `row_count: 0`), and
the host-agent `/uia/visible_list_cells` read against the live `V8TopLevelFrameSDI`
window.

Five diagnostics defects that only manifest on a real Russian-locale Windows host
were fixed under card
`realbase-com-doctor-uia-diagnostics-fixes` (archived
`openspec/changes/archive/2026-07-08-realbase-com-doctor-uia-diagnostics-fixes/`):
classic-JScript `JSON`-object absence, 1C COM `Columns.Count()` method call,
Cyrillic corruption of the cscript stdin payload, the `qa_mcp_doctor` `_com_check`
crash on a probe exception, and the UIA `#< CLIXML` wrapper breaking the
visible-cells parse.

Two follow-up observations remain for separate cards: the host-agent-launched
TestClient does not persist on this host (an interactive launch does), and the
`read_list_grid` positive read is blocked by a capture-replay session handshake
on Бухгалтерия 3.0 over the LAN (protocol-version capture refresh, epic 111
item 4).

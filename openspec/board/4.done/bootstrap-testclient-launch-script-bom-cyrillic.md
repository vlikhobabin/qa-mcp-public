# bootstrap writes launch-testclient.ps1 without BOM → PowerShell 5.1 corrupts the Cyrillic username → TestClient login fails

## Status
4.done

## Owner
qa-mcp (`delivery/bootstrap.ps1`, self-hosted release)

## OpenSpec Stage
finding → single change — **DELIVERED**. (Was release-blocking for Russian bases.)

## Result
✅ **DONE 2026-07-07.** Fixed in `delivery/bootstrap.ps1` (commit `3cb6f00`,
pushed): added `Write-Utf8Bom` (`UTF8Encoding($true)`) and use it for
`launch-testclient.ps1`; token/lease files keep no-BOM. **Re-published signed
v0.3.0** (bootstrap-only change; image/host-agent reused): buggy link
`…5f75994…` retracted (404), new signed link
`https://releases.aifor1c.ru:58443/qa-mcp/r-20260707-5c20aa8a485d4c38df39e1ef/`
(manifest signature verifies). **Re-validated on a REAL base ([redacted third-party configuration]) from
the published release, no manual patch:** `TestClient слушает :15381` → docker
load → license gate ON → MCP 63 tools. See [[qa-mcp-standalone-release-proven]].

## Source
Greenfield install of qa-mcp **v0.3.0** on a clean Windows 11 laptop
(`User@192.0.2.205`, Docker Desktop 29.6.1, 1C 8.3.27.2130), 2026-07-07,
driven over SSH. Every prerequisite was correct (license key, `Администратор`/no
password confirmed working interactively, valid file base) yet the bootstrap
failed at the TestClient step; root-caused to a text-encoding bug.

## Problem
`bootstrap.ps1` generates `launch-testclient.ps1` (the script the
`qa-mcp-testclient` scheduled task runs to `Start-Process 1cv8.exe … /TESTCLIENT`)
and writes it with **`Write-Utf8NoBom`** (`New-Object System.Text.UTF8Encoding($false)`
→ UTF-8 **without** a BOM). That script embeds the 1C username in `/N$User`, whose
default is Cyrillic **`Администратор`**.

Windows **PowerShell 5.1** (the default on Windows 10/11) reads a BOM-less `.ps1`
as the **ANSI/OEM code page (CP1251 on Russian Windows)**, not UTF-8. So when the
scheduled task runs `powershell -File launch-testclient.ps1`, the UTF-8 Cyrillic
bytes of `Администратор` are mis-decoded → the `/N` argument becomes mojibake →
`1cv8.exe /TESTCLIENT` cannot authenticate → the client exits → never binds the
TestClient TCP port → bootstrap reports
`TestClient так и не начал слушать TPort 15381` and aborts (before docker load /
license activation / container start).

By contrast `bootstrap.ps1` itself HAS a UTF-8 BOM (`ef bb bf`), so PowerShell
reads its `-User "Администратор"` default correctly; the corruption happens only
when the BOM-less generated launch script is re-read by PowerShell.

This breaks the install for **any tester whose 1C base uses a Cyrillic username**
— i.e. essentially every Russian 1C infobase (the default `Администратор`).

## Evidence
- Reproduced the decode: a UTF-8-no-BOM `.ps1` containing `'Администратор'`, run
  via `powershell -File`, mangled the string (mojibake + a `ParserError:
  UnexpectedToken`).
- The exact same 1C launch args passed as a proper **argument array** with the
  username built from **codepoints** in an ASCII `.ps1` → TestClient logged into
  the base and bound TPort 15381 within ~45s.
- **Fix proven live:** patched the local `bootstrap.ps1` so `launch-testclient.ps1`
  is written **with a UTF-8 BOM**
  (`[IO.File]::WriteAllText($LaunchScriptPath,$launch,(New-Object System.Text.UTF8Encoding($true)))`).
  Re-ran → `TestClient слушает :15381` → docker load v0.3.0 → license activated
  (gate ON) → container healthy → MCP `qa-native-manager` serves **63 tools** →
  `infobase_info` returns the live TestClient connection (user `Администратор`).

## Scope / Fix
- Write `launch-testclient.ps1` with a **UTF-8 BOM** (or UTF-16LE), OR construct
  the `/N` username from char codepoints so the launch script stays ASCII-safe.
  `Write-Utf8NoBom` is correct for token/lease files that are read as raw bytes,
  but NOT for a `.ps1` that PowerShell 5.1 re-executes with non-ASCII content.
- Audit any other bootstrap-generated `.ps1`/scripts containing non-ASCII that
  get run by `powershell -File` under 5.1.

## Acceptance
- Fresh `bootstrap.ps1 -Infobase <file base> -User Администратор` on a Russian
  Windows + PowerShell 5.1 host reaches `TestClient слушает :<port>` and completes
  (image load → license → container → MCP tools/list ≈63) with no manual patch.
- Regression: Latin usernames still work.

## Related
- Greenfield on `User@192.0.2.205` (Win11, PS 5.1), 2026-07-07.
- v0.3.0 release `r-20260707-5f75994ae1198564c2fce6361af0bce0` — **published
  bootstrap still has this bug**; do not distribute to Russian-base testers until
  fixed + re-published (the greenfield answers the "ship now vs test first"
  question: it needed this fix).

## Log
- 2026-07-07 found + root-caused + fixed-by-local-patch during the .205 greenfield;
  filed for a proper fix in the published bootstrap.

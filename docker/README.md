# qa-mcp — Docker delivery

Run the native 1C TestClient QA manager as an MCP server in a container, and point your AI Agent at it over
HTTP. Designed for **minimum setup**: your only inputs are the **path to the test infobase** and the **1C
platform version**.

## Two delivery models

| | **Model A — all-in-container** | **Model B — thin cross-machine** (card 119) |
| --- | --- | --- |
| 1C TestClient runs | INSIDE the container (Xvfb) | on **your host** (your installed, licensed 1C) |
| Image carries | MCP + X11 toolchain + 1C thick-client libs (~1.4 GB) | MCP only (Python) — **no 1C libs, no X11** (~260 MB) |
| You provide | a **Linux** 1C platform + infobase + **Linux license** (mounted) | nothing — the host already has a licensed 1C |
| Tool surface | full (incl. XTEST writes + screenshots) | **protocol surface** by default; display/XTEST/screenshot tools are recovered when the Windows host agent is installed |
| Best for | a **Linux** host | a **Windows** host (Docker Desktop) |

Model A is documented in the rest of this file. **On Windows, use Model B** (next section): it sidesteps
model A's two hard parts on Windows — there is no Linux-1C build to run in the container, and the Windows
license/identity does not carry into a Linux container.

### Supported platform baselines and version identity

The shipped runtime is release-verified with **8.3.27.2130** and
**8.5.1.1343**. Pass the complete live `x.y.z.w` version through
`QA_MCP_PLATFORM_VERSION` in model B or select the versioned binary through
`PLATFORM_ROOT` in model A. That full live version is what synthesized and
replayed TestManager frames declare; it is distinct from the bundled
protocol-data family selected internally.

The 8.5 baseline currently follows the validate-first policy: it keeps the
live identity `8.5.1.1343` while capture-backed operations reuse the validated
8.3 protocol-data set. Do not pre-populate `_bundled/8.5` merely because the
platform family changed. Add or recapture 8.5 protocol data only if a bounded
live validation exposes a red capability. Other builds in either supported
family may work, but require their own validate-first evidence before they are
declared supported.

## Model B — public standalone cross-machine (Windows)  ← recommended on Windows

The 1C TestClient runs on your Windows host (where it is already installed and licensed); a thin Python-only
container connects to it over TCP and serves MCP over HTTP. PROVEN end-to-end (card 119): Docker Desktop's
`host.docker.internal` reaches the client as a **loopback-origin** peer, so the genuine protocol bootstrap
drives a Windows-built client with **no protocol change** (evidence:
`docs/protocol-research/evidence/card119-windows-xmachine-2026-06-26/docker-on-windows-SOLVED.md`).

**1. Launch the TestClient on the host** (interactive session; pick any free `-TPort`):

```bat
"C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe" ENTERPRISE ^
  /IBConnectionString File="C:\1C_BASES\your_base"; /NАдминистратор ^
  /TESTCLIENT -TPort 15381 /DisableStartupDialogs /DisableStartupMessages
```

- It must run in your **interactive desktop session** — a launch from a service / SSH / session 0 binds the
  port then the client dies. Over a remote shell, wrap it in a `schtasks /RU <you> /IT` run-once task so it
  lands in your logged-on session.
- **Open the inbound TPort in the firewall:** `New-NetFirewallRule -DisplayName "qa-mcp TestClient 15381"
  -Direction Inbound -LocalPort 15381 -Protocol TCP -Action Allow`.

**2. Build + run the standalone container:**

```bash
docker build -f docker/Dockerfile.thin \
  --build-arg SOURCE_COMMIT="$(git rev-parse HEAD)" \
  -t qa-mcp-standalone .
export QA_MCP_BEARER_TOKEN="$(openssl rand -hex 32)"
docker run --rm -p 127.0.0.1:8000:8080 \
  -e QA_MCP_BEARER_TOKEN="$QA_MCP_BEARER_TOKEN" \
  -e QA_MCP_CLIENT_PORT=15381 -e QA_MCP_PLATFORM_VERSION=8.3.27.2130 \
  qa-mcp-standalone
# or:  docker compose -f docker/docker-compose.thin.yml up --build
```

Set `QA_MCP_PLATFORM_VERSION` to the version your host TestClient runs and `QA_MCP_CLIENT_PORT` to its `-TPort`.
The Dockerfile starts from a public uv/Python image pinned by digest. The build
installs dependencies from `uv.lock` with hash checking; source-only rebuilds
reuse that dependency layer. A reviewed public digest override may be supplied
as `PUBLIC_BASE_IMAGE`; mutable or private release inputs are not used.

**2b. Optional but required for screenshots / real OS input: install the Windows host agent.**

Build the agent once from the repo:

```bash
cd host-agent/windows-display-agent
GOOS=windows GOARCH=amd64 go build -o qa-mcp-host-agent.exe .
```

Run the installer on the Windows host in your interactive session:

```powershell
powershell -ExecutionPolicy Bypass -File .\host-agent\install-windows-host-agent.ps1 `
  -Port 8001 -BindAddress 0.0.0.0 -RemoteAddress 192.168.65.0/24
$agentToken = Get-Content -Raw "$env:LOCALAPPDATA\qa-mcp-host-agent\qa-mcp-host-agent.token"
```

The installer defaults to loopback. The `0.0.0.0` bind is only for Docker
Desktop model-B routing and must stay firewall-scoped with `-RemoteAddress`.
The scheduled task reads the shared token from the token file rather than a
process command-line argument.

Then pass the host-agent endpoint and token into the thin container:

```bash
docker run --rm -p 127.0.0.1:8000:8080 \
  -e QA_MCP_BEARER_TOKEN="$QA_MCP_BEARER_TOKEN" \
  -e QA_MCP_CLIENT_PORT=15381 -e QA_MCP_PLATFORM_VERSION=8.3.27.2130 \
  -e QA_MCP_HOST_AGENT=host.docker.internal:8001 \
  -e QA_MCP_HOST_AGENT_TOKEN="<token-from-token-file>" \
  -e QA_MCP_HOST_AGENT_EXPECTED_SHA256="<agent-sha256>" \
  qa-mcp-standalone
```

The host agent serves `GET /version`, `GET /health`, `/send_keys`, `/type`, `/click`, `/screenshot` and
`/window_list`. qa-mcp checks the version/hash before remote display calls. If the agent is absent or mismatched,
the tool returns a fail-closed diagnostic with the exact install/update command; v1 never auto-replaces the binary.
On Windows, host-agent `F5` and `Escape` requests are targeted to the resolved 1C window without requiring
`SetForegroundWindow`; other keyboard/text/mouse primitives still require real foreground and report structured
`foreground-denied` if the desktop foreground lock refuses activation.

Quick host-side verification:

```powershell
$agentToken = Get-Content -Raw "$env:LOCALAPPDATA\qa-mcp-host-agent\qa-mcp-host-agent.token"
Invoke-RestMethod http://127.0.0.1:8001/version -Headers @{ "X-QA-MCP-Agent-Token" = $agentToken }
Invoke-RestMethod http://127.0.0.1:8001/health -Headers @{ "X-QA-MCP-Agent-Token" = $agentToken }
```

**3. Point your Agent at it** — use **`127.0.0.1`, not `localhost`**:

```json
{ "mcpServers": { "qa-mcp": { "type": "http", "url": "http://127.0.0.1:8000/mcp", "headers": { "Authorization": "Bearer <QA_MCP_BEARER_TOKEN>" } } } }
```

> On Windows `localhost` resolves to IPv6 `::1` first, but `-p …:8000` publishes IPv4 → the MCP handshake
> fails with *"Server disconnected without sending a response"*. Use `127.0.0.1` and the exact `/mcp` path
> without a trailing slash.

The tools then default to `host=host.docker.internal`, `port=$QA_MCP_CLIENT_PORT`, so the Agent can call
`read_form_descriptor`, `run_scenario`, `assert_form_value`, `set_table_cell`, … with no host/port. Without
`QA_MCP_HOST_AGENT`, display tools (`capture_screenshot`, `get_window_list`, `write_form_value_xtest`,
`send_keys`, `write_form_fields_by_label`, `set_table_date_cell`, `open_external_processor`) return a clear
install/configuration diagnostic. With the host agent configured, those display primitives are routed to the
Windows interactive session. `launch_test_client`/`stop_test_client` remain local-boot tools and stay disabled in
remote-client mode. On a **Linux** Docker host, add `--add-host=host.docker.internal:host-gateway` (Docker Desktop
adds it automatically).

---

The remainder of this document covers **Model A** (all-in-container, Linux host).

## What's in the image (and what isn't)

| In the image | Provided by you at runtime (mounted) |
| --- | --- |
| The Python MCP (TestManager) + bundled protocol captures/templates (self-contained) | The **1C platform for Linux** (proprietary — not redistributable) → `/opt/1cv8` |
| The X11 toolchain it drives: Xvfb, xdotool, ImageMagick, scrot | The **test infobase** (file `.1CD`) → `/infobase` |
| The 1C thick-client shared libraries | A **1C license** for Linux (software license or network HASP) |

The MCP launches a `1cv8 /TESTCLIENT` headless under Xvfb *inside the container* and drives it over the
native protocol — so the platform, infobase and MCP are all co-located in one container (no Windows/Linux
GUI bridging). The genuine handshake captures the engine replays travel **inside the package**, so the image
needs no research tree.

## Prerequisites (one-time)

1. **Docker** (Docker Desktop on Windows).
2. **1C platform for Linux**, matching the version your infobase expects. Download the Linux distributive
   from `releases.1c.ru`, install/extract it, and note the dir that contains `x86_64/<version>/1cv8`. You'll
   mount that root to `/opt/1cv8`, so `/opt/1cv8/x86_64/<version>/1cv8` exists in the container.
3. **A Linux 1C license reachable in the container** — see Licensing below. This is the one real operational
   gotcha; the rest is plug-and-play.

## Free qa-mcp startup and open runtime assets

qa-mcp has no product-license gate. The image does not ship or invoke a
product-license broker and requires no qa-mcp entitlement, activation, lease,
product key, or license server. This is separate from the 1C platform license
described below.

The normal package ships readable Python modules and reviewed plaintext bundled
protocol assets. The standalone and downstream-consumer contracts use this one
public artifact; no runtime data key or alternate cloud-only image is required.

## Licensing (read this)

A 1C **soft license is bound to host identity** (OS user, `/etc/machine-id`, network), so a naive
mounted-platform container is rejected with *«Не найдена лицензия»*. The fix depends on the host OS:

- **Linux host (recommended) — reuse the host's installed, licensed platform.** Run the container
  *transparent* to the host identity: shared `--network host --uts host --ipc host`, bind-mount
  `/etc/machine-id` and your `~/.1cv8` (read-write — 1C writes session state there), and run as your own
  user (`--user $(id -u):$(id -g)`). Then the host's license validates inside the container exactly as on the
  host. The ready-made `docker/run-host-platform.sh` encodes all of this. **Verified end-to-end:** an Agent
  over HTTP calls `launch_test_client` → the real `1cv8 /TESTCLIENT` starts licensed and listening → tools
  read live form windows. The platform is mounted (`/opt/1cv8`), not baked into the image.
- **Windows host, or no host platform — network license / HASP.** A Windows-installed 1C is a Windows build a
  Linux container can't run, and the identity doesn't carry through the Docker VM. Point the container at a
  **1C license server / HASP** over the network (the client takes its license from the server), or activate a
  soft license *inside* the container against a pinned identity.

The image installs `iproute2` so the client can read network parameters (without `/sbin/ip` it fails to start
regardless of the license).

## Use the image

### A. Load a distributed image (Google/Yandex Disk link)

The image is shipped as a file. After downloading `qa-mcp.tar.gz`:

```bash
docker load -i qa-mcp.tar.gz        # registers image `qa-mcp:latest`
```

(Producer side: `docker build -t qa-mcp . && docker save qa-mcp:latest | gzip > qa-mcp.tar.gz`.)

### B. Run (Linux host — recommended, uses the host's licensed platform)

```bash
PLATFORM_ROOT=/opt/1cv8/x86_64/8.3.27.2130 \
INFOBASE_DIR=/path/to/your/infobase \
  docker/run-host-platform.sh
```

This is the **verified** path: the script runs the container transparent to the host identity so your
installed, **licensed** 1C platform is reused (see Licensing). `PLATFORM_DIR` defaults to `/opt/1cv8` and
`ONEC_HOME` to `~/.1cv8`; override if yours differ. The MCP binds host loopback by default and is then on
`http://127.0.0.1:8000/mcp`. To expose it beyond loopback, set
`QA_MCP_HTTP_HOST=<address>` and a strong `QA_MCP_BEARER_TOKEN`; the former
unsafe-bind flag cannot bypass authentication.

### B′. Run (manual / Windows host — network license)

```bash
docker run --rm -p 127.0.0.1:8000:8000 \
  -v /path/to/1c-linux:/opt/1cv8:ro \
  -v /path/to/your/infobase:/infobase \
  -e QA_MCP_HTTP_HOST=0.0.0.0 \
  -e QA_MCP_BEARER_TOKEN="<generated-secret>" \
  -e PLATFORM_ROOT=/opt/1cv8/x86_64/8.3.27.2130 \
  qa-mcp:latest
```

On Windows (Docker Desktop) use Windows paths for the mounts and license via a network server (see Licensing), and
use the manual bridge-mode command above. On a Linux host, Compose is the safer shortcut: set `PLATFORM_DIR`,
`INFOBASE_DIR`, `PLATFORM_ROOT` in `docker/.env`, then `docker compose -f docker/docker-compose.yml up`. The compose
file uses host networking for model A and binds the MCP to `127.0.0.1` by
default. A non-loopback bind requires `QA_MCP_BEARER_TOKEN` and unauthenticated
requests are rejected before tool dispatch.

### C. Point your Agent at it

Add `docker/mcp.json.example` to your Agent's MCP config (the tools then appear over HTTP):

```json
{ "mcpServers": { "qa-mcp": { "type": "http", "url": "http://127.0.0.1:8000/mcp" } } }
```

The Agent passes the infobase target per tool call (or relies on the container's `INFOBASE_PATH` /
`PLATFORM_ROOT` defaults).

## Configuration (env vars)

| Var | Default | Meaning |
| --- | --- | --- |
| `PLATFORM_ROOT` | `/opt/1cv8/current` | Versioned platform dir holding `1cv8` (= the platform version) |
| `QA_MCP_PLATFORM_VERSION` | inferred from `PLATFORM_ROOT` | Explicit full live `x.y.z.w` version; required in model B and must match the host TestClient |
| `INFOBASE_PATH` | `/infobase` | File infobase directory (`File="…";`) |
| `CONNECTION_STRING` | — | Full IBConnectionString instead of `INFOBASE_PATH` (e.g. a server infobase) |
| `TEST_CLIENT_USER` / `TEST_CLIENT_PASSWORD` | `Администратор` / empty | Infobase credentials |
| `QA_MCP_HTTP_PORT` | `8000` | HTTP port (also publish it with `-p`) |
| `QA_MCP_HTTP_HOST` | `127.0.0.1` | HTTP bind address; non-loopback values require `QA_MCP_BEARER_TOKEN` |
| `QA_MCP_BEARER_TOKEN` | empty | Project-owned Bearer secret for `/mcp`; mandatory for non-loopback serving |
| `QA_MCP_TRANSPORT` | `http` | `http` (streamable-http) \| `sse` \| `stdio` |
| `QA_MCP_HOME` | `/work` | Writable dir for lifecycle logs + screenshots (mount to keep them) |

## Troubleshooting

- **`1cv8: error while loading shared libraries: … not found`** — the mounted platform build needs a lib the
  image lacks. Find it and add it to the `Dockerfile` apt list:
  `docker run --rm -v /path/to/1c-linux:/opt/1cv8 qa-mcp ldd /opt/1cv8/x86_64/<ver>/1cv8 | grep 'not found'`.
- **TestClient won't start / license error** — confirm a Linux 1C license is reachable (see prerequisite 3).
- **No screenshots** — launch the TestClient with an owned display (`display=":101"`) so `capture_screenshot`
  has an X server; the default headless `xvfb-run` path runs protocol actions without a persistent display.
- **Cyrillic shows as boxes / wrong fonts** — the image installs MS core fonts (msttcorefonts) +
  DejaVu/Liberation. 1C registers TrueType fonts into ImageMagick via its `config_system` step; if form/report
  rendering looks wrong, run the platform's `config_system` once against the mounted install, or relax
  `/etc/ImageMagick-6/policy.xml` (the Debian default restricts some operations 1C uses).
- **WebKit / form rendering** — the image ships `libwebkit2gtk-4.0-37` (the 4.0 API 1C needs). Debian 12 is
  the last base that provides it; don't rebase onto Debian 13 / Ubuntu 24.04 without confirming your platform
  build accepts WebKit 4.1.

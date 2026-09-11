# Card 119 — Docker-on-Windows SOLVED — 2026-06-26 (session 2)

**Result: qa-mcp runs in a Docker container on Windows and drives the host's Windows-built 1C TestClient
end-to-end — with NO protocol change, NO Windows handshake capture, NO networking workaround.**

This **overturns** session-1's "protocol blocked / needs a genuine Windows handshake capture" conclusion
(`findings.md`). That was a **cross-machine-LAN transport artifact**, not a protocol/OS difference. The
operator's standing thesis — *"the protocol already worked on Windows; the blocker is the Docker setup of
already-working code"* — is **confirmed**.

Lab: `historical-user@192.0.2.202` (Windows 10.0.26200, Docker Desktop 27.5.1 / WSL2). Client base
`C:\1C_BASES\vanessa_client` @ 8.3.27.2130. qa-mcp = a fresh `origin/main` clone at `C:\Users\historical-user\TEMP\qa-cur`.

## The single root cause (why session 1 saw a "protocol block")

The 1C TestClient answers manager **frame 1** differently by the **peer address of the connection**:

| Connection to `/TESTCLIENT -TPort 15381` | frame-1 reply | handshake |
| --- | --- | --- |
| **remote peer** (another machine over the LAN — session 1's Linux→Windows test) | `66 53 b2 a6` (4 B) + EOF | refused |
| **loopback-origin peer** (127.0.0.1, OR Docker Desktop `host.docker.internal`) | **210 B JSON** `{1,1636…` | full |

`66 53 b2 a6` is a real protocol marker (the 4-byte tail of genuine client frame [8]); the client emits it as a
short "not a local peer" brush-off and closes. Over a loopback-origin connection it instead inlines the full
210-byte handshake and the whole bootstrap (frames 1..10) completes. **The bytes qa-mcp sends are identical in
both cases** — only the peer address differs. Session 1's test was the one case the client rejects (a genuinely
remote machine). Docker Desktop's `host.docker.internal` does **not** hit that case: its backend originates the
forwarded connection **from the Windows host itself**, so the client sees a loopback-origin peer.

## Evidence ladder (all GREEN except the deliberate negative, which there is none of — every same-host path works)

1. **Windows-native loopback** (`winloop_probe.py 127.0.0.1 15381`, system Python, zero NAT, zero container):
   greeting `53 f5 c6 1a 7b` (== Linux); **frame-1 reply = 210 B** `ef bb bf 7b 31 2c 31363635…` (`{1,1636…`);
   **full `open_and_bootstrap` frames 1..10 completed, received_stream = 2064 B, ack_guid obtained.**
   → The in-repo synthesized bootstrap drives a *Windows-built* client. Protocol is fine on Windows.

2. **Container, bind-mounted source** (`python:3.13-slim` + `pip install mcp`, `read_probe.py host.docker.internal
   15381`): real `_read_form_descriptor` returned **field_count = 43** with live values
   (`PF_EDIT_DATE='15.01.2026 10:30:00'`, `PF_CHECKBOX_TRUE='Да'`, `PF_EDIT_NUMBER='120,5'`, …).
   → The real qa-mcp READ engine drives the Windows client from a Linux container over `host.docker.internal`,
   default Docker Desktop NAT, no workaround.

3. **Thin model-B image** (`docker/Dockerfile.thin` → `qa-mcp-thin`, **261 MB**, no 1C libs / no X11 / no Xvfb):
   builds, runs `qa-native-mcp` (FastMCP streamable-HTTP) on `0.0.0.0:8000`. MCP client (both *in-container*
   loopback and *Windows-host* via `http://127.0.0.1:8000/mcp/`): **61 tools**, `read_form_descriptor(host=
   "host.docker.internal", port=15381)` → full fixture form. → The whole agent → MCP-HTTP → container →
   Windows client → form-data path works.

## Delivery gotchas captured (model B, Docker Desktop on Windows)

- **Client connection:** the tools must point at **`host.docker.internal`** (Docker Desktop) — that is what
  presents as a loopback-origin peer to the client. A raw container `--network` / LAN IP to a *different* box
  would hit the remote-peer rejection. (Inbound TPort must be firewall-allowed; the lab keeps a rule for 15381.)
- **Agent connection:** connect the agent to **`http://127.0.0.1:8000/mcp/`**, NOT `http://localhost:8000` —
  on Windows `localhost` resolves to IPv6 `::1` first and the `-p 8000:8000` publish is IPv4, so `localhost`
  fails with "Server disconnected without sending a response". Use `127.0.0.1` (or publish dual-stack). Trailing
  `/mcp/` slash.
- **TestClient lifecycle:** launch in the user's **interactive session 1** (a session-0/SSH launch binds the
  TPort then the process dies). `schtasks /RU historical-user /IT` + the kept `C:\Users\historical-user\TEMP\qatc_launch.ps1`.
- **Version:** set `QA_MCP_PLATFORM_VERSION` to the host client's version (here 8.3.27.2130) so the synth
  bootstrap declares the live version (epic-112 version-injection; the only knob the handshake needs).

## What model B still does NOT serve (unchanged from the card)

The DISPLAY-bound tools — XTEST writes (`write_form_fields_by_label`, `set_table_date_cell`, `send_keys`),
screenshots, OS window list — are Linux/X11 and the Windows render is GDI, not in the container's X server.
The PROTOCOL surface (read / assert / scenario runner / navigation / protocol writes / `measure` / OData) is
served as-is. Recovering the visual subset needs the host-side Windows input/screenshot agent (card agenda #2).

## Repro (next session / the operator)

```
# 0. Windows host: launch the client in session 1 (kept launcher)
schtasks /Create /TN QaTcLaunch /TR "powershell -ExecutionPolicy Bypass -File C:\Users\historical-user\TEMP\qatc_launch.ps1" /SC ONCE /ST 00:00 /RU historical-user /IT /F
schtasks /Run /TN QaTcLaunch          # 1cv8 ENTERPRISE /TESTCLIENT -TPort 15381 against vanessa_client

# 1. Build + run the thin image (model B)
docker build -f docker/Dockerfile.thin -t qa-mcp-thin .
docker run --rm -p 8000:8000 -e QA_MCP_PLATFORM_VERSION=8.3.27.2130 qa-mcp-thin

# 2. Point the agent at  http://127.0.0.1:8000/mcp/  and call tools with
#    host="host.docker.internal", port=15381
```

Artifacts on the lab box (kept): clone `C:\Users\historical-user\TEMP\qa-cur` (+ `.venv`, probes
`winloop_probe.py` / `read_probe.py` / `mcp_http_probe.py`), image `qa-mcp-thin`, launcher `qatc_launch.ps1`,
inbound firewall rule `qa-mcp TestClient 15381`.

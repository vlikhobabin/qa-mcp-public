# Card 119 — Windows cross-machine (model B) lab findings — 2026-06-26

Lab: `historical-user@192.0.2.202` (Windows 10.0.26200), driven from the Linux suite server over SSH.
1C installs present: 8.3.18 … **8.3.27.2130** … **8.5.1.1302** (64-bit) + a 32-bit tree.
Target base: `C:\1C_BASES\vanessa_client` pinned `Version=8.3.27.2130` — **byte-identical config + platform
to the Linux lab** the bundled qa-mcp captures were made on (the ideal control).

Launch used (in the user's interactive session 1, via a `schtasks /RU historical-user /IT` task so the GUI thick client
persists and is not tied to the SSH logon session):

    "C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe" ENTERPRISE \
      /IBConnectionString File="C:\1C_BASES\vanessa_client"; /NАдминистратор \
      /TESTCLIENT -TPort 15381 /DisableStartupDialogs /DisableStartupMessages

## A. TRANSPORT — model B premise PROVEN ✅

| Question | Result |
| --- | --- |
| Does `/TESTCLIENT -TPort` bind a LAN-reachable interface? | **YES** — `netstat`: `TCP 0.0.0.0:15381 LISTENING` **and** `[::]:15381` (IPv4+IPv6), not 127.0.0.1-only. |
| Does the client persist? | Only when launched in the **interactive session 1**. A launch from the non-interactive SSH session (session 0) binds the port but the process dies shortly after. `schtasks /RU historical-user /IT` puts it in session 1 (`SESSION=1`, `RESP=True`) where it stays up. |
| Firewall? | Inbound TCP 15381 is **dropped by default** (all 3 profiles enabled). One `New-NetFirewallRule -Direction Inbound -LocalPort 15381 -Protocol TCP -Action Allow` opens it. The SSH user `historical-user` is a local admin, so the rule adds without extra elevation. |
| Can the Linux box reach it cross-machine? | **YES**, once the firewall rule exists: `socket.create_connection(('192.0.2.202',15381))` succeeds; the client even sends a greeting. |

So model B's transport story holds: a thin (Python-only) qa-mcp can reach a Windows-hosted TestClient over TCP.

## B. PROTOCOL — Linux-captured bootstrap does NOT drive a Windows client ❌ (the real blocker)

Driving the three read-only `ui`-phase regression checks (`run_scenario` / `read_form_descriptor`,
`host=192.0.2.202 port=15381`) → **0/3, all `error`** at the **bootstrap** step (`ConnectionResetError` /
`Connection reset by peer`). Raw frame-by-frame probe pinned the divergence:

| Step | Linux client (genuine bundled capture `tm-v1-ro-batchQ3`) | Windows client (8.3.27.2130) |
| --- | --- | --- |
| greeting (C→M) | `53 f5 c6 1a 7b` (5 B) | **`53 f5 c6 1a 7b` (5 B) — identical** |
| manager frame 1 (M→C, 548 B) | client replies **210 B** JSON `EFBBBF 7B 31 2C 31363336…` (`{1,1636…`) | client replies **`66 53 b2 a6` (4 B)** then **EOF / reset** |
| manager frame 2 (M→C, 580 B) | client replies **450 B** | (never reached on a fresh client; 0 B then reset when reached) |
| manager frame 3 (M→C, 612 B) | client replies **262 B**, handshake continues into the binary phase | reset |

My synthesized manager frames match the capture (lengths 548/580/612; head `EFBBBF7B302C e23134a2-14ff-4160-ba5…`),
and the same code path is GREEN against a Linux client — so I am sending the right frames. The Windows client
simply does not engage them.

Hypotheses ruled out (each tested):
- **Version mismatch** — declaring a deliberately wrong version (`8.3.99.9999`) gives the *same* reset; declaring
  the correct `8.3.27.2130` also resets. Frame 3 is NOT version-gated here (unlike the 8.5 case, epic 112).
- **Session-constant GUID/token** — `synthesize_bootstrap(randomize_constants=True)` → same reset.
- **Inter-frame timing** — sending frames 1+2+3 back-to-back avoids the *immediate* reset but the client still
  emits only the 4-byte token and never the frame-3 ACK GUID (handshake never advances).
- **Single-connection poisoning** — a **freshly restarted** client (first connection, `FRESH_PID`, session 1)
  responds `66 53 b2 a6` + EOF to frame 1 identically. Not exhaustion.

The `66 53 b2 a6` token is not noise: it appears in the genuine Linux capture as the 4-byte tail of client
frame [8] (`{1,2758290683,1}` + `6653b2a6`) — i.e. a fixed protocol marker the Windows client jumps straight to
instead of producing the rich frame-1 response.

### Conclusion
A **Windows-built TestClient requires its own genuine handshake capture**; the Linux-captured bootstrap +
manager-frame templates do not drive it. This is the **platform (OS) analogue** of the epic-112 *version*
finding. The bundled-capture layout is already keyed (`src/qa_mcp/_bundled/8.3/captures/…`), so a `windows`/OS
key can slot in beside the version keys.

### Implication for card 119
The card's tool-classification claim — "the protocol surface works cross-machine as-is (pure protocol/TCP)" —
is **true at the wire/transport layer but false at the handshake layer for a Windows-built client**. Driving a
Windows client is gated on a genuine Windows manager↔client capture, which becomes a prerequisite change for
model B (ahead of, or alongside, the remote-client mode).

### Next step (proposed)
Capture a genuine Windows manager↔client session on the lab box (`vanessa_manager` is installed there) with
`pktmon` on loopback (Windows analog of the Linux `tcpdump`-on-`lo` recipe), extract bootstrap frames 1..N +
the manager-frame templates, and add a platform-keyed bundle so `run_scenario` selects Windows templates when
the live client is Windows. Then re-run the three `ui` checks cross-machine to confirm GREEN.

## Lab state left behind (model-B artifacts, intentionally kept)
- Inbound firewall rule `qa-mcp TestClient 15381` (TCP 15381, all profiles).
- `C:\Users\historical-user\TEMP\qatc_launch.ps1` (the session-1 launcher used here).
- No 1cv8 process left running; the scheduled task `QaTcLaunch` was deleted; port 15381 free.

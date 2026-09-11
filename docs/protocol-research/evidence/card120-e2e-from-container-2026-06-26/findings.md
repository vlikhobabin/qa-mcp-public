# card 120 — LIVE e2e from the Docker container on Windows (model B + host-agent)

**Date:** 2026-06-26 · **Lab:** `historical-user@192.0.2.202` · base `vanessa_client` @ 8.3.27.2130 ·
**Commit under test:** `02e7f32` (card 120) · **Result: WORKS end-to-end, with 1 real bug + 1 config note.**

## Topology exercised
Thin container `qa-mcp-thin:card120` (rebuilt from `02e7f32` — the shipped 4h-old `:latest` did NOT contain
card-120 code) on Docker Desktop → MCP-HTTP :8000, env `QA_MCP_REMOTE_CLIENT=1`,
`QA_MCP_CLIENT_HOST=host.docker.internal`, `QA_MCP_HOST_AGENT=host.docker.internal:8001`,
`QA_MCP_HOST_AGENT_TOKEN=card120testtoken`. TestClient + Go host-agent (`0.1.0-card120`, sha `1fe93f6f…`) in
session 1. MCP client driven from inside the container.

## What works (verified live)
- **Protocol path** — `read_form_descriptor` (no host arg → `host.docker.internal:15381`) → **43 live fields**.
- **Host-agent display route**:
  - `get_window_list` → **16 real session-1 windows** (incl. the TestClient «Демонстрационное приложение»),
    i.e. the container drove the agent's `EnumWindows`.
  - `capture_screenshot` → real **432 KB PNG**, `backend:"remote-agent"` (agent `PrintWindow`).
- **Full-stack WRITE** — `write_form_value_xtest` (defaults: Справочник.Валюты / Наименование) → protocol opens
  «Валюта (создание)» via `host.docker.internal:15381`, then the agent `/type` (`KEYEVENTF_UNICODE` SendInput)
  types into Наименование. Window-targeted `PrintWindow` proof: the value (`…120Контейнер`, Cyrillic clean) is
  in the Наименование field and the tab shows the dirty marker `*` (genuine edit committed to the form object).
  Requires `QA_MCP_HOST_AGENT_WINDOW` set + a clean client tab state (see notes).

## BUG 1 (real, blocking for the documented topology) — agent binds `127.0.0.1`, unreachable from the container
The installer (`host-agent/install-windows-host-agent.ps1`) runs the agent with `-addr 127.0.0.1:8001`. From the
container, `host.docker.internal` resolves to the Docker Desktop gateway `192.168.65.254`; a service bound to the
host's loopback is **not reachable** on that interface → `OSError: [Errno 101] Network is unreachable` on every
agent call. The TestClient works only because it binds `0.0.0.0:15381`.
- **Proof:** same container, same gateway IP — `:15381` (0.0.0.0) `CONNECT_OK`; `:8001` (127.0.0.1) unreachable.
  After rebinding the agent to `0.0.0.0:8001`, the container reached `/health` + `/version` and all tools worked.
- **Fix:** the installer / agent default must bind `0.0.0.0:8001` (like the TestClient), keeping security via the
  shared token + the firewall rule the installer already adds. `127.0.0.1` only works if qa-mcp runs natively on
  the host (not in a container) — i.e. it defeats model B. This is why the prior "live proof" passed: it did not
  go through the container (the shipped image lacked card-120 code).

## NOTE 2 (config, not a bug) — writes need `QA_MCP_HOST_AGENT_WINDOW` + clean tab state
The agent foregrounds the target window by title substring (`driver.Focus(window)`), fed from
`QA_MCP_HOST_AGENT_WINDOW` (default empty). For writes/clicks to hit 1C it must be set to a 1C window-title
substring (used `"Демонстрационное приложение"`). With it unset, input lands in whatever is foreground. Also, a
stale open tab (e.g. a prior `read_form_descriptor` fixture form) can leave the wrong tab active; a fresh client
opened «Валюта (создание)» cleanly.

## NOTE 3 (to re-confirm, low priority) — Latin glyphs in the write render
The typed `E2E120Контейнер` rendered ambiguously in the Наименование field (`E`/`Е` are homoglyphs at small
font); the Cyrillic part is unmistakably correct. `TypeText` is clean per-rune `KEYEVENTF_UNICODE` (identical to
the spike that proved clean), so this is most likely a homoglyph/font read, not a real garble — worth a clean
zoomed re-check but not blocking.

## Artifacts (PNGs git-ignored / local-only)
- `01-agent-screenshot-via-container.png` — desktop PNG captured by the agent, pulled through the container.
- `02-full-stack-write-Валюта-Наименование.png` — «Валюта (создание) *» with the value in Наименование.
- `mcp_e2e.py`, `mcp_write.py` — the in-container MCP client drivers.

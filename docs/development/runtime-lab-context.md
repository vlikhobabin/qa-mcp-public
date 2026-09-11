# QA lab and provider context

This is the dated Linux lab context extracted from AGENTS.md during the
2026-09-05 local-workflow migration. Validate current paths and target identity
before a runtime operation; these historical inventory counts are not current
capability or delivery proof. Runtime authority stays in AGENTS.md, the accepted
card and the applicable preflight/evidence contract.

## Linux Runtime Baseline

Use POSIX shell scripts, Linux-native executables, and Python entrypoints. Do
not add PowerShell, `.cmd`, `.bat`, WSL, or retired-platform workflow
entrypoints.

Active lab paths:

- `/opt/1c-dev/vanessa_client` - target TestClient file infobase.
- `/opt/1c-dev/vanessa_manager` - Vanessa/TestManager file infobase.
- `/opt/1c-dev/vanessa_qa` - Linux EDT workspace with `vanessa_client` and
  `vanessa_manager` projects imported into fresh Linux `.metadata`.
- `/opt/1cv8/x86_64/8.3.27.2130` - current Linux platform root.
- `/opt/1C/1CE/components/1c-edt-2026.1.1+1-x86_64` - current Linux EDT home.

The ignored `.ai1c/*.env` files record Linux paths for the `client` and
`manager` targets. COM live access is not part of the active contour.
**Linux-native TestClient runtime is proven**: `launch_test_client` boots a
native `/TESTCLIENT` headless under Xvfb, and the engine captures, replays and
live-verifies the protocol on Linux (cards 84/85/96/97/98). The native MCP
server (`src/qa_mcp/mcp_server.py`) exposes the capture-free tool surface (45
tools as of 2026-06-20).

As of 2026-07-06 the suite MCP toolchain is wired against the Linux
`vanessa_client` contour: `config-mcp` for controlled source authoring,
`meta-mcp` and `postgres-mcp` for metadata/code search, `bsl-mcp` for read-only
BSL diagnostics, `admin-mcp` for platform command planning/execution evidence,
and `live-mcp` for read-only data access through both the standard OData
interface and the custom HTTP-service (1C query / DCS), published by a local
Apache instance on `127.0.0.1:8316` (the 1C web module `wsap24.so`;
`MemoryDenyWriteExecute=no` is required for its TEXTREL libraries). This support
stack is independent of native TestClient protocol capture/replay, which now
runs Linux-native (see above).

## MCP Profile

The project-local profile is generated from the AI1C suite renderer and then
narrowed for this lab. Expected project-local provider entries are:

- `admin-mcp`
- `agentic-rag`
- `bsl-mcp`
- `config-mcp`
- `help-mcp`
- `knowledge-mcp`
- `live-mcp`
- `meta-mcp`
- `postgres-mcp`
- `qa-mcp`

Codex may also provide global `filesystem` and `context7` capabilities; they are
not qa-mcp-owned profile entries. `edt-mcp` and `vanessa-mcp` are not active
providers in this component profile. `config-mcp`, `meta-mcp`, `bsl-mcp`,
`admin-mcp` and `live-mcp` are support layers for controlled fixture authoring,
metadata mapping, diagnostics, platform execution evidence and read-only runtime
access. Raw protocol capture/replay should not depend on them. `live-mcp`
reaches `vanessa_client` via the standard OData interface and the custom
HTTP-service (Apache `127.0.0.1:8316`), configured in the component-local
ignored `live-mcp/.env` (default connection `vanessa_client`).

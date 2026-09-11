## Why

Containerized live-mcp needs to execute 1C COMConnector calls on the Windows
host, because `V83.COMConnector` is Windows-only and the thin Linux container
cannot open file infobases directly through COM. The qa-mcp Windows host-agent
is already the tokened, SHA-pinned bridge for host-side operations, so COM
execution should use the same authenticated host boundary instead of adding a
second bridge.

## What Changes

- Add authenticated `POST /com/execute` to the Windows host-agent.
- Accept live-mcp `WorkerRequest` JSON, validate the `operation` allowlist, and
  require operator-intent evidence for `guarded_posting_smoke`.
- Execute only the fixed installed `ai-com-worker.exe --worker` subprocess,
  selected by host configuration, and feed the request body to stdin.
- Return the worker's UTF-8 `WorkerResponse` JSON without platform-output
  truncation, CP866 fallback decoding, or request-body logging.
- Fail closed for missing workers, worker startup failures, timeout, empty
  stdout, invalid worker JSON, and unauthorized requests.
- Extend authenticated `/health` with COM worker availability diagnostics.
- Update the Windows installer, host-agent docs, host-agent version
  compatibility, and Linux-executable Go tests.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: adds the authenticated, allowlisted COM
  worker execution boundary and its fail-closed behavior.

## Impact

- Touches host-agent Go code and tests under `host-agent/windows-display-agent/`.
- Touches `host-agent/install-windows-host-agent.ps1`, `host-agent/README.md`,
  and the remote host-agent compatibility set in
  `src/qa_mcp/protocol/display_backend.py`.
- Touches OpenSpec artifacts and the existing
  `qa-mcp-windows-host-agent-security` capability.
- Does not touch native TestClient protocol capture/replay, replay tooling,
  1C metadata/source, BSL modules, MCP server tool contracts, runtime lab
  configuration, Vanessa MCP, EDT/meta snapshots, or the live-mcp Python worker
  implementation. Verification is offline Go unit coverage with fake workers,
  cross-compiled host-agent build proof, OpenSpec validation, and an explicit
  Windows/E2E handoff for real COM registration and license checks.

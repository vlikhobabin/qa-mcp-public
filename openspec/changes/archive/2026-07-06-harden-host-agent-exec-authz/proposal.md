## Why

The Windows host-agent is a token-authenticated bridge to workstation-level 1C
platform and COM execution, but a direct caller can currently bypass client-side
mutation policy by declaring a dangerous argv as `read_only`, and a valid token
holder can spawn unbounded long-lived subprocesses. This change moves those
guards into the host-agent process so the bridge fails closed even when called
directly.

## What Changes

- Enforce server-side platform argv classification for `/platform/execute` so a
  `read_only` request carrying known mutating 1C platform actions is rejected
  before executable resolution or process spawn.
- Preserve known positive read-only platform calls such as `ibcmd --version` and
  `ibcmd config generation-id`.
- Add a shared in-flight execution limiter across `/platform/execute`,
  `/com/execute`, and `/agent/complete` so valid-token subprocess requests are
  bounded instead of goroutine-unlimited.
- Evict stale failed-auth limiter keys after their window expires.
- Extend host-agent documentation and Go tests for the policy reject path,
  positive read-only path, concurrency cap, limiter eviction, and existing
  auth/redaction behavior.
- Defer per-capability token scoping to a later host-agent contract change; this
  card keeps the existing token wire contract.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: strengthens host-agent server-side
  execution authorization, subprocess concurrency limits, and failed-auth
  limiter cleanup.

## Impact

- Code: `host-agent/windows-display-agent/platform_exec.go`,
  `host-agent/windows-display-agent/main.go`, and Go tests in the same package.
- Docs: `host-agent/README.md` and the existing Windows host-agent security
  OpenSpec capability.
- This does not change native TestClient protocol capture/replay, Python manager
  MCP tools, live infobase data, Vanessa MCP, EDT/meta snapshots, or runtime lab
  configuration. Verification is host-agent Go unit coverage, OpenSpec
  validation, diff hygiene, and a retained verification-matrix record; no live
  Windows host execution is required for this Linux delivery pass.

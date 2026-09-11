## 1. Server-Side Platform Policy

- [x] 1.1 Add host-agent argv classification for known mutating 1C platform and `ibcmd` actions before executable resolution/spawn.
- [x] 1.2 Reject `read_only` `/platform/execute` requests that contain mutating argv with a clear fail-closed error.
- [x] 1.3 Preserve positive read-only platform calls such as `ibcmd --version` and `ibcmd config generation-id`.

## 2. Execution Capacity And Limiter Cleanup

- [x] 2.1 Add a shared in-flight execution semaphore to `Agent` and wrap `/platform/execute`, `/com/execute`, and `/agent/complete` process-spawning paths.
- [x] 2.2 Return HTTP 429 `execution-capacity-exceeded` without spawning when capacity is unavailable.
- [x] 2.3 Evict stale `failureLimiter` keys after their window expires while preserving active failed-auth rate limiting.

## 3. Documentation And Verification

- [x] 3.1 Update host-agent documentation to describe server-side mutation enforcement, concurrency cap, stale limiter cleanup, and deferred per-capability token scoping.
- [x] 3.2 Add Go tests for read-only mutating argv rejection/no-spawn, positive read-only argv, concurrency cap/no-spawn, stale limiter eviction, and existing auth/redaction behavior.
- [x] 3.3 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 3.4 Run `openspec validate harden-host-agent-exec-authz --strict`, `openspec validate --all`, and `git diff --check`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Host-agent `/platform/execute` server-side mutation boundary for 1C platform argv | Stubbed Go endpoint tests proving read-only `designer /Execute` is rejected before process spawn and known read-only `ibcmd` argv still passes | source_preflight, scenario_log, data_assertion from `go test ./...` in `host-agent/windows-display-agent` | `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Medium: tests prove classifier behavior for known high-risk argv, not every possible 1C platform command. |
| Delivery or runtime apply | Shared subprocess concurrency cap across host-agent exec endpoints | Go HTTP tests with occupied limiter slot and N+1 request returning 429 before process spawn | source_preflight, scenario_log from focused Go tests | `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Low: in-process tests do not load-test OS process tables, but prove the endpoint guard. |
| Delivery or runtime apply | Failed-auth limiter map lifecycle | Unit test with expired keys proving stale entries are removed | source_preflight, scenario_log from focused Go tests | `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Low: wall-clock behavior is covered through injected timestamps or controlled limiter state. |
| BSL-only module edit | BSL modules | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | No BSL or 1C configuration module files are changed. | None. |
| Managed form layout | 1C managed forms | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No managed form layout or UI command behavior is changed. | None. |

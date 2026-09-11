## Context

The host-agent already protects desktop, platform, COM, and local agent CLI
endpoints with one bearer token, constant-time comparison, Origin checks, no
shell dispatch, executable allowlists, bounded output, and redaction. The weak
point is that `/platform/execute` validates `operation` and `mutation_class` as
declared fields but does not verify that the supplied argv matches the declared
mutation boundary. A direct HTTP caller can therefore send a request labelled
`read_only` while invoking mutating 1C platform actions such as Designer
`/Execute`.

The same process also has no valid-token request cap. Each `/platform/execute`,
`/com/execute`, and `/agent/complete` call may spawn a process for up to 600
seconds. The existing failed-auth limiter protects only wrong-token callers and
keeps empty per-IP entries indefinitely.

## Goals / Non-Goals

**Goals:**

- Reject known mutating platform argv when the request declares
  `mutation_class: "read_only"`.
- Keep valid read-only platform probes working, including `ibcmd --version` and
  `ibcmd config generation-id`.
- Bound concurrent subprocess execution across the three host-agent exec
  endpoints with a simple shared semaphore.
- Remove stale failed-auth limiter keys after their window expires.
- Cover all new boundaries with Go unit tests that prove reject paths happen
  before process spawn.

**Non-Goals:**

- Replace the `/platform/execute` wire contract with structured host-rendered
  command templates.
- Implement per-capability tokens for display, platform, COM, and agent CLI
  scopes.
- Add COM `progId`/infobase allowlisting; that remains owned by the paired
  live-mcp card.
- Run live Windows, COM, or 1C infobase mutations during this Linux delivery
  pass.

## Decisions

1. Keep raw argv but add conservative server-side classification.

   The safer long-term shape is a host-rendered command template contract, but
   admin-mcp and config-mcp already use the current raw argv bridge. This change
   adds a fail-closed classifier for known mutating actions without breaking
   existing read-only probes. The classifier should normalize case and leading
   switch characters, include the internally prepended Designer mode when
   relevant, and reject `read_only` when it sees mutation markers such as
   `/Execute`, `/LoadCfg`, `/LoadConfigFromFiles`, `/UpdateDBCfg`, `/LoadIB`, or
   `ibcmd` write/import/apply/create/delete/update families.

2. Treat classifier misses as residual risk, not proof of read-only semantics.

   The host-agent cannot understand every possible 1C platform subcommand from
   arbitrary argv. The classifier is a defense-in-depth block for known dangerous
   forms. Owning providers must still generate only reviewed command plans and
   mark intentional mutations as `mutating`.

3. Use a shared process limiter in `Agent`.

   A small semaphore attached to `Agent` keeps the cap in-process, testable, and
   independent of the HTTP server's goroutine model. The limiter should wrap
   process-spawning sections only after auth and request validation, returning
   HTTP 429 with a clear `execution-capacity-exceeded` error when full. The cap
   is intentionally shared across `/platform/execute`, `/com/execute`, and
   `/agent/complete` because they all consume host process resources.

4. Evict failed-auth keys during limiter maintenance.

   On each failed-auth check, prune entries older than the configured window for
   the current key and remove other keys whose retained slice is empty. This
   bounds map growth without background goroutines or timers.

## Risks / Trade-offs

- Incomplete command classification -> mitigated by covering known high-risk
  Designer/1C/ibcmd mutation families and keeping admin-mcp/client policy as the
  first line of defense.
- False positives for uncommon read-only commands -> mitigated by allowing
  known admin read-only calls and returning an explicit error that points to the
  mutation classification.
- Host-level cap too low for legitimate parallel work -> mitigated by keeping
  the limiter local to process spawning and choosing a conservative default that
  can be adjusted in code later if E2E load requires it.
- Linux-only verification cannot prove Windows process behavior -> mitigated by
  Go tests for policy and semaphore behavior plus existing process-group
  timeout tests; live Windows smoke remains outside this card.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Host-agent `/platform/execute` server-side mutation boundary for 1C platform argv | Stubbed Go endpoint tests proving read-only `designer /Execute` is rejected before process spawn and known read-only `ibcmd` argv still passes | source_preflight, scenario_log, data_assertion from `go test ./...` in `host-agent/windows-display-agent` | `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Medium: tests prove classifier behavior for known high-risk argv, not every possible 1C platform command. |
| Delivery or runtime apply | Shared subprocess concurrency cap across host-agent exec endpoints | Go HTTP tests with occupied limiter slot and N+1 request returning 429 before process spawn | source_preflight, scenario_log from focused Go tests | `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Low: in-process tests do not load-test OS process tables, but prove the endpoint guard. |
| Delivery or runtime apply | Failed-auth limiter map lifecycle | Unit test with expired keys proving stale entries are removed | source_preflight, scenario_log from focused Go tests | `.artifacts/openspec/harden-host-agent-exec-authz/2026-07-06T134428Z/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Low: wall-clock behavior is covered through injected timestamps or controlled limiter state. |
| BSL-only module edit | BSL modules | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | No BSL or 1C configuration module files are changed. | None. |
| Managed form layout | 1C managed forms | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No managed form layout or UI command behavior is changed. | None. |

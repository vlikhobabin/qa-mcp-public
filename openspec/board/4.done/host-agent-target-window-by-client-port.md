# Auto-target the display window by driven-client TPort (drop the per-config window override)

## Status
4.done

## Owner
unassigned

## Order Index
133

## OpenSpec Stage
done. Apply-ready single change delivered. Removes the per-configuration
`QA_MCP_HOST_AGENT_WINDOW` override by resolving the F5/refresh window from the
client's own TPort. Live-verified on .201; independent OPSX review verdict = go
(cycle 1, zero findings, spec diff additive).

## Source
- 2026-07-08 [redacted third-party configuration] read closure (`read-list-grid-third-party-config-positive-read-runtime-closure`):
  the positive read needed `QA_MCP_HOST_AGENT_WINDOW=Бухгалтерия предприятия,
  редакция 3.0` because the container baked demo10413's window caption. Operator
  asked to auto-detect the client's own top-level window so no per-config
  override is needed.

## Problem
The host-agent targets display primitives by window caption
(`QA_MCP_HOST_AGENT_WINDOW`). A caption baked for one base mis-targets another,
so the F5 list refresh reaches no window and the read returns a false
`row_count:0, "no display backend was reachable"`. Captions also cannot
disambiguate multiple concurrent TestClients.

## Scope
1. Host-agent `port:<N>` selector: PID listening on TPort N
   (`GetExtendedTcpTable`) → its `V8TopLevelFrame…` window. Display endpoints
   accept `client_port` and target `port:<client_port>` when no explicit window.
2. Python `RemoteAgentBackend`: send the driven-client TPort as `client_port` on
   every display payload; explicit `QA_MCP_HOST_AGENT_WINDOW` still wins; older
   host-agents ignore the additive field.
3. Offline tests for the TCP-table parse + effective-window selection + Python
   payload/precedence. Bump host-agent version + compat set.

## Acceptance
- `go test ./...` (native) + `python -m pytest` GREEN with the new tests;
  `GOOS=windows go vet` + build clean.
- Live: a display request with `client_port` and no `window` resolves the
  client's own 1C window; an idle port fails closed; an explicit caption wins.
- Backward compatible: `client_port` is additive; no field removed.
- Regression: no change to protocol frames, replay templates, Python manager,
  MCP setup or runtime lab config.

## Change 1: `host-agent-target-window-by-client-port`

### Why
The per-configuration window caption is the sole reason the [redacted third-party configuration] refresh
needed a manual override; the client's TPort already identifies the exact window
to refresh.

### Goal
Resolve the display target window from the driven client's TPort so display
primitives target the correct TestClient with no per-config caption.

### Acceptance
- As in the card Acceptance.

### Related
- `read-list-grid-third-party-config-positive-read-runtime-closure` (the read closure
  that surfaced the per-config override). Capability
  `qa-mcp-windows-host-agent-security`.

## Log
- 2026-07-08 filed + implemented + offline-tested + live-verified on .201 from
  the [redacted third-party configuration] read-closure follow-up (operator-requested).
- 2026-07-08 delivered: change archived (spec ADDED requirement, purely additive
  diff). Independent fresh-context OPSX review (claude subagent, not the
  implementer): cycle-1 go, zero findings; go test/vet/build clean, pytest 796,
  openspec specs 12/12. Live .201: `/send_keys {client_port}` resolved the
  client's own V8 window; idle port failed closed; explicit caption still won.

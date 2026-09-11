## Context

`connect_testclient()` must authenticate when opening the configured relay
endpoint because actual protocol sessions need the fixed loopback target.
Readiness is different: authenticating necessarily consumes that target even
when the caller closes immediately. Launch and reattach already use
`relay_listener_reachable()`, but generic lifecycle probes still use the full
connector and are called by public status/info/state tools and the doctor.

## Decisions

1. `_port_open()` detects only the exact configured relay endpoint and delegates
   to `relay_listener_reachable()` there.
2. Direct endpoints retain `connect_testclient()` behavior, which is a normal
   TCP connection when the address is not the configured relay.
3. Protocol sessions continue to use `connect_testclient()` directly and
   therefore retain bounded authentication and fail-loud target errors.
4. Focused tests make the authenticated connector raise if a relay liveness or
   public status path attempts to use it.

## Verification

- Focused lifecycle and MCP status tests with connector-negative assertions.
- Full offline Python suite.
- Strict OpenSpec validation and `git diff --check`.
- Subsequent root T4 M9 launch/attach/descriptor/grid proof.

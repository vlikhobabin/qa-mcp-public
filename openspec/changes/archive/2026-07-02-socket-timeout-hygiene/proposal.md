## Why

The native write/session lifecycle can leak sockets when setup replay fails,
leave later sends under short read-idle timeouts, and terminate arbitrary
process groups when given a stale pid. Those failures make protocol problems
harder to diagnose and create unsafe teardown behavior.

## What Changes

- Close a `NativeWriteSession` socket if setup replay fails inside `__enter__`.
- Restore or apply a sane send timeout before outbound frames so slow sends are
  reported as send timeouts, not protocol divergence.
- Map `socket.timeout` from send paths to a distinct truthful failure reason.
- Add an ownership guard before `stop_test_client(pid)` kills a process group.
- Add offline tests for setup failure cleanup, slow-send classification, and
  teardown refusal for unowned or non-TestClient processes.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: native protocol sessions clean up sockets on failed
  setup, distinguish send timeouts from divergence, and stop only owned
  TestClient runtime processes.

## Impact

- Touches Python manager code under `src/qa_mcp/protocol/native_write.py` and
  `src/qa_mcp/protocol/lifecycle.py`.
- Touches offline lifecycle/session tests.
- Does not change MCP provider setup, OpenSpec workflow, or runtime lab config.
- Requires offline fake-socket and `/proc` ownership tests; live runtime use is
  not required for the safety refusal contract.

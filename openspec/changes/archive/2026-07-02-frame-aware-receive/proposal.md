## Why

The protocol receive layer currently treats an idle socket gap as the end of a
response, so a slow TestClient can split one wire response into multiple logical
frames. This makes cold or cross-machine clients look flaky even when the
protocol stream contains its normal tail marker.

## What Changes

- Replace idle-first receive behavior with frame-aware receive behavior that
  reads until the protocol tail marker is observed or a hard deadline expires.
- Keep the idle gap only as a fallback for responses that do not carry the known
  tail marker.
- Move the duplicate receive logic in `session.py` and `native_mutation.py` to a
  single shared helper that uses monotonic time.
- Add fake-socket tests proving a response split across an idle-window gap is
  returned as one frame and remains parseable.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: protocol reads are framed by the protocol tail marker
  before falling back to idle timing, and the shared receive helper uses
  monotonic deadlines.

## Impact

- Touches Python manager code under `src/qa_mcp/protocol/`.
- Touches offline protocol tests with fake sockets.
- Does not change MCP provider setup, OpenSpec workflow, or runtime lab config.
- Requires offline capture/fake-socket evidence for acceptance; a live read pass
  is useful final evidence but not needed to establish the frame-boundary unit
  contract.

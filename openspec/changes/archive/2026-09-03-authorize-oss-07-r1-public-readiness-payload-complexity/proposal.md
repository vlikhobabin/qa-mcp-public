## Why

Published OSS-07-R1-I1 intentionally prepared, but did not itself publish, the
separate ChangeRail authorization source required for the exact OSS-07-R1
successor to use a bounded `350`-line complexity ceiling. This change publishes
only that exact non-reusable metadata source while leaving the successor
payload absent and untouched.

## What Changes

- Publish the exact six-field investigation authorization prepared by
  OSS-07-R1-I1, binding its unchanged published card to the exact OSS-07-R1
  successor id/path with `production_loc_ceiling: 350` and no new authority or
  wire protocol.
- Require the source to depend on published I1 and to remain unchanged and
  tracked in `4.done` before the successor can reference it.
- Preserve the complete-scope accounting boundary: whitespace deletion,
  production-source reclassification and owned-scope exclusion cannot be used
  to evade the complexity gate.
- Touch only the OpenSpec workflow, documentation and board metadata. Do not
  change protocol tools, Python manager/MCP code, provider setup, tests,
  licenses, evidence payloads or runtime lab configuration.

## Capabilities

### New Capabilities
- `qa-mcp-public-readiness-payload-complexity-authorization`: Defines the exact
  non-reusable I1-to-OSS-07-R1 authorization source and its fail-closed,
  metadata-only publication boundary.

### Modified Capabilities
- None.

## Impact

The payload is limited to this card, one OpenSpec authorization change and its
synced capability. It adds no product/test implementation, public or wire
contract, credential or mutation authority, runtime behavior, or external
action. Exact SPDX `Apache-2.0` and published OSS-07-I2 remain unchanged;
OSS-07-I1 remains absent. No live 1C runtime, TestClient, Apache service,
Vanessa MCP, EDT/meta snapshot, offline capture, Windows, SSH, network, release,
OSS-08 or OSS-09 execution is required or authorized.

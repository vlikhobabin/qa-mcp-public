## Why

Published I10 prepared one exact bounded authorization object for I11, but
ChangeRail requires that object to be published separately as an unchanged
tracked `4.done` source before the repeated-defect successor can enter review.

## What Changes

- Publish the exact six-field authorization object from I10's machine decision,
  binding only published I10 to exact I11 at its authorization-time
  `3.inprogress` path, with `production_loc_ceiling: 301` and no new authority
  or wire protocol.
- Require I10a to depend on I10 and to complete fresh independent review and
  scoped publication before I11 may consume the authorization.
- State that I10a neither implements nor certifies I11 and leaves the S4-R1
  parent and I11 blocked.
- Touch only OpenSpec workflow, documentation and board metadata. Do not change
  protocol tools, Python manager/MCP code, provider setup, tests, host-agent
  product files or runtime lab configuration.

## Capabilities

### New Capabilities

- `qa-mcp-main-predicate-equivalence-successor-authorization`: Defines the
  exact, non-reusable, documentation-only I10-to-I11 authorization source.

### Modified Capabilities

- None.

## Impact

The payload is limited to this card, one OpenSpec authorization change and its
synced capability. It changes no product, test, public API, route, wire field or
runtime behavior and preserves Apache-2.0 unchanged. It requires no live 1C
runtime, Vanessa MCP, EDT/meta snapshot, capture evidence, Windows or
PowerShell execution, endpoint or lab access, S5/S7 work, SSH or other external
operation.

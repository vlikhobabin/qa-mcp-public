## Why

The exact OSS-07-R1 successor's complete unpublished public-readiness payload
was measured at approximately 313 added production lines, so it cannot pass
ChangeRail's default 300-line complexity guard without a published bounded
decision. The decision must preserve the honest complete scope rather than
making whitespace, source classification, or scope bookkeeping changes solely
to evade the guard.

## What Changes

- Publish one metadata-only complexity decision for exact successor
  `oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity` at its
  authorization-time `3.inprogress` path.
- Set the maximum future authorization envelope to
  `production_loc_ceiling: 350` and
  `allow_new_authority_or_wire_protocol: false`.
- Reject whitespace deletion, source reclassification, and scope exclusion as
  complexity-gate workarounds; a later authorization/admission session must
  measure the complete exact successor payload honestly.
- Preserve exact SPDX `Apache-2.0`, the published OSS-07-I2 safety matrix, and
  the non-restoration of OSS-07-I1.
- Touch only board and OpenSpec decision metadata. Do not copy, modify,
  review, or publish the OSS-07-R1 implementation payload, and do not implement
  OSS-08 or OSS-09.

## Capabilities

### New Capabilities
- `qa-mcp-public-readiness-payload-complexity-decision`: Defines the exact
  successor binding, maximum 350-line production envelope, prohibited
  accounting workarounds, closed authority/wire flag, and future admission
  conditions for the existing OSS-07-R1 payload.

### Modified Capabilities
- None.

## Impact

The payload changes only OpenSpec workflow, capability, archive, and board
metadata. It changes no protocol tool, Python manager code, MCP provider setup,
runtime lab configuration, implementation source, test, fixture, evidence
payload, license file, or external system. It requires no live 1C runtime,
Vanessa MCP, EDT/meta snapshot, Windows execution, SSH, Apache service, network,
credential, mutation, release, or other external action. Exact SPDX
`Apache-2.0` remains unchanged.

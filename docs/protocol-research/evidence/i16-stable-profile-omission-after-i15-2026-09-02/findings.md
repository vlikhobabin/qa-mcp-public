# I16 Stable-Profile Omission After I15

## Decision

Published I15 commit `1be1829ee71b96f8c1c690c9fa55c2e8e14c1425`
used its one authorized canary, received no typed Session-1 receipt, invoked no
candidate and admitted no S4/I13 row. Exact cleanup passed, attribution stayed
`NOT-VERIFIABLE` and no retry authority remains.

The card-405 release gate is therefore satisfied through explicit omission:
`open_external_processor` is absent from the stable standalone profile and
public support matrix until a separately reviewed future target-bound
qualification publishes.

The unchanged code-level `standalone` catalog remains a 64-tool pre-stable
runtime inventory and still registers the dormant tool; that membership is not
stable admission. The declared stable release support profile contains 63
tools, and the public support matrix lists only those 63. A later
release/cutover change must enforce that allowlist before stable promotion.

## Preserved Lineage

This is a support decision, not source removal or certification. Dormant
product/test source, tests, tracked EPFs, runtime authority and all published
foundations remain unchanged. I13 remains active, unarchived and uncertified;
S4-R1 and S7 remain incomplete. I14 and I15 are not certification evidence.

## Roadmap Handoff

The published I15 card is under `4.done`, and its typed evidence index contains
nine entries. OSS-07 remains a `1.backlog` story with no OpenSpec artifacts. It
is the next separate card after I16 publishes, and its first future change must
bind the operator-approved `Apache-2.0` decision. I16 does not plan or implement
OSS-07.

## Execution Boundary

No live contour, SSH, historical-user, Windows, 1C, `/Execute`, canary, S4/S5/S7 or
candidate action ran. The payload is limited to evidence/docs/spec/board
surfaces and changes no product, test, fixture, tracked EPF, runtime authority
or license path.

## Why

Published I11 fixes and verifies the private main-predicate equivalence seam,
but it deliberately contains no exact-source execution evidence. The S4-R1
parent and project roadmap must distinguish that completed offline correction
from the still-open certification matrix before downstream work can resume.

## What Changes

- Publish a per-criterion reconciliation of the S4-R1 parent against exact
  published I11 evidence.
- Update the parent and roadmap so stale I10/I10a/I11 instructions are replaced
  by the remaining certification boundary.
- Prepare one exact apply-ready successor for the missing execution and cleanup
  evidence, bound to published I11 and fail-closed when that evidence is
  unavailable.
- Change documentation and OpenSpec workflow only; no protocol tool, Python
  manager, MCP provider, runtime configuration, product or test behavior
  changes.

## Capabilities

### New Capabilities

- `qa-mcp-post-i11-observation-certification-handoff`: Defines the evidence
  reconciliation and exact successor handoff required between published I11
  and S4-R1 certification.

### Modified Capabilities

- None.

## Impact

The payload affects only board metadata, the roadmap, curated decision
documentation and OpenSpec artifacts. It preserves Apache-2.0, adds no public
or wire surface, and requires only Linux offline inspection of published source
and evidence. The successor records the separate execution evidence floor but
does not perform it in this change.

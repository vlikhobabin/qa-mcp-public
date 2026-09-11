## Why

Published I11 closes the private observation predicate defect but deliberately
does not execute the exact-source certification matrix required by S4-R1. The
unchanged published bytes need a separate evidence-only gate before the parent
or downstream work can resume.

## What Changes

- Prove the exact published I11 product/test blob identities before every
  certification row.
- Run and retain the parent-required S3/S4/S5 observation and cleanup evidence
  against unchanged source.
- Bind S3/S4 to zero action and each S5 row to exactly one addressed
  confirmation under the published S5-R1 action contract, with no other input
  or side effect.
- Fail closed when access is unavailable, source drifts, a row fails or cleanup
  is incomplete; require a separate investigation instead of changing code.
- Update documentation and OpenSpec evidence state only. No protocol tool,
  Python manager, MCP provider, runtime configuration, product or test source
  change is authorized.

## Capabilities

### New Capabilities

- `qa-mcp-published-i11-observation-lifecycle-certification`: Defines the exact
  evidence-only certification gate for the published I11 observation seam.

### Modified Capabilities

- None.

## Impact

Delivery requires the separately authorized exact-source execution contour and
inherits only published S5-R1 authority for one addressed confirmation in each
of two S5 rows. It retains bounded public-safe evidence plus OpenSpec/board
updates, preserves Apache-2.0 and adds no API, wire field, authority or
behavior. Offline regression and deterministic unexecuted cross-builds
supplement, but do not replace, the required execution rows.

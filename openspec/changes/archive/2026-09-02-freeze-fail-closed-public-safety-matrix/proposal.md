## Why

OSS-07-I1 exhausted both same-card rescues with a cycle-3 `NO-GO`: its v3
public-safety matrix could still report a false PASS because executable bytes,
semantic row labels, expected RED outcomes and observed `D12`/`G18` flow were
not independently bound. I2 is the required linked design/investigation
successor before broader public-readiness or OSS-08 work can resume.

## What Changes

- Define one clean-room, successor-owned executable matrix with exact per-row
  `P`/`S` semantics and exact expected RED result tuple `46/14/5/D14`.
- Add a freeze record and outer offline oracle that bind matrix and
  `audit_design.py` helper bytes before execution.
- Require execution-only `D12` evidence, original-byte `G18` flow evidence for
  every non-email rule, a structured-context allowlist, and hostile mutations
  that must fail while an unchanged control passes.
- Retain the immutable I1 verdict/history digests and concise blocker state
  without importing, restoring or reconstructing its unavailable nine-path
  dirty payload.
- Preserve SPDX `Apache-2.0` as the already-approved OSS-07 constraint without
  creating licensing/governance files or implementing the rest of OSS-07.

## Capabilities

### New Capabilities

- `qa-mcp-fail-closed-public-safety-matrix`: Defines the frozen offline matrix,
  independent byte/result oracle, context allowlist and mutation-proof evidence
  required to close the carried I1 false-PASS class.

### Modified Capabilities

- none.

## Impact

This is an offline design/investigation change affecting only its card,
OpenSpec artifacts and the successor-owned curated design/freeze/verifier
surface declared in the design. It changes no protocol tools, Python manager
code, MCP provider setup, runtime lab configuration, production source or test
source. It requires no live 1C runtime, TestClient, Vanessa MCP, EDT/meta
snapshot, Windows, SSH, Apache service, network or predecessor runtime
evidence. OSS-08 and the baseline OSS-07/roadmap cards remain unchanged.

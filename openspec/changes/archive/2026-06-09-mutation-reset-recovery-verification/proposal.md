## Why

Mutation scenarios are unsafe to promote unless the lab can prove that every
case resets cleanly and leaves a clear recovery path. V3 needs a dedicated
verification change so the reset and rollback story is explicit before any
corpus row is treated as trustworthy.

## What Changes

- Define the recovery sequence for V3 mutation cases: before, action, post and
  reset.
- Require deterministic rollback to the V1 baseline after each mutation or
  failed mutation attempt.
- Record the candidate action frame range separately from bootstrap,
  background refresh and cleanup traffic.
- Capture recovery expectations and residual-risk notes as part of the proof
  bundle.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V3 fixture behavior gains explicit recovery and reset
  verification requirements for local mutation cases.

## Impact

- Client fixture BSL and managed form code in the `vanessa_client` infobase.
- Reviewable capture summaries and later corpus evidence.
- Requires live 1C runtime evidence for verification.

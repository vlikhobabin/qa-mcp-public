## Why

The real-demo mutation pilot must end with a clear publication decision so
reviewers can distinguish accepted mappings from candidate evidence, rejected
rows and blockers. Without publication, a recoverable visual mutation could be
mistaken for accepted protocol knowledge.

## What Changes

- Publish compact evidence for selected, attempted and rejected real-demo
  mutation rows.
- State final row status: `accepted`, `candidate`, `rejected`, `blocked`,
  `partial` or `timeout`.
- Link target selection, manifest validation, guarded execution, recovery and
  frame-isolation evidence.
- Keep accepted output empty unless same-action replay, direct Python-manager
  probe or accepted typed contract proof supports the row.
- Record any residual demo data with owner and residual risk.
- Refresh `docs/protocol-research/api-inventory/case-api-map.json` and
  regenerate `docs/protocol-research/coverage-report.md` when row statuses
  changed.
- State whether the mutation scheme is proven well enough to plan the 30-50
  row batch corpus card per `docs/protocol-research/methodology.md`.
- Keep raw captures, full UI dumps, platform logs and generated replay payloads
  outside reviewed git.

## Capabilities

### New Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: Real demo mutation corpus pilots publish explicit
  accepted/candidate/rejected/blocked/partial/timeout decisions with compact
  evidence links and proof-gated accepted output.

## Impact

- Protocol research evidence docs, evidence index and accepted-output or
  candidate-output summaries under `docs/protocol-research/evidence/`.
- No new live 1C runtime execution is required by publication itself.
- Publication consumes compact evidence from the preceding card-61 changes.

## Why

V2 safe-action evidence must remain candidate until replay, direct
Python-manager probe or typed contract evidence proves the same non-mutating
action. The comparison and accepted-mapping tools need explicit gates so a
joined action frame range is not promoted by accident.

## What Changes

- Extend safe-action comparison and accepted-mapping gates for V2 action rows.
- Require stable normalized hashes, action result markers and replay/probe or
  typed contract proof before a row becomes accepted.
- Keep `candidate`, `blocked`, `partial`, `timeout`, `rejected` and
  `unsupported` rows visible in comparison output.
- Preserve raw replay payloads under ignored runtime paths and publish only
  compact proof links.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V2 safe-action tooling gains explicit comparison,
  replay/probe and accepted-mapping gates.

## Impact

- Comparison and accepted-mapping tools under `tools/protocol-research/`.
- Protocol research docs and reviewed evidence summaries.
- Requires repeated compact evidence or probe/replay summaries for acceptance
  verification.

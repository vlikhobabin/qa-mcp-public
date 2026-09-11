## Why

Downstream V3/V4 and demo pilot cards need one durable V2 proof record that
states what was reviewed, whether the row is accepted or candidate, and why.
Publication must preserve the V2 safety boundary while linking compact evidence.

## What Changes

- Publish the first focused V2 safe-action proof report with selected rows,
  action/background/recovery ranges, proof route and final status.
- Update protocol docs, evidence index and accepted-mapping or candidate outputs
  with compact links.
- Record residual risk and provider gaps when the row remains candidate,
  blocked, partial, timeout, rejected or unsupported.
- Keep raw captures, platform logs and generated replay/probe payloads out of
  reviewed git.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: The lab publishes a durable first focused V2
  safe-action proof decision with accepted or candidate status and evidence
  links.

## Impact

- Protocol research README/status docs, evidence index and V2 safe-action
  evidence directories.
- Accepted mapping output only changes if proof gates are satisfied.
- Requires completed subset, capture, frame isolation and proof-attempt changes;
  no new live 1C runtime execution is required by publication itself.

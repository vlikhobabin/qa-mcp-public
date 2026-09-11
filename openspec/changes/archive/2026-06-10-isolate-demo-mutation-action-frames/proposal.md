## Why

Real-demo mutation rows cannot become protocol evidence unless the action
traffic is separated from bootstrap, background refresh and recovery traffic.
The guarded pilot may prove runtime behavior, but frame isolation decides
whether a row can be considered for accepted or candidate corpus status.

## What Changes

- Review guarded-pilot phase events and captured traffic to identify action,
  background/refresh and recovery ranges where available.
- Preserve dynamic-field, normalized-hash, operation-token and response-marker
  notes for real-demo mutation rows when the evidence supports them.
- Classify rows as `accepted`, `candidate`, `rejected`, `blocked`, `partial`
  or `timeout` according to frame isolation and proof status.
- Keep ambiguous or missing frame ranges visible with owner route and residual
  risk.
- Do not execute new mutations in this change.

## Capabilities

### New Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: Real demo mutation evidence requires separated action,
  background and recovery ranges before any row can be considered for accepted
  corpus output.

## Impact

- Protocol analyzer/reviewer output and compact frame-isolation evidence under
  `.artifacts/openspec/isolate-demo-mutation-action-frames/<run-id>/`.
- May consume ignored runtime capture output produced by
  `execute-demo-mutation-guarded-pilot`.
- Does not start a new 1C process or perform additional UI mutations.

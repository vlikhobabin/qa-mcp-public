## Why

Manual bridge tokens violate the ordinary-member flow and expose long-lived secrets to prompts.

## What Changes

- redeem a short-lived server/project/user-bound onboarding grant once and store only protected bridge refresh/registration state while retaining explicit-token advanced compatibility.
- Add fail-closed validation, redaction and lifecycle evidence.
- Document the versioned contract consumed by the root workstation orchestrator.

## Capabilities

### New Capabilities
- `bridge-bootstrap-client`: Team bridge bootstrap grant client.

### Modified Capabilities
- None.

## Impact

This is component-owned behavior in /opt/ai-dev-suite-for-1c/qa-mcp. Dependency: root f5-40-c10-team-git-onboarding-contract. The root repository owns the exchange/orchestration contract and consumes only an independently reviewed component commit.

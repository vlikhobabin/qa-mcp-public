## Why

Root onboarding needs evidence that redeemed identity survives registration, heartbeat, restart and refresh.

## What Changes

- extend bridge lifecycle smoke/evidence to prove bootstrap redemption, protected refresh, per-user/project attribution, restart recovery and exact process cleanup.
- Add fail-closed validation, redaction and lifecycle evidence.
- Document the versioned contract consumed by the root workstation orchestrator.

## Capabilities

### New Capabilities
- `bridge-bootstrap-evidence`: Team bridge bootstrap registration evidence.

### Modified Capabilities
- None.

## Impact

This is component-owned behavior in /opt/ai-dev-suite-for-1c/qa-mcp. Dependency: team-bridge-bootstrap-token-client. The root repository owns the exchange/orchestration contract and consumes only an independently reviewed component commit.

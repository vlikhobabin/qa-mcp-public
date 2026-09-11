## Why

A full-path registry URL accidentally configured as a base URL makes the
host-agent POST to `/`, but the current health diagnostic collapses the
registry's actionable HTTP response to `registry-rejected`. Operators should
be able to identify this field misconfiguration from bounded, secret-safe
host-agent output without reproducing a two-plane stand failure.

## What Changes

- Report non-2xx registration responses with the HTTP status in health state
  and with a logged body snippet bounded to 512 bytes.
- Warn once during startup when an explicitly configured registry URL has no
  endpoint path, while preserving the documented verbatim full-URL contract.
- Add a cross-repository contract test that sends the real Go registration
  client's request through the root `team_registry.py` router and proves the
  full `/v1/bridges/register` path, successful registration, and audit event.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bridge-bootstrap-client`: Require actionable, bounded and secret-safe
  registration-rejection diagnostics and explicit warning of endpoint-less
  registry URLs in both explicit-token and bootstrapped registration flows.

## Impact

This component-owned change touches the Windows host-agent Go registration
client, startup logging, Go/Python contract tests, the component OpenSpec spec,
and delivery evidence. It does not change the registration payload, append or
rewrite URL paths, change an MCP provider contract, or alter runtime lab
configuration. The router contract test reads the root-owned
`deploy/docker/bin/team_registry.py` and schemas without modifying the root
repository. Verification is offline and requires neither live 1C runtime nor
Vanessa, EDT/meta snapshots, protocol captures, or business-data mutation.

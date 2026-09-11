## ADDED Requirements

### Requirement: qa-mcp gates startup on the suite license broker, fail-closed
When the license gate is enabled, qa-mcp startup SHALL run the native broker
`ai1c-license check --component qa-mcp --json` and **ALLOW startup only when ALL**
hold: the broker exit code is `0`, the response has `allowed: true`, the status is
`licensed` **or** `offline_grace`, and the response schema + component match.
Otherwise startup SHALL **fail closed** (the process exits non-zero without
serving tools). The broker path and timeout SHALL be configurable via environment.

#### Scenario: A licensed broker response allows startup
- **WHEN** the gate is enabled and the broker returns exit `0` with `allowed:true`
  and status `licensed` for component `qa-mcp`
- **THEN** qa-mcp starts and serves its tools normally

#### Scenario: Every deny case fails closed
- **WHEN** the gate is enabled and the broker returns any of: non-zero exit,
  `allowed:false`, missing/unlaunchable broker, timeout, malformed JSON,
  unsupported schema, component mismatch, no lease, denied entitlement, expired
  lease/grace, invalid signature, unknown/revoked key, or fingerprint mismatch
- **THEN** qa-mcp does **not** serve tools and exits non-zero with an actionable,
  diagnostic-safe message

### Requirement: Offline grace starts but is surfaced diagnostic-safely
When the broker returns `offline_grace` (allowed), qa-mcp SHALL start **and**
surface the grace state — including the broker's grace timestamp — in
diagnostic-safe startup output, so the operator knows the lease is running on the
offline window.

#### Scenario: Offline grace is reported without sensitive data
- **WHEN** the broker returns exit `0`, `allowed:true`, status `offline_grace`
- **THEN** qa-mcp starts
- **AND** it surfaces the offline-grace state + grace timestamp in startup output
- **AND** the output contains no keys, raw hardware ids, customer/1C/infobase/path
  data, traces, screenshots or credentials

### Requirement: The gate is env-flagged and OFF by default
The gate SHALL run only when explicitly enabled by environment
(`QA_MCP_LICENSE_GATE`); when unset, qa-mcp SHALL start with **no broker call** and
behave exactly as the current free delivery.

#### Scenario: Unset flag preserves current behavior
- **WHEN** `QA_MCP_LICENSE_GATE` is unset
- **THEN** qa-mcp starts without invoking the broker and serves tools as today

#### Scenario: The contract matrix is covered by tests with a fake broker
- **WHEN** the gate logic is tested
- **THEN** a fake broker exercises allowed / offline_grace / denied / malformed /
  missing-broker / timeout, each asserting the correct allow-or-fail-closed outcome
  with no live server or real broker binary

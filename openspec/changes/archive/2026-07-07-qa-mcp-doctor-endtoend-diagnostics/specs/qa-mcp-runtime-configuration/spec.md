## ADDED Requirements

### Requirement: Doctor configuration is centralized and secret-safe
The qa-mcp runtime settings accessor SHALL centralize non-secret diagnostic
configuration used by `qa_mcp_doctor`, including proxy bearer-token environment
presence, host-agent address, host-agent token presence, client endpoint, and
COM doctor inputs. Settings and diagnostic results MUST expose presence booleans
or redacted summaries instead of secret values.

#### Scenario: Bearer-token presence is parsed from an explicit environment
- **WHEN** tests build settings from an explicit environment mapping
- **THEN** the settings can report whether `QA_MCP_BEARER_TOKEN` is present
- **AND** the settings object does not expose the bearer token value through a
  diagnostic field

#### Scenario: Host-agent token presence is reported without the token
- **WHEN** the host-agent token is configured
- **THEN** doctor settings expose that the token is present
- **AND** no result field contains the token value

#### Scenario: Missing optional doctor inputs produce skipped checks
- **WHEN** optional COM doctor or host-agent inputs are absent
- **THEN** `qa_mcp_doctor` marks dependent checks as skipped with stable reason
  codes
- **AND** the missing inputs are reported by environment-variable name rather
  than by a raw credential or local secret value

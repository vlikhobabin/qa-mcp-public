## ADDED Requirements

### Requirement: Doctor reports workstation bsl-agent supervision separately
`qa_mcp_doctor` SHALL include a separate `bsl_agent_supervision` check derived from authenticated host-agent health. Disabled optional supervision SHALL be reported as a passing solo-mode state; configured ready supervision SHALL report bounded state, version, and restart count; configured non-ready supervision SHALL fail with an actionable readiness code.

#### Scenario: Solo mode is healthy
- **WHEN** host-agent health reports `bsl_agent.configured=false`
- **THEN** the doctor check passes with state `disabled` and does not make the overall doctor incomplete.

#### Scenario: Configured helper is ready
- **WHEN** host-agent health reports a ready configured helper
- **THEN** the doctor check passes and includes version and restart count without local paths.

#### Scenario: Configured helper is not ready
- **WHEN** host-agent health reports starting, backoff, failed-closed, or stopped for a configured helper
- **THEN** the doctor check fails with bounded lifecycle detail.

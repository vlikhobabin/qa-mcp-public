## ADDED Requirements

### Requirement: Doctor status distinguishes required failures from optional gaps
`qa_mcp_doctor` SHALL return `ok=false` and `status=fail` when any required
check fails. Optional skipped probes SHALL keep `ok=true` and produce
`status=partial` when every required check passes. Doctor results MUST identify
which checks are required without exposing credentials.

#### Scenario: Optional probe skipped yields partial success
- **WHEN** all required doctor checks pass
- **AND** an optional effective-user probe is unavailable
- **THEN** the doctor result reports `ok=true`
- **AND** the doctor result reports `status=partial`
- **AND** the skipped optional check is marked as not required.

#### Scenario: Required auth failure remains failed
- **WHEN** the required bearer-token check fails
- **THEN** the doctor result reports `ok=false`
- **AND** the doctor result reports `status=fail`
- **AND** the failed check is marked as required.

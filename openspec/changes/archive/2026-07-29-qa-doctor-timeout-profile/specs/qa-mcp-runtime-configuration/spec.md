## ADDED Requirements

### Requirement: Doctor COM timeout is centrally configured
The qa-mcp settings accessor SHALL parse
`QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS` as the default timeout for
`qa_mcp_doctor` COM checks. CLI and MCP tool timeout arguments MUST override
the environment setting for debugging, and doctor diagnostics MUST expose only
the effective numeric timeout.

#### Scenario: Doctor consumes environment timeout by default
- **WHEN** `QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS=90` is present
- **AND** `qa_mcp_doctor` runs without an explicit timeout argument
- **THEN** the COMConnector doctor probe receives `timeout_sec=90`
- **AND** the check data reports `timeout_sec=90` without secret values.

#### Scenario: Explicit doctor timeout overrides profile
- **WHEN** `QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS=90` is present
- **AND** a caller passes `timeout_sec=1.5`
- **THEN** the COMConnector doctor probe receives `timeout_sec=1.5`
- **AND** the reported effective timeout is `1.5`.

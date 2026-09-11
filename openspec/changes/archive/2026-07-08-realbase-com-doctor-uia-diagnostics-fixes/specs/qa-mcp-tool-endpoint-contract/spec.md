## ADDED Requirements

### Requirement: qa_mcp_doctor always returns a complete ordered chain

The `qa_mcp_doctor` tool SHALL always return one ordered pass/fail/skipped chain.
A failure inside any individual check — including a timeout or connection error
raised by the COMConnector-doctor probe — SHALL be recorded as a structured
`fail` leg for that check and MUST NOT propagate as an unhandled exception that
aborts the remaining diagnostics.

#### Scenario: A slow or busy COM leg does not crash the chain

- **WHEN** the COMConnector-doctor probe raises a `TimeoutError` or connection
  error (for example because the target file base is busy)
- **THEN** `qa_mcp_doctor` SHALL record the `com_connector_doctor` check as a
  `fail` with code `com-doctor-probe-failed` and SHALL still return the remaining
  checks in the ordered chain

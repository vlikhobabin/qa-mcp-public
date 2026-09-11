## ADDED Requirements

### Requirement: Connection diagnostics avoid Designer metadata dumps
The qa-mcp connection diagnostics SHALL NOT invoke Designer metadata dump
commands such as `DESIGNER /DumpConfigToFiles` during ordinary setup,
connection, catalog-name, or open-link troubleshooting. Diagnostics MUST use
light-weight routes such as MCP/HTTP auth checks, host-agent health, live
TestClient descriptor/window evidence, configured metadata descriptors, or
optional COM read-smoke checks.

#### Scenario: Doctor does not spawn Designer
- **WHEN** an operator runs `qa_mcp_doctor` or `qa-mcp-doctor` to diagnose a
  model-B setup
- **THEN** the diagnostic chain uses host-agent `/version` and `/health`,
  TestClient TPort smoke, window evidence, and optional COM doctor checks
- **AND** it does not call host-agent `/platform/execute` with executable
  `designer`, `1cv8 DESIGNER`, or `/DumpConfigToFiles`.

#### Scenario: Form-level guidance remains light-weight
- **WHEN** a form-level tool cannot infer a target and returns
  `open-link-required` or catalog-name guidance
- **THEN** the guidance points to `qa_mcp_doctor`, descriptor/open-link input,
  metadata-provider input, or optional COM read-smoke routes
- **AND** it does not recommend Designer metadata dump as a routine diagnostic
  fallback.

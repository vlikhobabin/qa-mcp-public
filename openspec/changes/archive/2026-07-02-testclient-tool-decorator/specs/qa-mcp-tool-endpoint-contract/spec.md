## ADDED Requirements

### Requirement: Endpoint tools honor the attached TestClient endpoint
Every MCP tool that opens a TestClient protocol connection SHALL use the endpoint recorded by `attach_test_client` when the caller omits `host` and `port`.

#### Scenario: Attached endpoint is reused
- **WHEN** `attach_test_client` records host `X` and port `Y`
- **AND** an endpoint-touching MCP tool is called without explicit `host` or `port`
- **THEN** the tool connects to `X:Y`
- **AND** it does not fall back to `127.0.0.1:15381`

#### Scenario: Explicit endpoint overrides attachment
- **WHEN** an endpoint-touching MCP tool is called with explicit `host` and `port`
- **THEN** the tool uses the explicit endpoint for that call

### Requirement: Endpoint tool errors are structured
Endpoint-touching MCP tools SHALL return structured error results for attachment resolution failures, invalid capture names and invalid argument values rather than raising raw tracebacks through the MCP boundary.

#### Scenario: Invalid capture is reported as a structured result
- **WHEN** a wrapped endpoint-touching tool receives a bad `capture` value
- **THEN** the tool returns a structured error result
- **AND** the result identifies the invalid input without exposing a raw traceback

#### Scenario: Existing write-path verdicts are preserved
- **WHEN** the underlying write or replay path returns a structured `retarget_failed` or `send_timeout` result
- **THEN** the endpoint wrapper returns that structured verdict unchanged except for allowed attachment metadata

### Requirement: Local boot tools are unavailable in remote-client mode
MCP tools that start local 1C platform processes SHALL fail closed in remote-client mode with the standard structured local-only guidance.

#### Scenario: Measure scenario is guarded in remote mode
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `measure_scenario` is called
- **THEN** it returns the structured local-only "not served here" result
- **AND** it does not attempt to execute local `dbgs`, `1cv8`, or Apache service commands

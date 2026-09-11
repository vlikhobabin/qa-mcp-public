## ADDED Requirements

### Requirement: Attach endpoint behavior is registry-tested
The qa-mcp offline test suite SHALL include a registry-driven contract test that covers every endpoint-touching MCP tool and verifies attach-aware endpoint selection.

#### Scenario: Endpoint registry contract uses attached endpoint
- **WHEN** the test attaches sentinel host `X` and port `Y`
- **AND** each endpoint-touching registered tool is invoked without explicit `host` or `port`
- **THEN** the monkeypatched connector observes `X:Y` for every covered tool
- **AND** the test fails if any covered tool falls back to the default endpoint

#### Scenario: Endpoint tool classification is complete
- **WHEN** the registered MCP tool list is inspected by the contract test
- **THEN** every endpoint-touching tool is either covered by an endpoint assertion or explicitly classified as not opening a TestClient protocol connection

### Requirement: Wrapper failure modes are tested offline
The qa-mcp offline test suite SHALL prove that wrapper-level failure modes return structured results without live 1C runtime.

#### Scenario: Bad wrapper inputs return structured results
- **WHEN** a wrapped endpoint tool receives invalid arguments or an invalid capture value in the offline contract test
- **THEN** the returned value is a structured error result
- **AND** no raw traceback crosses the MCP tool boundary

#### Scenario: Remote mode blocks local measurement startup
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `measure_scenario` is exercised by the offline test suite
- **THEN** the returned value is the structured local-only result
- **AND** no local platform executable is required

## ADDED Requirements

### Requirement: Extracted protocol helpers preserve endpoint wrapper contracts

Endpoint-touching MCP tool wrappers SHALL keep using the active attached
TestClient endpoint, explicit endpoint overrides and structured wrapper errors
after their wire-level implementation is moved into protocol modules.

#### Scenario: Attached endpoint still reaches extracted helper

- **WHEN** `attach_test_client` records host `X` and port `Y`
- **AND** an endpoint-touching tool calls an extracted protocol helper without
  explicit host or port arguments
- **THEN** the helper connects to `X:Y`
- **AND** it does not fall back to `127.0.0.1:15381`

#### Scenario: Structured protocol verdicts pass through wrapper

- **WHEN** an extracted protocol helper returns a structured error or blocked
  result
- **THEN** the MCP wrapper returns that verdict unchanged except for existing
  attachment metadata
- **AND** no raw traceback crosses the MCP boundary

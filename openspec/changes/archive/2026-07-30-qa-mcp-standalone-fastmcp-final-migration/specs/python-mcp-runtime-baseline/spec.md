## ADDED Requirements

### Requirement: qa-mcp uses standalone FastMCP without MCP surface drift
qa-mcp SHALL use standalone FastMCP with the suite-approved exact FastMCP pin
and an MCP SDK 1.x upper bound. The migration SHALL preserve the public MCP
tool names, descriptions, input schemas and output schemas captured before the
migration.

#### Scenario: Runtime dependencies are pinned
- **WHEN** the component manifest and lock file are inspected
- **THEN** FastMCP resolves to `3.4.2`
- **AND** the MCP SDK dependency cannot resolve to version 2.x.

#### Scenario: Tool surface comparison is retained
- **WHEN** before and after tool surface snapshots are compared
- **THEN** the tool count remains `68`
- **AND** no tool is added, removed or schema-changed by the framework
  migration.

#### Scenario: HTTP and stdio transports remain covered
- **WHEN** focused offline MCP tests run after migration
- **THEN** stdio startup remains covered by an MCP client roundtrip
- **AND** the direct HTTP JSON-RPC UTF-8 body gate remains covered by unit
  tests.

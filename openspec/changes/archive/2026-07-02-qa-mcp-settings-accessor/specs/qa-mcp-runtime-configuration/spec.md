## ADDED Requirements

### Requirement: QA MCP environment settings are parsed through one accessor

The Python manager SHALL document and parse supported `QA_MCP_*` environment
variables through a centralized settings accessor. Modules MUST NOT duplicate
remote-client truth parsing or OData default constants after migration.

#### Scenario: Settings can be built from an explicit environment mapping

- **WHEN** tests call `Settings.from_env()` with an explicit environment mapping
- **THEN** the returned settings object reflects that mapping
- **AND** the test does not need to mutate process-global environment variables

#### Scenario: Remote-client truth parsing is centralized

- **WHEN** modules need to decide whether the runtime is a remote-client contour
- **THEN** they use the settings/accessor path
- **AND** the truthy and default false behavior matches the pre-refactor code

#### Scenario: OData defaults are defined once

- **WHEN** the OData client and regression command line need default host, port
  or path values
- **THEN** they import the defaults from the shared configuration path
- **AND** the effective default values remain unchanged

#### Scenario: Supported QA_MCP variables are documented together

- **WHEN** a maintainer needs to inspect supported qa-mcp environment variables
- **THEN** the settings module names each supported `QA_MCP_*` variable and its
  default behavior in one place

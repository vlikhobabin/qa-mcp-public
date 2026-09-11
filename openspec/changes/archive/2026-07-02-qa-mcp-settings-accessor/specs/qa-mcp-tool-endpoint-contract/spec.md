## ADDED Requirements

### Requirement: Remote-client local-only gating uses centralized settings

Local-only MCP tool guards SHALL use the centralized settings/accessor path for
remote-client detection while preserving the existing structured local-only
result.

#### Scenario: Remote-client mode still blocks local boot tools

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** a local-boot tool such as `measure_scenario` is called
- **THEN** the tool returns the standard local-only structured result
- **AND** it does not attempt to execute local platform commands

#### Scenario: Default local mode is preserved

- **WHEN** `QA_MCP_REMOTE_CLIENT` is unset
- **THEN** local-boot guards behave as they did before the settings accessor
- **AND** no new environment variable is required

## ADDED Requirements

### Requirement: Platform version selection is provided by a leaf module

The Python manager SHALL expose active platform-family selection and live
platform version detection from a cycle-free `qa_mcp.versioning` module that
protocol code can import at module load time. Existing regression imports MUST
remain compatible.

#### Scenario: Protocol modules import versioning without lazy cycle workaround

- **WHEN** protocol modules select bundled protocol assets
- **THEN** they import version helpers from `qa_mcp.versioning` at top level
- **AND** they do not carry lazy import comments whose only purpose is avoiding
  a `regression.versioning` cycle

#### Scenario: Regression versioning remains compatible

- **WHEN** existing callers import `active_version_key` from
  `qa_mcp.regression.versioning`
- **THEN** the import still succeeds
- **AND** it returns the same platform-family key as the leaf module

#### Scenario: Existing version policy is preserved

- **WHEN** `QA_MCP_PLATFORM_VERSION` is unset, a bare supported family, a full
  supported platform version or an unsupported value
- **THEN** version selection returns or rejects values exactly as it did before
  the move

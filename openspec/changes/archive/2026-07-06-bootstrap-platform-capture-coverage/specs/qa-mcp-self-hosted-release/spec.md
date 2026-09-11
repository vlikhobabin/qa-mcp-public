## ADDED Requirements

### Requirement: Bootstrap selects only capture-covered platform families by default

The qa-mcp Windows bootstrap SHALL choose a 1C platform executable using parsed
semantic platform versions, not lexicographic path order. When `-PlatformExe` is
omitted and multiple installed platform families are present, bootstrap MUST
prefer the newest candidate whose family has direct bundled capture coverage.

#### Scenario: Mixed 8.3 and 8.5 host defaults to direct coverage

- **WHEN** bootstrap auto-discovers installed `1cv8.exe` candidates for
  `8.3.27.2130` and `8.5.1.1343`
- **THEN** it selects the `8.3.27.2130` executable because the `8.3` family has
  a populated bundled capture set
- **AND** the selection does not depend on lexicographic sorting of the full
  executable path

### Requirement: Bootstrap diagnoses explicit platform families without direct captures

The qa-mcp Windows bootstrap SHALL warn loudly when the selected platform family
has no direct bundled capture set. The warning MUST name the selected platform
version, explain whether a validated fallback is used, and tell the operator to
use `-PlatformExe` when they need a direct-covered platform.

#### Scenario: Explicit 8.5 selection uses documented fallback warning

- **WHEN** an operator supplies `-PlatformExe` for `8.5.1.1343`
- **THEN** bootstrap keeps that platform selection and passes
  `QA_MCP_PLATFORM_VERSION=8.5.1.1343` into the container
- **AND** it prints a warning that 8.5 has no direct bundled capture set and
  uses the validated 8.3 protocol-data fallback

#### Scenario: Unsupported family does not report a green deployment

- **WHEN** the selected platform family has neither direct capture coverage nor
  a declared fallback
- **THEN** bootstrap stops before reporting success
- **AND** the diagnostic names `-PlatformExe` as the way to choose a supported
  executable

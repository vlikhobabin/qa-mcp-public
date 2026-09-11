## ADDED Requirements

### Requirement: Bootstrap prints the canonical MCP path

The qa-mcp bootstrap SHALL print MCP client configuration that uses the
canonical HTTP MCP path `/mcp` without a trailing slash. Active delivery
runbooks MUST use the same path for MCP client setup and troubleshooting.

#### Scenario: Printed MCP URL is routable
- **WHEN** bootstrap prints the MCP server URL for port `8000`
- **THEN** the URL is `http://127.0.0.1:8000/mcp`
- **AND** the printed guidance does not instruct the operator to keep a
  trailing `/mcp/`

#### Scenario: Runbooks match bootstrap
- **WHEN** an operator follows active delivery runbook MCP setup examples
- **THEN** the configured URL uses `/mcp`
- **AND** troubleshooting for `not_found` points at removing a trailing slash

### Requirement: Bootstrap guidance handles Windows setup edge cases

Active qa-mcp delivery runbooks SHALL explicitly cover Docker Desktop readiness,
empty 1C password invocation, manual PowerShell UTF-8 request bytes, and
explicit `-WindowTitle` selection for ambiguous 1C windows.

#### Scenario: Empty password is omitted
- **WHEN** an infobase user has a blank password
- **THEN** the runbook instructs the operator to omit `-Password`
- **AND** it does not instruct the operator to pass `-Password ""`

#### Scenario: Docker readiness is checked before install
- **WHEN** an operator starts a Windows model-B install
- **THEN** the runbook requires `docker info` or equivalent Docker Desktop
  readiness before continuing

#### Scenario: Manual Cyrillic request uses UTF-8 bytes
- **WHEN** the runbook shows a manual PowerShell HTTP request that can contain
  Cyrillic payload text
- **THEN** the example builds the request body with
  `[System.Text.Encoding]::UTF8.GetBytes(...)`

#### Scenario: Ambiguous window title has an explicit override
- **WHEN** automatic window matching is missing or generic
- **THEN** the runbook instructs the operator to rerun bootstrap with
  `-WindowTitle` set to a stable title fragment

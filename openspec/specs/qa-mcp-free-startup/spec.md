# qa-mcp Free Startup Specification

## Purpose

Define the invariant that qa-mcp is distributed and started without its own
product-license activation, entitlement, lease, broker, key, or license server,
while keeping the separate 1C platform licensing prerequisite explicit.

## Requirements

### Requirement: qa-mcp startup is independent of product licensing

qa-mcp startup MUST NOT activate a qa-mcp product license, check an
entitlement or lease, invoke a product-license broker, or deny MCP service
because qa-mcp product-license material is absent, invalid, expired, or
unreachable.

#### Scenario: Startup has no product-license configuration

- **WHEN** qa-mcp starts without legacy product-license environment variables
- **THEN** it reaches its configured MCP transport without invoking
  `ai1c-license` or another product-license broker

#### Scenario: Legacy license variables are set

- **WHEN** qa-mcp starts with `QA_MCP_LICENSE_GATE`,
  `QA_MCP_LICENSE_BROKER`, and `QA_MCP_LICENSE_TIMEOUT` set to arbitrary values
- **THEN** those values are ignored without being disclosed
- **AND** qa-mcp reaches its configured MCP transport without launching a
  broker or performing a product-license decision

#### Scenario: Product-license services and material are unavailable

- **WHEN** no qa-mcp entitlement, lease, broker executable, activation server,
  product key, or license server is available
- **THEN** qa-mcp startup is not denied for that reason

### Requirement: 1C platform licensing remains a separate prerequisite

Free qa-mcp product startup MUST NOT be documented or implemented as a bypass
of the 1C platform's own installation and license requirements.

#### Scenario: Free qa-mcp behavior is described

- **WHEN** current startup or delivery guidance explains that qa-mcp requires
  no product license
- **THEN** it distinguishes that policy from the legal requirement for a
  working, properly licensed 1C platform installation

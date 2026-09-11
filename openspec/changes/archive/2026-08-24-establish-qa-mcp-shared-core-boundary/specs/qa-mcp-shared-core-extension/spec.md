## ADDED Requirements

### Requirement: MCP applications are composed from explicit public contracts
qa-mcp SHALL expose a public application factory that accepts explicit runtime
settings, executor and tool profile inputs without importing downstream product
code.

#### Scenario: Standalone application is constructed
- **WHEN** the standalone entrypoint constructs the MCP application
- **THEN** it supplies the public standalone executor and tool profile
- **AND** the server does not require Runtime Proxy, live-mcp or Team modules.

#### Scenario: Fake downstream executor is constructed offline
- **WHEN** a contract test supplies a fake executor implementing the public
  interface
- **THEN** the application is created and its selected tools execute through
  that fake without importing AI for 1C code.

### Requirement: Tool profiles register only supported tools
The application factory MUST register tools from an explicit named profile and
MUST NOT register omitted tools as structured-unavailable placeholders.

#### Scenario: Standalone and research profiles differ
- **WHEN** the standalone and research profiles are listed offline
- **THEN** each exposes its documented deterministic tool set
- **AND** research-only tools are absent from the standalone registry.

### Requirement: Shared operations own behavior semantics
MCP wrappers and scenario steps SHALL invoke common qa-mcp operation functions
for equivalent TestClient actions and SHALL preserve one result/error taxonomy.

#### Scenario: Equivalent action paths return the same verdict class
- **WHEN** an MCP tool and a scenario step execute the same fake operation
- **THEN** both use the shared operation implementation
- **AND** success, blocked, ambiguous and failure verdict classes agree.

### Requirement: Runtime state is isolated per application
Attachment, target, session and executor state MUST belong to an explicit
application/runtime context and MUST NOT leak between separately constructed
servers.

#### Scenario: Two application instances attach different endpoints
- **WHEN** two servers attach different fake TestClient endpoints
- **THEN** each operation uses only its own attachment
- **AND** stopping one context does not clear or mutate the other.

### Requirement: Public extension contracts remain product neutral
Public contract models MUST describe generic target identity, lifecycle,
protocol/display primitives, artifacts and operation results without requiring
private AI for 1C identifiers or transports.

#### Scenario: Public dependency boundary is scanned
- **WHEN** public package imports and build metadata are inspected
- **THEN** no reverse dependency on Runtime Relay, RPW, live-mcp, Team or a
  private AI for 1C package is present.

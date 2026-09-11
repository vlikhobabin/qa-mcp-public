## ADDED Requirements

### Requirement: Project lifecycle uses one immutable target
Every project-bound TestClient launch, attach and status SHALL use the target
identity and physical profile frozen in the application context.

#### Scenario: Declared target launches
- **WHEN** project lifecycle launches its preconfigured file or client-server
  target
- **THEN** attachment and generated session report the same logical target,
  fingerprint and binding generation.

#### Scenario: Existing target is attached
- **WHEN** a non-mutating observation proves the configured endpoint belongs to
  the declared target/generation
- **THEN** qa-mcp records a non-owned target-bound session.

#### Scenario: Owned remote launch reports canonical raw identity
- **WHEN** the host agent reports one explicit positive integer PID and TPort
  plus one explicit non-empty lifecycle id in the top-level launch result, raw
  `client_target` and raw lifecycle handle
- **THEN** qa-mcp admits the session only when all three projections agree
  exactly.

### Requirement: Admission blocks caller retargeting
Project-mode lifecycle MUST reject caller-supplied path, connection, env file,
endpoint, target or rebind values before side effects.

#### Scenario: Direct override is supplied
- **WHEN** a caller supplies an alternate physical or logical target value
- **THEN** lifecycle returns `runtime-target-override-forbidden`
- **AND** application target/session state is unchanged.

### Requirement: Missing or mismatched target is non-mutating
qa-mcp MUST return typed blocked outcomes for unavailable configuration, stale
generation, mismatched observation and unproven attach identity before
lifecycle mutation.

#### Scenario: Declared target is unavailable
- **WHEN** preflight cannot establish its configured target/platform
- **THEN** no Apache, Xvfb, TestClient, host-agent or protocol call starts.

#### Scenario: Legacy fallback exists
- **WHEN** a default env or alternate infobase exists after declared-target
  failure
- **THEN** project lifecycle ignores it and records no session.

#### Scenario: Raw remote identity is incomplete or mistyped
- **WHEN** project-bound remote launch reports a missing, zero, boolean or
  string PID or TPort, or a missing, blank or alias-only `client_target`
  lifecycle id
- **THEN** qa-mcp returns a typed blocked outcome without substituting a
  configured default or compatibility alias
- **AND** no session, attachment or downstream endpoint probe is created.

#### Scenario: Raw remote identity projections disagree
- **WHEN** top-level launch, `client_target` or lifecycle handle PID, TPort or
  lifecycle id differs from either other projection
- **THEN** qa-mcp returns `runtime-target-mismatch`
- **AND** no session or attachment is created.

### Requirement: Standalone lifecycle remains explicit
An application without a project binding SHALL retain its existing explicit
local launch, attach and status inputs and behavior.

#### Scenario: Unbound tool schema is inspected
- **WHEN** a standalone server lists lifecycle tools
- **THEN** its existing local configuration inputs remain available.

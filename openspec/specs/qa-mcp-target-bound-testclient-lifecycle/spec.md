# qa-mcp Target-Bound TestClient Lifecycle

## Purpose

Define fail-closed admission of TestClient lifecycle state to one immutable
provider-declared project runtime target while preserving explicit standalone
lifecycle compatibility.

## Requirements

### Requirement: Project lifecycle uses one immutable target
Every project-bound TestClient launch, attach and status SHALL use the target
identity and private physical-config snapshot frozen in the application context.

#### Scenario: Declared target launches
- **WHEN** project lifecycle launches its preconfigured file or client-server
  target
- **THEN** attachment and generated session report the same logical target,
  fingerprint and binding generation.

#### Scenario: Fixture drifts after composition
- **WHEN** the env fixture changes, disappears or becomes a symlink after
  application composition
- **THEN** lifecycle uses its admitted physical configuration and does not
  silently select the changed fixture target.

#### Scenario: A resolution is rebound
- **WHEN** a newly validated resolution replaces an earlier one
- **THEN** only a session with that resolution's target object and binding
  generation may be composed; an earlier session is rejected.

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

### Requirement: Bound attach requires observed target provenance
A non-owned project-bound attach MUST require current observation of the actual
process target and binding generation. Endpoint reachability, a PID/port check,
copied configuration or caller-supplied identity SHALL NOT establish that proof.
Missing, mismatched or stale observation MUST produce a typed blocked outcome
before session admission or protocol/UI commands.

#### Scenario: Reachable endpoint has no target observation
- **WHEN** a bound attach sees a reachable TCP endpoint or a listening remote PID/port without current observed target provenance
- **THEN** it returns a blocked result without admitting a session or sending protocol/UI commands
- **AND** previously admitted application state is unchanged

#### Scenario: Declared identity is presented as observation
- **WHEN** a profile copy, caller fingerprint or old owned handle is offered as proof for a new non-owned attach
- **THEN** it is rejected as insufficient current process observation
- **AND** the implementation does not synthesize a trusted observer result

#### Scenario: Supported lifecycle paths remain available
- **WHEN** validated owned launch or explicit unbound attach is used
- **THEN** its existing lifecycle and ownership contract is preserved
- **AND** documentation identifies general non-owned bound attach as unavailable until a reviewed observer supplies the required proof

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

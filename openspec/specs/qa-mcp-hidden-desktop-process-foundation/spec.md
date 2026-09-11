# qa-mcp-hidden-desktop-process-foundation Specification

## Purpose

Define the dormant, exact-owned Win32 desktop/process/environment/run-identity
foundation used by later bounded hidden-worker successors.
## Requirements
### Requirement: Hidden desktop identity is bounded and opaque
The host foundation MUST accept only bounded non-empty run and worker-token
identity, MUST derive an exact `Winsta0\qa-mcp-*` desktop name, and MUST expose
only opaque hashes rather than raw identity values.

#### Scenario: Valid identity is derived
- **WHEN** distinct bounded run and worker-token values are supplied
- **THEN** the foundation returns a deterministic exact desktop name and
  distinct non-empty hashes without retaining either raw value

#### Scenario: Identity is absent or oversized
- **WHEN** either identity value is blank or exceeds its declared bound
- **THEN** the foundation rejects it before any Windows handle or process is
  created

### Requirement: Reserved worker environment fails closed
The host foundation MUST remove inherited variables in the reserved
`QA_MCP_INTERNAL_HIDDEN_` namespace case-insensitively, MUST admit only bounded
well-formed explicit additions, and MUST produce a deterministic environment.

#### Scenario: Stale internal values are inherited
- **WHEN** the base environment contains stale or differently-cased reserved
  keys
- **THEN** all stale values are removed and only the exact bounded additions
  are present

#### Scenario: Environment addition is malformed or oversized
- **WHEN** an addition lacks a name/value separator, is outside the reserved
  namespace or makes the environment exceed its bound
- **THEN** composition fails without launching a process

### Requirement: Desktop and process creation remain exact-owned
On Windows, the foundation MUST create only the validated named desktop, MUST
launch the exact absolute executable with that explicit desktop and no
inherited handles or visible console.

#### Scenario: Exact hidden child starts successfully
- **WHEN** a native focused test supplies a valid identity, exact worker
  executable and bounded environment
- **THEN** the child starts on the named hidden desktop without a visible
  console and all current-run handles are closed exactly

#### Scenario: Desktop or process creation fails
- **WHEN** a native creation operation fails
- **THEN** only handles created by that call are closed and no unrelated
  process, desktop or input surface is touched

#### Scenario: Process termination fails during exact cleanup
- **WHEN** cleanup of a just-created exact process encounters a termination
  failure
- **THEN** the foundation attempts both exact thread and process handle closes,
  clears only successfully closed handles, joins the cause, termination and
  close errors, and touches no unrelated handle

### Requirement: Foundation is dormant and input-free
S1 MUST add no existing production caller, public route, wire field or stable
tool admission, and its source MUST NOT invoke global input, foreground,
cursor or desktop-switch APIs.

#### Scenario: S1 publish scope is inspected
- **WHEN** the reviewed source and manifest are checked
- **THEN** only the internal foundation, focused tests and documentation are
  added, existing host behavior is unchanged, and added production LOC is at
  most `300`

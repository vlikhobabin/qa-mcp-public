## MODIFIED Requirements

### Requirement: TestClient launch failures include bounded diagnostics

The protocol lab SHALL return enough bounded launch evidence to distinguish a
native process crash, a transient TPort and a post-listener startup failure
without copying full runtime logs into MCP responses.

#### Scenario: Launch times out after process stderr is written

- **WHEN** `launch_test_client` fails because the TestClient TPort never starts
  listening
- **THEN** qa-mcp tears down only the process and display resources it owns
- **AND** the raised diagnostic includes the port, timeout, output directory,
  process return code when available and bounded tail lines from launch logs
- **AND** sensitive values such as the infobase password are not included.

#### Scenario: TestClient exits after transient listener readiness

- **WHEN** TPort becomes connectable but the owned TestClient exits during the
  default 20-second bounded stability window
- **THEN** launch fails instead of returning an alive/listening success payload
- **AND** bounded password-redacted output identifies the post-listener failure
- **AND** owned client and display resources are cleaned.

#### Scenario: Launch preserves the cold-client manager session

- **WHEN** local readiness verifies a newly listening TPort
- **THEN** it does not read the TestClient protocol greeting
- **AND** the first descriptor or scenario tool can own the cold-client manager
  session.

#### Scenario: Launch target TPort is already occupied

- **WHEN** a local `launch_test_client` request targets a TPort that is already
  listening
- **THEN** launch fails before changing Apache or starting Xvfb or 1C
- **AND** the existing endpoint is not attributed to a new lifecycle PID.

#### Scenario: Caller disconnects during local readiness

- **WHEN** qa-mcp has started the local client and Xvfb but the MCP caller
  disconnects before readiness completes
- **THEN** an exact ownership marker already records their PID, start time and
  process group
- **AND** a later stateless cleanup can validate and terminate only those
  recorded resources.

#### Scenario: Stateless cleanup follows a stale client marker

- **WHEN** the primary client PID from an exact qa-mcp ownership marker has
  already exited but its recorded Xvfb is still alive
- **THEN** cleanup validates the Xvfb PID, start time, process group and command
  before terminating it
- **AND** it removes the ownership marker after all owned resources are absent
- **AND** an unowned, reused or mismatched process remains a refusal.

## ADDED Requirements

### Requirement: Project target profiles configure every qa-mcp runtime layer

The protocol lab SHALL use the project target profile for runtime settings and
synthesized manager bootstrap version selection while preserving explicit
process-environment overrides.

#### Scenario: Project profile supplies qa-mcp runtime settings

- **WHEN** the MCP process has `QA_MCP_TARGET_ENV_FILE` pointing at a readable
  UTF-8 target profile
- **THEN** qa-mcp settings such as OData, platform, host and port are loaded
  from that profile
- **AND** synthesized manager bootstrap frames declare the target platform
  version from that profile
- **AND** an explicitly supplied process environment value takes precedence.

### Requirement: Doctor bearer defaults follow the active transport

The qa-mcp doctor SHALL select its default proxy bearer requirement from the
active MCP transport while retaining an explicit caller override.

#### Scenario: Doctor defaults follow the active transport

- **WHEN** `qa_mcp_doctor` is called without an explicit bearer requirement
- **THEN** stdio skips the bearer check and HTTP transport requires it.

### Requirement: Descriptor runtime failures are explicit and actionable

Descriptor tools SHALL distinguish manager protocol drift and a persistently
empty cold form from invalid caller arguments or ambiguous success.

#### Scenario: Descriptor encounters manager ACK drift

- **WHEN** a descriptor protocol call cannot find the client ACK GUID after
  manager frame 3
- **THEN** the tool returns `manager-handshake-moved` with a bounded action hint
- **AND** it does not classify the runtime failure as `invalid-arguments`.

#### Scenario: Heavy configuration returns an empty first descriptor

- **WHEN** `read_form_descriptor(open_link=...)` receives no opened form,
  fields or elements from a cold client
- **THEN** navigation polls for its SecondaryFrame and ManagedForm using the
  configured bounded warmup attempts and delay inside the same manager session
- **AND** a persistent empty result returns `descriptor-empty` instead of an
  ambiguous success payload.

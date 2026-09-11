## ADDED Requirements

### Requirement: TestClient launch prepares Linux runtime libraries

The protocol lab SHALL prepare the native Linux TestClient process environment
so a system `libgcc_s.so.1` can be preloaded before `1cv8` starts when the
operator has not opted out.

#### Scenario: System libgcc is autodetected for launch

- **WHEN** `launch_test_client` starts a Linux `1cv8` process and
  `QA_MCP_TESTCLIENT_LIBGCC_PRELOAD` is unset
- **THEN** qa-mcp prepends the first existing supported system libgcc path to
  the child `LD_PRELOAD`
- **AND** any existing `LD_PRELOAD` entries remain after the qa-mcp entry
- **AND** the returned status identifies that a non-secret preload path was
  applied

#### Scenario: Operator disables or overrides preload

- **WHEN** `QA_MCP_TESTCLIENT_LIBGCC_PRELOAD` is set to an empty string
- **THEN** qa-mcp starts the child without adding a libgcc preload
- **AND** when the variable is set to a non-empty value, qa-mcp uses that value
  instead of autodetection

### Requirement: TestClient launch failures include bounded diagnostics

The protocol lab SHALL return enough bounded launch evidence to distinguish a
native process crash from an ordinary TPort timeout without copying full
runtime logs into MCP responses.

#### Scenario: Launch times out after process stderr is written

- **WHEN** `launch_test_client` fails because the TestClient TPort never starts
  listening
- **THEN** qa-mcp tears down only the process and display resources it owns
- **AND** the raised diagnostic includes the port, timeout, output directory,
  process return code when available and bounded tail lines from launch logs
- **AND** sensitive values such as the infobase password are not included

### Requirement: Running TestClient endpoints can be attached without ownership

The protocol lab SHALL expose an attach path for an already-listening
`/TESTCLIENT` endpoint that can create the same protocol session entry point as
a lifecycle-owned launch while preserving external process ownership.

#### Scenario: Listening endpoint is attached

- **WHEN** an operator provides a TestClient host and TPort that is already
  listening
- **THEN** qa-mcp returns an attached handle whose status records
  `attached=true` and `owns_process=false`
- **AND** the handle can create a `TestClientSession` for read-only protocol
  tools
- **AND** stopping the handle does not terminate the external TestClient
  process

#### Scenario: Missing endpoint fails closed

- **WHEN** an operator attempts to attach to a host and TPort that is not
  listening
- **THEN** qa-mcp returns a clear attach diagnostic
- **AND** no process cleanup is attempted because qa-mcp owns no external
  process

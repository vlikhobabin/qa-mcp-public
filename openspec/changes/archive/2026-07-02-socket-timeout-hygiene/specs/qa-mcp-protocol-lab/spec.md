## ADDED Requirements

### Requirement: Native write sessions clean up sockets on setup failure
The Python manager SHALL close sockets created during native write-session
startup if setup replay fails before the context manager is entered.

#### Scenario: Setup replay raises during enter
- **WHEN** `NativeWriteSession.__enter__` creates a socket and setup replay then
  raises an exception
- **THEN** the created socket is closed before the exception is re-raised
- **AND** the failed session does not leave an open socket handle behind

### Requirement: Native sends use a send-appropriate timeout and reason
The Python manager SHALL avoid sending outbound protocol frames under the short
receive-idle timeout and SHALL report send timeouts distinctly from protocol
response divergence.

#### Scenario: Outbound send is slow
- **WHEN** sending a multi-frame or multi-kilobyte protocol request exceeds the
  send timeout
- **THEN** the operation returns or raises a distinct send-timeout reason
- **AND** the failure is not reported as protocol divergence from the TestClient
  response

#### Scenario: Receive timeout follows send timeout setup
- **WHEN** a request is sent and the manager begins draining the response
- **THEN** receive draining uses the configured receive timeout behavior
- **AND** the send timeout does not permanently replace the receive timeout

### Requirement: TestClient teardown refuses unowned process groups
The Python manager SHALL refuse to terminate a process group for a pid that is
not recorded or recognizable as a qa-mcp-owned TestClient runtime process.

#### Scenario: Pid is not an owned TestClient process
- **WHEN** `stop_test_client(pid)` is called with a stale, recycled, or unrelated
  pid whose process identity is not an expected TestClient runtime component
- **THEN** teardown returns a structured refusal
- **AND** no process group kill is attempted for that pid

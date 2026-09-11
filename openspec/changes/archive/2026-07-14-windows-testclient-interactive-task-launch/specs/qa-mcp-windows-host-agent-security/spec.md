## ADDED Requirements

### Requirement: Windows TestClient launch uses a verified interactive task shell broker

The Windows host-agent SHALL launch a new 1C TestClient with its current token
only after its process session matches the active console session. The launch
SHALL retain the installed host-agent's InteractiveToken logon and Limited run
level without requiring `WTSQueryUserToken`, `SeTcbPrivilege` or a SYSTEM
principal. After that verification, it SHALL use a transient hidden
InteractiveToken task whose fixed action contains no TestClient credential. The
fixed broker SHALL receive the executable/argument request only over an
authenticated ephemeral loopback connection, and the task SHALL be removed
before launch returns.

#### Scenario: Normal installed principal launches a persistent client

- **WHEN** the Limited/Interactive host-agent receives a valid semantic
  TestClient launch request in an active user session
- **THEN** the fixed broker starts the resolved 1cv8 executable through the
  interactive Windows shell with the current user's normalized environment
- **AND** the broker returns no credential or PID handoff artifact
- **AND** the host-agent resolves the requested TPort listener owner, then
  reopens and reports that actual 1cv8 PID
- **AND** the returned PID, TPort and window remain live at the immediate and
  at-least-60-second probes.

#### Scenario: Interactive session verification fails

- **WHEN** no active console session exists or the host-agent runs in a
  different session
- **THEN** launch fails with `testclient-interactive-session-unavailable`
- **AND** no process, task, wrapper or PID handoff file is created.

### Requirement: Transient launch credentials are secret-safe

The Windows host-agent SHALL NOT place the TestClient password in a scheduled
task action, file, HTTP response or log. It SHALL create no transient wrapper or
PID handoff file for TestClient launch.

#### Scenario: Password-bearing launch succeeds

- **WHEN** a launch request contains a non-empty infobase password
- **THEN** the per-launch task action contains no executable request or
  credential and no plaintext launch artifact is created
- **AND** the shell-broker command line does not contain that password
- **AND** the transient task is absent before the launch response
- **AND** response/log metadata contains only the existing redaction marker.

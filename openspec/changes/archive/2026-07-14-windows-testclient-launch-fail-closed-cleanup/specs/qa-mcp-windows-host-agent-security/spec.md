## MODIFIED Requirements

### Requirement: Transient launch credentials are secret-safe

The Windows host-agent SHALL NOT place the TestClient password in a scheduled
task action, file, HTTP response or log. It SHALL create no transient wrapper or
PID handoff file for TestClient launch and SHALL remove the exact transient task
before returning on success, failure or request cancellation.

#### Scenario: Password-bearing launch succeeds

- **WHEN** a launch request contains a non-empty infobase password
- **THEN** the per-launch task action contains no executable request or
  credential and no plaintext launch artifact is created
- **AND** the shell-broker command line does not contain that password
- **AND** the transient task is absent before the launch response
- **AND** response/log metadata contains only the existing redaction marker.

#### Scenario: Launch request is canceled after task registration

- **WHEN** the request context is canceled after the exact random task name may
  have been registered
- **THEN** an idempotent host-agent cleanup uses that exact name with a bounded
  context independent of the canceled request
- **AND** no wildcard or name-wide task cleanup is used
- **AND** cleanup failure prevents the launch from being reported as successful.

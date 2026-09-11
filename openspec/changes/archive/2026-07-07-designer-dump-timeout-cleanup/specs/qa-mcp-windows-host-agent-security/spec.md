## ADDED Requirements

### Requirement: Platform timeout diagnostics report spawned process identity
The Windows host-agent `/platform/execute` endpoint SHALL report the spawned
process identity in bounded timeout and cancellation diagnostics while
terminating the process group where supported. The response MUST keep the
existing redaction, allowlist, mutation-class, and operator-intent policy.

#### Scenario: Timed-out platform command reports spawned PID
- **WHEN** an authenticated platform command exceeds the requested or configured
  timeout
- **THEN** the host-agent terminates the spawned process group where supported
- **AND** the fail-closed timeout response includes the spawned process PID in a
  structured field such as `pids`
- **AND** returned diagnostics remain bounded and secret-redacted.

#### Scenario: Canceled platform command reports spawned PID
- **WHEN** an authenticated platform command is canceled after the process has
  been spawned
- **THEN** the host-agent attempts the same process-group cleanup path
- **AND** the fail-closed cancellation response includes the spawned process PID
  in a structured field such as `pids`.

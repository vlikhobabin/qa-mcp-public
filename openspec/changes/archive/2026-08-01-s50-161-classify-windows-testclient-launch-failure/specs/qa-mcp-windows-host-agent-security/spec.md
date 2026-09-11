## ADDED Requirements

### Requirement: Windows TestClient launch distinguishes broker handoff from platform early exit

The Windows host-agent SHALL treat an authenticated shell-broker acknowledgement
as process-start provenance rather than lifecycle ownership. It SHALL bind an
owned lifecycle only to a live process that owns the requested TPort and matches
the verified interactive session. Launch failure metadata MUST remain bounded
and MUST NOT expose credentials, tokens or raw command lines.

#### Scenario: Broker fails before process acknowledgement

- **WHEN** task registration, authenticated rendezvous or shell start fails
  before a valid `started <pid>` acknowledgement
- **THEN** launch fails as a broker/start failure
- **AND** it does not claim that 1C accepted the launch or that a lifecycle is
  owned.

#### Scenario: Acknowledged process exits without a TPort owner

- **WHEN** the broker returns a valid process PID
- **AND** no process owns the requested TPort within the bounded launch wait
- **AND** the acknowledged PID is no longer alive
- **THEN** launch fails as `testclient-exited-early`
- **AND** reports the bounded PID, `alive:false`, `listening:false` and
  `readiness:"exited_early"` without a lifecycle handle.

#### Scenario: Listener owner differs from acknowledged PID

- **WHEN** the broker acknowledges a transient launcher PID and another process
  in the verified interactive session owns the requested TPort
- **THEN** the listener-owner PID becomes the authoritative lifecycle PID
- **AND** cleanup targets only that lifecycle handle and its exact transient
  task.

#### Scenario: Live acknowledged PID cannot be opened

- **WHEN** the acknowledged PID remains alive but the host-agent cannot open the
  required ownership handle and no TPort owner is available
- **THEN** launch fails with a bounded PID-handoff classification
- **AND** it does not classify the condition as a platform/file-infobase early
  exit.

#### Scenario: Live acknowledged PID never owns the requested TPort

- **WHEN** the host-agent opens and session-checks a process handle as its first
  operation after receiving the acknowledged PID, before waiting for task
  completion or unregistering the exact task
- **AND** the bounded listener-owner wait ends without a TPort owner while that
  retained process remains alive
- **THEN** the host-agent does not adopt that PID or continue through generic
  port readiness
- **AND** it terminates only through the retained acknowledged-process handle,
  without reopening the numeric PID, before returning
  `testclient-not-listening` without a lifecycle handle.

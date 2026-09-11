## ADDED Requirements

### Requirement: Remote TestClient launch reports bounded start provenance

The remote `launch_test_client` result SHALL preserve the Windows host-agent's
typed start boundary so callers can distinguish failure before shell-broker
acknowledgement from an acknowledged 1C process that exits before TPort
readiness.

#### Scenario: Acknowledged Windows process exits early

- **WHEN** the host-agent reports `testclient-exited-early` after a valid broker
  acknowledgement and before any TPort owner exists
- **THEN** the MCP result preserves `testclient-exited-early`, the bounded PID,
  `alive:false`, `listening:false`, and `readiness:"exited_early"`
- **AND** it does not publish an active attachment or owned lifecycle target.

#### Scenario: Windows broker never acknowledges a process

- **WHEN** the host-agent reports a broker/start failure before valid process
  acknowledgement
- **THEN** the MCP result preserves that start-failure class
- **AND** it does not reinterpret it as platform/file-infobase early exit.

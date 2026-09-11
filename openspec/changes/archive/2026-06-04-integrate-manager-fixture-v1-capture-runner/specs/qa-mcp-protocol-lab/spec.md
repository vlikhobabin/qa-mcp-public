## ADDED Requirements

### Requirement: Manager fixture V1 capture shares one run id

The protocol lab SHALL orchestrate manager fixture V1 read-only runs so proxy
traffic, manager side-channel events and runtime logs share one capture or
run id.

#### Scenario: Manager fixture capture is run

- **WHEN** the Windows-native capture runner executes the manager fixture V1
  scenario
- **THEN** it routes the TestClient connection through the TCP proxy and passes
  the proxy endpoint to the manager harness
- **AND** it stores proxy traffic, manager output and 1C logs under the same
  ignored runtime run directory

#### Scenario: Capture runner cleanup runs

- **WHEN** the manager fixture V1 capture exits successfully or fails
- **THEN** the runner records owned TestClient, proxy and manager PIDs and
  stops only those owned processes
- **AND** unrelated 1C sessions are left running
- **AND** raw TCP payloads and full process logs remain outside reviewed git
  changes

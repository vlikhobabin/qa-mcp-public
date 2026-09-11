## ADDED Requirements

### Requirement: Manager fixture V1 pending probes require a clean runtime endpoint

The protocol lab SHALL prepare or explicitly gap a clean Windows-native
TestClient endpoint before attempting manager fixture V1 pending-row replay or
direct probes.

#### Scenario: Endpoint readiness is retained

- **WHEN** a pending-row probe pass starts for manager fixture V1
- **THEN** the protocol lab records the run id, TestClient port, proxy port,
  fixture route and endpoint readiness state
- **AND** the evidence identifies which PIDs are runner-owned for cleanup

#### Scenario: Runtime startup is unavailable

- **WHEN** a clean TestClient endpoint cannot be started or attached
- **THEN** the protocol lab records a compact provider/runtime gap
- **AND** no pending row is accepted from the unavailable runtime pass

#### Scenario: Cleanup ownership is preserved

- **WHEN** endpoint preparation exits successfully or fails
- **THEN** cleanup stops only TestClient, proxy and manager PIDs created or
  explicitly owned by the pending-row runtime route
- **AND** unrelated 1C sessions remain untouched

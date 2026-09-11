## ADDED Requirements

### Requirement: Manager fixture V1 live capture invokes the custom harness

The protocol lab SHALL execute non-dry-run `manager-fixture-v1-readonly`
captures by invoking the dedicated manager fixture harness through the TCP
proxy and preserving all runtime outputs under one run id.

#### Scenario: Live manager fixture capture runs

- **WHEN** the capture runner starts a non-dry-run
  `manager-fixture-v1-readonly` scenario
- **THEN** it starts or prepares the TestClient, proxy and manager processes
  using Windows-native entrypoints
- **AND** it passes the shared run id, proxy TestClient port, output directory
  and manifest path to the manager harness
- **AND** the runtime directory contains proxy `traffic.jsonl`, manager
  harness manifest, case events and result output

#### Scenario: Required runtime asset is missing

- **WHEN** the configured Vanessa EPF or required manager runtime asset is not
  available
- **THEN** the capture runner fails closed or records a compact provider gap
- **AND** the run is not reported as live protocol evidence

#### Scenario: Capture cleanup runs

- **WHEN** the live capture exits successfully or fails
- **THEN** the runner stops only the TestClient, proxy and manager PIDs it
  created
- **AND** unrelated 1C sessions remain untouched

## ADDED Requirements

### Requirement: Remote launch and protocol attachment share the routed endpoint

In remote-client mode with a configured relay, `launch_test_client` SHALL send
the real local TPort to the host-agent launcher, combine that target-readiness
result with a container-to-relay listener check, record the active attachment
and serve subsequent protocol tools through the relay endpoint. Readiness and
reattach checks SHALL NOT dial the single-manager target before the real
protocol tool. Display-bound operations SHALL continue resolving the Windows
client by its real local TPort rather than by the relay listener port.

#### Scenario: Product launch uses the relay

- **WHEN** host-agent launch reports the local TestClient PID/TPort ready
- **THEN** qa-mcp verifies container reachability of the configured relay
  listener without opening its loopback target
- **AND** records that relay host/port for `attach_test_client`,
  `read_form_descriptor`, `read_list_grid` and later protocol tools.
- **AND** display refresh for those tools resolves the 1C window by the real
  local TPort.

#### Scenario: Relay authentication fails on the protocol tool

- **WHEN** the host-agent launch and relay listener checks pass but the
  configured relay rejects authentication or cannot reach its target
- **THEN** the first descriptor/read connection fails loud
- **AND** the diagnostic names relay authentication/target readiness without
  exposing the token.

#### Scenario: Reattach follows product launch

- **WHEN** `attach_test_client` addresses the relay endpoint already recorded by
  a ready host-agent product launch
- **THEN** it reuses that source-bound attachment and listener check
- **AND** does not open and discard a loopback TestManager session.

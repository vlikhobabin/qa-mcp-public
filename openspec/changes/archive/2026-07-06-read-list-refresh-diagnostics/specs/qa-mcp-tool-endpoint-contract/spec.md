## ADDED Requirements

### Requirement: List-reading refresh diagnostics preserve host-agent causes
`read_list_grid`, `read_list_column`, and list-read polling helpers SHALL
preserve structured display-backend failure causes when a requested refresh or
clean-state sweep cannot be delivered. The result MUST distinguish an
unreachable or unconfigured display backend from host-agent primitive failures
such as `foreground-denied`, version mismatch, unsupported key, or
authentication failure.

#### Scenario: Foreground denial is surfaced in zero-row list diagnostics
- **WHEN** a list-reading tool requests display refresh
- **AND** the remote host-agent reports `foreground-denied`
- **AND** the underlying list replay returns zero rows
- **THEN** the tool result identifies `foreground-denied` in refresh metadata or
  the zero-row reason
- **AND** the result does not claim that no display backend was reachable.

#### Scenario: Unreachable host-agent remains a reachability diagnostic
- **WHEN** a list-reading tool requests display refresh
- **AND** the remote host-agent cannot be reached or is not configured
- **THEN** the tool result identifies the host-agent reachability/configuration
  problem
- **AND** it retains install or configuration guidance when available.

#### Scenario: Refresh failure does not raise through the MCP boundary
- **WHEN** a display refresh or clean-state sweep fails before a list read
- **THEN** the list-reading tool still returns a structured MCP result
- **AND** the refresh method, refresh diagnostic, poll outcome, and row count
  remain visible to the caller.

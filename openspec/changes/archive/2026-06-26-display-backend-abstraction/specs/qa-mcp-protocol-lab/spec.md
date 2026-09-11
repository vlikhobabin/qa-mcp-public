## ADDED Requirements

### Requirement: Display-bound tools select an explicit backend
The protocol lab SHALL route display-bound MCP tools through an explicit
display backend that preserves local Linux behavior and can delegate to a
configured remote host agent in model-B remote-client mode.

#### Scenario: Local backend preserves Linux display behavior
- **WHEN** remote-client mode is not enabled
- **THEN** display-bound tools use the existing Linux XTEST, screenshot and
  OS-window primitives
- **AND** their public MCP parameters and result shapes remain compatible with
  the current local TestClient workflow

#### Scenario: Remote backend handles model-B display calls
- **WHEN** `QA_MCP_REMOTE_CLIENT=1` and `QA_MCP_HOST_AGENT` names a reachable
  host agent
- **THEN** display-bound tools route keyboard, mouse, screenshot and OS-window
  primitive requests to the remote agent
- **AND** higher-level locate and protocol orchestration remain in Python

### Requirement: Remote display backend fails closed with actionable diagnostics
The protocol lab SHALL return structured display-backend diagnostics instead of
running Linux display commands when model-B remote-client mode has no usable
host display agent.

#### Scenario: Remote mode lacks agent configuration
- **WHEN** a display-bound MCP tool is called with `QA_MCP_REMOTE_CLIENT=1` and
  no `QA_MCP_HOST_AGENT`
- **THEN** the tool returns `ok=false` with a stable backend error code
- **AND** the result explains that the Windows host-side input/screenshot agent
  must be installed or configured

#### Scenario: Unguarded display tool is normalized
- **WHEN** `open_external_processor` is called in model-B remote-client mode
- **THEN** it follows the same display backend dispatch and diagnostics as the
  other display-bound tools
- **AND** it does not crash by directly invoking Linux screenshot or XTEST
  helpers

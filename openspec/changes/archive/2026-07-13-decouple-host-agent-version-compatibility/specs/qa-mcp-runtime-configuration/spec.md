## ADDED Requirements

### Requirement: Doctor reports host-agent compatibility relationship
`qa_mcp_doctor` SHALL report the authenticated host-agent build version,
display protocol and bounded version relationship when the handshake succeeds,
without exposing credentials or local paths.

#### Scenario: Newer protocol-compatible agent is connected
- **WHEN** host-agent handshake accepts an unknown build through the supported protocol
- **THEN** `host_agent_http` passes
- **AND** its data reports build version, display protocol and
  `version_relationship: protocol-compatible`.

#### Scenario: Exact operator pin is active
- **WHEN** the configured expected version exactly matches the host-agent build
- **THEN** doctor reports `version_relationship: pinned`.

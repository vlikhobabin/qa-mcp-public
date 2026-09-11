## ADDED Requirements

### Requirement: MCP server delegates protocol wire work to protocol modules

The MCP server SHALL keep raw TestClient socket access, frame rebinding,
foreground protocol flows and read-sweep wire mechanics in protocol-owned
modules rather than in `mcp_server.py`. The extraction MUST preserve observable
tool behavior.

#### Scenario: MCP server has no raw protocol socket dependency

- **WHEN** the source tree is inspected after extraction
- **THEN** `src/qa_mcp/mcp_server.py` contains no direct
  `socket.create_connection` usage
- **AND** it does not import `GuidRebinder` directly

#### Scenario: Foreground protocol behavior is preserved

- **WHEN** a tool opens or foregrounds a form through an extracted protocol
  helper
- **THEN** the same endpoint, capture bootstrap and activation retry behavior is
  used as before extraction
- **AND** result metadata still records activation retry when that path is used

#### Scenario: Read-sweep helpers remain protocol evidence preserving

- **WHEN** extracted descriptor, field, table-cell or window-list reads process
  TestClient responses
- **THEN** they keep the same response parsing and partial/truncated envelope
  behavior
- **AND** no new protocol claim is accepted without existing tests or retained
  evidence

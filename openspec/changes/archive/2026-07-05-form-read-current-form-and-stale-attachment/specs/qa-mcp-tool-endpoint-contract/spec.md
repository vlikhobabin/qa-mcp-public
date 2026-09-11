## ADDED Requirements

### Requirement: Form-read tools require actionable open-link context

`read_form_descriptor` and `read_table_cell` SHALL return a structured,
actionable result when the caller omits `open_link` and the tool cannot infer a
live ManagedForm GUID for the current form. The result MUST NOT expose the raw
`managed_form_guid_ascii` or `managed_form_guid_utf16le` template exception as
the primary diagnostic.

#### Scenario: Descriptor read without open_link is actionable
- **WHEN** `read_form_descriptor` is called without `open_link`
- **AND** the tool cannot infer a live ManagedForm GUID
- **THEN** it returns a structured error such as `open-link-required`
- **AND** the result instructs the caller to pass `open_link`

#### Scenario: Table-cell read without open_link is actionable
- **WHEN** `read_table_cell` is called without `open_link`
- **AND** the tool cannot infer a live ManagedForm GUID
- **THEN** it returns a structured error such as `open-link-required`
- **AND** the result instructs the caller to pass `open_link`

### Requirement: Stale attachments are invalid for endpoint-touching tools

Endpoint-touching MCP tools SHALL treat an attached endpoint as invalid when the
attachment liveness state is `listening=false`. Such tools MUST return a
structured stale-attachment result with an action hint instead of attempting a
protocol operation against the dead endpoint.

#### Scenario: Dead attached endpoint is rejected
- **WHEN** `attach_test_client` has recorded an endpoint
- **AND** a subsequent liveness check reports `listening=false`
- **AND** an endpoint-touching tool is called without explicit `host` and `port`
- **THEN** the tool returns a structured stale-attachment error
- **AND** no protocol connection is opened to the recorded endpoint

#### Scenario: Stale attachment suggests recovery
- **WHEN** an endpoint-touching tool rejects a stale attachment
- **THEN** the result includes an action hint such as restarting
  `qa-mcp-testclient` or re-running `attach_test_client`
- **AND** the result identifies the stale endpoint host and port when available

## ADDED Requirements

### Requirement: Attached TestClient endpoints drive replay-backed tools

The protocol lab SHALL let an already-listening `/TESTCLIENT` endpoint attached through `attach_test_client`
drive the same replay-backed introspection, read and write/session tool paths as a qa-mcp-launched client while
preserving external process ownership.

#### Scenario: Attached endpoint returns a real form descriptor

- **WHEN** `attach_test_client` records a listening out-of-band TestClient endpoint
- **AND** `read_form_descriptor` is run against an existing form through that attached endpoint
- **THEN** qa-mcp uses the attached endpoint session route instead of an unrelated ad hoc session
- **AND** the result includes non-empty live descriptor evidence such as `opened`, `elements`, `element_count` or
  `fields`
- **AND** an attach/bootstrap failure is returned as a bounded diagnostic rather than `{opened:null, fields:{}}`
  with no failure phase

#### Scenario: Attached endpoint is available to write/session tools

- **WHEN** a replay-backed write or scenario tool is invoked after a successful attach
- **THEN** qa-mcp resolves the same attached endpoint context for the tool session factory unless the caller
  explicitly overrides `host` and `port`
- **AND** the tool result preserves the existing write/action safety result contract
- **AND** stopping or cleaning up the attached context does not terminate the external TestClient process

#### Scenario: Missing attached endpoint fails closed

- **WHEN** a tool is asked to use an attached endpoint that is no longer listening
- **THEN** qa-mcp returns a stable attach-session diagnostic that includes the host, port and failed phase
- **AND** no owned-process cleanup is attempted for the external TestClient

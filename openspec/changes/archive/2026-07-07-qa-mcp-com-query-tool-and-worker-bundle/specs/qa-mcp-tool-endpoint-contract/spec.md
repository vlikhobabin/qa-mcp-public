## ADDED Requirements

### Requirement: Host-side COM query tools expose read-only file-infobase data
qa-mcp SHALL expose MCP tools for host-side COM read queries that work when the
target file infobase has no OData publishing. The tools MUST call the configured
Windows host-agent, MUST use authenticated `/com/execute`, MUST return structured
transport metadata, and MUST fail closed before sending obvious write or
side-effecting query text to the host.

#### Scenario: Read-only query returns host COM rows
- **WHEN** `query_com` is called with `infobase_path`, optional credentials, a
  read-only 1C query, and host-agent configuration
- **THEN** qa-mcp sends an `execute_query` WorkerRequest to host-agent
  `/com/execute`
- **AND** the result contains `ok: true`, `rows`, `transport: "com"`,
  host-agent response metadata, and COM worker result metadata

#### Scenario: Count assertion compares COM query count
- **WHEN** `assert_com_count` is called with a read-only count query and an
  expected comparator
- **THEN** qa-mcp executes the query through the host COM transport
- **AND** the result includes the observed count, expected value, comparator,
  `ok` verdict, and the underlying `query_com` response

#### Scenario: Write-shaped query is rejected locally
- **WHEN** a caller supplies query text containing an obvious write or
  side-effecting 1C query operation such as insert, update, delete, create,
  post, unpost, execute, or external file operations
- **THEN** qa-mcp returns `ok: false` with a read-only policy diagnostic
- **AND** no request is sent to host-agent `/com/execute`

#### Scenario: Missing host-agent settings are actionable
- **WHEN** a COM query tool is called without `QA_MCP_HOST_AGENT` or
  `QA_MCP_HOST_AGENT_TOKEN`
- **THEN** qa-mcp returns a structured configuration diagnostic
- **AND** the result explains that host-side COM queries require the Windows
  host-agent and bundled `ai-com-worker.exe`

### Requirement: COMConnector doctor is exposed through qa-mcp
qa-mcp SHALL expose a `com_connector_doctor` MCP tool that calls the Windows
host-agent COMConnector doctor endpoint and returns structured registration,
bitness, TypeLib, connection, and optional read-query smoke diagnostics.

#### Scenario: TypeLib registration gap includes elevated repair command
- **WHEN** host-agent reports that `V83.COMConnector` ProgID and
  `InprocServer32` exist but the 64-bit TypeLib registration is missing
- **THEN** `com_connector_doctor` returns `ok: false` with a
  `typelib-missing` diagnostic
- **AND** the result includes the exact elevated
  `C:\Windows\System32\regsvr32.exe` command for the discovered 64-bit
  `comcntr.dll`

#### Scenario: Green doctor preserves COM smoke evidence
- **WHEN** the host-agent doctor verifies 64-bit registry evidence, creates
  `V83.COMConnector`, connects to the supplied file infobase, and executes the
  supplied read query
- **THEN** `com_connector_doctor` returns `ok: true`
- **AND** the result includes bounded smoke-query metadata without exposing the
  infobase password

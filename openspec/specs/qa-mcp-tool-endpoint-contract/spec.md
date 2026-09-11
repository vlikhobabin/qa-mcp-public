# qa-mcp-tool-endpoint-contract Specification

## Purpose

Define the MCP TestClient tool endpoint contract: protocol-backed tools honor the active attached TestClient endpoint, return structured wrapper-level errors, and retain offline registry tests that prevent endpoint split-brain regressions.
## Requirements
### Requirement: Endpoint tools honor the attached TestClient endpoint
Every MCP tool that opens a TestClient protocol connection SHALL use the endpoint recorded by `attach_test_client` when the caller omits `host` and `port`.

#### Scenario: Attached endpoint is reused
- **WHEN** `attach_test_client` records host `X` and port `Y`
- **AND** an endpoint-touching MCP tool is called without explicit `host` or `port`
- **THEN** the tool connects to `X:Y`
- **AND** it does not fall back to `127.0.0.1:15381`

#### Scenario: Explicit endpoint overrides attachment
- **WHEN** an endpoint-touching MCP tool is called with explicit `host` and `port`
- **THEN** the tool uses the explicit endpoint for that call

### Requirement: Endpoint tool errors are structured
Endpoint-touching MCP tools SHALL return structured error results for attachment resolution failures, invalid capture names and invalid argument values rather than raising raw tracebacks through the MCP boundary.

#### Scenario: Invalid capture is reported as a structured result
- **WHEN** a wrapped endpoint-touching tool receives a bad `capture` value
- **THEN** the tool returns a structured error result
- **AND** the result identifies the invalid input without exposing a raw traceback

#### Scenario: Existing write-path verdicts are preserved
- **WHEN** the underlying write or replay path returns a structured `retarget_failed` or `send_timeout` result
- **THEN** the endpoint wrapper returns that structured verdict unchanged except for allowed attachment metadata

### Requirement: Local boot tools are unavailable in remote-client mode
MCP tools that start local 1C platform processes SHALL fail closed in remote-client mode with the standard structured local-only guidance.

#### Scenario: Measure scenario is guarded in remote mode
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `measure_scenario` is called
- **THEN** it returns the structured local-only "not served here" result
- **AND** it does not attempt to execute local `dbgs`, `1cv8`, or Apache service commands

### Requirement: Attach endpoint behavior is registry-tested
The qa-mcp offline test suite SHALL include a registry-driven contract test that covers every endpoint-touching MCP tool and verifies attach-aware endpoint selection.

#### Scenario: Endpoint registry contract uses attached endpoint
- **WHEN** the test attaches sentinel host `X` and port `Y`
- **AND** each endpoint-touching registered tool is invoked without explicit `host` or `port`
- **THEN** the monkeypatched connector observes `X:Y` for every covered tool
- **AND** the test fails if any covered tool falls back to the default endpoint

#### Scenario: Endpoint tool classification is complete
- **WHEN** the registered MCP tool list is inspected by the contract test
- **THEN** every endpoint-touching tool is either covered by an endpoint assertion or explicitly classified as not opening a TestClient protocol connection

### Requirement: Wrapper failure modes are tested offline
The qa-mcp offline test suite SHALL prove that wrapper-level failure modes return structured results without live 1C runtime.

#### Scenario: Bad wrapper inputs return structured results
- **WHEN** a wrapped endpoint tool receives invalid arguments or an invalid capture value in the offline contract test
- **THEN** the returned value is a structured error result
- **AND** no raw traceback crosses the MCP tool boundary

#### Scenario: Remote mode blocks local measurement startup
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `measure_scenario` is exercised by the offline test suite
- **THEN** the returned value is the structured local-only result
- **AND** no local platform executable is required

### Requirement: Extracted protocol helpers preserve endpoint wrapper contracts
Endpoint-touching MCP tool wrappers SHALL keep using the active attached
TestClient endpoint, explicit endpoint overrides and structured wrapper errors
after their wire-level implementation is moved into protocol modules.

#### Scenario: Attached endpoint still reaches extracted helper
- **WHEN** `attach_test_client` records host `X` and port `Y`
- **AND** an endpoint-touching tool calls an extracted protocol helper without
  explicit host or port arguments
- **THEN** the helper connects to `X:Y`
- **AND** it does not fall back to `127.0.0.1:15381`

#### Scenario: Structured protocol verdicts pass through wrapper
- **WHEN** an extracted protocol helper returns a structured error or blocked
  result
- **THEN** the MCP wrapper returns that verdict unchanged except for existing
  attachment metadata
- **AND** no raw traceback crosses the MCP boundary

### Requirement: Remote-client local-only gating uses centralized settings
Local-only MCP tool guards SHALL use the centralized settings/accessor path for
remote-client detection while preserving the existing structured local-only
result.

#### Scenario: Remote-client mode still blocks local boot tools
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** a local-boot tool such as `measure_scenario` is called
- **THEN** the tool returns the standard local-only structured result
- **AND** it does not attempt to execute local platform commands

#### Scenario: Default local mode is preserved
- **WHEN** `QA_MCP_REMOTE_CLIENT` is unset
- **THEN** local-boot guards behave as they did before the settings accessor
- **AND** no new environment variable is required

### Requirement: List-reading tools resolve the live dynamic-list table
`read_list_grid` and `read_list_column` SHALL resolve the table they read from the live form descriptor for the supplied `open_link` unless the caller supplies an explicit `table` argument. The tools SHALL include the resolved table name in the result and SHALL retarget the underlying list replay to that table instead of assuming `Список`.

#### Scenario: Single descriptor table is used
- **WHEN** `read_list_grid` or `read_list_column` is called for a list form whose descriptor contains exactly one `Table` element named `Валюты`
- **THEN** the tool reads table `Валюты`
- **AND** the result reports `table` as `Валюты`
- **AND** the tool does not report that table `Список` was read

#### Scenario: Explicit table overrides descriptor inference
- **WHEN** `read_list_grid` or `read_list_column` is called with `table="Валюты"`
- **THEN** the tool reads table `Валюты`
- **AND** the result reports `table` as `Валюты`
- **AND** the descriptor is used only to validate or diagnose that selection

#### Scenario: Legacy list table remains supported
- **WHEN** the descriptor identifies the target dynamic-list table as `Список`
- **THEN** `read_list_grid` and `read_list_column` continue to read table `Список`
- **AND** existing callers that omit `table` keep working

### Requirement: List-reading empty diagnostics are table-aware
`read_list_grid` and `read_list_column` SHALL distinguish table-resolution failures from a resolved table that is genuinely empty after refresh. The tools MUST NOT state that a list is genuinely empty when the descriptor table could not be resolved, was ambiguous, or did not match an explicit caller-supplied table.

#### Scenario: Table cannot be resolved
- **WHEN** a list-reading tool cannot resolve a table from the descriptor for the supplied `open_link`
- **THEN** the tool returns a structured diagnostic such as `list-table-unresolved`
- **AND** the diagnostic includes the available descriptor tables when known
- **AND** the reason does not claim that the list is genuinely empty

#### Scenario: Explicit table does not match descriptor
- **WHEN** a caller supplies `table="Список"` but the descriptor exposes only table `Валюты`
- **THEN** the tool returns a structured diagnostic such as `list-table-not-found`
- **AND** the result identifies the requested table and available descriptor tables
- **AND** the tool does not run the replay against the wrong table and then call zero rows empty

#### Scenario: Resolved table is empty after refresh
- **WHEN** the table is resolved successfully
- **AND** the refreshed list replay returns zero rows
- **THEN** the existing refreshed-empty diagnostic may state that the resolved list is genuinely empty
- **AND** the result identifies the table that was actually read

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

### Requirement: List-reading tools fail loud for uncertain zero-row results
`read_list_grid`, `read_list_column`, and `read_list_row` SHALL NOT return a
normal-looking empty result when display refresh, clean-state sweep, or
target-window confirmation failed before a zero-row or all-empty list result.
Such results MUST be marked with `ok: false` and
`data_confidence: "unknown"` while preserving the underlying structured error
and the original row/value payload for diagnostics.

#### Scenario: Refresh window lookup fails before a zero-row grid read
- **WHEN** `read_list_grid` resolves the form descriptor for an `open_link`
- **AND** the requested refresh fails with a structured `window-not-found`
  diagnostic
- **AND** the protocol grid replay returns `row_count: 0`
- **THEN** the top-level result includes `ok: false`
- **AND** the top-level result includes `data_confidence: "unknown"`
- **AND** the top-level result exposes the `window-not-found` diagnostic outside
  the nested `list_refresh` object
- **AND** callers can still inspect `row_count`, `rows`, `list_refresh`, and
  `table_resolution`.

#### Scenario: Refresh opt-out still fails loud when clean-state confirmation fails
- **WHEN** a list-reading tool is called with `refresh=false`
- **AND** the clean-state sweep or target-window confirmation fails
- **AND** the replay returns zero rows, no value, or an all-empty row
- **THEN** the result is marked `ok: false`
- **AND** the result uses `data_confidence: "unknown"` rather than presenting
  the zero as confirmed empty data.

#### Scenario: Confirmed refreshed empty list remains valid
- **WHEN** a list-reading tool successfully refreshes and confirms a clean
  state
- **AND** the replay returns zero rows from the resolved table
- **THEN** the result MAY report `row_count: 0` as confirmed empty
- **AND** the result MUST NOT be marked `ok: false` solely because the list is
  empty.

### Requirement: Remote-client list diagnostics include host window evidence
Remote-client list reads SHALL include a bounded diagnostic of the host-agent
window identity that was searched and the discovered Windows-side 1C windows
when they fail loud because zero-row data is uncertain and that authenticated
diagnostic route is available. If visible UI Automation cell text is available
from the host-agent, the result MUST include it as diagnostic fallback evidence;
if not, it MUST include the structured diagnostic failure.

#### Scenario: Remote zero-row failure lists discovered 1C windows
- **WHEN** `read_list_grid` fails loud in remote-client mode
- **AND** the host-agent `/window_list` route is reachable
- **THEN** the result includes the target window identity
- **AND** the result includes discovered `V8TopLevelFrame*` windows with handle,
  class, title, and PID.

#### Scenario: Visible UIA cells are attached as fallback evidence
- **WHEN** `read_list_grid` fails loud in remote-client mode
- **AND** the host-agent visible-cell diagnostic returns UI Automation cell text
- **THEN** the result includes a bounded visible-cell list
- **AND** callers can compare that diagnostic with the protocol `rows` before
  trusting the read.

#### Scenario: Diagnostic failures do not hide the original list failure
- **WHEN** a remote-client list read is already marked uncertain
- **AND** host window or visible-cell diagnostics fail
- **THEN** the result remains `ok: false`
- **AND** the diagnostic failure is recorded separately from the original
  refresh or sweep error.

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

#### Scenario: Green doctor preserves COM smoke diagnostics
- **WHEN** the host-agent doctor verifies 64-bit registry state, creates
  `V83.COMConnector`, connects to the supplied file infobase, and executes the
  supplied read query
- **THEN** `com_connector_doctor` returns `ok: true`
- **AND** the result includes bounded smoke-query metadata without exposing the
  infobase password

### Requirement: Remote-client launch uses host-agent when configured

`launch_test_client` SHALL support remote-client mode by routing launch through
the configured authenticated Windows host-agent instead of failing as a
local-only tool. The tool MUST render or request the same target identity as the
local lifecycle path, preserve structured host-agent launch diagnostics, wait
for the configured TestClient TPort to become reachable from the container, and
remember the endpoint for subsequent endpoint-touching tools only after the
host-agent readiness result and the container-side TPort probe both prove the
client is usable. When the host-agent reports early exit or not-listening from
its persistence dwell, qa-mcp MUST preserve that failure and MUST NOT record an
active attachment. Because the host-agent launch endpoint waits synchronously
for readiness, the Python HTTP request for `/testclient/launch` MUST use a
timeout that covers the launch `timeout_seconds` readiness wait plus a bounded
margin; unrelated host-agent calls MUST keep the configured default host-agent
timeout.

#### Scenario: Remote launch establishes and remembers a host TestClient
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** host-agent launch settings are configured
- **AND** `launch_test_client` is called with a target infobase, user and TPort
- **AND** the host-agent returns `ok: true`, `alive: true` and
  `listening: true`
- **AND** the TPort is reachable from the container
- **THEN** qa-mcp returns `ok: true` with the host PID when reported, the TPort
  and a redacted command summary
- **AND** a follow-up endpoint-touching tool called without explicit `host` and
  `port` uses the launched endpoint.

#### Scenario: Launch HTTP timeout covers readiness wait
- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** the configured `host_agent_timeout` is shorter than the
  `launch_test_client` readiness `timeout_seconds`
- **AND** `launch_test_client` calls the host-agent `/testclient/launch`
  endpoint
- **THEN** the HTTP request timeout covers the readiness `timeout_seconds` plus
  the client-side launch margin
- **AND** the request is not limited to the shorter default host-agent timeout
- **AND** other host-agent primitive calls continue to use the configured
  default host-agent timeout unless they explicitly document a longer wait.

#### Scenario: Dead remote endpoint can be re-established
- **WHEN** a previous remote-client attachment is stale or no longer listening
- **AND** the caller invokes `launch_test_client` again
- **THEN** qa-mcp requests a new host-agent launch or reuses an already
  listening TPort reported by the host-agent
- **AND** the remembered endpoint is updated only when the resulting endpoint is
  live from the container.

#### Scenario: Host-agent early exit is returned as a launch failure
- **WHEN** qa-mcp is in remote-client mode
- **AND** the host-agent launch response reports `ok: false` with
  `error: "testclient-exited-early"`, including a process exit detected before
  the host-agent persistence dwell completed
- **THEN** `launch_test_client` returns a structured failure result with the
  same host-agent error code and diagnostic detail
- **AND** the result includes the redacted manual host command fallback
- **AND** no active attached endpoint is recorded.

#### Scenario: Host-agent not-listening result is returned as a launch failure
- **WHEN** qa-mcp is in remote-client mode
- **AND** the host-agent launch response reports `ok: false` with
  `error: "testclient-not-listening"`, including a port that drops before the
  host-agent persistence dwell completed
- **THEN** `launch_test_client` returns a structured failure result with the
  same host-agent error code and diagnostic detail
- **AND** no active attached endpoint is recorded.

#### Scenario: Container reachability remains required after host readiness
- **WHEN** qa-mcp is in remote-client mode
- **AND** the host-agent reports the TestClient process as ready on the host
- **AND** the TPort is not reachable from the container
- **THEN** `launch_test_client` returns `remote-testclient-port-not-listening`
- **AND** the host-agent readiness payload is preserved for diagnostics
- **AND** no active attached endpoint is recorded.

#### Scenario: Missing host-agent launch returns an exact manual command
- **WHEN** qa-mcp is in remote-client mode
- **AND** the host-agent launch route is unavailable, unreachable or too old
- **THEN** `launch_test_client` returns a structured failure result
- **AND** the result includes the exact host command an operator can run with
  the resolved connection string, user and `-TPort`
- **AND** secret values such as the TestClient password are redacted while
  `password_set` remains visible.

#### Scenario: Local launch behavior is unchanged
- **WHEN** `QA_MCP_REMOTE_CLIENT` is unset or false
- **THEN** `launch_test_client` uses the existing Linux/Xvfb lifecycle path
- **AND** no host-agent TestClient launch request is sent.

### Requirement: JSON-RPC diagnostics echo received Cyrillic arguments
qa-mcp SHALL expose an MCP diagnostic that returns the exact Unicode argument
values received after JSON-RPC parsing, including `open_link` and arbitrary
caller-provided Cyrillic text. The diagnostic MUST flag values that contain
Unicode replacement characters or question-mark mojibake patterns so callers can
distinguish an encoding failure from an invalid 1C navigation link.

#### Scenario: Cyrillic navigation link is echoed unchanged
- **WHEN** a caller sends a diagnostic request with
  `open_link="e1cib/list/Справочник.Валюты"`
- **THEN** the result includes the same `received.open_link` value
- **AND** the result reports no mojibake warning for that value

#### Scenario: Mojibake navigation link is flagged
- **WHEN** a caller sends a diagnostic request with
  `open_link="e1cib/list/??????????.??????"`
- **THEN** the result echoes the same received value
- **AND** the result includes a structured warning that the value looks like
  mojibake or replacement text

### Requirement: Direct HTTP JSON-RPC bodies require UTF-8
qa-mcp's direct HTTP MCP transport SHALL reject JSON request bodies whose
`Content-Type` declares a non-UTF-8 charset or whose bytes cannot be decoded as
UTF-8. The rejection MUST occur before MCP tool dispatch and MUST return a
clear JSON error that names the UTF-8 request-body requirement.

#### Scenario: Non-UTF-8 charset is rejected
- **WHEN** qa-mcp direct HTTP transport receives a JSON-RPC POST with
  `Content-Type: application/json; charset=windows-1251`
- **THEN** the response is an HTTP client error
- **AND** the JSON error explains that JSON-RPC bodies must use UTF-8
- **AND** no MCP tool is dispatched

#### Scenario: Invalid UTF-8 bytes are rejected
- **WHEN** qa-mcp direct HTTP transport receives an `application/json` POST
  whose body bytes are not valid UTF-8
- **THEN** the response is an HTTP client error
- **AND** the JSON error explains that the request body is not valid UTF-8
- **AND** no MCP tool is dispatched

#### Scenario: UTF-8 JSON body is accepted
- **WHEN** qa-mcp direct HTTP transport receives a JSON-RPC POST with
  `Content-Type: application/json; charset=utf-8`
- **AND** the body bytes decode as UTF-8
- **THEN** the request reaches normal MCP dispatch

### Requirement: End-to-end doctor reports the setup chain

The qa-mcp Python manager SHALL expose a `qa_mcp_doctor` diagnostic as an MCP
tool and a CLI entry point. The doctor result MUST be secret-safe and MUST
return an ordered chain of named checks with pass, fail, or skipped status plus
an overall verdict.

#### Scenario: Healthy setup returns a green chain

- **WHEN** the proxy auth environment, host-agent route, platform discovery,
  TestClient TPort, open-link-free TestClient smoke, and COM doctor checks are
  all available
- **THEN** `qa_mcp_doctor` returns `ok: true`
- **AND** every check result includes a stable check name and `status: "pass"`
- **AND** the result does not include bearer tokens, host-agent tokens,
  passwords, or raw credential values

#### Scenario: Partial setup reports failed links

- **WHEN** one diagnostic link cannot be reached or cannot be executed
- **THEN** `qa_mcp_doctor` returns `ok: false`
- **AND** the failing check includes an actionable error code and hint
- **AND** later checks whose prerequisites are missing are marked as skipped
  rather than reported as successful

### Requirement: Auth diagnostics distinguish missing token environment

The qa-mcp doctor and HTTP/MCP auth diagnostics SHALL report whether the
expected bearer-token environment variable is present without exposing the
token value. A missing environment variable MUST be distinguishable from a
supplied but rejected token.

#### Scenario: Bearer env is missing

- **WHEN** the configured MCP proxy requires bearer auth
- **AND** `QA_MCP_BEARER_TOKEN` is absent from the active qa-mcp process
- **THEN** the diagnostic result includes `token_env_present: false`
- **AND** the result does not include any token value
- **AND** the error is not a generic unauthorized result with no remediation
  hint

#### Scenario: Bearer env is present but rejected

- **WHEN** `QA_MCP_BEARER_TOKEN` is present
- **AND** the proxy rejects the supplied credential
- **THEN** the diagnostic result includes `token_env_present: true`
- **AND** the error identifies an auth mismatch without exposing the token value

### Requirement: TestClient smoke does not require open_link

The qa-mcp endpoint contract SHALL include a low-level TestClient smoke that
proves the MCP process can connect to the TestClient TPort without requiring
`open_link` or a managed-form target. Tools that do require `open_link` MUST
keep actionable examples in their schema or error guidance.

#### Scenario: Smoke passes after attach without open_link

- **WHEN** a TestClient endpoint is listening and attach-aware endpoint
  resolution succeeds
- **AND** no `open_link` is supplied
- **THEN** the TestClient smoke returns `ok: true`
- **AND** it identifies the endpoint that was checked

#### Scenario: Form-level tool still reports open_link guidance

- **WHEN** a form-level tool cannot infer a current ManagedForm GUID
- **THEN** it returns `open-link-required`
- **AND** its guidance includes an example such as `e1cib/list/<metadata>` for
  list forms
- **AND** callers can run the open-link-free smoke to verify that the
  underlying MCP-to-TestClient connection is healthy

### Requirement: Attach diagnostics report effective user and login dialog state

The qa-mcp attach and doctor diagnostics SHALL distinguish a connected
TestClient session from a client stuck at the 1C login/access dialog. When the
effective infobase user is queryable, diagnostics MUST report it separately
from the configured launch user.

#### Scenario: Wrong user leaves client at login dialog

- **WHEN** the TestClient process is reachable by TPort
- **AND** the client is still showing the 1C login or access dialog
- **THEN** attach or doctor diagnostics report a distinct login-dialog-stuck
  state
- **AND** they do not report the client as fully attached

#### Scenario: Effective user differs from configured user

- **WHEN** the effective infobase user can be queried
- **AND** it differs from the configured launch user
- **THEN** diagnostics include both values with secret-safe field names
- **AND** the mismatch is visible in the doctor result

### Requirement: Connection diagnostics avoid Designer metadata dumps

The qa-mcp connection diagnostics SHALL NOT invoke Designer metadata dump
commands such as `DESIGNER /DumpConfigToFiles` during ordinary setup,
connection, catalog-name, or open-link troubleshooting. Diagnostics MUST use
light-weight routes such as MCP/HTTP auth checks, host-agent health, live
TestClient descriptor/window evidence, configured metadata descriptors, or
optional COM read-smoke checks.

#### Scenario: Doctor does not spawn Designer

- **WHEN** an operator runs `qa_mcp_doctor` or `qa-mcp-doctor` to diagnose a
  model-B setup
- **THEN** the diagnostic chain uses host-agent `/version` and `/health`,
  TestClient TPort smoke, window evidence, and optional COM doctor checks
- **AND** it does not call host-agent `/platform/execute` with executable
  `designer`, `1cv8 DESIGNER`, or `/DumpConfigToFiles`.

#### Scenario: Form-level guidance remains light-weight

- **WHEN** a form-level tool cannot infer a target and returns
  `open-link-required` or catalog-name guidance
- **THEN** the guidance points to `qa_mcp_doctor`, descriptor/open-link input,
  metadata-provider input, or optional COM read-smoke routes
- **AND** it does not recommend Designer metadata dump as a routine diagnostic
  fallback.

### Requirement: qa_mcp_doctor always returns a complete ordered chain

The `qa_mcp_doctor` tool SHALL always return one ordered pass/fail/skipped chain.
A failure inside any individual check — including a timeout or connection error
raised by the COMConnector-doctor probe — SHALL be recorded as a structured
`fail` leg for that check and MUST NOT propagate as an unhandled exception that
aborts the remaining diagnostics.

#### Scenario: A slow or busy COM leg does not crash the chain

- **WHEN** the COMConnector-doctor probe raises a `TimeoutError` or connection
  error (for example because the target file base is busy)
- **THEN** `qa_mcp_doctor` SHALL record the `com_connector_doctor` check as a
  `fail` with code `com-doctor-probe-failed` and SHALL still return the remaining
  checks in the ordered chain

### Requirement: List reads retry an empty form descriptor from a cold client

`read_list_grid` / `read_list_column` table resolution SHALL treat a live form descriptor with
no opened form AND no elements as a cold client whose form has not rendered yet (distinct from a
genuinely empty catalog, which still exposes a `Table` element) and SHALL retry the descriptor
read a bounded number of times (configurable via `QA_MCP_DESCRIPTOR_WARMUP_ATTEMPTS` and
`QA_MCP_DESCRIPTOR_WARMUP_DELAY_SEC`) before failing. When all attempts still return an empty
descriptor, the `list-table-unresolved` diagnostic SHALL report `descriptor_empty: true`, the
`warmup_attempts` count, and a reason indicating the client may still be warming up. The retry
SHALL be bounded (no unbounded loop).

#### Scenario: A cold-client empty descriptor is retried and then resolves

- **WHEN** the first live descriptor read returns an empty descriptor (no opened form, 0 elements)
  and a subsequent read within the bounded attempts returns the rendered form with a table
- **THEN** the table resolves normally and the result records how many warm-up retries were needed

#### Scenario: Exhausted retries report a warming-up diagnostic without looping forever

- **WHEN** every attempt (up to the configured bound) returns an empty descriptor
- **THEN** resolution stops after the bounded number of attempts and returns a
  `list-table-unresolved` diagnostic carrying `descriptor_empty: true`, the `warmup_attempts`
  count, and a "client may still be warming up" reason

### Requirement: Remote host-agent compatibility is protocol-based
The remote display backend SHALL use the authenticated host-agent display
protocol id as the default compatibility boundary instead of requiring an
exact build label. Explicit operator version and SHA-256 pins SHALL remain
exact. Known legacy build labels without a protocol field MAY remain compatible;
unknown builds without a supported protocol SHALL fail closed.

#### Scenario: Shipped image connects to a newer wire-compatible agent
- **WHEN** `/version` returns an unknown newer build label and the supported
  display protocol id
- **THEN** the handshake succeeds without an operator override
- **AND** reports `version_relationship: protocol-compatible`.

#### Scenario: Unknown agent omits or changes the protocol
- **WHEN** an unknown build returns no display protocol or an unsupported one
- **THEN** the handshake fails closed before a display primitive executes.

#### Scenario: Operator pins a build label or hash
- **WHEN** `QA_MCP_HOST_AGENT_EXPECTED_VERSION` or the expected SHA-256 is set
- **THEN** the corresponding raw value is compared exactly
- **AND** a mismatch fails closed even when the display protocol is supported.

### Requirement: Remote TestClient launch reports the durable interactive mechanism

The remote `launch_test_client` result SHALL report bounded launch-context
metadata identifying the verified host-agent session mechanism while preserving the
existing alive/listening/readiness and early-exit classifications.

#### Scenario: Interactive host-agent session reaches readiness

- **WHEN** the verified active-session host-agent yields a live PID and the requested TPort remains
  listening through the readiness dwell
- **THEN** the result reports `launch_context.method` as
  `interactive_task_shell_broker`, `alive:true`, `listening:true` and
  `readiness:"ready"`
- **AND** it does not expose command lines, credentials or token handles.

#### Scenario: Interactive child exits early

- **WHEN** the host-agent starts 1cv8 but that PID exits before TPort readiness
- **THEN** the existing `testclient-exited-early` result remains fail-loud
- **AND** the result identifies the interactive host-agent-session mechanism.

### Requirement: Remote TestClient launch selects the exact QA platform build

The remote launch contract SHALL carry the exact non-empty four-component QA
platform version to the Windows host-agent, which SHALL resolve 1cv8 only from
that catalog version and SHALL NOT silently select a newer installed build.

#### Scenario: Requested platform is installed

- **WHEN** the provider requests `8.3.27.2130` and the station also contains a
  newer platform build
- **THEN** the host-agent launches 1cv8 from the `8.3.27.2130` catalog directory
- **AND** reports that resolved version in bounded launch metadata.

#### Scenario: Requested platform is invalid or absent

- **WHEN** `platform_version` is empty, is not exactly four numeric components,
  or that exact catalog version has no resolved 1cv8
- **THEN** launch fails before process creation with
  `invalid-platform-version` or `platform-version-not-found`
- **AND** it does not fall back to a different installed build.

### Requirement: Remote launch and protocol attachment share the routed endpoint

In remote-client mode with a configured relay, `launch_test_client` SHALL send
the real local TPort to the host-agent launcher, combine that target-readiness
result with a container-to-relay listener check, record the active attachment
and serve subsequent protocol tools through the relay endpoint. Readiness and
reattach, status, info, state and doctor liveness checks SHALL NOT authenticate
the relay or dial the single-manager target before a real protocol operation.
Display-bound operations SHALL continue resolving the Windows client by its
real local TPort rather than by the relay listener port.

#### Scenario: Generic relay liveness is requested

- **WHEN** a lifecycle or public status/info/state path checks the exact
  configured relay endpoint
- **THEN** qa-mcp performs only a TCP listener reachability check
- **AND** sends no authentication preface and opens no loopback target.

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

### Requirement: Remote-client launches create provider-owned lifecycle handles

`launch_test_client` in remote-client mode SHALL mark a host-agent-launched
TestClient as provider-owned only when the host-agent explicitly reports
`owns_process: true` for that launched process, and SHALL return enough
sanitized lifecycle handle metadata, including an opaque lifecycle id, for a
later `stop_test_client` call to clean up the same host process. Manually
attached TestClients and legacy host-agent launch results that do not
explicitly report ownership and a lifecycle id SHALL remain unowned.

#### Scenario: Host-agent launch returns an owned handle

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `launch_test_client` successfully launches a TestClient through the
  configured host-agent
- **THEN** the returned result includes `owns_process: true`
- **AND** the returned result identifies host-agent lifecycle ownership without
  exposing credentials or raw host runtime logs
- **AND** the returned lifecycle handle includes an opaque `id` that is not
  derived from the PID alone
- **AND** the active attachment keeps using the launched protocol endpoint.

#### Scenario: Manual attachment remains unowned

- **WHEN** `attach_test_client` records an already-listening TestClient endpoint
- **THEN** the returned result includes `owns_process: false`
- **AND** a later cleanup request cannot terminate that manually attached
  client through qa-mcp.

#### Scenario: Legacy host-agent launch result is not inferred as owned

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** the configured host-agent returns a successful launch result with a
  PID but without `owns_process: true`
- **THEN** qa-mcp records the endpoint as an active attachment
- **AND** the returned attachment remains `owns_process: false`
- **AND** qa-mcp does not synthesize a lifecycle handle from the PID alone.

### Requirement: Remote-client stop routes through host-agent ownership

`stop_test_client` SHALL remain local process-group cleanup for locally launched
clients, but in remote-client mode it SHALL route cleanup through the configured
host-agent only when the caller supplies the opaque lifecycle handle returned by
the provider-owned remote launch. The tool SHALL return a structured result for
stopped, already stopped, and refused states, and SHALL refuse PID-only remote
cleanup requests. Generic display protocol compatibility SHALL NOT by itself
authorize remote TestClient stop: qa-mcp MUST first prove that the host-agent
supports lifecycle-handle stop semantics through the current lifecycle-stop
version or an explicit advertised capability preserved by the remote
`/version` handshake. Only a capability list entry named
`testclient-lifecycle-handle-stop` or a capability mapping entry with that name
and an explicit boolean `true` SHALL authorize future protocol-compatible
host-agent stop routing.

#### Scenario: Owned remote launch is stopped through the host-agent

- **WHEN** a remote-client `launch_test_client` result includes an owned
  lifecycle handle
- **AND** `stop_test_client` is called with that PID and the returned lifecycle
  handle
- **THEN** qa-mcp sends the stop request to the same host-agent lifecycle route
- **AND** the result reports a typed final state for that exact launched process.

#### Scenario: Repeated stop is idempotent

- **WHEN** `stop_test_client` has already finalized an owned remote TestClient
- **AND** the caller repeats `stop_test_client` for the same lifecycle handle
- **THEN** the result reports an already-finalized state
- **AND** no unrelated 1C process is targeted.

#### Scenario: PID-only remote cleanup is refused

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `stop_test_client` is called with a PID but without the lifecycle
  handle id returned by `launch_test_client`
- **THEN** the result is a structured `missing_lifecycle_handle` refusal
- **AND** qa-mcp does not call the host-agent stop route.

#### Scenario: Protocol-compatible legacy stop route is refused

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** the host-agent handshake reports the shared display protocol but does
  not prove lifecycle-handle TestClient stop support
- **AND** `stop_test_client` is called with an otherwise valid lifecycle handle
- **THEN** the result is a structured
  `host-agent-testclient-lifecycle-unsupported` failure
- **AND** qa-mcp does not call the host-agent stop route.

#### Scenario: Future host-agent capability authorizes lifecycle stop

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** the host-agent handshake reports the shared display protocol with a
  future protocol-compatible version
- **AND** the `/version` response advertises
  `testclient-lifecycle-handle-stop` either in a capability-name list or in a
  capability mapping whose value is the boolean `true`
- **AND** `stop_test_client` is called with an owned lifecycle handle
- **THEN** qa-mcp sends `/testclient/stop` through the host-agent lifecycle
  route
- **AND** it does not require an exact version pin for that future compatible
  host-agent.

#### Scenario: Truthy non-boolean capability values do not authorize stop

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** the host-agent handshake reports the shared display protocol with a
  protocol-compatible version
- **AND** the `/version` response advertises
  `testclient-lifecycle-handle-stop` in a capability mapping whose value is not
  an explicit boolean `true`
- **AND** `stop_test_client` is called with an otherwise valid lifecycle handle
- **THEN** the result is a structured
  `host-agent-testclient-lifecycle-unsupported` failure
- **AND** qa-mcp does not call the host-agent stop route.

#### Scenario: Unowned remote PID is refused

- **WHEN** `QA_MCP_REMOTE_CLIENT=1`
- **AND** `stop_test_client` is called with a lifecycle handle id that does not
  belong to a provider-owned remote launch
- **THEN** the result is a structured refusal
- **AND** qa-mcp does not attempt local process cleanup or host-side broad
  process termination.

#### Scenario: Not-ready remote launch exposes cleanup handle when host-owned

- **WHEN** the host-agent starts a TestClient process but reports the launch as
  not ready while the process is still alive
- **AND** the host-agent response includes `owns_process: true` and a lifecycle
  handle
- **THEN** qa-mcp returns that sanitized cleanup handle in the structured launch
  failure
- **AND** it does not record the not-ready endpoint as an active attachment.

### Requirement: Open-list navigation defaults to released runtime assets
The `open_list` endpoint SHALL open a requested list through the supported
versioned navigation-template path when the caller omits `capture` or supplies
a blank capture selector. The public default MUST NOT name a historical
development capture and MUST NOT resolve a blank selector as
`/work/traffic.jsonl`.

#### Scenario: Caller omits capture
- **WHEN** a caller invokes `open_list` without `capture`
- **THEN** qa-mcp selects the bundled bootstrap and navigation templates for the active platform family
- **AND** it sends the requested `e1cib/list/...` navigation through the attached TestClient endpoint
- **AND** it does not resolve a development capture directory or `/work/traffic.jsonl`

#### Scenario: Caller supplies a blank capture selector
- **WHEN** a caller invokes `open_list` with an empty or whitespace-only `capture`
- **THEN** qa-mcp treats the selector as omitted and uses the supported template-backed navigation path
- **AND** it does not interpret the current work directory as a capture directory

### Requirement: Open-list explicit capture compatibility is retained
The `open_list` endpoint SHALL preserve its explicit capture replay path for a
non-blank capture selector, including neutral versioned captures bundled in the
released package.

#### Scenario: Caller selects a bundled capture explicitly
- **WHEN** a caller invokes `open_list` with a non-blank bundled capture name
- **THEN** qa-mcp resolves and derives that capture explicitly
- **AND** the native open-list helper receives the caller's target catalog and attached endpoint

### Requirement: Open-list asset failures occur before protocol writes
The template-backed `open_list` path MUST validate every required bootstrap and
navigation-template asset before it opens a TestClient connection or writes a
protocol frame. An unavailable asset SHALL return a typed capability diagnostic
without exposing a traceback or machine-local asset path.

#### Scenario: Optional navigation template is missing
- **WHEN** the default or explicitly selected navigation-template asset cannot be loaded or lacks the required splice frame
- **THEN** `open_list` returns `ok: false` with error `open-list-navigation-unavailable`
- **AND** the result identifies capability `template-backed-open-list` and the failing asset class
- **AND** `protocol_write_attempted` is `false`
- **AND** no TestClient session or socket is opened

### Requirement: Remote display tools inherit the active TestClient target

When qa-mcp has an active remote TestClient launch or attachment, `capture_screenshot`, `send_keys`, `type_text`, `click`, and host-agent visible-list-cell reads SHALL send the bounded active `client_target` whenever the caller does not supply an explicit non-empty, non-wildcard window selector. The target SHALL identify the host TestClient by PID and TPort and SHALL include the opaque lifecycle id when the process is provider-owned. An explicit selector SHALL take precedence. The MCP result SHALL preserve typed target-validation and desktop-session failures and MUST NOT retry with an empty, wildcard, generic 1C, or foreground-window target.

#### Scenario: Owned launch supplies implicit display target

- **WHEN** remote `launch_test_client` returns an owned lifecycle handle and records it as the active attachment
- **AND** a caller invokes a remote display tool without an explicit window
- **THEN** qa-mcp sends a `client_target` derived from that lifecycle handle
- **AND** the request includes the same lifecycle id, PID, and TPort without exposing a raw HWND.

#### Scenario: Attach supplies a non-owning display target

- **WHEN** remote `attach_test_client` connects to an already-listening TestClient and the authenticated host-agent resolves that listener to its process-owned 1C window
- **THEN** the attach result and active attachment include a bounded non-owning `client_target`
- **AND** `owns_process` remains false.

#### Scenario: Explicit selector wins

- **WHEN** an active remote TestClient target exists
- **AND** a display tool is called with an explicit non-empty, non-wildcard window selector
- **THEN** qa-mcp sends the explicit selector as the target override
- **AND** does not replace it with the active `client_target`.

#### Scenario: Weak implicit target fails closed

- **WHEN** an active remote TestClient context exists but its `client_target` is missing, stale, mismatched, or unsupported by the host-agent
- **AND** no explicit window selector was supplied
- **THEN** the MCP result reports the typed target failure
- **AND** qa-mcp does not retry against an empty selector, wildcard, generic 1C window, or foreground application.

#### Scenario: Desktop session diagnostic is preserved

- **WHEN** the host-agent refuses a lifecycle-bound display request because the Windows session is locked, disconnected, or non-interactive
- **THEN** the MCP result preserves the corresponding distinct typed error and bounded detail
- **AND** it does not report a generic screenshot/input conflict or success.

### Requirement: Remote TestClient launch reports bounded start provenance

The remote `launch_test_client` result SHALL preserve the Windows host-agent's
typed start boundary so callers can distinguish failure before shell-broker
acknowledgement from an acknowledged 1C process that exits before TPort
readiness.

#### Scenario: Acknowledged Windows process exits early

- **WHEN** the host-agent reports `testclient-exited-early` after a valid broker
  acknowledgement and before any TPort owner exists
- **THEN** the MCP result preserves `testclient-exited-early`, the bounded PID,
  `alive:false`, `listening:false`, and `readiness:"exited_early"`
- **AND** it does not publish an active attachment or owned lifecycle target.

#### Scenario: Windows broker never acknowledges a process

- **WHEN** the host-agent reports a broker/start failure before valid process
  acknowledgement
- **THEN** the MCP result preserves that start-failure class
- **AND** it does not reinterpret it as platform/file-infobase early exit.

### Requirement: Disposable Windows UI proof remains bound to one owned TestClient lifecycle

The remote qa-mcp launch and UI operations SHALL use the owned lifecycle target
returned for the restored disposable infobase. The first protocol/UI operation
MUST NOT be preceded by a consuming generic TCP readiness connection.

#### Scenario: Restored S50 infobase yields a usable lifecycle target

- **WHEN** `launch_test_client` starts the restored S50 disposable infobase on
  the authorized Windows host
- **THEN** it returns a live owned PID, TPort and lifecycle handle
- **AND** the first lifecycle-bound UI operation can open
  `Справочник.S50ProofItems` without targeting a stale or unrelated window.

#### Scenario: Catalog item is created and read back

- **WHEN** the lifecycle-bound qa-mcp UI path opens the S50 catalog and creates
  one uniquely named disposable item
- **THEN** the same lifecycle shows that name in the visible list or visible
  cells
- **AND** screenshot evidence is retained only under ignored runtime state.

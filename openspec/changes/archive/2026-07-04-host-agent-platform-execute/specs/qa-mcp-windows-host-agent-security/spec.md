## ADDED Requirements

### Requirement: Host-agent executes only allowlisted local 1C platform commands
The Windows host-agent SHALL expose `POST /platform/execute` as an authenticated
sensitive endpoint for host-side 1C platform command execution. The endpoint
MUST accept only semantic executable names from the fixed allowlist `ibcmd`,
`designer`, `1cv8`, and `1cv8c`; resolve them from configured 1C platform
catalog directories; reject arbitrary paths or shell fragments before spawning;
and require policy boundary fields supplied by the owning provider.

#### Scenario: Authenticated allowlisted command returns bounded process result
- **WHEN** an authenticated request supplies an allowlisted executable, argv,
  timeout, `operation`, `mutation_class`, and any required operator-intent
  evidence
- **THEN** the host-agent resolves the executable from the configured platform
  catalog, runs it without a shell, and returns `{ "ok": true, "exit_code": 0,
  "stdout": "...", "stderr": "...", "response_id": "platform-exec" }`
- **AND** the response includes the resolved executable path without exposing
  bearer tokens or secret command arguments.

#### Scenario: Off-allowlist executable is rejected before spawn
- **WHEN** an authenticated request supplies an executable name outside
  `ibcmd`, `designer`, `1cv8`, or `1cv8c`, or supplies an absolute/path-like
  executable value
- **THEN** the endpoint returns a fail-closed response with `ok: false`
- **AND** no process is spawned.

#### Scenario: Platform execute requires operator intent
- **WHEN** an authenticated request supplies `operation:
  "platform_command_execute"` without a non-empty `operator_intent`
- **THEN** the endpoint rejects the request before resolving or spawning the
  executable
- **AND** diagnostics identify the missing policy field without inventing
  operator approval.

#### Scenario: Platform plan does not require operator intent
- **WHEN** an authenticated request supplies `operation:
  "platform_command_plan"` with an allowlisted executable and required
  mutation classification
- **THEN** the endpoint may run the requested platform validation command
- **AND** it still enforces executable allowlist, catalog resolution, timeout,
  bounded output, and redaction behavior.

#### Scenario: Missing or invalid token is rejected before request validation
- **WHEN** a request to `POST /platform/execute` omits
  `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns the existing unauthorized response
- **AND** the request body is not validated, logged, or passed to any process.

#### Scenario: Platform command timeout terminates the process group
- **WHEN** an authenticated platform command exceeds the requested or configured
  timeout
- **THEN** the host-agent terminates the spawned process group where supported
- **AND** it returns a fail-closed timeout response with bounded, redacted
  diagnostics.

#### Scenario: Platform command diagnostics redact secret arguments
- **WHEN** a spawned platform command fails and echoes request arguments such as
  `/P`, `--password`, `pwd=...`, or `password=...`
- **THEN** the host-agent redacts those secret-bearing values in returned
  stdout, stderr, and error detail
- **AND** logs and response diagnostics do not reveal the original secret.

#### Scenario: Authenticated health reports platform catalog availability
- **WHEN** an authenticated client calls `/health`
- **THEN** the response includes bounded platform catalog discovery diagnostics
  for allowlisted 1C executables
- **AND** unauthenticated clients still cannot access detailed health through
  the sensitive endpoint boundary.

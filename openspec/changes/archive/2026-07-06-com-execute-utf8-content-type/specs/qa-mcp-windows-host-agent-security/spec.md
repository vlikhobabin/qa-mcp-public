## MODIFIED Requirements

### Requirement: Host-agent executes only allowlisted COM worker operations
The Windows host-agent SHALL expose `POST /com/execute` as an authenticated
sensitive endpoint that executes only the fixed installed COM worker for
allowlisted live-mcp WorkerRequest operations. The endpoint MUST NOT accept or
forward arbitrary executable paths, shell fragments, container-provided argv, or
secret request payloads into logs or diagnostics. Successful worker JSON stdout
MUST be returned as UTF-8 JSON without platform-output truncation, CP866
fallback decoding, or JSON restructuring, and the HTTP response MUST declare
`Content-Type: application/json; charset=utf-8`.

#### Scenario: Authenticated read operation returns worker response unchanged
- **WHEN** an authenticated request supplies a WorkerRequest with operation
  `execute_query` and the configured COM worker writes valid UTF-8 WorkerResponse
  JSON to stdout
- **THEN** the host-agent runs the fixed worker with `--worker`, passes the
  original request JSON on stdin, and returns the worker JSON response body
  without truncating, re-encoding, or restructuring it
- **AND** the success response declares `Content-Type:
  application/json; charset=utf-8`
- **AND** request fields such as infobase password, connection path, and query
  text are not written to logs or error details

#### Scenario: Unknown COM operation is rejected before spawn
- **WHEN** an authenticated request supplies an operation outside `ping`,
  `connect_check`, `execute_query`, `metadata_snapshot`, and
  `guarded_posting_smoke`
- **THEN** the endpoint returns a fail-closed `operation-not-allowed` response
- **AND** no worker process is spawned

#### Scenario: Guarded posting smoke requires operator intent
- **WHEN** an authenticated request supplies operation `guarded_posting_smoke`
  without non-empty operator-intent evidence
- **THEN** the endpoint returns a fail-closed `operator-intent-required`
  response before resolving or spawning the worker
- **AND** the request body is not logged or passed to a process

#### Scenario: Missing or invalid token is rejected before request validation
- **WHEN** a request to `POST /com/execute` omits
  `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns the existing unauthorized response
- **AND** the WorkerRequest body is not validated, logged, or passed to any
  process

#### Scenario: Missing worker fails closed for readiness
- **WHEN** an authenticated request supplies an allowlisted operation but the
  configured COM worker executable is absent or not executable
- **THEN** the endpoint returns `ok: false` with a bounded
  `com-worker-not-found` error suitable for readiness diagnostics
- **AND** no shell fallback or arbitrary executable path is attempted

#### Scenario: Worker timeout terminates the process group
- **WHEN** an authenticated COM worker request exceeds the requested or
  configured timeout
- **THEN** the host-agent terminates the worker process group where supported
- **AND** it returns a fail-closed `timeout` response with bounded diagnostics
  that do not include the WorkerRequest body

#### Scenario: Invalid worker JSON fails closed
- **WHEN** the COM worker exits successfully but writes empty stdout or
  non-JSON stdout
- **THEN** the endpoint returns a fail-closed worker output error
- **AND** the invalid output detail is bounded and secret-safe

#### Scenario: Authenticated health reports COM worker availability
- **WHEN** an authenticated client calls `/health`
- **THEN** the response includes bounded COM worker availability diagnostics
  for the configured worker path
- **AND** unauthenticated clients still cannot access detailed health through
  the sensitive endpoint boundary

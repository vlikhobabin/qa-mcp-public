## ADDED Requirements

### Requirement: Host-agent stops only provider-owned launched TestClients
The Windows host-agent SHALL expose an authenticated TestClient stop route that
can terminate only a TestClient process previously launched and recorded by
that same host-agent process under an opaque lifecycle id. Stop requests with
unknown, stale, invalid, missing, or mismatched lifecycle ids MUST be refused
without terminating any process.

#### Scenario: Exact owned launched process is stopped
- **WHEN** `/testclient/launch` has returned a ready owned process PID and
  lifecycle handle id
- **AND** an authenticated caller invokes the stop route with that PID and
  lifecycle handle
- **THEN** the host-agent terminates only that recorded process
- **AND** the response includes a typed final state and sanitized lifecycle
  metadata.

#### Scenario: Started but not ready process remains owned for cleanup
- **WHEN** `/testclient/launch` starts a TestClient process
- **AND** the process remains alive but its TPort does not become listening
  before the launch timeout
- **THEN** the host-agent records that exact process under an opaque lifecycle
  id
- **AND** the launch failure response includes `owns_process: true` and a
  sanitized lifecycle handle with that id
- **AND** a later authenticated stop request with that lifecycle handle can
  terminate only that recorded process.

#### Scenario: Repeated stop returns final state
- **WHEN** a recorded TestClient process has already exited or has already been
  stopped through the host-agent
- **AND** the caller repeats the stop request for that lifecycle handle
- **THEN** the host-agent returns an idempotent already-finalized state
- **AND** no process-name, window-title, lock-file, or port-based broad cleanup
  is attempted.

#### Scenario: Unknown lifecycle handle is refused
- **WHEN** an authenticated caller invokes the stop route with a lifecycle handle
  id that was not issued and recorded by this host-agent process
- **THEN** the host-agent returns a structured `not-owned` refusal
- **AND** no process is terminated.

#### Scenario: PID-only stop is refused
- **WHEN** an authenticated caller invokes the stop route with a PID but without
  a lifecycle handle id
- **THEN** the host-agent returns a structured `missing_lifecycle_handle`
  refusal
- **AND** no process is terminated.

#### Scenario: Stop route remains authenticated
- **WHEN** a request to the TestClient stop route omits
  `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns the existing unauthorized response
- **AND** no process lookup or termination is attempted.

### Requirement: Remote TestClient lifecycle evidence remains bounded
Host-agent TestClient lifecycle responses and retained qa-mcp evidence SHALL
include only sanitized lifecycle states, reason codes, PID/port values, launch
method, and process absence result. They MUST NOT include credentials, infobase
contents, screenshots, raw runtime logs, raw command lines, or unrelated 1C
process inventories.

#### Scenario: Stop evidence omits sensitive runtime data
- **WHEN** a remote TestClient launch/stop verification is retained
- **THEN** the evidence records the lifecycle route, typed state, PID/port, and
  absence or refusal result
- **AND** it excludes credentials, infobase contents, screenshots, raw runtime
  logs, and unrelated process inventories.

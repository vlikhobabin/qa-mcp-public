## MODIFIED Requirements

### Requirement: Host-agent launches TestClient through a constrained detached endpoint

The Windows host-agent SHALL expose an authenticated sensitive endpoint for
detached 1C TestClient launch and status. The endpoint MUST construct the
`1cv8 ENTERPRISE ... /TESTCLIENT -TPort` command from semantic request fields,
resolve the platform executable from the configured catalog, reject arbitrary
executables or shell fragments, and start the process without a shell. On
Windows, newly spawned TestClient processes MUST be created from the active
interactive session primary token with the interactive desktop
`winsta0\\default`, rather than inheriting the long-running Task Scheduler
host-agent process token. The launch path MUST supply bounded GUI child
environment keys and return bounded launch metadata. For a newly spawned
client, the endpoint MUST classify readiness from process liveness and TPort
liveness before returning: it MUST report success only when the process is
still alive and the TPort is listening, and it MUST return a structured failure
when the interactive launch context cannot be prepared, the process exits
early, or the TPort never becomes ready within the bounded timeout.

#### Scenario: Authenticated TestClient launch returns ready process metadata
- **WHEN** an authenticated request supplies a valid connection string or file
  infobase path, user, TPort and optional safe startup flags
- **THEN** the host-agent resolves `1cv8` from the configured platform catalog
- **AND** on Windows it starts the TestClient with `CreateProcessAsUserW` using
  the active interactive session primary token and `winsta0\\default`
- **AND** it starts without a shell using bounded GUI child environment keys
- **AND** it waits until the process is alive and the TPort is listening before
  returning success
- **AND** the response includes `ok: true`, spawned PID, `alive: true`,
  `listening: true`, `readiness: "ready"`, TPort, platform version or
  executable metadata, a redacted command summary, and bounded launch-context
  metadata that does not expose token handles or secret environment values.

#### Scenario: Launch rejects arbitrary execution inputs
- **WHEN** a request supplies an absolute executable path, shell fragment,
  unknown executable, invalid port, empty target, or NUL-containing argument
- **THEN** the endpoint returns a fail-closed response
- **AND** no process is spawned.

#### Scenario: Unauthorized launch is rejected before body validation
- **WHEN** a request to the TestClient launch endpoint omits
  `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns the existing unauthorized response
- **AND** the request body is not validated, logged, or passed to any process.

#### Scenario: Passwords are redacted from diagnostics
- **WHEN** a launch request includes a TestClient password or a
  password-bearing connection string
- **THEN** returned command summaries, errors and logs do not include the secret
  value
- **AND** the response may report only that a password was supplied.

#### Scenario: Interactive session token is required on Windows
- **WHEN** the Windows host-agent cannot obtain or duplicate the active
  interactive session user token for a new TestClient launch
- **THEN** the endpoint returns `ok: false` with a structured launch-context
  diagnostic
- **AND** it does not fall back to direct Task Scheduler token inheritance
- **AND** no response claims the TestClient is attached or ready.

#### Scenario: Early process exit is not reported as ready
- **WHEN** the host-agent starts `1cv8` for a TestClient launch
- **AND** the process exits before its TPort becomes listening
- **THEN** the endpoint returns `ok: false` with
  `error: "testclient-exited-early"`
- **AND** the response includes `alive: false`, `listening: false`, the PID
  when known, the redacted command summary, and bounded launch-context metadata
- **AND** the response does not claim the TestClient is attached or ready.

#### Scenario: Non-listening process is not reported as ready
- **WHEN** the host-agent starts `1cv8` for a TestClient launch
- **AND** the process is still alive when the bounded launch timeout expires
- **AND** the requested TPort is not listening
- **THEN** the endpoint returns `ok: false` with
  `error: "testclient-not-listening"`
- **AND** the response includes `alive: true`, `listening: false`, the PID when
  known, the redacted command summary, and bounded launch-context metadata.

#### Scenario: Already-listening TPort can be reused
- **WHEN** an authenticated launch request targets a TPort that is already
  listening before a new process is spawned
- **THEN** the endpoint returns `ok: true`, `reused_existing: true`,
  `listening: true`, and `readiness: "ready"`
- **AND** no additional `1cv8` process is spawned.

#### Scenario: TestClient status reports bounded liveness metadata
- **WHEN** an authenticated client asks for TestClient launch status by TPort
  or PID
- **THEN** the host-agent reports process `alive` when a PID is supplied and
  reports whether the requested TPort is listening
- **AND** `listening: true` alone is not treated as proof that a supplied PID is
  alive
- **AND** unauthenticated clients cannot access the detailed status.

#### Scenario: Host-agent version declares interactive-session TestClient launch support
- **WHEN** qa-mcp performs the remote host-agent version handshake before
  `launch_test_client`
- **THEN** the reported host-agent version is accepted only if it belongs to the
  bounded compatibility family that includes honest TestClient launch readiness
  and Windows interactive-session launch support, unless an exact operator
  override is configured.

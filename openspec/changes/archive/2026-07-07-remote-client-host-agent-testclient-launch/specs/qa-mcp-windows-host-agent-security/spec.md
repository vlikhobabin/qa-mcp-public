## ADDED Requirements

### Requirement: Host-agent launches TestClient through a constrained detached endpoint

The Windows host-agent SHALL expose an authenticated sensitive endpoint for
detached 1C TestClient launch and status. The endpoint MUST construct the
`1cv8 ENTERPRISE ... /TESTCLIENT -TPort` command from semantic request fields,
resolve the platform executable from the configured catalog, reject arbitrary
executables or shell fragments, start the process without waiting for GUI exit,
and return bounded launch metadata.

#### Scenario: Authenticated TestClient launch returns process metadata
- **WHEN** an authenticated request supplies a valid connection string or file
  infobase path, user, TPort and optional safe startup flags
- **THEN** the host-agent resolves `1cv8` from the configured platform catalog
- **AND** it starts the TestClient detached without a shell
- **AND** the response includes `ok: true`, spawned PID, TPort, platform
  version or executable metadata, and a redacted command summary.

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

#### Scenario: TestClient status reports bounded liveness metadata
- **WHEN** an authenticated client asks for TestClient launch status by TPort
  or PID
- **THEN** the host-agent reports whether the process or TPort is alive when
  that information is available
- **AND** unauthenticated clients cannot access the detailed status.

#### Scenario: Host-agent version declares TestClient launch support
- **WHEN** qa-mcp performs the remote host-agent version handshake before
  `launch_test_client`
- **THEN** the reported host-agent version is accepted only if it belongs to the
  bounded compatibility family that includes TestClient launch support, unless
  an exact operator override is configured.

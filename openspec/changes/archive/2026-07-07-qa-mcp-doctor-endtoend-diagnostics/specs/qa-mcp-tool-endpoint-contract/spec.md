## ADDED Requirements

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
- **AND** the result does not include bearer tokens, host-agent tokens, passwords,
  or raw credential values

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
- **AND** the error is not a generic unauthorized result with no remediation hint

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
- **AND** its guidance includes an example such as
  `e1cib/list/<metadata>` for list forms
- **AND** callers can run the open-link-free smoke to verify that the underlying
  MCP-to-TestClient connection is healthy

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

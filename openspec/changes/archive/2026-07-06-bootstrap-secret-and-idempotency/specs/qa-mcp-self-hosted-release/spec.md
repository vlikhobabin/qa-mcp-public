## ADDED Requirements

### Requirement: Bootstrap does not persist plaintext TestClient credentials

The qa-mcp Windows bootstrap SHALL NOT leave a plaintext TestClient launch
script containing an infobase password after the TestClient launch attempt
completes. Any temporary launch helper that can contain `/P<password>` SHALL be
restricted to the current user while it exists and SHALL be removed after
success or failure cleanup.

#### Scenario: Password launch helper is removed after success
- **WHEN** bootstrap launches TestClient with a non-empty `-Password`
- **AND** the TestClient starts listening on the requested `ClientPort`
- **THEN** `%LOCALAPPDATA%\qa-mcp-setup\launch-testclient.ps1` does not remain
  on disk with the plaintext password

#### Scenario: Password launch helper is cleaned after launch failure
- **WHEN** bootstrap creates a temporary TestClient launch helper
- **AND** the TestClient fails to start listening on the requested `ClientPort`
- **THEN** cleanup removes the temporary helper or leaves only an ACL-protected,
  non-plaintext diagnostic artifact

### Requirement: Bootstrap reruns cannot silently reuse stale TestClient state

The qa-mcp Windows bootstrap SHALL detect an existing listener or scheduled task
on the requested TestClient port before launching a new TestClient. When it
cannot prove that the existing listener belongs to the same intended bootstrap
run, it SHALL stop with an explicit stale-client diagnostic or replace the owned
previous TestClient before continuing.

#### Scenario: Existing listener blocks ambiguous rerun
- **WHEN** `ClientPort` already accepts TCP connections before bootstrap starts
  the new TestClient
- **AND** bootstrap cannot prove that listener is the intended client for the
  requested `Infobase`
- **THEN** bootstrap exits with a clear stale-client diagnostic
- **AND** it does not report success against the stale listener

#### Scenario: Rerun does not keep stale scheduled task state
- **WHEN** a previous `qa-mcp-testclient` scheduled task exists
- **THEN** bootstrap deletes or replaces that task before the new launch attempt
- **AND** the task action does not preserve a stale password-bearing launch file

#### Scenario: Window title is tied to the launched client when available
- **WHEN** bootstrap derives a `WindowTitle` automatically
- **THEN** it prefers the process launched for this bootstrap run over the first
  arbitrary `1cv8` process
- **AND** it warns or fails loudly when it cannot disambiguate the active
  TestClient window

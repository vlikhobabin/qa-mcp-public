## ADDED Requirements

### Requirement: Bootstrap launches the TestClient with 1C-correct argument quoting

The bootstrap-generated TestClient launcher SHALL pass the 1C client arguments so that a
user name, password, or infobase path containing spaces is delivered to `1cv8` as 1C
expects — the value quoted immediately after its flag (`/N"<name>"`, `/P"<password>"`,
`/IBConnectionString "<connection>"`), with internal double-quotes doubled. The launcher
SHALL NOT rely on PowerShell array-form `Start-Process -ArgumentList @(…)` for these
arguments, because that wraps a spaced `/N<name>` element as `"/N<name>"` (quote before
the flag), which 1C rejects.

#### Scenario: A 1C user name containing spaces launches successfully

- **WHEN** bootstrap is run for a base whose 1C user name contains spaces (for example the
  [redacted third-party configuration] demo user `Тестовый Пользователь (Демо)`)
- **THEN** the generated launcher issues `/N"<name>"` (quote after the flag) as a single
  command-line token, the TestClient logs in and binds its TPort, and bootstrap does not
  abort with a login failure

#### Scenario: The launcher passes one verbatim command-line string, not an array

- **WHEN** the generated `launch-testclient.ps1` is inspected
- **THEN** it invokes `Start-Process … -ArgumentList '<one command-line string>'` with the
  1C-correct token quoting, and does not use the array form `-ArgumentList @(…)`

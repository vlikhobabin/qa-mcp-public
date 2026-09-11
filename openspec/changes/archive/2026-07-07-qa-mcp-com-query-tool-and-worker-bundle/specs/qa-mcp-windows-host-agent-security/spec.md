## ADDED Requirements

### Requirement: Host-agent health classifies COM worker feature impact
The authenticated host-agent `/health` response SHALL classify missing
`ai-com-worker.exe` as a feature-impact warning for COM flows while preserving
the top-level host-agent health for non-COM tools.

#### Scenario: Missing COM worker names affected features
- **WHEN** an authenticated client calls `/health`
- **AND** the configured COM worker executable is absent or not executable
- **THEN** the `com_worker` health object includes `available:false`,
  `severity:"warning"`, and affected feature names for host-side COM query,
  `/com/execute`, and COM read-smoke diagnostics
- **AND** the top-level `ok` value does not imply that COM worker dependent
  flows are available

#### Scenario: Available COM worker clears feature-impact warning
- **WHEN** an authenticated client calls `/health`
- **AND** the configured COM worker executable is present and executable
- **THEN** the `com_worker` health object includes `available:true`
- **AND** no missing-worker feature-impact warning is reported

### Requirement: Host-agent exposes an authenticated COMConnector doctor
The Windows host-agent SHALL expose an authenticated COMConnector doctor that
checks the 64-bit `V83.COMConnector` registration path, TypeLib registration,
COM creation, file-infobase connection, and optional read-query smoke without
accepting arbitrary host commands or exposing secrets.

#### Scenario: Missing or invalid token is rejected before doctor work
- **WHEN** a request to the COMConnector doctor omits
  `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns the existing unauthorized response
- **AND** no registry, COM creation, connection, or query smoke check is run

#### Scenario: TypeLib-missing diagnostic includes exact repair guidance
- **WHEN** the ProgID and `InprocServer32` entries exist for
  `V83.COMConnector`
- **AND** the 64-bit TypeLib entry for
  `{98AC3B5B-5323-418F-8F07-E32F231D2393}` is missing
- **THEN** the doctor returns `ok:false` with `error:"typelib-missing"`
- **AND** the diagnostic includes an elevated
  `C:\Windows\System32\regsvr32.exe "<path-to-comcntr.dll>"` repair command

#### Scenario: Doctor green path records read-query smoke
- **WHEN** the 64-bit COMConnector registry evidence is complete
- **AND** a host-side COM connection to the supplied file infobase succeeds
- **AND** an optional read query executes successfully
- **THEN** the doctor returns `ok:true`
- **AND** the response includes bounded platform, bitness, TypeLib, connection,
  and read-query smoke metadata without returning the infobase password

#### Scenario: Doctor rejects write-shaped smoke query
- **WHEN** a caller supplies a smoke query containing an obvious write or
  side-effecting 1C query operation
- **THEN** the doctor returns a read-only policy diagnostic
- **AND** it does not execute the query through COM

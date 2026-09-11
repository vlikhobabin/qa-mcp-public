## ADDED Requirements

### Requirement: Windows JSON-RPC examples send UTF-8 request bodies
Active qa-mcp delivery and troubleshooting runbooks SHALL send manual
PowerShell JSON-RPC examples as UTF-8 bytes and SHALL declare
`Content-Type: application/json; charset=utf-8` whenever the request body can
contain Cyrillic text such as a 1C navigation link.

#### Scenario: Manual Cyrillic request declares UTF-8
- **WHEN** a runbook shows a manual PowerShell JSON-RPC request with
  `open_link="e1cib/list/Справочник.Валюты"` or another Cyrillic argument
- **THEN** the example builds the request body with
  `[System.Text.Encoding]::UTF8.GetBytes(...)`
- **AND** the request declares
  `Content-Type: application/json; charset=utf-8`

#### Scenario: Non-UTF-8 PowerShell body is documented as a failure mode
- **WHEN** troubleshooting describes a Cyrillic navigation link failure
- **THEN** it explains that sending the JSON body as a PowerShell string or as
  a non-UTF-8 charset can corrupt the link before qa-mcp receives it
- **AND** it points operators to the echo diagnostic before treating the link as
  invalid in 1C

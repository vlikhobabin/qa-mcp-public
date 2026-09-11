## ADDED Requirements

### Requirement: JSON-RPC diagnostics echo received Cyrillic arguments
qa-mcp SHALL expose an MCP diagnostic that returns the exact Unicode argument
values received after JSON-RPC parsing, including `open_link` and arbitrary
caller-provided Cyrillic text. The diagnostic MUST flag values that contain
Unicode replacement characters or question-mark mojibake patterns so callers can
distinguish an encoding failure from an invalid 1C navigation link.

#### Scenario: Cyrillic navigation link is echoed unchanged
- **WHEN** a caller sends a diagnostic request with
  `open_link="e1cib/list/Справочник.Валюты"`
- **THEN** the result includes the same `received.open_link` value
- **AND** the result reports no mojibake warning for that value

#### Scenario: Mojibake navigation link is flagged
- **WHEN** a caller sends a diagnostic request with
  `open_link="e1cib/list/??????????.??????"`
- **THEN** the result echoes the same received value
- **AND** the result includes a structured warning that the value looks like
  mojibake or replacement text

### Requirement: Direct HTTP JSON-RPC bodies require UTF-8
qa-mcp's direct HTTP MCP transport SHALL reject JSON request bodies whose
`Content-Type` declares a non-UTF-8 charset or whose bytes cannot be decoded as
UTF-8. The rejection MUST occur before MCP tool dispatch and MUST return a
clear JSON error that names the UTF-8 request-body requirement.

#### Scenario: Non-UTF-8 charset is rejected
- **WHEN** qa-mcp direct HTTP transport receives a JSON-RPC POST with
  `Content-Type: application/json; charset=windows-1251`
- **THEN** the response is an HTTP client error
- **AND** the JSON error explains that JSON-RPC bodies must use UTF-8
- **AND** no MCP tool is dispatched

#### Scenario: Invalid UTF-8 bytes are rejected
- **WHEN** qa-mcp direct HTTP transport receives an `application/json` POST
  whose body bytes are not valid UTF-8
- **THEN** the response is an HTTP client error
- **AND** the JSON error explains that the request body is not valid UTF-8
- **AND** no MCP tool is dispatched

#### Scenario: UTF-8 JSON body is accepted
- **WHEN** qa-mcp direct HTTP transport receives a JSON-RPC POST with
  `Content-Type: application/json; charset=utf-8`
- **AND** the body bytes decode as UTF-8
- **THEN** the request reaches normal MCP dispatch

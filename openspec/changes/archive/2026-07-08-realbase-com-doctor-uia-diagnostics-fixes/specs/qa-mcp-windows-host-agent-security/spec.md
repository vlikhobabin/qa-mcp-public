## ADDED Requirements

### Requirement: COMConnector doctor read-smoke works against a real Russian-locale file base

The Windows host-agent `/com/doctor` read-smoke SHALL connect to a file infobase
and return a structured read result using only facilities available to the
classic WSH JScript engine invoked by `cscript //E:JScript`, and SHALL preserve
non-ASCII (Cyrillic) connection credentials end to end.

#### Scenario: JScript serializes without the JSON object

- **WHEN** the doctor read-smoke script produces its result on an engine where
  the `JSON` object is not defined
- **THEN** the host-agent SHALL serialize the result with a self-contained
  encoder and MUST NOT depend on `JSON.stringify`/`JSON.parse`

#### Scenario: 1C COM column count is read as a method

- **WHEN** the read-smoke enumerates a query result's columns
- **THEN** it SHALL invoke `Columns.Count()` as a method and MUST NOT read
  `Columns.Count` as a property (which raises "Object doesn't support this
  property or method")

#### Scenario: Cyrillic username survives the doctor payload transport

- **WHEN** the host-agent passes a `/com/doctor` request whose user is a Cyrillic
  1C user (for example `Админ`) to the JScript over `cscript` stdin
- **THEN** the payload SHALL be ASCII `\uXXXX`-escaped so the ANSI stdin decoding
  cannot corrupt the username, and `COMConnector.Connect` SHALL authenticate with
  the intended credentials rather than failing with a wrong-user/password error

#### Scenario: Non-zero cscript exit surfaces the structured error

- **WHEN** the doctor read-smoke script exits non-zero after writing a structured
  `{ok:false,error,detail}` object to stdout
- **THEN** the host-agent SHALL report that structured detail, and MUST NOT
  replace it with an empty-stderr placeholder such as "COM worker failed without
  diagnostic output"

### Requirement: UIA visible-cells read tolerates a PowerShell CLIXML wrapper

The Windows host-agent `/uia/visible_list_cells` read SHALL return the visible
list cells even when the underlying PowerShell invocation prepends a
`#< CLIXML` progress/verbose wrapper to its redirected output.

#### Scenario: First-use module progress does not break the JSON parse

- **WHEN** the UIA PowerShell script's first `Add-Type` emits a "Preparing
  modules for first use" progress record that PowerShell serializes as a
  `#< CLIXML` wrapper around the JSON output
- **THEN** the host-agent SHALL suppress the progress stream and/or extract the
  JSON object from the wrapped output, and SHALL return `ok:true` with the real
  cells instead of a `primitive-failed` / invalid-JSON error

## ADDED Requirements

### Requirement: Open-list navigation defaults to released runtime assets
The `open_list` endpoint SHALL open a requested list through the supported
versioned navigation-template path when the caller omits `capture` or supplies
a blank capture selector. The public default MUST NOT name a historical
development capture and MUST NOT resolve a blank selector as
`/work/traffic.jsonl`.

#### Scenario: Caller omits capture
- **WHEN** a caller invokes `open_list` without `capture`
- **THEN** qa-mcp selects the bundled bootstrap and navigation templates for the active platform family
- **AND** it sends the requested `e1cib/list/...` navigation through the attached TestClient endpoint
- **AND** it does not resolve a development capture directory or `/work/traffic.jsonl`

#### Scenario: Caller supplies a blank capture selector
- **WHEN** a caller invokes `open_list` with an empty or whitespace-only `capture`
- **THEN** qa-mcp treats the selector as omitted and uses the supported template-backed navigation path
- **AND** it does not interpret the current work directory as a capture directory

### Requirement: Open-list explicit capture compatibility is retained
The `open_list` endpoint SHALL preserve its explicit capture replay path for a
non-blank capture selector, including neutral versioned captures bundled in the
released package.

#### Scenario: Caller selects a bundled capture explicitly
- **WHEN** a caller invokes `open_list` with a non-blank bundled capture name
- **THEN** qa-mcp resolves and derives that capture explicitly
- **AND** the native open-list helper receives the caller's target catalog and attached endpoint

### Requirement: Open-list asset failures occur before protocol writes
The template-backed `open_list` path MUST validate every required bootstrap and
navigation-template asset before it opens a TestClient connection or writes a
protocol frame. An unavailable asset SHALL return a typed capability diagnostic
without exposing a traceback or machine-local asset path.

#### Scenario: Optional navigation template is missing
- **WHEN** the default or explicitly selected navigation-template asset cannot be loaded or lacks the required splice frame
- **THEN** `open_list` returns `ok: false` with error `open-list-navigation-unavailable`
- **AND** the result identifies capability `template-backed-open-list` and the failing asset class
- **AND** `protocol_write_attempted` is `false`
- **AND** no TestClient session or socket is opened

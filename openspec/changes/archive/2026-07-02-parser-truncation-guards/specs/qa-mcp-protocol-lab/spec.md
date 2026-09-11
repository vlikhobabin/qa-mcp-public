## ADDED Requirements

### Requirement: Response parsers tolerate truncated envelopes
The Python manager SHALL treat truncated response envelopes as partial data
instead of raising parser exceptions from out-of-bounds byte indexing.

#### Scenario: Truncated value envelope is scanned
- **WHEN** a response blob ends at or immediately after a value marker without
  enough bytes for the expected value envelope
- **THEN** form-field extraction returns a partial result or `None` for the
  affected value
- **AND** no `IndexError` escapes the parser

#### Scenario: Truncated window caption envelope is scanned
- **WHEN** a response blob ends at or immediately after a window caption marker
- **THEN** window extraction returns a partial result or omits that caption
- **AND** no `IndexError` escapes the parser

### Requirement: Response parsers reject unsupported field-name encodings safely
The Python manager SHALL handle non-Latin field-name scans as unsupported
scanner input and return no value rather than raising a Unicode encoding error.

#### Scenario: Cyrillic field name is scanned
- **WHEN** a parser helper receives a Cyrillic field name for a scanner path that
  is limited to Latin-1 byte search
- **THEN** the helper returns `None`
- **AND** no `UnicodeEncodeError` escapes the parser

### Requirement: List-grid reads do not stop on adjacent duplicate rows
The Python manager SHALL preserve adjacent duplicate list-grid rows and SHALL
surface timeout or empty-row stops explicitly when a list-grid sweep ends early.

#### Scenario: Adjacent duplicate rows are read
- **WHEN** a list-grid contains two adjacent rows whose requested column values
  are equal
- **THEN** `read_list_grid` returns both rows
- **AND** the sweep does not treat equality with the previous row as end of list

#### Scenario: Row read times out
- **WHEN** a row read times out before the requested values can be confirmed
- **THEN** the list-grid result includes explicit truncation or stop-reason
  metadata
- **AND** callers can distinguish timeout truncation from a genuine empty row

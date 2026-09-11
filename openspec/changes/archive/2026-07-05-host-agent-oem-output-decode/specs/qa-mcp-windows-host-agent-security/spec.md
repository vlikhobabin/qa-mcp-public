## ADDED Requirements

### Requirement: Platform command output preserves localized diagnostics
The Windows host-agent SHALL return readable bounded stdout and stderr strings
from `POST /platform/execute` for valid UTF-8, ASCII, and Russian OEM console
output. Secret-bearing arguments echoed by a platform command MUST remain
redacted after decoding.

#### Scenario: CP866 Russian stdout is decoded before JSON response
- **WHEN** an authenticated `/platform/execute` request runs an allowlisted
  platform command whose stdout contains Russian text encoded as CP866
- **THEN** the response `stdout` contains readable Unicode text
- **AND** the response does not contain replacement-character noise for that
  text.

#### Scenario: UTF-8 and ASCII output are preserved
- **WHEN** an authenticated `/platform/execute` request returns valid UTF-8 or
  ASCII stdout/stderr
- **THEN** the host-agent returns the same text content in JSON
- **AND** the existing output length bounds still apply by rune count.

#### Scenario: Decoded output is still redacted
- **WHEN** a platform command echoes password-like arguments or connection
  string secret values in stdout or stderr
- **THEN** the host-agent redacts those values after decoding
- **AND** the returned diagnostics contain the redaction marker rather than the
  original secret.

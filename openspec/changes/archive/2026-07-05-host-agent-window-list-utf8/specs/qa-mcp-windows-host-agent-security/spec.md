## ADDED Requirements

### Requirement: Host-agent window list preserves localized titles

The Windows host-agent SHALL return authenticated `/window_list` entries with
readable Unicode window titles in JSON. Russian and other non-ASCII titles MUST
NOT be returned as mojibake, replacement-character noise, or host code-page
artifacts.

#### Scenario: Russian 1C title is readable
- **WHEN** an authenticated client calls `/window_list` and a visible top-level
  window has the title `Клиент тестирования 3.1.5`
- **THEN** the JSON response contains that title as readable Unicode text
- **AND** the response does not contain mojibake such as `Ð` fragments for that
  title

#### Scenario: ASCII title remains unchanged
- **WHEN** an authenticated client calls `/window_list` and a visible top-level
  window has an ASCII title
- **THEN** the JSON response contains the same text content
- **AND** existing geometry fields and authentication behavior remain unchanged

### Requirement: Host-agent window selection diagnostics identify weak matches

Window-selection helpers that consume `/window_list` SHALL distinguish a
strong explicit title match from a weak generic or missing match. When only a
generic `Клиент тестирования` fallback is available, the helper MUST emit
operator guidance to pass `-WindowTitle` with a more specific fragment.

#### Scenario: Weak fallback is reported
- **WHEN** bootstrap auto-detection cannot find a specific 1C title and falls
  back to `Клиент тестирования`
- **THEN** the operator output marks the title as a fallback
- **AND** it tells the operator to rerun with `-WindowTitle` if focus or
  screenshot tools target the wrong window

#### Scenario: Strong title needs no warning
- **WHEN** bootstrap auto-detection receives a non-empty `/window_list` title
  that is not the generic fallback
- **THEN** the selected title is reported normally
- **AND** no weak-fallback warning is emitted

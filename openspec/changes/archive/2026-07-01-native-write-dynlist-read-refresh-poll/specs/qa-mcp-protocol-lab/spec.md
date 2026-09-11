## ADDED Requirements

### Requirement: Dynamic-list reads force a refresh and poll until stable
Dynamic-list read primitives (`read_list_grid`, `read_list_row`, `read_list_column`, `search_list`) SHALL, before
reporting row results, force a list refresh and poll the row read until it is stable, so that a reported `0`-row result
denotes a genuinely empty list rather than a stale or not-yet-loaded dynamic list. The refresh SHALL prefer a protocol
replay of the list's «Обновить»/F5 command and MUST fall back to an OS-level `F5` keystroke into the focused list window
when the protocol command is not reachable. Polling SHALL re-read the row count until it is stable (two equal successive
reads) or non-zero, up to a bounded timeout. A shared helper SHALL provide this behavior to all four primitives so the
refresh-and-poll policy is applied uniformly.

#### Scenario: Freshly created record is returned after refresh
- **WHEN** a record is created and committed, then a dynamic-list read is issued for that catalog's list on a freshly
  launched TestClient with refresh enabled
- **THEN** the read forces a list refresh, polls until the row count is stable, and returns the persisted record
- **AND** the read does not report `0 rows` while the record is present in the list

#### Scenario: Genuinely empty list is unambiguous after refresh
- **WHEN** a dynamic-list read is issued against a list that contains no records
- **THEN** after the forced refresh and stable-poll the read reports `0 rows` as an empty result
- **AND** the result does not carry the legacy "EITHER empty OR cold-boundary" ambiguity for the refreshed path

#### Scenario: Read waits for an expected minimum row count
- **WHEN** a dynamic-list read is issued with `wait_for_rows`/`expected_min_rows` set to N
- **THEN** the read blocks until at least N rows are read or the bounded timeout elapses
- **AND** the returned result records whether the expected minimum was met within the timeout

### Requirement: Dynamic-list refresh is on by default and evidence-backed
Dynamic-list read primitives SHALL default to `refresh=True`, and SHALL expose an explicit opt-out for tests that must
assert a row is absent WITHOUT a refresh. The read result SHALL record the refresh action taken (protocol «Обновить»
command replay or `F5` fallback) and the poll outcome (stable row count or timeout) as retained evidence for the read,
so a currency-correct read is observable and auditable rather than implicit.

#### Scenario: Refresh default is applied and recorded
- **WHEN** a dynamic-list read is issued without an explicit `refresh` argument
- **THEN** the primitive applies the refresh-and-poll path and records the refresh method and poll outcome in the result

#### Scenario: Refresh opt-out is honored for absence assertions
- **WHEN** a dynamic-list read is issued with the refresh opt-out set
- **THEN** the primitive reads without forcing a refresh
- **AND** the result marks that no refresh was applied so an absence assertion is not masked by an implicit refresh

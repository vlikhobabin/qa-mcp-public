## ADDED Requirements

### Requirement: Protocol cleanup removes only verified dead helpers

The Python manager SHALL remove dead protocol helpers only when current source
references and tests prove they are not on a live path. Helpers that remain live
MUST be preserved even if they appeared in an earlier review's dead-code list.

#### Scenario: Verified dead MCP helpers are absent

- **WHEN** cleanup is complete
- **THEN** source search finds no `_RESOLVE_SF_RE`, `_CreateForegroundHold` or
  `_OPEN_LINK_LABEL_ALIASES`
- **AND** the offline test suite still passes

#### Scenario: Live splice activation helper is preserved

- **WHEN** cleanup is complete
- **THEN** `_splice_window_activate_command` remains available to the label
  locate retry path
- **AND** the retry path tests or source checks prove it is still referenced

#### Scenario: Mutation helper module is removed only if no live path imports it

- **WHEN** `mutation.py` is considered for removal
- **THEN** source analysis proves `native_mutation` no longer imports it on a
  live path or the import has been replaced safely
- **AND** otherwise the module remains and the residual reason is recorded

### Requirement: Duplicate protocol utilities collapse only with equivalent behavior

The Python manager SHALL collapse duplicate protocol utilities only when the
replacement preserves behavior for existing callers and is covered by focused
tests or source checks.

#### Scenario: Duplicate helper is replaced by shared implementation

- **WHEN** a duplicate helper such as date normalization, GUID substitution,
  capture chunk loading or LEB128 decoding is removed
- **THEN** all former call sites use the shared implementation
- **AND** focused tests cover the previous behavior

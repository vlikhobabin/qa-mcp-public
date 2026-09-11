## ADDED Requirements

### Requirement: Screenshot cleanup follows trusted current production
The bound screenshot producer SHALL allocate a fresh owned destination within the
admitted root and validate backend-returned identity before reading, registering
or deleting it. A borrowed old path or symlink SHALL NOT authorize cleanup.
Sanitized policy SHALL remove only its own current raw capture and retain safe
verifiable artifact metadata; full_local SHALL retain useful current evidence.

#### Scenario: Borrowed backend file is preserved
- **WHEN** a backend returns an unrelated pre-existing path, wrong destination or symlink
- **THEN** bound capture is non-success and neither reads it as accepted evidence nor deletes/modifies the borrowed file
- **AND** unrelated sentinels and concurrent sibling bytes remain unchanged

#### Scenario: Cleanup and failure isolation
- **WHEN** an owned capture succeeds or its producer/validation/cleanup fails while a sibling is paused after production
- **THEN** only the current scope records and owned temporary resources are closed or cleaned
- **AND** no success claims missing evidence or failed required sanitization, and the sibling remains usable

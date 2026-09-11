## MODIFIED Requirements

### Requirement: Release publishing waits for pytest
qa-mcp release publishing SHALL depend on a passing offline pytest job before
building or pushing source-visible release artifacts.

#### Scenario: Release build is gated by pytest
- **WHEN** the release workflow is triggered by a version tag or manual dispatch
- **THEN** the source-visible artifact build and publish job starts only after
  the Python pytest job succeeds

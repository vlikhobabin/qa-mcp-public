## ADDED Requirements

### Requirement: Offline pytest runs for repository changes
qa-mcp SHALL run the offline Python pytest suite in GitHub Actions for branch
pushes and pull requests using the repository's locked `uv` environment.

#### Scenario: Push or pull request runs pytest with coverage
- **WHEN** a branch push or pull request triggers the CI workflow
- **THEN** the workflow installs development dependencies with `uv`
- **AND** it runs pytest for `qa_mcp` with line coverage reporting
- **AND** it fails when pytest fails or coverage drops below the configured floor

#### Scenario: CI run stays hermetic
- **WHEN** the default CI pytest job runs on a hosted Linux runner
- **THEN** live 1C runtime tests are excluded by marker selection
- **AND** the job does not require a local 1C client, infobase, display server,
  capture refresh, or live regression harness

### Requirement: Release publishing waits for pytest
qa-mcp release publishing SHALL depend on a passing offline pytest job before
building or pushing protected image artifacts.

#### Scenario: Release build is gated by pytest
- **WHEN** the release workflow is triggered by a version tag or manual dispatch
- **THEN** the protected image build and publish job starts only after the
  Python pytest job succeeds

### Requirement: Pytest categories are explicit
qa-mcp SHALL declare pytest markers for offline, live, integration, slow, and
capture-dependent tests so CI selection is intentional.

#### Scenario: Strict marker collection recognizes qa-mcp categories
- **WHEN** pytest collects tests with strict marker validation
- **THEN** the configured qa-mcp marker names are accepted
- **AND** future live or integration tests can be selected or excluded without
  relying only on missing-file skip behavior

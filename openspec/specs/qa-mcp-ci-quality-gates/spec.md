# qa-mcp-ci-quality-gates Specification

## Purpose

qa-mcp CI checks changed modules and their affected consumers in separate offline
and integration lanes. Full-suite coverage belongs to epic closure or explicit
operator agreement; live 1C runtime checks remain separately authorized.

## Requirements

### Requirement: Offline pytest runs for repository changes
qa-mcp SHALL run affected offline Python tests in GitHub Actions for branch
pushes and pull requests using the repository's locked `uv` environment.
Affected subprocess/build/display tests SHALL run in a separate integration lane.

#### Scenario: Push or pull request runs affected tests
- **WHEN** a branch push or pull request triggers the CI workflow
- **THEN** the workflow installs development dependencies with `uv`
- **AND** it selects tests from changed modules and their declared/transitive consumers against the event comparison base
- **AND** it fails when selected tests fail or a changed product input lacks a test mapping
- **AND** it does not silently fall back to a full suite or require whole-product coverage from a partial run

#### Scenario: CI run stays hermetic
- **WHEN** the default CI pytest job runs on a hosted Linux runner
- **THEN** live Linux/Windows 1C tests are excluded from both ordinary lanes
- **AND** the job does not require a local 1C client, infobase, preexisting live display server,
  capture refresh, or live regression harness

### Requirement: Release publishing waits for pytest
qa-mcp release publishing SHALL depend on a passing affected Python pytest job before
building or pushing source-visible release artifacts.

#### Scenario: Release build is gated by pytest
- **WHEN** the release workflow is triggered by a version tag or manual dispatch
- **THEN** the source-visible artifact build and publish job starts only after
  Python pytest job succeeds
- **AND** the affected comparison uses the previous release baseline without treating a release trigger as full-suite authorization

### Requirement: Full suite requires explicit authority
qa-mcp MUST reserve full offline/integration pytest and the combined coverage floor
of at least 60 percent for epic closure or explicit operator agreement.

#### Scenario: Ordinary delivery does not authorize a full run
- **WHEN** a card completes or a push, PR or release event occurs
- **THEN** affected-module checks remain the default
- **AND** the event alone does not authorize a full-suite run

#### Scenario: Authorized full verification records its reason
- **WHEN** an operator requests full verification or an epic reaches its final verification
- **THEN** the invocation records the epic card or explicit agreement
- **AND** offline and integration execute separately, combine coverage and retain their counts, durations and results

### Requirement: Pytest categories are explicit
qa-mcp SHALL declare pytest markers for offline, live, integration, slow, and
capture-dependent tests and explicit offline/integration/live-linux/live-windows
selection lanes so CI selection is intentional.

#### Scenario: Strict marker collection recognizes qa-mcp categories
- **WHEN** pytest collects tests with strict marker validation
- **THEN** the configured qa-mcp marker names are accepted
- **AND** future live or integration tests can be selected or excluded without
  relying only on missing-file skip behavior

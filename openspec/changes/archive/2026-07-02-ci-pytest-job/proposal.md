## Why

The release workflow can build and publish qa-mcp artifacts without running the
offline Python test suite. That lets a red or shrinking pytest suite escape
notice until a developer runs it locally.

## What Changes

- Add a GitHub Actions CI workflow that runs the offline pytest suite on push
  and pull request events.
- Report Python coverage for `qa_mcp` and enforce a modest floor below the
  current baseline so regressions are visible without overfitting the first
  gate.
- Register pytest markers for offline, live, integration, and slow test
  categories so CI can stay hermetic while future live tests are explicitly
  separated.
- Gate the release workflow so the protected image build only runs after the
  pytest job passes.
- Update verification docs with the CI-equivalent pytest and coverage command.

## Capabilities

### New Capabilities

- `qa-mcp-ci-quality-gates`: CI runs the offline Python test suite with coverage
  and blocks release publishing when the suite is red.

### Modified Capabilities

- none

## Impact

- Touches GitHub Actions workflow files, pytest configuration, and local
  verification docs.
- Does not change protocol tools, Python manager runtime code, MCP provider
  setup, OpenSpec workflow, or runtime lab configuration.
- Requires only offline pytest and OpenSpec evidence; no live 1C runtime,
  Vanessa MCP, EDT/meta snapshots, capture replay, or networked 1C access is
  required.

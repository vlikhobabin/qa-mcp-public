## Context

The repository currently has one GitHub Actions workflow:
`.github/workflows/release.yml`. That workflow runs Go tests for the Windows
host agent and verifies the protected image, but it never runs the Python pytest
suite. Local docs describe `python -m pytest -q` as the offline verification
command, while the card asks for the locked `uv` route with coverage reporting.

The Python test suite is expected to stay hermetic by default. Live 1C runtime,
capture refresh, networked infobase, display, and regression harness execution
remain separate from the CI gate.

## Goals / Non-Goals

**Goals:**

- Run offline pytest on push and pull request events.
- Use the locked `uv` environment and install development dependencies needed
  by the coverage gate.
- Report skipped tests and line coverage, and fail below a 60% coverage floor.
- Prevent release image build and publish when pytest fails.
- Register explicit pytest marker categories for future live/integration tests.

**Non-Goals:**

- Do not run native 1C `/TESTCLIENT`, live regression, capture refresh, display
  screenshot, Docker image verification, or external-network tests in the
  regular pytest CI job.
- Do not raise the coverage floor above the current local baseline in this
  change.
- Do not reclassify the existing capture-gated skip tests unless they require a
  separate behavior change.

## Decisions

- Add a standalone `.github/workflows/ci.yml` workflow for push and pull request
  pytest checks. Keeping it separate from the tag-only release workflow makes
  the every-change gate visible even when no release is being cut.
- Add a `python-tests` job to `release.yml` and make the existing release job
  depend on it with `needs: python-tests`. This avoids relying on a separate
  workflow completion trigger before protected image build and publish.
- Use `uv sync --extra dev --locked` followed by
  `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`.
  The marker expression keeps future live tests out of CI, while `-ra` keeps
  skip reasons visible for machine-dependent tests.
- Add `pytest-cov` to the development optional dependencies because `--cov`
  depends on that pytest plugin.
- Register `offline`, `live`, `integration`, `slow`, and `capture` markers in
  `pyproject.toml`. The first gate excludes only `live`; the remaining markers
  provide named categories for later tests without changing current collection.

## Risks / Trade-offs

- [Risk] The 60% coverage floor can hide smaller regressions above the threshold.
  Mitigation: set the first gate just below the current baseline and document
  that it is intended to ratchet upward as coverage improves.
- [Risk] Capture-gated tests can still skip on clean runners.
  Mitigation: keep `-ra` in CI output so skipped reasons are visible instead of
  silently disappearing.
- [Risk] Running pytest in both CI and release workflows duplicates several
  minutes of work on tag builds.
  Mitigation: keep the release-local job because it is the reliable pre-build
  gate for protected image publishing.

## 1. Supplied Bundle Trust Boundary

- [x] 1.1 Add RED tests for `--skip-gates` supplied-executable bypass and missing VCS/source metadata.
- [x] 1.2 Make publisher verification unconditional and require the adjacent source-bound bundle manifest and sha sidecar.
- [x] 1.3 Require exact VCS revision and modified-state metadata in the artifact verifier.

## 2. Verification And Handoff

- [x] 2.1 Run focused release/artifact tests, deterministic local builds and the
  clean-source refusal contract, shell syntax, full offline Python/Go gates,
  strict OpenSpec and `git diff --check`.
- [x] 2.2 Sync the release contract, update documentation and add the change to the combined atomic QA card scope.

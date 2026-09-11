## 1. Installer G12 contract

- [x] 1.1 Add a focused RED test for complete registry parameters,
  all-or-nothing validation and scheduled-task flags.
- [x] 1.2 Implement fail-closed registry validation and task rendering while
  preserving empty-registry solo mode.
- [x] 1.3 Run the focused installer/release suite and source checks.

## 2. Current source-bound Windows proof

- [x] 2.1 Build and verify a new source-bound Windows bundle from the complete
  current Go tree and retain its manifest and SHA.
- [x] 2.2 Generate fresh ignored stand credentials, bring up the bounded T4
  license/registry control plane and stage the exact workspace/user inputs.
- [x] 2.3 Run the supported installer on both authorized Windows builds and
  retain exact staged/installed/running SHA, G12 registered state and G14
  ready/restart/windowless state.

## 3. Cleanup and lifecycle

- [x] 3.1 Remove only resources owned by this run and prove exact comparison
  with the immutable initial preflight.
- [x] 3.2 Produce a sanitized evidence index/final scan and update both owner
  cards plus the combined scoped manifest.
- [x] 3.3 Run full QA gates, sync the release spec and archive the change
  without publishing.

## 1. Windowless process attributes

- [x] 1.1 Preserve caller-applied Windows process flags when adding an owned
      process group.
- [x] 1.2 Start the console-dependent BSL helper with hidden initial window
      semantics while retaining its console and process group.
- [x] 1.3 Add Windows attribute regressions for ordinary and BSL helpers.

## 2. Owned reinstall reconciliation

- [x] 2.1 Stop only a stale BSL process whose executable equals the staged
      installer-owned path before artifact replacement.
- [x] 2.2 Add installer contract coverage that rejects name-wide cleanup.

## 3. Verification

- [x] 3.1 Run focused/full Go and Python tests, Windows cross-build, source-bound
      artifact build, strict OpenSpec validation and diff/secret checks.
- [x] 3.2 Install on `.201` and `.205`; prove healthy stable BSL supervision and
      no visible/focus-stealing helper consoles, retaining sanitized T4 evidence.

## Verification Evidence

- The source-bound binary was installed on both stations with SHA256
  `55e57bd2bc4c35f026b4c600ed327b2f5e6c9fed24146966d3d39e37814e304d`.
- Full Python (829), Go and Windows cross-build suites passed; strict OpenSpec
  and diff checks passed.
- Final M9 retained one host-agent and one BSL process on each station, BSL
  `ready`, restart_count=0, visible_count=0 and transient_task_count=0:
  `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260713T200946Z-release-ready-rerun/matrix/M09/solo-regression.json`.

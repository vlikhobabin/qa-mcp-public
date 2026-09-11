## 1. Add Isolated Snapshot Proof

- [x] 1.1 Add failing tests for Git-visible snapshot selection, ignored-state
  exclusion, package legal metadata and mandatory gate failures.
- [x] 1.2 Implement owned-temporary snapshot copy/build/smoke behavior and
  concise JSON outcomes without copying `.git`, auth, env, runtime state or
  the 34 absolute `/opt/changerail` symlinks.
- [x] 1.3 Prove locked public dependencies and source/wheel/sdist build in the
  isolated snapshot using documented offline commands, including package
  install/import, focused tests, audit/provenance/docs/I2 and inspected package
  metadata plus LICENSE/NOTICE.

## 2. Run Final Offline Floor

- [x] 2.1 Run complete non-live pytest, package build, public audit,
  provenance check, docs/link checks and I2 23-mutation oracle with retained
  raw evidence only under ignored ChangeRail state.
- [x] 2.2 Run strict change/all OpenSpec validation plus tracked and untracked
  whitespace checks, then reconcile the exact delivery manifest scope.
- [x] 2.3 Record Docker daemon, Windows, SSH, 1C, TestClient, live services and
  network clone as not applicable for this public-safe source-readiness gate;
  do not run them because OSS-08 owns release publication.

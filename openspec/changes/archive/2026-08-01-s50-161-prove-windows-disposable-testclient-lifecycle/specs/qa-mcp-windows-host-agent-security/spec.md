## ADDED Requirements

### Requirement: Disposable Windows TestClient proof uses a platform-restored infobase and exact cleanup

A cross-platform disposable TestClient proof SHALL create the Windows file
infobase through the target Windows platform and restore a portable backup, or
otherwise validate the copied format on Windows before launch. It MUST retain
before/after exact-owned inventory and MUST NOT clean unrelated tasks,
processes, ports, Docker resources or user data.

#### Scenario: Portable deployed proof is restored on Windows

- **WHEN** a disposable extension-bearing Linux proof is transferred to the
  authorized Windows station
- **THEN** a portable backup is restored into a Windows-created exact run-owned
  file infobase using the pinned platform build
- **AND** successful restore evidence precedes TestClient launch.

#### Scenario: UI mutation is recovered by exact stage cleanup

- **WHEN** qa-mcp creates a unique disposable catalog item in the restored proof
  infobase
- **THEN** retained evidence shows the item in the catalog UI and ignored
  screenshot evidence exists
- **AND** cleanup removes the exact restored stage and owned lifecycle resources
  so the item and infobase cannot survive the run.

#### Scenario: Cleanup proves a rerunnable contour

- **WHEN** the proof finishes or fails after staging
- **THEN** post-cleanup inventory shows the exact stage, scheduled tasks,
  host-agent/TestClient processes and proof listeners absent
- **AND** a fresh preflight confirms the same run namespace is clean without
  inspecting or removing unrelated user resources.

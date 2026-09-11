## ADDED Requirements

### Requirement: COM worker asset is optional and manifest driven
qa-mcp self-hosted releases SHALL support an optional `ai-com-worker.exe`
release asset supplied by the operator and SHALL keep the non-COM release path
working when the asset is absent.

#### Scenario: Release staging includes COM worker asset
- **WHEN** the publish helper stages a self-hosted release with
  `--com-worker-exe <path-to-ai-com-worker.exe>`
- **THEN** the versioned release directory contains `ai-com-worker.exe`
- **AND** the versioned release directory contains `ai-com-worker.exe.sha256`
- **AND** `manifest.json` declares `ai-com-worker.exe` under assets with sha256
  and size metadata

#### Scenario: Release staging without COM worker remains compatible
- **WHEN** the publish helper stages a self-hosted release without
  `--com-worker-exe`
- **THEN** the release is staged with the existing required assets
- **AND** `manifest.json` does not declare `ai-com-worker.exe`
- **AND** the helper emits an operator-visible warning that COM worker delivery
  is not bundled

#### Scenario: Bootstrap installs declared COM worker
- **WHEN** `bootstrap.ps1` runs from a self-hosted release whose manifest
  declares `ai-com-worker.exe`
- **THEN** bootstrap downloads `ai-com-worker.exe` from `ReleaseBase`
- **AND** bootstrap verifies the downloaded file against the manifest sha256
- **AND** bootstrap passes the verified worker path to
  `install-windows-host-agent.ps1` before the host-agent scheduled task is
  created

#### Scenario: Bootstrap tolerates releases without COM worker
- **WHEN** `bootstrap.ps1` runs from a self-hosted release whose manifest does
  not declare `ai-com-worker.exe`
- **THEN** bootstrap installs the host-agent using the existing non-COM path
- **AND** bootstrap does not fail solely because the optional COM worker asset is
  absent

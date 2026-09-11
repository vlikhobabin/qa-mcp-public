## ADDED Requirements

### Requirement: Standard self-hosted publish wires the COM worker asset
The standard qa-mcp self-hosted publish path SHALL accept the ready
`ai-com-worker.exe` from an explicit argument or ignored release defaults and
SHALL pass the verified asset through the existing manifest/bootstrap/installer
path so host-agent `/com/execute` is available after install when the asset was
provided.

#### Scenario: Release defaults can supply COM worker asset
- **WHEN** `.ai/release.env` or `.ai1c/release.env` defines a COM worker
  executable path and the operator does not pass `--com-worker-exe`
- **THEN** `publish_self_hosted.sh` stages that worker as `ai-com-worker.exe`
- **AND** the versioned release directory includes the worker, sha256 sidecar,
  and manifest asset metadata

#### Scenario: Explicit COM worker argument still wins
- **WHEN** release defaults define a COM worker executable path
- **AND** the operator passes `--com-worker-exe <other-path>`
- **THEN** the helper stages the explicit path
- **AND** the staged manifest records the explicit worker's hash and size

#### Scenario: Release without COM worker stays non-COM compatible
- **WHEN** no COM worker path is supplied by argument or release defaults
- **THEN** the release remains valid for non-COM flows
- **AND** the helper emits an operator-visible warning that host-side COM query
  and COMConnector doctor flows require `ai-com-worker.exe`

### Requirement: Delivery docs identify COM worker health impact
The self-hosted delivery handoff SHALL state that `com_worker.available:false`
is a feature-impact warning for host-side COM flows and not a silent healthy
state for COM query usage.

#### Scenario: Missing worker warning names affected flows
- **WHEN** a release or install omits `ai-com-worker.exe`
- **THEN** delivery docs and bootstrap output identify host-side COM query and
  COMConnector read-smoke flows as unavailable until the worker is installed
- **AND** regular TestClient protocol tools remain described separately from
  the missing COM worker feature impact

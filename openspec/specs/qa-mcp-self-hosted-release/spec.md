# qa-mcp-self-hosted-release Specification

## Purpose
Define the qa-mcp self-hosted release channel for Windows model-B delivery,
including manifest-driven assets, checksum verification, Docker archive loading
and bearer-token MCP access.
## Requirements
### Requirement: Self-hosted release assets are manifest driven
qa-mcp releases SHALL publish a component manifest, Docker archive, sha256 sidecars
and Windows assets under the qa-mcp self-hosted release namespace.

#### Scenario: Release staging creates versioned assets
- **WHEN** the publish helper stages version `vX.Y.Z`
- **THEN** it creates a manifest, image archive, sha256 sidecars, bootstrap,
  host-agent installer, host-agent executable and delivery docs in the versioned
  release directory

#### Scenario: Public release link is activated
- **WHEN** the helper is invoked with server activation options
- **THEN** exactly one current public qa-mcp release link points at the staged version

### Requirement: Self-hosted activation is atomic and immutable
The qa-mcp self-hosted publish helper SHALL activate a staged release on the
release server by copying into a temporary server-side version directory and
atomically moving that directory into `versions/<version>` only after the copy
has completed. After activation, the version directory SHALL be made read-only
for normal write paths so post-activation hand edits cannot silently mutate the
published asset set.

#### Scenario: Interrupted server copy does not wedge retries
- **WHEN** server activation is interrupted while assets are being copied to the
  release server
- **THEN** no final `versions/<version>` directory is left behind
- **AND** a later publish of the same version can retry activation after the
  temporary directory is cleaned

#### Scenario: Activated version directory is immutable
- **WHEN** server activation succeeds for version `vX.Y.Z`
- **THEN** `versions/vX.Y.Z` exists only after the complete staged directory has
  been copied
- **AND** the helper removes write permission from the activated version
  directory tree

### Requirement: Publish helper preserves explicit operator arguments
Ignored release environment files SHALL supply defaults only. Explicit
command-line arguments to `publish_self_hosted.sh` SHALL override values sourced
from `.ai/release.env` or legacy `.ai1c/release.env`.

#### Scenario: CLI version wins over release env
- **WHEN** `.ai1c/release.env` or `.ai/release.env` defines `VERSION`
- **AND** the operator invokes `publish_self_hosted.sh --version vCLI`
- **THEN** the staged manifest and directory use `vCLI`

#### Scenario: CLI release link wins over release env
- **WHEN** `.ai1c/release.env` or `.ai/release.env` defines `RELEASE_LINK_ID`
- **AND** the operator invokes `publish_self_hosted.sh --release-link-id r-cli`
- **THEN** the generated public release URL uses `r-cli`

### Requirement: Supplied image archive tag matches the manifest tag
When `--skip-build` stages an existing Docker archive, the publish helper SHALL
verify that the archive contains the image tag that will be written to
`manifest.json`. A mismatch SHALL fail before sidecars, manifest generation,
upload, or public-link activation.

#### Scenario: Missing image tag fails before staging
- **WHEN** the operator invokes `publish_self_hosted.sh --skip-build`
- **AND** `--image-archive` does not contain the supplied or default
  `--image-tag`
- **THEN** the helper exits non-zero with a clear image-tag mismatch error
- **AND** no version directory is staged

### Requirement: Delivery docs are generated through the manifest path
Durable qa-mcp delivery documents that are part of the tester handoff SHALL be
copied by `publish_self_hosted.sh`, receive sha256 sidecars, and be declared in
`manifest.json`. Post-activation manual copies into `versions/<version>` SHALL
not be a supported way to publish delivery docs.

#### Scenario: Agent install runbook is manifest staged
- **WHEN** the publish helper stages a self-hosted release
- **THEN** `agent-install-runbook.md` is present in the versioned release
  directory
- **AND** `agent-install-runbook.md.sha256` is present
- **AND** `manifest.json` declares `agent-install-runbook.md` with sha256 and
  size metadata

#### Scenario: Public link cleanup tolerates non-symlink entries
- **WHEN** activation succeeds and `public/` contains an unrelated non-symlink
  entry
- **THEN** cleanup skips that entry without causing the already-successful
  activation to exit non-zero

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

### Requirement: Bootstrap installs without GitHub or GHCR
The qa-mcp bootstrap SHALL install model B from `ReleaseBase` by downloading the
manifest and release assets, verifying sha256, loading the Docker archive and running
the loaded image tag.

#### Scenario: Bootstrap downloads from release base
- **WHEN** bootstrap runs with a self-hosted `ReleaseBase`
- **THEN** it downloads `manifest.json` and all required assets from that release
  base instead of GitHub Releases or GHCR

#### Scenario: Hash mismatch blocks execution
- **WHEN** a downloaded asset hash differs from the manifest value
- **THEN** bootstrap stops before executing that asset or loading the image

### Requirement: Bootstrap release bases are HTTPS-only
The qa-mcp Windows bootstrap SHALL reject plain `http://` release bases before
downloading `manifest.json`, scripts, executables, sidecars or Docker archives.

#### Scenario: HTTP release base is refused
- **WHEN** an operator invokes `bootstrap.ps1 -ReleaseBase http://example.test/qa-mcp/r-test`
- **THEN** bootstrap exits with a clear HTTPS-required error
- **AND** no release asset is downloaded

#### Scenario: HTTPS release base is accepted for verification
- **WHEN** an operator invokes `bootstrap.ps1 -ReleaseBase https://releases.example.test/qa-mcp/r-test`
- **THEN** bootstrap proceeds to manifest signature verification before trusting
  any manifest asset metadata

### Requirement: Manifest metadata has a detached trust anchor
The qa-mcp self-hosted release channel SHALL publish a detached signature for
`manifest.json`, and `bootstrap.ps1` SHALL verify that signature with an
out-of-band public key before trusting manifest asset hashes or executing any
downloaded release asset.

#### Scenario: Missing manifest signature blocks bootstrap
- **WHEN** bootstrap downloads `manifest.json`
- **AND** the detached manifest signature is missing
- **THEN** bootstrap stops before downloading or executing manifest-declared
  assets

#### Scenario: Invalid manifest signature blocks bootstrap
- **WHEN** bootstrap downloads `manifest.json` and its detached signature
- **AND** signature verification fails against the configured public key
- **THEN** bootstrap stops before downloading or executing manifest-declared
  assets

#### Scenario: Valid manifest signature permits asset hash checks
- **WHEN** bootstrap verifies `manifest.json` against the configured public key
- **THEN** bootstrap may download manifest-declared assets
- **AND** each asset is still checked against the manifest sha256 before use

### Requirement: Bootstrap configures bearer-token MCP access
The qa-mcp bootstrap SHALL configure the suite proxy token for the container and
print MCP client configuration that includes a bearer token.

#### Scenario: Generated MCP token
- **WHEN** bootstrap runs without an explicit MCP proxy token
- **THEN** it generates one, passes it to the container, and includes it in the
  printed client configuration

### Requirement: Bootstrap prints the canonical MCP path

The qa-mcp bootstrap SHALL print MCP client configuration that uses the
canonical HTTP MCP path `/mcp` without a trailing slash. Active delivery
runbooks MUST use the same path for MCP client setup and troubleshooting.

#### Scenario: Printed MCP URL is routable
- **WHEN** bootstrap prints the MCP server URL for port `8000`
- **THEN** the URL is `http://127.0.0.1:8000/mcp`
- **AND** the printed guidance does not instruct the operator to keep a
  trailing `/mcp/`

#### Scenario: Runbooks match bootstrap
- **WHEN** an operator follows active delivery runbook MCP setup examples
- **THEN** the configured URL uses `/mcp`
- **AND** troubleshooting for `not_found` points at removing a trailing slash

### Requirement: Bootstrap guidance handles Windows setup edge cases

Active qa-mcp delivery runbooks SHALL explicitly cover Docker Desktop readiness,
empty 1C password invocation, manual PowerShell UTF-8 request bytes, and
explicit `-WindowTitle` selection for ambiguous 1C windows.

#### Scenario: Empty password is omitted
- **WHEN** an infobase user has a blank password
- **THEN** the runbook instructs the operator to omit `-Password`
- **AND** it does not instruct the operator to pass `-Password ""`

#### Scenario: Docker readiness is checked before install
- **WHEN** an operator starts a Windows model-B install
- **THEN** the runbook requires `docker info` or equivalent Docker Desktop
  readiness before continuing

#### Scenario: Manual Cyrillic request uses UTF-8 bytes
- **WHEN** the runbook shows a manual PowerShell HTTP request that can contain
  Cyrillic payload text
- **THEN** the example builds the request body with
  `[System.Text.Encoding]::UTF8.GetBytes(...)`

#### Scenario: Ambiguous window title has an explicit override
- **WHEN** automatic window matching is missing or generic
- **THEN** the runbook instructs the operator to rerun bootstrap with
  `-WindowTitle` set to a stable title fragment

### Requirement: Bootstrap does not persist plaintext TestClient credentials
The qa-mcp Windows bootstrap SHALL NOT leave a plaintext TestClient launch
script containing an infobase password after the TestClient launch attempt
completes. Any temporary launch helper that can contain `/P<password>` SHALL be
restricted to the current user while it exists and SHALL be removed after
success or failure cleanup.

#### Scenario: Password launch helper is removed after success
- **WHEN** bootstrap launches TestClient with a non-empty `-Password`
- **AND** the TestClient starts listening on the requested `ClientPort`
- **THEN** `%LOCALAPPDATA%\qa-mcp-setup\launch-testclient.ps1` does not remain
  on disk with the plaintext password

#### Scenario: Password launch helper is cleaned after launch failure
- **WHEN** bootstrap creates a temporary TestClient launch helper
- **AND** the TestClient fails to start listening on the requested `ClientPort`
- **THEN** cleanup removes the temporary helper or leaves only an ACL-protected,
  non-plaintext diagnostic artifact

### Requirement: Bootstrap reruns cannot silently reuse stale TestClient state
The qa-mcp Windows bootstrap SHALL detect an existing listener or scheduled task
on the requested TestClient port before launching a new TestClient. When it
cannot prove that the existing listener belongs to the same intended bootstrap
run, it SHALL stop with an explicit stale-client diagnostic or replace the owned
previous TestClient before continuing.

#### Scenario: Existing listener blocks ambiguous rerun
- **WHEN** `ClientPort` already accepts TCP connections before bootstrap starts
  the new TestClient
- **AND** bootstrap cannot prove that listener is the intended client for the
  requested `Infobase`
- **THEN** bootstrap exits with a clear stale-client diagnostic
- **AND** it does not report success against the stale listener

#### Scenario: Rerun does not keep stale scheduled task state
- **WHEN** a previous `qa-mcp-testclient` scheduled task exists
- **THEN** bootstrap deletes or replaces that task before the new launch attempt
- **AND** the task action does not preserve a stale password-bearing launch file

#### Scenario: Window title is tied to the launched client when available
- **WHEN** bootstrap derives a `WindowTitle` automatically
- **THEN** it prefers the process launched for this bootstrap run over the first
  arbitrary `1cv8` process
- **AND** it warns or fails loudly when it cannot disambiguate the active
  TestClient window

### Requirement: Bootstrap selects only capture-covered platform families by default

The qa-mcp Windows bootstrap SHALL choose a 1C platform executable using parsed
semantic platform versions, not lexicographic path order. When `-PlatformExe` is
omitted and multiple installed platform families are present, bootstrap MUST
prefer the newest candidate whose family has direct bundled capture coverage.

#### Scenario: Mixed 8.3 and 8.5 host defaults to direct coverage

- **WHEN** bootstrap auto-discovers installed `1cv8.exe` candidates for
  `8.3.27.2130` and `8.5.1.1343`
- **THEN** it selects the `8.3.27.2130` executable because the `8.3` family has
  a populated bundled capture set
- **AND** the selection does not depend on lexicographic sorting of the full
  executable path

### Requirement: Bootstrap diagnoses explicit platform families without direct captures

The qa-mcp Windows bootstrap SHALL warn loudly when the selected platform family
has no direct bundled capture set. The warning MUST name the selected platform
version, explain whether a validated fallback is used, and tell the operator to
use `-PlatformExe` when they need a direct-covered platform.

#### Scenario: Explicit 8.5 selection uses documented fallback warning

- **WHEN** an operator supplies `-PlatformExe` for `8.5.1.1343`
- **THEN** bootstrap keeps that platform selection and passes
  `QA_MCP_PLATFORM_VERSION=8.5.1.1343` into the container
- **AND** it prints a warning that 8.5 has no direct bundled capture set and
  uses the validated 8.3 protocol-data fallback

#### Scenario: Unsupported family does not report a green deployment

- **WHEN** the selected platform family has neither direct capture coverage nor
  a declared fallback
- **THEN** bootstrap stops before reporting success
- **AND** the diagnostic names `-PlatformExe` as the way to choose a supported
  executable

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

### Requirement: Windows JSON-RPC examples send UTF-8 request bodies
Active qa-mcp delivery and troubleshooting runbooks SHALL send manual
PowerShell JSON-RPC examples as UTF-8 bytes and SHALL declare
`Content-Type: application/json; charset=utf-8` whenever the request body can
contain Cyrillic text such as a 1C navigation link.

#### Scenario: Manual Cyrillic request declares UTF-8
- **WHEN** a runbook shows a manual PowerShell JSON-RPC request with
  `open_link="e1cib/list/Справочник.Валюты"` or another Cyrillic argument
- **THEN** the example builds the request body with
  `[System.Text.Encoding]::UTF8.GetBytes(...)`
- **AND** the request declares
  `Content-Type: application/json; charset=utf-8`

#### Scenario: Non-UTF-8 PowerShell body is documented as a failure mode
- **WHEN** troubleshooting describes a Cyrillic navigation link failure
- **THEN** it explains that sending the JSON body as a PowerShell string or as
  a non-UTF-8 charset can corrupt the link before qa-mcp receives it
- **AND** it points operators to the echo diagnostic before treating the link as
  invalid in 1C

### Requirement: Bootstrap launches the TestClient with 1C-correct argument quoting

The bootstrap-generated TestClient launcher SHALL pass the 1C client arguments so that a
user name, password, or infobase path containing spaces is delivered to `1cv8` as 1C
expects — the value quoted immediately after its flag (`/N"<name>"`, `/P"<password>"`,
`/IBConnectionString "<connection>"`), with internal double-quotes doubled. The launcher
SHALL NOT rely on PowerShell array-form `Start-Process -ArgumentList @(…)` for these
arguments, because that wraps a spaced `/N<name>` element as `"/N<name>"` (quote before
the flag), which 1C rejects.

#### Scenario: A 1C user name containing spaces launches successfully

- **WHEN** bootstrap is run for a base whose 1C user name contains spaces (for example the
  [redacted third-party configuration] demo user `Тестовый Пользователь (Демо)`)
- **THEN** the generated launcher issues `/N"<name>"` (quote after the flag) as a single
  command-line token, the TestClient logs in and binds its TPort, and bootstrap does not
  abort with a login failure

#### Scenario: The launcher passes one verbatim command-line string, not an array

- **WHEN** the generated `launch-testclient.ps1` is inspected
- **THEN** it invokes `Start-Process … -ArgumentList '<one command-line string>'` with the
  1C-correct token quoting, and does not use the array form `-ArgumentList @(…)`

### Requirement: Windows installer renders durable workstation BSL supervision
The delivered Windows host-agent installer SHALL accept the BSL helper and
workspace inputs, SHALL render configuration path, syntax-helper directory,
platform version, writable cache, child log and startup timeout into the fixed
scheduled-task command, and SHALL configure Task Scheduler to restart the
host-agent after failure.

#### Scenario: Complete thin-workstation BSL inputs are supplied
- **WHEN** the operator installs host-agent with the BSL helper, workspace,
  configuration, syntax-helper and platform-version inputs
- **THEN** the scheduled-task action contains the corresponding fixed `-bsl-*` flags
- **AND** cache and child-log paths resolve below writable local state
- **AND** the startup timeout is at least 480 seconds.

#### Scenario: Host-agent task exits unexpectedly
- **WHEN** the registered scheduled task exits with a failure status
- **THEN** Task Scheduler applies a bounded restart interval and count
- **AND** logon-trigger and unlimited execution-time behavior remain intact.

### Requirement: Windows host-agent artifacts are reproducible and source-bound

The qa-mcp release tooling SHALL provide one non-interactive Linux command that
builds and verifies the current Windows amd64 GUI host-agent from a clean
checkout, emits a sha256 sidecar and machine-readable provenance, and SHALL make
the signed self-hosted publisher consume that same verified artifact contract
for both built and explicitly supplied assets.

#### Scenario: Clean checkout builds the current artifact

- **WHEN** the host-agent artifact command runs from a clean checkout with Go
  available
- **THEN** it emits `qa-mcp-host-agent.exe`, its sha256 and a provenance
  manifest without requiring an operator-authored cross-build command
- **AND** the manifest identifies source revision/fingerprint, agent version,
  toolchain, target architecture and Windows GUI subsystem.

#### Scenario: Identical inputs build reproducibly

- **WHEN** the artifact is built twice from identical source and Go toolchain
- **THEN** both executable sha256 values are equal
- **AND** both bundles pass the same verifier.

#### Scenario: Stale or incomplete executable is refused

- **WHEN** an executable has the wrong PE architecture/subsystem, missing or
  mismatched VCS/source metadata, or lacks a required bridge-registration,
  BSL-supervision or TestClient marker
- **THEN** verification exits non-zero before release staging or installation
- **AND** the diagnostic names the missing or mismatched bounded contract fact.

#### Scenario: Public release stages a built verified artifact

- **WHEN** `publish_self_hosted.sh` builds a release rather than receiving an
  explicit existing executable
- **THEN** it obtains the executable through the shared artifact builder
- **AND** the existing detached signed component manifest remains the download
  trust anchor for bootstrap installation.

#### Scenario: Public release stages a supplied verified bundle

- **WHEN** `publish_self_hosted.sh` receives an explicit existing executable,
  including when regression gates are skipped
- **THEN** it requires and verifies the adjacent source-bound bundle manifest
  and sha sidecar before copying any asset into the version staging directory
- **AND** a bare, stale or source-mismatched executable fails before staging.

#### Scenario: Dirty source is explicit

- **WHEN** a release build has tracked host-agent inputs that differ from HEAD
- **THEN** the builder fails closed by default
- **AND** a local test-only override records dirty state and the actual source
  fingerprint rather than claiming clean-HEAD provenance.

### Requirement: Windows host-agent reinstall reconciles only its staged BSL helper

Before replacing the staged BSL artifact, the Windows host-agent installer SHALL
stop a stale helper only when its executable path exactly equals the
installer-owned target path. It SHALL NOT terminate every process with the
`bsl-agent.exe` image name.

#### Scenario: Previous owned helper survived supervisor termination

- **WHEN** reinstall finds a running `bsl-agent.exe` at the staged target path
- **THEN** it stops that process before copying the replacement and starting the
  scheduled task
- **AND** the new supervisor does not enter a bind-conflict restart loop.

#### Scenario: Unrelated helper has the same image name

- **WHEN** another `bsl-agent.exe` runs from a different path
- **THEN** installer cleanup leaves it unchanged.

### Requirement: Windows installer renders durable bridge registration

The delivered Windows host-agent installer SHALL accept the complete bridge
registry identity, credential-file, advertised-endpoint, heartbeat and TTL
inputs as one all-or-nothing set, SHALL render them into the fixed scheduled
task for a verified executable, and SHALL preserve solo mode when the complete
set is absent.

#### Scenario: Complete bridge registration inputs are supplied

- **WHEN** the operator installs a verified artifact with registry URL, user,
  registry token file, bridge token file, advertised endpoint, heartbeat and
  TTL
- **THEN** the scheduled-task action contains the corresponding fixed
  `registry-*` flags
- **AND** the host-agent reports registered state through its authenticated
  health contract.

#### Scenario: Partial bridge registration inputs are rejected

- **WHEN** any registry input is supplied without the complete required set
- **THEN** the installer fails before copying the executable or replacing the
  scheduled task
- **AND** no credential value is printed.

#### Scenario: Registry inputs are absent

- **WHEN** the installer receives no registry inputs
- **THEN** it omits every `registry-*` task flag
- **AND** the installed host-agent retains its existing solo-mode behavior.

### Requirement: Multi-version release evidence preserves live platform identity

A qa-mcp release that declares both supported platform baselines SHALL retain a
release-equivalent Agent/MCP HTTP attach/read result for `8.3.27.2130` and
`8.5.1.1343`. Each result MUST identify its delivery model, canonical `/mcp`
endpoint, full live platform version, attach outcome, read outcome, and cleanup
or retained-runtime disposition. An 8.5 result MAY use the validated 8.3
protocol-data set, but it MUST continue to declare the live 8.5 full version.

#### Scenario: Both supported baselines have release-equivalent proof

- **WHEN** a release is reviewed as supporting 1C `8.3.27.2130` and
  `8.5.1.1343`
- **THEN** retained evidence contains one Agent/MCP HTTP attach/read result for
  each full platform build
- **AND** each result names Windows model-B or Linux host-platform model-A and
  uses the canonical `/mcp` endpoint

#### Scenario: 8.5 validates with 8.3 protocol data

- **WHEN** the 8.5 release smoke resolves capture-backed operations through the
  validated `_bundled/8.3` protocol-data set
- **THEN** synthesized and replayed session frames continue to declare the live
  full version `8.5.1.1343`
- **AND** the delivery does not require `_bundled/8.5` to be populated while the
  validate-first smoke remains green

#### Scenario: Validate-first smoke exposes protocol drift

- **WHEN** the 8.5 release smoke fails because a protocol capability is red
- **THEN** the release evidence records the failed capability and sanitized
  outcome
- **AND** support work is routed to a separate protocol/capture change before
  any 8.5-specific corpus is bundled

### Requirement: Active delivery guidance distinguishes platform and protocol-data versions

Active qa-mcp delivery guidance SHALL document `8.3.27.2130` and
`8.5.1.1343` as supported baseline builds, SHALL state that same-family builds
require validate-first evidence, and SHALL distinguish the full live platform
version passed through `QA_MCP_PLATFORM_VERSION` / `PLATFORM_ROOT` from the
protocol-data family selected at runtime.

#### Scenario: Operator selects a supported full platform build

- **WHEN** an operator follows active delivery guidance for 8.3 or 8.5
- **THEN** the guidance passes the selected full `x.y.z.w` build into the
  shipped runtime
- **AND** it explains that another build in the same family may work only after
  validate-first verification

#### Scenario: Operator follows the 8.5 fallback policy

- **WHEN** an operator deploys against `8.5.1.1343`
- **THEN** active guidance states that the validated 8.3 protocol-data set is
  reused while the live platform identity remains 8.5
- **AND** it instructs recapture or `_bundled/8.5` population only after a red
  capability is identified

### Requirement: Same-family compatible builds retain validate-first evidence

The qa-mcp supported-build manifest SHALL admit a new full build from an
already-supported platform family only after live protocol evidence shows that
the existing bundled corpus works with the live build identity. A green
compatibility result SHALL NOT replace committed capture templates.

#### Scenario: 8.3.27.2214 reuses the existing 8.3 corpus

- **WHEN** a TestClient on `8.3.27.2214` accepts the genuine TestManager
  handshake and the existing bundled 8.3 corpus passes the required read-only
  UI checks
- **THEN** `8.3.27.2214` is recorded in
  `compatible_platform_versions` for the 8.3 manifest
- **AND** the committed 8.3 template hash remains unchanged
- **AND** raw capture payloads remain outside Git.

### Requirement: Streamable HTTP request validation preserves the ASGI receive lifecycle

The self-hosted HTTP runtime SHALL validate and replay a JSON-RPC request body
once, and SHALL forward subsequent receive events from the original ASGI
channel so the Streamable HTTP transport can deliver its response and observe
client disconnects.

#### Scenario: Downstream receives the validated body and real disconnect

- **WHEN** a valid UTF-8 JSON-RPC body passes through the request gate
- **THEN** the first downstream receive returns that validated body exactly once
- **AND** a later downstream receive obtains the real `http.disconnect` event
  instead of an unbounded sequence of synthetic empty request bodies

### Requirement: Container cleanup discovers ownership markers under runtime home

Stateless TestClient cleanup in an installed or container runtime SHALL resolve
its ownership-marker root from the explicit
`QA_MCP_TESTCLIENT_OWNERSHIP_ROOT` override when present, otherwise from the
writable `QA_MCP_HOME`, before falling back to the source-checkout default.

#### Scenario: Container launch and cleanup share the same ownership root

- **WHEN** a container sets `QA_MCP_HOME=/work`, launches an owned TestClient,
  and does not set an explicit ownership-root override
- **THEN** launch writes and cleanup discovers the ownership marker below
  `/work/runtime/protocol-research/testclient-lifecycle`
- **AND** cleanup still validates the recorded PID identity before stopping the
  owned TestClient and Xvfb

#### Scenario: Explicit ownership root wins

- **WHEN** both `QA_MCP_HOME` and `QA_MCP_TESTCLIENT_OWNERSHIP_ROOT` are set
- **THEN** stateless cleanup searches the explicit ownership root

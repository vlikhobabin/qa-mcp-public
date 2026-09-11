# Package the current Windows host-agent binary

## Status

4.done

## Owner

unassigned

## OpenSpec Stage

archived

## Source

- Final root T4 two-workstation gate, 2026-07-13.
- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260713T162024Z-final-gate/stand-provision/stations-bootstrap.json`

## Summary

The source tree and published QA image contained the current G12/G14 host-agent
code, but the checked-in/delivered Windows executable was stale and lacked the
required bridge-registration and BSL-supervision flags. The final T4 gate had
to cross-compile the exact published HEAD before two symmetric stations could
be bootstrapped.

## Scope

- Define one reproducible release artifact for the Windows GUI host-agent.
- Tie its version/digest to the source revision and installer contract.
- Fail packaging tests when required command-line flags or discovery fields are
  absent from the shipped executable.

## Evidence

- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260713T162024Z-final-gate/stand-provision/stations-bootstrap.json`
- Built gate digest: `b3d440a72ed3429396fd7841e15909a29338399e728fd70871b5db5e09bc86d2`.
- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260714T114204Z-source-bound-release-ready-rerun/stand-provision/stations-bootstrap.json`
- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260714T114204Z-source-bound-release-ready-rerun/matrix/M09/solo-regression.json`
- Final installed artifact digest:
  `55e57bd2bc4c35f026b4c600ed327b2f5e6c9fed24146966d3d39e37814e304d`.
- Retained source fingerprint:
  `622c96dcfae7500a09ee5ac96b2e46af1c4e38200ef1ad11b4f37ff661bdbe92`.
- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260714T114204Z-source-bound-release-ready-rerun/evidence-index.json`
- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260714T114204Z-source-bound-release-ready-rerun/verdict.json`
- Current rescue artifact SHA:
  `9c5e61eaaa44250640ebd2bbe3962e6b1f4d44d8e89364e41b90dfa5b6864792`.
- Current Go source fingerprint:
  `63e8d4072e7bc3d48c09c71c7f2d24872d8c6ef0992e0afb115b67ae9e03e220`.
- `../.artifacts/openspec/windows-testclient-task-cleanup-runtime-proof/20260714T160743Z-current-source-bound-runtime-proof/runtime-proof-summary.json`
- Current production installer SHA:
  `a309acf5b3e97a051c14c74dc464a33cf0e1191375239ebba7de3e8067edf1a5`.
- `../.artifacts/openspec/windows-host-agent-current-bundle-two-station-installer-proof/20260714T170159Z-initial/runtime-proof-summary.json`
- `../.artifacts/openspec/windows-host-agent-current-bundle-two-station-installer-proof/20260714T170159Z-initial/windows-runtime/two-station-installer-proof.json`
- `../.artifacts/openspec/windows-host-agent-current-bundle-two-station-installer-proof/20260714T170159Z-initial/matrix/M10/cleanup-audit.json`
- `../.artifacts/openspec/windows-host-agent-current-bundle-two-station-installer-proof/20260714T170159Z-initial/evidence-index.json`

## Acceptance

- A clean checkout produces or downloads the current signed/versioned Windows
  executable without an operator cross-build.
- The thin-workstation installer provisions G12 registration and G14 BSL
  supervision from that artifact on both supported Windows versions.

## Affected Repositories

- `/opt/ai-dev-suite-for-1c/qa-mcp` for host-agent artifact build/verification,
  installer guidance, tests and release integration.
- Root T4 runbook consumes the generated artifact path in its own repository
  delivery diff.

## Change Set

1. `windows-host-agent-release-artifact`
2. `windows-host-agent-supplied-artifact-verification`
3. `windows-testclient-task-cleanup-runtime-proof`
4. `windows-host-agent-current-bundle-two-station-installer-proof`

## Verify

- `uv run pytest -q tests/test_windows_host_agent_artifact.py tests/test_host_agent_installer_contract.py tests/test_self_hosted_release_scripts.py`
- `go test ./...` in `host-agent/windows-display-agent`
- build twice and compare manifest/digest
- `bin/openspec validate --all --strict`
- `git diff --check`

## Archive

- `openspec/changes/archive/2026-07-13-windows-host-agent-release-artifact/`
- `openspec/changes/archive/2026-07-14-windows-host-agent-supplied-artifact-verification/`
- `openspec/changes/archive/2026-07-14-windows-testclient-task-cleanup-runtime-proof/`
- `openspec/changes/archive/2026-07-14-windows-host-agent-current-bundle-two-station-installer-proof/`

## Related

- `openspec/changes/archive/2026-07-13-windows-host-agent-release-artifact/`
- `openspec/specs/qa-mcp-self-hosted-release/spec.md`
- `tools/release/publish_self_hosted.sh`
- `host-agent/install-windows-host-agent.ps1`

## Result

Implemented. A single Linux-native builder now emits and verifies a
source-bound Windows amd64 GUI bundle, the self-hosted publisher reuses it,
and the installer refuses an implicit ignored checkout-adjacent executable.
The root T4 bootstrap independently verifies and retains the bundle provenance
before station staging. The final source-bound artifact was installed on both
stations and completed the real M9 launch/read/stability contract; the final
T4 reducer reports `release_ready` with M1-M10 all `pass`. The card remains in
`3.inprogress` until an independent ChangeRail review.

The next independent review found that `--skip-gates` bypassed verification of
a supplied executable and that bare build metadata did not require exact VCS
fields. Change 2 makes supplied-artifact verification unconditional, requires
the adjacent source-bound manifest and sha sidecar, and requires exact
`vcs.revision` plus `vcs.modified` agreement. The focused artifact/release
suite has 18 passing tests, including deterministic double-build verification.

Review cycle 3 then found that the final retained T4 binary was source-bound to
the pre-cleanup Go tree. Change 3 rebuilt from the current tree, retained the
manifest and source fingerprint, verified the staged/running SHA on Windows,
and completed both native cleanup scenarios plus a 62-second normal launch.

Review cycle 4 accepted the current artifact and cleanup proof but found that
the explicit two-Windows-version G12/G14 acceptance remained bound to the older
artifact. Change 4 first added the missing all-or-nothing G12 registry inputs
to the production installer, then ran that exact installer on Windows builds
`10.0.22631` and `10.0.26200`. Both stations reported the same installer SHA,
artifact SHA in manifest/sidecar/stage/install/running process, registered
30/90-second G12 state, ready/windowless G14 state and complete 15-flag task
contract. Exact cleanup returned mismatch count zero.

Published reviewed payload as `e53053b48a0f2d977f49d7193aa9bcaaaa0e1446`; push status `pending` on `main`/`origin`.

## Next

- done

## Change 1: `windows-host-agent-release-artifact`

### Why

The full self-hosted publisher can build the executable, but no standalone
clean-checkout contract produces and verifies the exact Windows GUI artifact.
The ignored default binary can therefore drift silently from current source.

### Goal

Provide one non-interactive host-agent-only build command that emits the
Windows GUI executable, sha256 and machine-readable source/toolchain manifest;
verify the current registration/BSL/TestClient surface before any installer or
release pipeline consumes it.

### Scope

- Add a Linux-native builder with deterministic GOOS/GOARCH/CGO/trimpath and
  windowsgui settings.
- Record source revision, dirty state, source fingerprint, Go version, build
  settings, agent version, digest, size and required capability markers.
- Add an offline verifier for PE architecture/subsystem, Go build metadata and
  required registration/BSL/TestClient CLI/contract strings.
- Make the full self-hosted publisher call the same builder instead of its own
  ad hoc `go build` line.
- Update installer/default guidance so ignored binaries are not represented as
  shipped current assets.

### Acceptance

- One command from a clean checkout emits a verified artifact bundle without
  requiring the operator to construct a cross-build command.
- Two builds from identical source/toolchain have the same executable digest.
- Missing GUI subsystem, wrong architecture, source fingerprint or any required
  G12/G14/TestClient marker fails before release staging.
- Manifest and sha sidecar contain no secrets and tie the binary to source.
- Existing signed self-hosted manifest remains the download/install trust path.

### Depends On

- existing `qa-mcp-self-hosted-release` signed manifest channel.

### Related

- `openspec/changes/archive/2026-07-13-windows-host-agent-release-artifact/`

## Change 2: `windows-host-agent-supplied-artifact-verification`

### Goal

Ensure no publisher option can stage an unverified standalone executable and
bind every supplied artifact to the current source through its complete
verified bundle.

### Related

- `openspec/changes/archive/2026-07-14-windows-host-agent-supplied-artifact-verification/`
- `openspec/board/3.inprogress/windows-host-agent-atomic-release-delivery.md`

## Change 3: `windows-testclient-task-cleanup-runtime-proof`

### Goal

Retain Windows-native proof from the exact source fingerprint and artifact SHA
that the combined QA payload will publish.

### Related

- `openspec/changes/archive/2026-07-14-windows-testclient-task-cleanup-runtime-proof/`
- `openspec/board/3.inprogress/windows-host-agent-atomic-release-delivery.md`

## Change 4: `windows-host-agent-current-bundle-two-station-installer-proof`

### Goal

Prove the exact current artifact through the supported installer on both
Windows builds with real G12 registration, G14 BSL supervision and exact
immutable cleanup.

### Related

- `openspec/changes/archive/2026-07-14-windows-host-agent-current-bundle-two-station-installer-proof/`
- `openspec/board/3.inprogress/windows-host-agent-atomic-release-delivery.md`

## Log

- 2026-07-13T22:00:00Z accepted from final T4 ad hoc cross-build evidence and
  decomposed into one qa-mcp apply-sized change.
- 2026-07-13 delivered `windows-host-agent-release-artifact`: RED 4 failures;
  GREEN 816 offline Python tests, Go tests, focused Ruff, deterministic double
  build and source-bound bundle verification. Awaiting independent review.
- 2026-07-14 independent review returned no-go on the supplied-executable
  bypass, incomplete VCS validation and split publication scope; Change 2
  passed RED/GREEN and all release, full offline, Go, cross-build and OpenSpec
  gates. Atomic publication is delegated to the combined QA delivery card.
- 2026-07-14 review cycle 3 required a current source-bound Windows proof;
  Change 3 produced it with exact artifact/test hashes and zero cleanup residue.
- 2026-07-14 review cycle 4 required current-artifact G12/G14 proof on both
  supported Windows builds. Change 4 used the supported installer on both,
  retained source/artifact/installer binding and restored the immutable
  baseline exactly.
- 2026-07-14T19:09:40Z publish finalized card into `4.done` with commit `e53053b48a0f2d977f49d7193aa9bcaaaa0e1446` and push status `pending`.

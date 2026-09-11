## 1. Regression first

- [x] 1.1 Add offline tests for absent standalone builder, stale/malformed PE,
      missing required marker, dirty-source refusal and deterministic double
      build; record RED.

## 2. Artifact and release integration

- [x] 2.1 Implement build/verify commands with fixed cross-target settings,
      source fingerprint, PE/build-info checks, manifest and sha sidecar.
- [x] 2.2 Make `publish_self_hosted.sh` use the shared builder and verify an
      explicitly supplied host-agent executable before staging.
- [x] 2.3 Update installer/host-agent/release docs to point to the builder or
      signed bootstrap and stop presenting an ignored adjacent exe as current.

## 3. Verification and handoff

- [x] 3.1 Run focused Python tests, Go tests, double-build digest comparison,
      shell syntax, strict OpenSpec validation, secret scan and diff check.
- [x] 3.2 Record RED/GREEN and root T4 artifact handoff before spec sync/archive.

## Verification Evidence

- RED: `uv run pytest -q tests/test_windows_host_agent_artifact.py` observed
  four failures because the standalone tool and launcher did not exist.
- GREEN: the same focused artifact suite passed `4 passed`; the combined
  artifact/installer/publisher suite passed `18 passed`.
- `uv run pytest -q -ra -m "not live"` passed `816` tests.
- `(cd host-agent/windows-display-agent && go test ./...)` passed.
- Two builder invocations from the same source/toolchain produced identical
  executable bytes and sha256; persistent handoff verification produced
  `419661e0851bb7f9f62c893d362857dade581ed1d20036aace1e80039c54d786`.
- `file` classified the handoff as `PE32+ ... (GUI), x86-64`; the product
  verifier also passed source fingerprint, Go/VCS settings and all required
  bridge/BSL/TestClient markers.
- Focused Ruff for every changed Python file passed. Repository-wide Ruff has
  186 pre-existing findings outside this change and is not claimed green.
- `sh -n tools/release/publish_self_hosted.sh`, strict change validation and
  `git diff --check` passed.
- Root T4 now consumes the bundle through `bootstrap-stations`, re-verifies it
  before any station copy and retains manifest plus sha evidence.

## 1. Release Staging

- [x] 1.1 Add `--com-worker-exe <path>` to
  `tools/release/publish_self_hosted.sh` usage and argument parsing.
- [x] 1.2 Validate the supplied worker path, copy it to the staged version
  directory as `ai-com-worker.exe`, and include it in sha256 sidecar generation.
- [x] 1.3 Pass `ai-com-worker.exe=<staged-path>` to
  `tools/release/component_manifest.py` only when the optional worker is
  supplied.
- [x] 1.4 Emit an operator-visible warning when `--com-worker-exe` is omitted,
  while preserving the existing non-COM release path.

## 2. Bootstrap Installation

- [x] 2.1 Add a non-fatal manifest asset presence check to
  `delivery/bootstrap.ps1`.
- [x] 2.2 When `ai-com-worker.exe` is declared in the manifest, download it with
  `Download-ReleaseAsset`, verify its sha256 through `Assert-AssetSha256`, and
  store it under the setup directory.
- [x] 2.3 Pass `-ComWorkerExe <verified-worker-path>` to
  `install-windows-host-agent.ps1` only after the worker asset has been
  downloaded and verified.
- [x] 2.4 Preserve existing bootstrap behavior when the manifest has no worker
  asset.

## 3. Tests And Verification

- [x] 3.1 Extend release script tests to assert the new flag, shell syntax, and
  optional-worker warning contract.
- [x] 3.2 Extend manifest tests to prove `ai-com-worker.exe` appears in assets
  with sha256 metadata when supplied.
- [x] 3.3 Add or extend bootstrap contract tests to prove the worker asset is
  downloaded, verified and passed with `-ComWorkerExe`, while the absent-worker
  path remains non-fatal.
- [x] 3.4 Run focused Linux offline checks:
  `pytest tests/test_self_hosted_release_scripts.py tests/test_component_manifest.py`.
- [x] 3.5 Record Windows-native verification as deferred unless a Windows host
  with a live-mcp-built `ai-com-worker.exe` is available: bootstrap from a
  manifest containing the worker, confirm host-agent install, and retain
  `/com/execute` `/health` evidence showing `available:true`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | qa-mcp self-hosted release staging and Windows bootstrap worker handoff | Linux offline release staging/manifest/bootstrap contract tests | `source_preflight`, `scenario_log` from focused pytest output | `.artifacts/openspec/stage-and-fetch-com-worker/20260705T200134Z/linux-release-tests.log` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Linux checks prove script contracts, not Windows COM runtime health |
| Delivery or runtime apply | Windows host-agent install with live-mcp `ai-com-worker.exe` | Windows bootstrap run from a release manifest that declares `ai-com-worker.exe`, followed by host-agent `/com/execute` `/health` | `scenario_file`, `scenario_log`, `data_assertion` showing `available:true` | `.artifacts/openspec/stage-and-fetch-com-worker/20260705T200134Z/windows-com-worker-health.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Windows host and live-mcp-built `ai-com-worker.exe` are unavailable in this Linux workspace |
| BSL-only module edit | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | No BSL modules are changed | No residual risk; surface is unaffected |
| Managed form layout | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No 1C managed forms are changed | No residual risk; surface is unaffected |
| Role rights | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/meta-mcp` | No 1C roles or rights are changed | No residual risk; surface is unaffected |

## Provider Gap Records

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround |
| --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | Windows host-agent install with live-mcp `ai-com-worker.exe` | `scenario_log`, `data_assertion` | Blocks retained Windows `/com/execute` `/health` proof in this Linux delivery run; Linux tests still prove release and bootstrap contracts | Run bootstrap on a Windows host with a live-mcp-built `ai-com-worker.exe` and retain `.artifacts/openspec/stage-and-fetch-com-worker/<windows-run-id>/com-worker-health.json` |

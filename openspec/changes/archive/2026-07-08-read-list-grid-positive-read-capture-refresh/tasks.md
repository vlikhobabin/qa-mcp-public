## 1. Capture Metadata And Selection

- [x] 1.1 Add failing offline pytest coverage for capture metadata loading,
  platform/config tag normalization, exact match, and fallback diagnostics.
- [x] 1.2 Implement a sanitized capture metadata sidecar model and selector for
  platform/config-matched capture lookup.
- [x] 1.3 Stamp the existing bundled/demo capture metadata as generic
  `demo10413`/8.3.27.2130 evidence without committing raw capture payloads.

## 2. Refresh-Capture Procedure And Tooling

- [x] 2.1 Update `docs/capture-refresh-runbook.md` so config-matched refreshes
  are documented for the [redacted third-party configuration]/Бухгалтерия 3.0 LAN failure mode.
- [x] 2.2 Add a Linux-native command/helper under `tools/protocol-research/` to
  prepare or validate sanitized refresh-capture metadata.
- [x] 2.3 Retain a provider-gap artifact for the unavailable real Windows .205
  [redacted third-party configuration] positive-read proof.

## 3. Manager-Handshake Drift Preflight

- [x] 3.1 Add failing offline pytest coverage for ACK success and missing
  frame-3 ACK/GUID classification as `manager-handshake-moved`.
- [x] 3.2 Implement the bounded manager-handshake preflight in the protocol
  layer.
- [x] 3.3 Propagate the specific drift diagnostic into descriptor/list-read
  setup failures where applicable.

## 4. Verification And Handoff

- [x] 4.1 Run focused pytest for capture metadata and handshake drift behavior.
- [x] 4.2 Run broader affected pytest coverage for protocol/session/list-read
  regressions.
- [x] 4.3 Run `python -m qa_mcp.regression.versioning` or the equivalent offline
  drift check without live [redacted third-party configuration] claims.
- [x] 4.4 Run the 1C verification matrix checker in preflight and archive-gate
  modes, retaining outputs under `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/<run-id>/`.
- [x] 4.5 Run `openspec validate read-list-grid-positive-read-capture-refresh --strict`
  and `git diff --check`.
- [x] 4.6 Sync the `qa-mcp-protocol-lab` delta into the main spec and archive the
  change after tasks, verification notes, and provider-gap evidence are complete.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Real Windows .205 [redacted third-party configuration] `read_list_grid` positive read for `Справочник.Валюты` | Operator-owned run with config-matched capture, visible rows returned, and retained sanitized MCP transcript | `qa_testclient_bundle` or provider-gap report | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/third-party-config-positive-read-provider-gap.md` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real Windows .205 / [redacted third-party configuration] host is unavailable; positive-read proof remains unproven. |
| Native protocol claim | Capture metadata sidecars and config-matched capture selection | Offline unit tests for platform/config tag parsing, exact match, fallback selection, and safe serialization | Focused pytest output and retained summary | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/capture-metadata-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline metadata tests do not prove live replay compatibility. |
| QA/TestClient UI automation | Manager-handshake drift preflight before descriptor/list read | Offline unit tests using fake socket/session responses for ACK success and frame-3 ACK/GUID absence | Focused pytest output and retained summary | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/handshake-drift-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live preflight still requires an available TestClient endpoint. |
| Protocol research tooling | Refresh-capture procedure/tooling | Runbook review plus CLI/help or dry-run output proving metadata path and raw-capture boundary | Documentation/tooling check summary | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/refresh-procedure-check.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | The procedure is not a substitute for the unavailable Windows capture run. |
| Business data mutation | Object writes, posting, delete/fill/import/export | No mutation is part of this protocol-lab change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change is read-only protocol metadata/preflight/tooling. | None beyond unproven live positive-read acceptance. |

## Provider Gap Records

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround | source_card | sanitized_evidence | sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | QA/TestClient UI automation | qa_testclient_bundle | Blocks proof that `read_list_grid` on [redacted third-party configuration] / 8.3.27.2130 / Бухгалтерия 3.0 returns visible `Справочник.Валюты` rows using a config-matched capture. | Operator can run the documented refresh procedure and positive-read smoke later on the real Windows .205 host, then replace this provider-gap artifact with a sanitized proof bundle. | `openspec/board/1.backlog/read-list-grid-positive-read-capture-refresh.md` | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/third-party-config-positive-read-provider-gap.md` | no credentials, screenshots or live data copied |

## Verification Notes

- RED focused pytest: `uv run --with pytest --with pyyaml pytest tests/test_capture_metadata.py tests/test_manager_handshake_drift.py tests/test_mcp_server.py -k 'capture_metadata or manager_handshake or list_table_resolution_reports_manager_handshake_drift'` failed before implementation with `ModuleNotFoundError: No module named 'qa_mcp.protocol.capture_metadata'`; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_6f6ef26140674b3983f0022298a6f61f/`.
- GREEN focused pytest: the same command passed after implementation; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_8542375b68bf44feaa16192b4987fda6/`.
- Refresh metadata helper: `python3 tools/protocol-research/prepare_capture_metadata.py --output .artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/sample-capture-metadata.json --capture-id third-party-config-currencies --platform-build 8.3.27.2130 --configuration-name "Бухгалтерия 3.0" --configuration-vendor "[redacted third-party configuration]" --capture-dir runtime/protocol-research/captures/third-party-config-currencies --manager-templates runtime/protocol-research/templates/third-party-config/manager_frame_templates.json --notes "offline sanitized metadata helper check" --check` passed; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_94ac7ec9aa8c4663937636fd75e68b65/`.
- Broader affected pytest: `uv run --with pytest --with pyyaml pytest tests/test_capture_metadata.py tests/test_manager_handshake_drift.py tests/test_mcp_server.py tests/test_versioning.py tests/test_protocol_session.py tests/test_native_write.py -k 'capture_metadata or manager_handshake or list_table_resolution_reports_manager_handshake_drift or drift or versioning or read_list_grid or bootstrap or session'` passed; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_0f560989ae2d457e8412d713bb3c6c41/`.
- Offline versioning drift check: `uv run python -m qa_mcp.regression.versioning` passed; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_c89195c00be2471d8e407e392a292c7a/`.
- OpenSpec strict validation: `openspec validate read-list-grid-positive-read-capture-refresh --strict` passed; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_fa3ab4a86d434d61a1debff0a6086ded/`.
- Whitespace check: `git diff --check` passed; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_22b1b63036724b61a64db94587887169/`.
- Matrix preflight passed with one provider gap; retained at `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/matrix-preflight.json`.
- Matrix archive gate initially flagged missing retained summary files; after adding `capture-metadata-tests.md`, `handshake-drift-tests.md`, and `refresh-procedure-check.md`, archive mode passed with one provider gap; retained at `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/matrix-archive-gate.json`.
- Synced main spec validation: `openspec validate qa-mcp-protocol-lab --strict` passed; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_b539c55db13447f1a47a3ade8929df73/`.
- Workspace OpenSpec validation after sync: `openspec validate --all` passed; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_0885a9d16a444b11890fcbec126bad19/`.
- Suite regression full pytest: `uv run --with pytest --with pyyaml pytest` passed with 787 collected tests; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_f41d6c25eeb54b6fa04a2285a774b25d/`.
- Suite drift gate: component-local `scripts/check_suite_source_of_truth_drift.py` is absent; suite fallback `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` passed with 0 findings; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_833bbeea8fb1439397c931084604b3c8/`. The missing local-script attempt is retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_8202c804c445432d88d9d57ed0b5cbdd/`.
- Suite smoke pytest: `uv run --with pytest --with pyyaml pytest -m smoke` passed with 3 selected tests; retained at `.artifacts/ai-run/trc_44400a7839ba4212bf79e2ade64a92f4/run_74544b3617334f4ebe62ebad53638b81/`.

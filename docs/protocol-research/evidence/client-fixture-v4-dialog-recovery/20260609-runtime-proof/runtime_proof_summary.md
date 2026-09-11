# Client Fixture V4 Runtime Proof

Run id: `20260609-v4-designer-apply`

## Scope

This proof covers the client fixture V4 marker surface for warning, question,
fixture-local modal lifecycle, expected-error and bounded-wait cases. It does
not promote any V4 protocol mapping to accepted status.

## Runtime Route

- Manager/TestClient route: Vanessa MCP against profile
  `qa-mcp-vanessa-client`.
- Target form: `QA MCP Protocol Fixture V1`.
- Test client infobase: `C:\1C_BASES\vanessa_client`.
- Source updated before deploy:
  `C:\1C_BASES\EDT\vanessa_qa\vanessa_client\src\DataProcessors\ФикстураПротоколаTestClient\Forms\Форма\`.
- Live deploy evidence:
  `.artifacts/openspec/v4-dialog-recovery-verification/20260609-v4-designer-apply/runtime-apply/`.

Screenshot bootstrap was disabled for the lazy Vanessa manager session, so the
retained UI proof uses accepted Vanessa fallback bundles containing
`active-window.json`, `active-form.json`, `form-analysis.txt`,
`provider-gap.json` and `summary.json`.

## Marker Proof

The local runtime validator checked 16 retained fallback bundles and found all
expected V4 marker tokens:

- Baseline/reset:
  `PF_V4_DIALOG_NONE`, `PF_V4_DIALOG_BASELINE`, `PF_V4_TEXT_NONE`,
  `PF_V4_RESULT_NONE`, `PF_V4_RECOVERY_BASELINE_READY`,
  `PF_V4_DIAGNOSTIC_NONE`, `PF_V4_WAIT_IDLE`,
  `PF_V4_WAIT_PROGRESS_0`, `PF_V4_STATUS_BASELINE`.
- Warning action/reset:
  `PF_V4_WARNING_CLOSED`, `PF_V4_WARNING_ACK`,
  `PF_V4_WARNING_RECOVERY_PENDING`,
  `PF_V4_WARNING_RECOVERY_TO_BASELINE`.
- Question action/reset:
  `PF_V4_QUESTION_ANSWERED`, `PF_V4_QUESTION_YES`,
  `PF_V4_QUESTION_YES_RECOVERY_PENDING`,
  `PF_V4_QUESTION_RECOVERY_TO_BASELINE`.
- Fixture-modal lifecycle action/reset:
  `PF_V4_MODAL_OPEN`, `PF_V4_MODAL_OPENED`,
  `PF_V4_MODAL_CLOSED`, `PF_V4_MODAL_CLOSE_RECOVERY_PENDING`,
  `PF_V4_MODAL_RECOVERY_TO_BASELINE`.
- Expected-error action/reset:
  `PF_V4_EXPECTED_ERROR_MATCHED`,
  `PF_V4_EXPECTED_DIAGNOSTIC_MARKER`,
  `PF_V4_STATUS_EXPECTED_ERROR`,
  `PF_V4_EXPECTED_ERROR_RECOVERY_TO_BASELINE`,
  `PF_V4_DIAGNOSTIC_NONE`.
- Bounded wait action/reset:
  `PF_V4_WAIT_COMPLETED`, `PF_V4_WAIT_PROGRESS_100`,
  `PF_V4_WAIT_CANCELLED`, `PF_V4_WAIT_PROGRESS_40`,
  `PF_V4_WAIT_RETRIED`, `PF_V4_WAIT_PROGRESS_50`,
  `PF_V4_WAIT_RECOVERY_TO_BASELINE`.

Validation summary:
`.artifacts/openspec/v4-dialog-recovery-verification/20260609-v4-designer-apply/recovery-proof/runtime-proof-validation.json`.

## Decision

- Runtime marker proof status: `passed`.
- Publication status: candidate-only.
- Accepted promotion remains gated by V4-specific replay, direct Python manager
  probe or typed contract proof with phase isolation.

## 1. Matrix And Preflight

- [x] 1.1 Run the matrix checker in preflight mode for `design.md` and retain `.artifacts/openspec/native-write-persistence-cleanup-proof/<run-id>/matrix-preflight.json`.
- [x] 1.2 Record pre-state for the chosen owner, including existing contract count or accepted fixture-state residual risk.
- [x] 1.3 Confirm the reviewed cleanup route before running any live save proof.

## 2. Implementation

- [x] 2.1 Replace the hard-coded persistence provider-gap stub with a verifier that records read-back/list/data assertion evidence.
- [x] 2.2 Add cleanup-required gating and unresolved-leftover reporting for live mutation proof.
- [x] 2.3 Return first-contract and second-contract assertion summaries for `Наименование` and `Основной`.

## 3. Verification

- [x] 3.1 Add focused offline tests for persistence summary success, provider-gap failure and cleanup-required failure.
- [x] 3.2 Run focused pytest for the touched scenario/MCP tests and retain output under `.artifacts/openspec/native-write-persistence-cleanup-proof/<run-id>/pytest.log`.
- [x] 3.3 Live-run the demo10413 contract create proof only after preflight and cleanup route confirmation, retaining UI, data assertion and cleanup evidence.
- [x] 3.4 Run the matrix checker in archive mode for `design.md` and retain `.artifacts/openspec/native-write-persistence-cleanup-proof/<run-id>/matrix-archive-gate.json`.

## 4. OpenSpec

- [x] 4.1 Run `openspec validate native-write-persistence-cleanup-proof --strict`.
- [x] 4.2 Run `git diff --check -- openspec/changes/native-write-persistence-cleanup-proof openspec/board src tests`.

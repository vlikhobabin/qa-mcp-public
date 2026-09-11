## 1. Contract Tests

- [x] 1.1 Add focused offline tests for optional `not-required`, required
  `missing`, `current`, `stale` and `unavailable` QA proof receipt states.
- [x] 1.2 Confirm RED evidence before implementation with the focused test file.

## 2. Receipt Implementation

- [x] 2.1 Add a pure-Python qa-mcp workspace proof receipt module with typed
  inputs, bounded diagnostics and source identity comparison.
- [x] 2.2 Reject forbidden mutable source routes and omit raw screenshots,
  protocol logs, source bodies, customer data and infobase dump fields from
  retained receipt output.

## 3. Verification And Handoff

- [x] 3.1 Run focused pytest for the new receipt contract and explain why each
  test would fail if the receipt behavior regressed.
- [x] 3.2 Run `uv run pytest -q tests/test_workspace_proof_receipts.py`.
- [x] 3.3 Run `uv run python -m compileall -q src tests`.
- [x] 3.4 Run `openspec validate qa-server-ssh-workspace-proof-receipts --strict`.
- [x] 3.5 Run `openspec validate --all --strict`.
- [x] 3.6 Run `git diff --check`.
- [x] 3.7 Record that Windows-native/live TestClient verification is not
  applicable because this change does not execute UI, protocol replay, COM,
  infobase access or platform startup.

## Verification Notes

- RED: `uv run pytest -q tests/test_workspace_proof_receipts.py` failed before
  implementation with `ModuleNotFoundError: No module named
  'qa_mcp.workspace_proof_receipts'`.
- PASS: `uv run pytest -q tests/test_workspace_proof_receipts.py` - 5 passed.
  The tests assert exact policy states, source identity freshness comparison,
  forbidden-route rejection and raw proof body omission, so they fail if the
  receipt contract regresses.
- REVIEW RESCUE: independent review cycle 1 found required proof could be
  marked `current` without project/repository identity or `source_scope`.
  Regression coverage now requires `project_id`, `repository_id` and non-empty
  `source_scope`; `uv run pytest -q tests/test_workspace_proof_receipts.py`
  passes with 8 tests.
- REVIEW RESCUE: independent review cycle 2 found URL-like, Windows-drive and
  traversal `source_scope` routes could still be retained while proof reported
  `current`. Regression coverage now rejects `ssh://...`, `C:/...` and
  `..\\...` scope values; `uv run pytest -q tests/test_workspace_proof_receipts.py`
  passes with 11 tests.
- PASS: `uv run pytest -q` - 906 passed after the cycle-2 review rescue.
- PASS: `uv run python -m compileall -q src tests`.
- PASS: `openspec validate qa-server-ssh-workspace-proof-receipts --strict`.
- PASS: `openspec validate --all --strict` - 22 passed, 0 failed.
- PASS: `git diff --check`.
- NOT APPLICABLE: Windows-native/live TestClient verification. This change is a
  pure offline receipt contract and does not execute UI, protocol replay, COM,
  infobase access or platform startup.

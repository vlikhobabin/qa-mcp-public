## 1. Installer Reconciliation Contract

- [x] 1.1 Add focused installer contract tests for secret-safe fingerprinting,
  running-process command-line drift, idempotent no-restart reruns and owned BSL
  child cleanup.
- [x] 1.2 Implement desired profile fingerprint helpers and pre-copy installed
  artifact hash capture.
- [x] 1.3 Implement task/process drift classification and conditional
  stop/start behavior with concise restart reasons.
- [x] 1.4 Preserve existing ACL, token-file, firewall, onboarding, registry and
  BSL validation behavior.

## 2. Documentation And Card Evidence

- [x] 2.1 Update `host-agent/README.md` with the idempotent ensure/reconcile
  behavior and runtime proof boundary.
- [x] 2.2 Update the component card with verification command outcomes and
  Linux/Windows evidence limitations.

## 3. Verification

- [x] 3.1 Run RED focused installer contract tests before implementation and
  record the failing target.
- [x] 3.2 Run `uv run pytest -q tests/test_host_agent_installer_contract.py`.
- [x] 3.3 Run `cd host-agent/windows-display-agent && go test ./...`.
- [x] 3.4 Run `openspec validate host-agent-ensure-reconciles-task-arguments
  --strict`, `openspec validate --all --strict` and `git diff --check`.
- [x] 3.5 Sync the modified spec and archive the change after verification.

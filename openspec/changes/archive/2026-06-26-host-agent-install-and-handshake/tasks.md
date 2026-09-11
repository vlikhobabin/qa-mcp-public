## 1. Install Script And Docs

- [x] 1.1 Add the Windows host-agent install script with explicit task,
  firewall and token configuration steps.
- [x] 1.2 Document the one-time install command in the model-B Docker docs.
- [x] 1.3 Document v1 detect-and-instruct semantics and the absence of
  auto-replace/self-update.

## 2. Python Handshake

- [x] 2.1 Add expected host-agent version/hash metadata to the Python package.
- [x] 2.2 Implement `/version` handshake and structured absent/mismatch/auth
  diagnostics in the remote backend.
- [x] 2.3 Add tests for successful, absent, mismatched and unauthorized agent
  states.

## 3. Tests And Evidence

- [x] 3.1 Run PowerShell parse/syntax validation for the install script on the
  Windows lab.
- [x] 3.2 Run Python focused tests for handshake behavior.
- [x] 3.3 Retain install and handshake evidence under
  `.artifacts/openspec/host-agent-install-and-handshake/20260626-card120/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | N/A | No BSL or 1C metadata source changes in this install/handshake change. | N/A | N/A | N/A | /opt/ai-dev-suite-for-1c/bsl-mcp | Host install and Python handshake do not edit BSL. | None for BSL. |
| Delivery or runtime apply | Windows install script, scheduled task, firewall and Python handshake | Windows syntax/check transcript plus Python handshake tests. | source_preflight, scenario_log | `.artifacts/openspec/host-agent-install-and-handshake/20260626-card120/install-handshake-evidence.md` | required | /opt/ai-dev-suite-for-1c/qa-mcp |  | Actual firewall policy can vary by host. |
| Managed form layout | N/A | This change does not itself drive a form; it gates agent readiness. | N/A | N/A | N/A | /opt/ai-dev-suite-for-1c/qa-mcp | Runtime UI proof belongs to `remote-display-e2e`. | Misconfigured install would block later display verification. |

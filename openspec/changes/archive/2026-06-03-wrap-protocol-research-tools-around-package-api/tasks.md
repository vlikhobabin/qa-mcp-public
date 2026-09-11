## 1. Wrapper Refactor

- [x] 1.1 Refactor `python_manager_client.py` to re-export or delegate to package APIs where compatibility requires it.
- [x] 1.2 Refactor `python_manager_probe.py` to use package read-only session/query APIs.
- [x] 1.3 Review corpus/comparison scripts and import package descriptors or helpers only where behavior remains stable.
- [x] 1.4 Preserve current CLI arguments and output schemas or document any intentional migration.

## 2. Compatibility Tests

- [x] 2.1 Add import/CLI smoke tests for promoted wrapper entrypoints.
- [x] 2.2 Add fixture-backed tests that wrapper output keeps expected schema keys.
- [x] 2.3 Ensure scripts still compile when invoked from the repository root on Windows-native Python.

## 3. Documentation And Evidence

- [x] 3.1 Update protocol docs with the package API as the reusable source of truth and tools as research wrappers.
- [x] 3.2 If wrapper behavior regenerates compact evidence, write it under a new evidence id and update `docs/protocol-research/evidence-index.md`.
- [x] 3.3 Keep raw probe/capture output under ignored `runtime/protocol-research/`.

## 4. Verification

- [x] 4.1 Run `scripts\check.ps1`.
- [x] 4.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.3 Run focused wrapper compatibility tests.
- [x] 4.4 Run `python tools\protocol-research\python_manager_probe.py --help` or equivalent non-live CLI smoke.
- [x] 4.5 Run `bin\openspec.cmd validate wrap-protocol-research-tools-around-package-api --strict`.
- [x] 4.6 Run `bin\openspec.cmd validate --all`.
- [x] 4.7 Run `git diff --check -- openspec/changes/wrap-protocol-research-tools-around-package-api src tools/protocol-research tests docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Protocol research CLI wrappers and package import boundaries | Offline wrapper compatibility tests and CLI smoke | `scripts\check.ps1`, CLI `--help` smoke, focused wrapper tests | `tests/`; `tools/protocol-research/`; `docs/protocol-research/` | required | project:qa-mcp | N/A for deploy/apply: local Python tools only | Medium: wrapper refactor can subtly change CLI output |
| Managed form layout | Optional live read-only probe wrapper smoke | Existing accepted evidence; optional fresh live smoke if runtime available | accepted mappings and optional package/probe smoke summary | `docs/protocol-research/evidence/accepted-mappings/`; optional `docs/protocol-research/evidence/python-manager-package-smoke/<run-id>/` | required | /opt/vanessa-mcp-stack | N/A for UI mutation: wrappers only exercise read-only queries | Low: no new UI family coverage is added |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata source or EDT workspace is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | CLI wrapper compatibility is not role-visible behavior | None |

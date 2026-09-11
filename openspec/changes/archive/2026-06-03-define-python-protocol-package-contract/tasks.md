## 1. Contract Shape

- [x] 1.1 Define the public `qa_mcp.protocol` contract for read-only operation descriptors, evidence status and unresolved reasons.
- [x] 1.2 Document accepted versus supported-but-unresolved operation status for `active-window-context`, `active-form-context`, `form-summary`, `form-element-details` and typed input.
- [x] 1.3 Keep the contract stdlib-only and avoid adding runtime package dependencies.

## 2. Evidence Boundary

- [x] 2.1 Link accepted descriptors to compact accepted-mapping evidence under `docs/protocol-research/evidence/`.
- [x] 2.2 Ensure unresolved descriptors do not require raw captures or ignored runtime probe output for offline tests.
- [x] 2.3 Update protocol package docs or research docs with the package contract boundary.

## 3. Tests

- [x] 3.1 Add offline tests for package import and operation descriptor status.
- [x] 3.2 Add fixture-backed tests that verify accepted active-window and active-form descriptors from committed evidence.
- [x] 3.3 Add tests proving unresolved element-detail or typed-input descriptors are not classified as accepted.

## 4. Verification

- [x] 4.1 Run `scripts\check.ps1`.
- [x] 4.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.3 Run focused package contract tests.
- [x] 4.4 Run `bin\openspec.cmd validate define-python-protocol-package-contract --strict`.
- [x] 4.5 Run `bin\openspec.cmd validate --all`.
- [x] 4.6 Run `git diff --check -- openspec/changes/define-python-protocol-package-contract src tests docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `qa_mcp.protocol` package contract and docs | Offline package import and descriptor status tests | `scripts\check.ps1`, focused tests, OpenSpec validation | `tests/`; `docs/protocol-research/`; `openspec/changes/define-python-protocol-package-contract/` | required | project:qa-mcp | N/A for deploy/apply: local package contract only | Low: contract could lag future evidence until updated |
| Managed form layout | Read-only active-window and active-form accepted mappings | Reuse existing compact accepted evidence | accepted mappings report and corpus comparison evidence | `docs/protocol-research/evidence/accepted-mappings/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/` | required | /opt/vanessa-mcp-stack | N/A for fresh UI run: this change only consumes committed evidence | Low: current fixture remains limited to the existing form |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata source or EDT workspace is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Read-only package contract does not change role behavior | Low: future role-specific protocol differences remain out of scope |

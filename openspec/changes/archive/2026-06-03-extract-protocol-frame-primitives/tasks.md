## 1. Package Modules

- [x] 1.1 Create package modules for frame constants, payload helpers, bootstrap loading and template rendering under `src/qa_mcp/protocol/`.
- [x] 1.2 Move or wrap deterministic helpers from `tools/protocol-research/python_manager_client.py` without changing live session behavior.
- [x] 1.3 Preserve compatibility imports or aliases needed by existing exploratory scripts.

## 2. Fixture Tests

- [x] 2.1 Add offline tests for ACK GUID extraction, manager header adaptation and manager frame sequence parsing.
- [x] 2.2 Add offline tests for template rendering replacement metadata.
- [x] 2.3 Add bootstrap loading tests using compact or synthetic fixtures rather than ignored raw runtime captures.

## 3. Documentation

- [x] 3.1 Update protocol research docs with the package-owned primitive boundary if the public module names are introduced.
- [x] 3.2 Record any fixture paths or evidence sources used by tests.

## 4. Verification

- [x] 4.1 Run `scripts\check.ps1`.
- [x] 4.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.3 Run focused primitive/template tests.
- [x] 4.4 Run `python -m py_compile src\qa_mcp\protocol\*.py tools\protocol-research\python_manager_client.py`.
- [x] 4.5 Run `bin\openspec.cmd validate extract-protocol-frame-primitives --strict`.
- [x] 4.6 Run `bin\openspec.cmd validate --all`.
- [x] 4.7 Run `git diff --check -- openspec/changes/extract-protocol-frame-primitives src tools/protocol-research tests docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Package frame/template primitives and compatibility imports | Offline fixture tests and compile checks | `scripts\check.ps1`, py_compile, focused primitive tests | `tests/`; `src/qa_mcp/protocol/`; `tools/protocol-research/python_manager_client.py` | required | project:qa-mcp | N/A for deployment apply: local Python package code only | Medium: byte helpers can drift from exploratory script behavior |
| Managed form layout | Managed-form GUID and read-only form descriptor template fields | Existing compact evidence reuse and offline template checks | accepted mapping evidence and template fixture tests | `docs/protocol-research/evidence/accepted-mappings/`; `tests/` | required | /opt/vanessa-mcp-stack | N/A for fresh UI evidence: no live session behavior changes here | Low: fixture covers only accepted active form/window frames |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata source or EDT workspace is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Frame primitive extraction is not role-visible behavior | None |

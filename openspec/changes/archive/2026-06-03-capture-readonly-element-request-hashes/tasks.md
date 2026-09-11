## 1. Capture Source Selection

- [x] 1.1 Consume the audit output from `audit-readonly-element-hash-evidence`
  and choose existing extraction, fresh capture or unavailable-proof path for
  each target row.
- [x] 1.2 Verify Windows lab prerequisites with `scripts\check-protocol-lab.ps1`
  when a live capture is needed. Existing compact evidence was sufficient, so
  no live capture prerequisite was needed for implementation.
- [x] 1.3 Record the selected source path and planned evidence id before
  running extraction or capture.

## 2. Request Hash Evidence

- [x] 2.1 Extract manager-to-client request frames from existing captures when
  the audit marks a row `extractable_existing_capture`.
- [x] 2.2 If extraction is insufficient and runtime is available, run a
  read-only direct Python-manager probe for `form-element-details` using the
  short `1..17,101..106` schedule and the full `1..106` schedule only as a
  fallback. Extraction was sufficient, so no fresh probe was run.
- [x] 2.3 Preserve raw capture/probe output under
  `runtime/protocol-research/captures/<capture-id>/` and
  `runtime/protocol-research/python-manager-probe/<probe-id>/`.
- [x] 2.4 Produce compact reviewed evidence under
  `docs/protocol-research/evidence/readonly-element-request-hashes/<evidence-id>/`
  with capture id, frame range, request/response sizes, normalized hash,
  dynamic fields, operation token, response markers and replay/probe status.

## 3. Tooling Adjustments

- [x] 3.1 Add only the minimal extraction or reporting support needed under
  `tools/protocol-research/` if existing tools cannot emit reviewed element
  request-hash evidence. No tool changes were needed.
- [x] 3.2 Add focused offline tests for any touched capture/extraction helper.
  No helper was touched, so no focused helper test was added.

## 4. Verification

- [x] 4.1 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.2 Run focused extraction/probe tests or `python -m py_compile` for
  any touched `tools/protocol-research/` modules. No tools were touched; the
  retained JSON evidence was parsed with `ConvertFrom-Json`.
- [x] 4.3 Run `bin\openspec.cmd validate capture-readonly-element-request-hashes --strict`.
- [x] 4.4 Run `bin\openspec.cmd validate --all`.
- [x] 4.5 Run `git diff --check -- openspec\changes\capture-readonly-element-request-hashes tools\protocol-research docs\protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Read-only capture/extraction tooling and retained runtime output boundary | Windows preflight, extraction command plan, owned-process cleanup note | `scripts\check-protocol-lab.ps1`, compact request-hash evidence or unavailable proof | `docs/protocol-research/evidence/readonly-element-request-hashes/<evidence-id>/`; `runtime/protocol-research/captures/<capture-id>/` excluded from git | required | project:qa-mcp | N/A for deployment apply: local lab capture/extraction only | Medium: live TestClient timing can make request slices non-repeatable |
| Managed form layout | `form-element-details` and `typed-input-field-readonly` read-only element responses | Direct Python-manager probe schedule and response-marker plan | Probe result summary, frame ranges, response markers, optional screenshot not required | `docs/protocol-research/evidence/python-manager-probe/<probe-id>/`; `.artifacts/openspec/capture-readonly-element-request-hashes/<run-id>/` when UI evidence is retained | required | /opt/vanessa-mcp-stack | N/A for form mutation: read-only protocol query only | Medium: element target can differ if active form fixture changes |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata source is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Capture uses current lab user and does not change role rights | Low: role-specific UI payload differences remain out of scope |

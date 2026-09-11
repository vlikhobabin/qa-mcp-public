## 1. Case Model And Markers

- [x] 1.1 Define a corpus case manifest format with `case_id`, `api_call`,
  `ui_target`, expected state, safety class and replay expectation.
- [x] 1.2 Add case event records for `case_start`, `case_step`,
  `case_result` and `case_end` to the capture flow.
- [x] 1.3 Correlate case events with proxy chunk counters and timestamps to
  derive frame ranges without manual slicing.

## 2. Runner Implementation

- [x] 2.1 Add a Windows-native corpus runner entry point under
  `tools/protocol-research/`.
- [x] 2.2 Reuse the verified Vanessa attach-running path for the first
  read-only cases.
- [x] 2.3 Keep PID ownership and cleanup behavior equivalent to
  `run_protocol_capture.ps1`.
- [x] 2.4 Seed the first read-only case matrix for active window, active form
  and basic form-element properties.

## 3. Normalization And Evidence

- [x] 3.1 Generate normalized per-case rows with request/response sizes,
  dynamic fields, normalized hash, operation token and response markers.
- [x] 3.2 Write compact corpus reports under
  `docs/protocol-research/evidence/`.
- [x] 3.3 Update `docs/protocol-research/evidence-index.md` with generated
  corpus evidence.
- [x] 3.4 Keep raw capture streams, logs and generated replay output under
  ignored runtime directories.

## 4. Replay And Probe Confirmation

- [x] 4.1 Detect supported read-only frame families for replay or direct
  Python-manager probing.
- [x] 4.2 Record `replay_status` for accepted, rejected, partial, timeout,
  pending and unsupported mappings.
- [x] 4.3 Run at least one direct Python-manager probe against a live
  TestClient without a 1C TestManager instance for a supported corpus mapping.

## 5. Verification

- [x] 5.1 Run `scripts\check.ps1`.
- [x] 5.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 5.3 Run a short read-only corpus capture and retain its raw output under
  `runtime/protocol-research/captures/<run-id>/`.
- [x] 5.4 Analyze the run and retain compact evidence under
  `docs/protocol-research/evidence/`.
- [x] 5.5 Run `bin\openspec.cmd validate build-marked-protocol-corpus-runner --strict`.
- [x] 5.6 Run `bin\openspec.cmd validate --all`.
- [x] 5.7 Run `git diff --check -- openspec/changes/build-marked-protocol-corpus-runner tools/protocol-research docs/protocol-research scripts`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Windows protocol corpus runner and capture orchestration | Non-interactive command plan for `tools/protocol-research` runner and cleanup manifest | `scripts\check.ps1`, `scripts\check-protocol-lab.ps1`, corpus capture summary, PID cleanup proof | `runtime/protocol-research/captures/20260602-172319/capture_summary.json`; reviewed summary `docs/protocol-research/evidence/corpus/20260602-172319-readonly-smoke/corpus_summary.json` | provided | project:qa-mcp | N/A for deployment apply: this is local lab tooling, not infobase deployment | Medium: live 1C process startup is environment-dependent |
| Managed form layout | Active window/form and form-element read-only corpus cases | Read-only case matrix with expected active form/window and element markers | Vanessa attach-running result, active-window/form data where the case requires it, compact corpus evidence | `docs/protocol-research/evidence/corpus/20260602-172319-readonly-smoke/`; direct probe `docs/protocol-research/evidence/python-manager-probe/corpus-20260602-172319/` | provided | /opt/vanessa-mcp-stack | N/A for layout mutation: runner only reads form state | Low: background UI refresh may add traffic noise |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No 1C BSL source is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | First corpus matrix uses existing lab administrator access only | Low: role-specific protocol differences remain out of scope |

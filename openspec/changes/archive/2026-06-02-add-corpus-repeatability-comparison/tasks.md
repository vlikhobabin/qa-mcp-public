## 1. Comparison Inputs

- [x] 1.1 Define accepted comparison input paths for reviewed
  `corpus_cases.jsonl` files.
- [x] 1.2 Group rows by `case_id` and record capture ids, evidence paths and
  replay statuses for each group.
- [x] 1.3 Detect missing cases across repeated inputs.

## 2. Comparison Output

- [x] 2.1 Report stable versus divergent `normalized_hash` values per case.
- [x] 2.2 Compare request/response sizes, operation tokens, response markers
  and dynamic field replacement summaries.
- [x] 2.3 Emit compact repeatability JSON and Markdown reports under
  `docs/protocol-research/evidence/`.
- [x] 2.4 Keep raw capture inputs and temporary comparison output under
  ignored `runtime/protocol-research/` paths.

## 3. Runtime Evidence

- [x] 3.1 Run at least two short Windows Vanessa attach-running captures for
  the same expanded read-only case set.
- [x] 3.2 Generate corpus rows for each run.
- [x] 3.3 Compare the repeated rows and classify stable entries, missing cases
  and normalizer-investigation candidates.

## 4. Verification

- [x] 4.1 Run `scripts\check.ps1`.
- [x] 4.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.3 Run the repeatability comparison over at least two corpus evidence
  inputs.
- [x] 4.4 Run `bin\openspec.cmd validate add-corpus-repeatability-comparison --strict`.
- [x] 4.5 Run `bin\openspec.cmd validate --all`.
- [x] 4.6 Run `git diff --check -- openspec/changes/add-corpus-repeatability-comparison tools/protocol-research docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Repeated local corpus captures and offline comparison tooling | Non-interactive repeated capture and comparison command plan | `scripts\check.ps1`, `scripts\check-protocol-lab.ps1`, repeated capture summaries, compact comparison report | `runtime/protocol-research/captures/<run-a>/capture_summary.json`; `runtime/protocol-research/captures/<run-b>/capture_summary.json`; `docs/protocol-research/evidence/corpus-comparison/<comparison-id>/` | required | project:qa-mcp | N/A for deployment apply: local protocol tooling only | Medium: repeated live captures can be noisy or unavailable |
| Managed form layout | Same active form read-only matrix repeated across captures | Case-set consistency plan and missing-case reporting | Vanessa attach-running result for each run and case event comparison | `runtime/protocol-research/captures/<run-id>/case_events.jsonl`; compact comparison report | required | /opt/vanessa-mcp-stack | N/A for layout mutation: no form source is changed | Medium: UI refresh timing may shift frame ranges |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Comparison uses existing lab access only | Low: role-specific repeatability remains out of scope |

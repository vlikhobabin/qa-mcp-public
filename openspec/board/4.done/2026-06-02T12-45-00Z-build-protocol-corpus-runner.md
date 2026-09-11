# Build Protocol Corpus Runner

## Status
4.done

## Priority
P0 - first implementation track after the protocol dictionary strategy.

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- 2026-06-02 qa-mcp protocol research planning
- 2026-06-02 protocol dictionary strategy discussion

## Summary
Create a repeatable corpus runner that executes small marked protocol cases
and writes a normalized evidence table for requests, responses, dynamic
fields, hashes, operation tokens and replay status. The runner should prefer
many short, labeled read-only cases over one large unsegmented command run.

## Acceptance
- The runner can execute at least read-only active-window, form and element
  cases through the currently verified Vanessa attach-running capture path.
- Each case writes a stable JSON row with `case_id`, `api_call`, `frame_range`,
  `normalized_hash`, `operation_token`, `response_markers` and `replay_status`.
- Case events are explicit enough to map `1C API call -> frame range -> result`
  without manual traffic slicing.
- The first matrix covers `TestedApplication`, `TestedForm`,
  `TestedClientApplicationWindow` and basic form-element read-only operations.
- Each accepted mapping is repeated across captures and confirmed by Python
  replay/probe where feasible.
- The evidence index documents the generated corpus output.

## Change Set
- `openspec/changes/archive/2026-06-02-define-protocol-corpus-contract/`
- `openspec/changes/archive/2026-06-02-build-marked-protocol-corpus-runner/`

## Verify
- `bin\openspec.cmd validate define-protocol-corpus-contract --strict` passed
- `bin\openspec.cmd validate build-marked-protocol-corpus-runner --strict` passed
- `scripts\check.ps1` passed; pytest was not installed and was skipped
- `scripts\check-protocol-lab.ps1` passed
- `python tools\protocol-research\protocol_corpus_runner.py --run-capture --capture-scenario all ...` passed
- direct `python_manager_probe.py --query form-element-details` passed against a live TestClient without TestManager
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict` passed
- `bin\openspec.cmd validate --all` passed after archive
- `git diff --check` passed with only CRLF warnings

## Archive
- `openspec/changes/archive/2026-06-02-define-protocol-corpus-contract/`
- `openspec/changes/archive/2026-06-02-build-marked-protocol-corpus-runner/`

## Related
- `openspec/board/4.done/2026-06-02T13-50-55Z-define-protocol-dictionary-strategy.md`
- `openspec/changes/archive/2026-06-02-define-protocol-corpus-contract/`
- `openspec/changes/archive/2026-06-02-build-marked-protocol-corpus-runner/`
- `docs/protocol-research/methodology.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- `docs/protocol-research/evidence/corpus/20260602-084433-readonly-smoke/`
- `docs/protocol-research/evidence/corpus/20260602-172319-readonly-smoke/`
- `docs/protocol-research/evidence/python-manager-probe/corpus-20260602-172319/`
- `docs/protocol-research/evidence/infrastructure-checks/20260602-161326/infra_check.md`
- `tools/protocol-research/analyze_request_series.py`
- `tools/protocol-research/run_protocol_capture.ps1`
- `tools/protocol-research/protocol_proxy.py`
- `tools/protocol-research/protocol_corpus_runner.py`

## Result
Implemented and verified the first marked protocol corpus runner. The runner
can build normalized read-only corpus rows for active-window, active-form and
form-element cases, records side-channel case events next to raw runtime
captures, and writes reviewed corpus evidence under
`docs/protocol-research/evidence/corpus/`.

Publish scope was committed by `$opsx-pub` as a scoped protocol-runner change;
the final commit hash is reported by the publish summary.

## Publish Verification Review
- `1c-change-verification-planner` reviewed archived matrices before publish.
- Contract-only verification row is provided by OpenSpec validation and
  `docs/protocol-research/corpus-evidence-contract.md`.
- Runtime apply/local tooling row is provided by fresh capture
  `runtime/protocol-research/captures/20260602-172319/capture_summary.json`;
  cleanup stopped only owned manager, proxy and TestClient PIDs.
- Managed form/read-only UI row is provided by
  `docs/protocol-research/evidence/corpus/20260602-172319-readonly-smoke/`
  and direct probe evidence under
  `docs/protocol-research/evidence/python-manager-probe/corpus-20260602-172319/`.
- BSL, role, form mutation and report surfaces are N/A because the card adds
  local protocol tooling and read-only evidence, not 1C source or metadata.

## Next
- none

## Change Plan Notes
Proposed ordered changes:

## Change 1: `define-protocol-corpus-contract`

### Why
Broad command capture needs a stable evidence contract before many cases are
recorded; otherwise normalized hashes, dynamic fields and replay status will be
hard to compare across runs.

### Goal
Define reviewed corpus evidence rows, semantic metadata policy and replay/probe
status rules for read-only protocol mappings.

### Scope
- Protocol research docs and evidence policy.
- Delta requirements for `qa-mcp-protocol-lab`.
- No tool implementation.

### Acceptance
- Corpus row fields are defined.
- Raw/runtime versus compact evidence boundaries are explicit.
- Replay/probe status is required before a mapping is accepted.

### Depends On
- none

### Related
- `openspec/changes/define-protocol-corpus-contract/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Change 2: `build-marked-protocol-corpus-runner`

### Why
The lab needs short marked cases that connect 1C testing API calls to protocol
frame ranges and replay outcomes without manual traffic slicing.

### Goal
Implement a Windows-native marked corpus runner over the verified Vanessa
attach-running path and generate normalized compact evidence.

### Scope
- `tools/protocol-research/` runner, marker and analyzer work.
- Compact evidence output under `docs/protocol-research/evidence/`.
- Replay/probe integration for supported read-only mappings.
- No promotion into `src/qa_mcp`.

### Acceptance
- Active window/form/element read-only cases can be captured with markers.
- Per-case evidence rows include normalized hashes, dynamic fields, markers and
  replay status.
- Owned process cleanup is retained.

### Depends On
- `define-protocol-corpus-contract`

### Related
- `openspec/changes/build-marked-protocol-corpus-runner/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Log
- 2026-06-02T12:45:00Z card created
- 2026-06-02T13:50:55Z reprioritized as P0 and aligned with protocol dictionary strategy
- 2026-06-02T14:04:00Z moved to 2.todo and prepared OpenSpec artifacts for two changes
- 2026-06-02T14:21:52Z generated baseline readonly-smoke corpus evidence from capture 20260602-084433
- 2026-06-02T14:23:19Z ran fresh Vanessa attach-running capture 20260602-172319 through protocol_corpus_runner
- 2026-06-02T14:25:20Z confirmed form-element-details with direct Python-manager probe without TestManager
- 2026-06-02T14:30:00Z archived both OpenSpec changes and moved card to 4.done
- 2026-06-02T14:36:00Z reviewed 1C verification matrix evidence for publish
- 2026-06-02T14:40:00Z published by `$opsx-pub` as a scoped git commit

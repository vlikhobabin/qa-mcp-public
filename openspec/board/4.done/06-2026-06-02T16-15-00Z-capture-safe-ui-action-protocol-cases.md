# Capture Safe UI Action Protocol Cases

## Status
4.done

## Execution Order
06

## Priority
P3 - start only after accepted read-only mappings, controlled fixture evidence
and element-hash gaps are stable or explicitly deferred.

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- 2026-06-02 follow-up after `Build Protocol Corpus Runner`
- `openspec/board/4.done/2026-06-02T16-14-18Z-expand-readonly-protocol-corpus-matrix.md`
- `openspec/board/4.done/04-2026-06-03T05-30-00Z-capture-controlled-readonly-fixture-evidence.md`
- `openspec/board/4.done/05-2026-06-03T05-31-00Z-resolve-readonly-element-hash-gaps.md`

## Summary
Add the first safe UI-action protocol cases after read-only corpus evidence is
repeatable. These cases should exercise UI state transitions that do not write
business data, such as focus changes, window activation, tab switching and
menu expansion.

This card covers the next action layer after the read-only dictionary. It must
not include business-data writes, command execution with side effects or text
input into persisted fields until recovery and rollback semantics are
documented.

## Acceptance
- The case matrix includes only safe non-mutating UI actions:
  focus/activate element, activate window, switch tab/page and expand menus.
- Each action case records pre-state, action, post-state and recovery/cleanup
  expectation.
- Case rows include `case_id`, `api_call`, `ui_target`, `frame_range`,
  `normalized_hash`, dynamic fields, `operation_token`, `response_markers`,
  `replay_status` and action result markers.
- The runner or analyzer distinguishes background refresh traffic from the
  action-related frame range.
- At least one safe action mapping is confirmed by replay or direct
  Python-manager probing where feasible.
- Any unsupported action is explicitly marked `unsupported`, `pending`,
  `partial`, `timeout` or `rejected`, not accepted.
- No live write/action with business-data mutation is performed by this card.
- The card starts only after controlled read-only fixture evidence is accepted
  or explicitly deferred, known element-hash gaps are resolved or explicitly
  deferred, and rollback/recovery expectations for the chosen action are
  documented.

## Change Set
- `openspec/changes/archive/2026-06-03-define-safe-ui-action-scope/`
- `openspec/changes/archive/2026-06-03-extend-safe-action-case-events/`
- `openspec/changes/archive/2026-06-03-capture-safe-ui-action-evidence/`
- `openspec/changes/archive/2026-06-03-classify-safe-ui-action-mappings/`

## Verify
- `scripts\check.ps1` passed; `pytest` is not installed and was skipped by the script.
- `scripts\check-protocol-lab.ps1` passed static checks; no manager or TestClient was started by the static check.
- Focused `protocol_corpus_runner` and `compare_corpus_runs` direct Python harnesses passed.
- `python -m py_compile` passed for modified protocol research tools and focused tests.
- Safe-action live capture `20260603-134132` completed; cleanup stopped only owned manager, proxy and TestClient PIDs.
- `ConvertFrom-Json` parsed compact capture, classification and accepted-mapping JSON evidence.
- `bin\openspec.cmd validate define-safe-ui-action-scope --strict` passed.
- `bin\openspec.cmd validate extend-safe-action-case-events --strict` passed.
- `bin\openspec.cmd validate capture-safe-ui-action-evidence --strict` passed.
- `bin\openspec.cmd validate classify-safe-ui-action-mappings --strict` passed.
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict` passed after spec sync.
- `bin\openspec.cmd validate --all` passed after archive; final state has no active changes.
- `git diff --check` passed with line-ending warnings only.

## Archive
- `openspec/changes/archive/2026-06-03-define-safe-ui-action-scope/`
- `openspec/changes/archive/2026-06-03-extend-safe-action-case-events/`
- `openspec/changes/archive/2026-06-03-capture-safe-ui-action-evidence/`
- `openspec/changes/archive/2026-06-03-classify-safe-ui-action-mappings/`

## Related
- Publish commit message: `feat(protocol): capture safe ui action evidence`
- `openspec/board/4.done/2026-06-02T16-14-18Z-expand-readonly-protocol-corpus-matrix.md`
- `openspec/board/4.done/2026-06-02T12-45-00Z-build-protocol-corpus-runner.md`
- `openspec/board/4.done/01-2026-06-02T18-01-06Z-accept-readonly-corpus-probe-mappings.md`
- `openspec/board/4.done/02-2026-06-02T12-46-00Z-promote-python-testmanager-core.md`
- `openspec/board/4.done/03-2026-06-02T12-47-00Z-prepare-edt-meta-protocol-fixtures.md`
- `openspec/board/4.done/04-2026-06-03T05-30-00Z-capture-controlled-readonly-fixture-evidence.md`
- `openspec/board/4.done/05-2026-06-03T05-31-00Z-resolve-readonly-element-hash-gaps.md`
- `openspec/changes/archive/2026-06-03-define-safe-ui-action-scope/`
- `openspec/changes/archive/2026-06-03-extend-safe-action-case-events/`
- `openspec/changes/archive/2026-06-03-capture-safe-ui-action-evidence/`
- `openspec/changes/archive/2026-06-03-classify-safe-ui-action-mappings/`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/evidence/corpus/20260603-134132-safe-action/`
- `docs/protocol-research/evidence/corpus-comparison/safe-action-20260603-134132/`
- `docs/protocol-research/evidence/accepted-mappings/safe-action-20260603-134132/`
- `docs/protocol-research/protocol-corpus-runner.md`
- `tools/protocol-research/protocol_corpus_runner.py`
- `tools/protocol-research/compare_corpus_runs.py`
- `runtime/protocol-research/`

## Result
All four OpenSpec changes were implemented, verified, synced to
`openspec/specs/qa-mcp-protocol-lab/spec.md` and archived.

The first safe-action candidate and live capture covered activating an
already-open internal TestClient window without business-data mutation. The
compact reviewed capture is retained under
`docs/protocol-research/evidence/corpus/20260603-134132-safe-action/`; raw
capture output remains under ignored `runtime/protocol-research/captures/`.

The final classification is intentionally unresolved:
`safe-activate-existing-window` is `pending` with
`missing_action_frame_range`, `missing_request_frames`,
`missing_safe_action_hash`, `pending_action_result` and
`replay_or_probe_unavailable`. The accepted safe-action mapping set is empty,
and no package descriptor was promoted.

Published with scoped commit message
`feat(protocol): capture safe ui action evidence`; final commit hash is
reported by git history.

## Next
- none

## Change 1: `define-safe-ui-action-scope`

### Why
The lab needs a reviewable safety contract before live UI action traffic is
captured.

### Goal
Define the allowed non-mutating action families, excluded mutation cases and
precondition gates for action target selection.

### Scope
- Protocol-lab safe-action docs and spec requirements.
- Candidate matrix fields for pre-state, action, post-state and recovery.
- Explicit links to deferred/unresolved fixture and element-hash outcomes.
- No live capture, replay, package descriptor or write/action mutation.

### Acceptance
- Allowed action families and excluded mutation families are documented.
- Candidate rows require pre/post state and recovery expectation.
- Unresolved read-only prerequisites remain visible in target selection.
- Strict OpenSpec validation passes for the change.

### Depends On
- archived prerequisite cards `04` and `05`

### Related
- `openspec/changes/define-safe-ui-action-scope/`

### Notes For `$opsx-do`
- Implement this before touching capture tooling or live 1C runtime.

## Change 2: `extend-safe-action-case-events`

### Why
Safe UI action captures need action/result markers so reviewers can separate
the intended action from background refresh traffic.

### Goal
Extend the runner/analyzer event and compact-row contract for safe action
state transitions.

### Scope
- Manifest/event fields for pre-state, action, post-state, recovery and result
  markers.
- Action frame range versus background refresh range separation.
- Offline tests and evidence contract docs.
- No live runtime capture or accepted action mapping.

### Acceptance
- Action rows retain the required corpus fields plus action result markers.
- Background refresh ranges are recorded separately from action ranges.
- Unsupported action statuses remain explicit.
- Strict OpenSpec validation passes for the change.

### Depends On
- `define-safe-ui-action-scope`

### Related
- `openspec/changes/extend-safe-action-case-events/`

### Notes For `$opsx-do`
- Verify offline before running live capture.

## Change 3: `capture-safe-ui-action-evidence`

### Why
The first live safe-action evidence must prove what action was attempted, what
state changed transiently and what stayed non-mutating.

### Goal
Run Windows-native safe-action captures and retain compact reviewed evidence
or explicit unresolved outcomes.

### Scope
- Vanessa attach-running safe-action capture path or scoped wrapper.
- Raw output under ignored `runtime/protocol-research/`.
- Compact action corpus evidence under `docs/protocol-research/evidence/`.
- Cleanup proof for owned PIDs only.
- No command execution with side effects, input or business-data writes.

### Acceptance
- Available action cases record frame ranges, hashes, dynamic fields, operation
  tokens, markers and status.
- Unavailable or unsafe candidates are marked unresolved, not accepted.
- Evidence index links compact reviewed evidence.
- Strict OpenSpec validation passes for the change.

### Depends On
- `extend-safe-action-case-events`

### Related
- `openspec/changes/capture-safe-ui-action-evidence/`

### Notes For `$opsx-do`
- Live 1C runtime is expected; keep raw captures and logs out of git.

## Change 4: `classify-safe-ui-action-mappings`

### Why
Captured action traffic must be classified and replay/probe checked before it
can become working protocol knowledge.

### Goal
Classify safe-action rows, attempt replay/probe where safe and publish
accepted or unresolved mapping evidence.

### Scope
- Action comparison/classification evidence.
- Optional direct Python-manager probe or replay for at least one supported
  non-mutating action where feasible.
- Accepted-mapping evidence only for rows with accepted proof.
- No mutation, rollback/write semantics or historical evidence rewrite.

### Acceptance
- Every row has an accepted or unresolved classification.
- Accepted rows retain action frame evidence and replay/probe proof.
- Unresolved rows remain visible with reason and owner route.
- Strict OpenSpec validation passes for the change.

### Depends On
- `capture-safe-ui-action-evidence`

### Related
- `openspec/changes/classify-safe-ui-action-mappings/`

### Notes For `$opsx-do`
- Do not promote package descriptors unless accepted safe-action evidence
  exists.

## Log
- 2026-06-02T16:15:00Z card created as the first post-read-only action layer
- 2026-06-02T18:01:06Z deferred behind accepted read-only mappings, package core and fixture coverage
- 2026-06-03T06:45:37+03:00 package core dependency completed; still deferred behind fixture coverage
- 2026-06-03T05:32:00Z renumbered to `06` and deferred behind controlled fixture evidence plus element-hash gap decisions
- 2026-06-03T13:11:45+03:00 `$opsx-ff` prepared four apply-ready OpenSpec changes and moved card to `2.todo`
- 2026-06-03T14:02:39+03:00 `$opsx-do` implemented, verified, synced and archived all four changes; safe-action mapping remains pending with empty accepted output
- 2026-06-03T14:16:59+03:00 `$opsx-pub` created scoped publish commit with message `feat(protocol): capture safe ui action evidence`

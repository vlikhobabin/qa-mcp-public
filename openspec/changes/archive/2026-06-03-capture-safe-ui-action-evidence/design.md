## Context

This change is the first live-capture layer for safe UI actions. It depends on
the safe-action scope and event contract from the prior changes. The current
lab uses `C:\1C_BASES\vanessa_client`, `C:\1C_BASES\vanessa_manager` and
`C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe`.

The controlled fixture and element hash cards are archived but retain
unresolved boundaries. This capture plan must not convert those unresolved
read-only rows into accepted action evidence by assumption.

## Goals / Non-Goals

Goals:

- Capture short Windows-native action cases for non-mutating transitions when
  the active lab form exposes suitable targets.
- Retain raw capture output under `runtime/protocol-research/captures/<run-id>/`
  and compact evidence under
  `docs/protocol-research/evidence/corpus/<run-id>-safe-action/`.
- Record pre-state, action, post-state, recovery expectation, action frame
  range, background refresh range, dynamic fields, normalized hash, operation
  token, response markers and replay/probe status.
- Preserve unsupported or unavailable actions as explicit evidence rows.

Non-goals:

- Do not execute business commands or persisted writes.
- Do not use text input, checkbox toggles, table edits, posting, save or
  deletion behavior.
- Do not classify rows as accepted in this change; classification belongs to
  `classify-safe-ui-action-mappings`.
- Do not commit raw traffic, platform logs, infobase files or local secrets.

## Capture Sources

Inputs:

- safe action candidate manifest from the preceding scope/event changes;
- local lab paths from `openspec/config.yaml`;
- existing read-only fixture and element-hash evidence summaries;
- optional Vanessa attach-running scenario or wrapper that can trigger only
  the selected non-mutating UI action.

Runtime outputs:

- raw capture and process logs under
  `runtime/protocol-research/captures/<capture-id>/`;
- side-channel case events under the same ignored runtime root;
- compact reviewed rows under
  `docs/protocol-research/evidence/corpus/<capture-id>-safe-action/`;
- optional retained UI evidence bundle under
  `.artifacts/openspec/capture-safe-ui-action-evidence/<run-id>/`.

## Frame And Replay Strategy

The capture should use narrow case markers around one action at a time. The
analyzer records the action frame range and any adjacent background refresh
range separately. Replays or direct Python-manager probes are optional in this
change; when attempted, their status must be recorded as accepted, partial,
pending, unsupported, timeout or rejected.

Candidate frame ranges should not be accepted from timestamps alone when the
action marker cannot be joined to TCP chunks or response markers. Those rows
remain `partial` or `pending` with a reason.

## Safety Constraints

- Use only non-mutating focus, window activation, tab/page switch or menu
  expansion actions.
- Confirm expected pre-state before performing the action.
- Restore the prior focus, tab/page or menu-expanded state when the action can
  be reverted safely.
- Capture cleanup may stop only PIDs started by the capture tooling.
- Operator-facing evidence must not copy credentials, customer data, raw TCP
  payloads or full runtime logs into git.

## Risks / Trade-offs

- The current form may lack a safe tab or menu target -> record unsupported
  rows and do not synthesize action evidence.
- Vanessa attach-running timing can introduce refresh traffic -> preserve
  refresh ranges and avoid accepting ambiguous frame ranges.
- Some safe actions may still trigger server-side refresh -> record the
  observed post-state and recovery expectation before later classification.

## Migration Plan

No migration is required. Implementation writes new compact evidence under a
new evidence id and leaves read-only evidence unchanged.

## Open Questions

- Which target should be used for the first direct replay/probe attempt after
  capture, if any.
- Whether a small wrapper is needed around the existing capture script to
  expose tab/page switching without command execution.

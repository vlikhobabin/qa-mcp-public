## Context

This change consumes the prepared fixture source and the planned manifest at
`docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_case_manifest.json`.
The target families remain `Button`, `Table`, `CommandBar`, `Page`, `Label`
and `CheckBox`.

## Goals / Non-Goals

Goals:

- Run one or more short live fixture captures for the available read-only
  family rows.
- Produce compact corpus rows with capture id, frame range, request/response
  sizes, normalized hash, dynamic fields, operation token, response markers
  and replay/probe status when available.
- Run direct Python-manager probes against the captured templates where the
  current package/tool support allows it.
- Preserve timeout, rejected, partial, pending or unsupported outcomes.

Non-goals:

- Do not classify rows as accepted in this change; classification is handled
  by `classify-readonly-fixture-evidence`.
- Do not add action/write protocol support.
- Do not rewrite historical corpus evidence.

## Capture Sources

Inputs:

- fixture source summary from
  `docs/protocol-research/evidence/fixture-sources/<run-id>/source_summary.md`;
- fixture case manifest from the prior fixture-plan evidence directory;
- local Windows lab paths from `openspec/config.yaml`.

Runtime outputs:

- raw captures under `runtime/protocol-research/captures/<capture-id>/`;
- probe runtime output under
  `runtime/protocol-research/python-manager-probe/<probe-id>/`;
- compact corpus evidence under
  `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`;
- compact probe evidence under
  `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` when
  promoted for review.

## Frame And Replay Strategy

The corpus runner must derive frame ranges from case markers or an equivalent
reviewable mapping. Each available family row records dynamic fields and
normalized hash behavior from compact evidence only. Direct Python-manager
probes should reuse generated manager frame templates from the capture and
record whether the response markers match the expected family.

If the current runner cannot target the external fixture source or cannot join
probe evidence to a fixture row, the row stays non-accepted with an explicit
tool/provider gap.

## Safety Constraints

- Use only read-only form open, active-form, form-summary or element-detail
  queries.
- No click, command invocation, checkbox toggle, table edit, text input or
  persisted business-data mutation.
- Runtime cleanup stops only PIDs started by the capture/probe tooling.
- Raw payloads and full logs remain in ignored runtime paths.

## Open Questions

- The exact capture scenario may require a small wrapper around the existing
  `form-analysis` or `all` scenario if the fixture form is not opened by the
  standard runner. Such a gap must be recorded instead of accepting a row.

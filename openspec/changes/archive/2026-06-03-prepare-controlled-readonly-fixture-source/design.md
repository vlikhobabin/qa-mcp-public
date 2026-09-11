## Context

`plan-controlled-readonly-fixtures` produced a fixture plan and a pending
manifest for six read-only fixture cases:

- `fixture-button-readonly`
- `fixture-table-readonly`
- `fixture-commandbar-readonly`
- `fixture-page-readonly`
- `fixture-label-readonly`
- `fixture-checkbox-readonly`

The next delivery needs a real source boundary for these cases before live
capture starts. The approved baseline remains Windows-native:
`C:\1C_BASES\vanessa_client`, `C:\1C_BASES\vanessa_manager` and
`C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe`.

## Goals / Non-Goals

Goals:

- Identify the external EDT workspace, exported fixture source or other
  controlled source used to expose the six element families.
- Retain a compact source summary and family readiness table.
- Record blocked, partial or unavailable families with owner route and
  residual risk.
- Keep generated fixture output, full provider payloads and local runtime
  artifacts outside reviewed git changes.

Non-goals:

- Do not run the protocol corpus capture as part of this change.
- Do not promote new accepted mappings.
- Do not require EDT/meta providers for later raw protocol capture or replay.
- Do not exercise action or write semantics.

## Decisions

- Use a dedicated ignored bundle root such as
  `.artifacts/openspec/prepare-controlled-readonly-fixture-source/<run-id>/`
  for generated source, EDT validation output and provider logs.
- Retain compact reviewed evidence under
  `docs/protocol-research/evidence/fixture-sources/<run-id>/`.
- Treat each fixture family independently. A family can proceed when its
  source row identifies target form/element, expected read-only state and
  validation evidence; otherwise it stays `blocked`, `pending` or `partial`.
- Use provider support only for source readiness. The native protocol claim
  still requires capture plus replay or direct Python-manager evidence in
  later changes.

## Capture And Replay Strategy

This change does not assert frame ranges, dynamic fields or hashes. It prepares
the source inputs that later capture steps will use. If a validation run opens
a 1C form, it must be read-only and must retain only compact form/source
summaries. Any raw UI, provider, platform or generated output remains under
ignored runtime or artifact paths.

## Safety Constraints

- No click, checkbox toggle, table edit, text input, command execution or
  business-data mutation is allowed.
- Runtime cleanup may stop only owned PIDs recorded by the validation command.
- If the fixture source cannot be prepared safely, delivery records a blocker
  instead of inventing coverage.

## Open Questions

- The exact fixture source may be the external `demo10413` EDT workspace, a
  generated extension or a controlled existing form. Delivery must document
  whichever source is actually used.

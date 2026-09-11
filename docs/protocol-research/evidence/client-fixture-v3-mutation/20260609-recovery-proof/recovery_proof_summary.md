# Client Fixture V3 Mutation Recovery Proof

Published at: `2026-06-09T04:41:41Z`.

This reviewed summary promotes no protocol mappings. It records the recovery
proof boundary for the closed V3 mutation surface and keeps every row as a
fixture-local candidate until mutation-specific replay, direct Python-manager
probe or typed contract proof exists.

## Source Evidence

- State-model reset proof:
  `.artifacts/openspec/mutation-state-model/20260608-v3-surface/runtime-reset-proof/`
- Handler runtime proof:
  `.artifacts/openspec/mutation-form-handlers/20260608-v3-surface/runtime-handler-proof/`
- Archived prerequisite card:
  `openspec/board/4.done/03-2026-06-04-client-fixture-v3-mutation-sandbox-surface.md`

Raw captures, generated runner output, platform logs, full form-analysis dumps
and screenshots remain in ignored runtime or artifact paths. This directory
contains only compact reviewed summaries.

## Evidence Sequence

Every V3 mutation row uses the same sequence:

| Phase | Required proof |
| --- | --- |
| `before` | Baseline markers are visible before the action. |
| `action` | The reviewed fixture-local mutation is attempted against one allowlisted marker. |
| `post` | The target value, `PF_LAST_ACTION`, `PF_MUTATION_STATE`, `PF_MUTATION_TARGET` and `PF_MUTATION_POST_STATE` reflect the expected local mutation. |
| `reset` | `PF_RESET_STATE` or an equivalent reset hook returns the fixture to the V1 baseline. |
| `rerun` | The same row can be executed again after reset with the same observable markers, or remains candidate with the missing proof named. |

## Candidate Rows

| Case | Family | Target marker | Post-state marker | Recovery proof | Promotion status |
| --- | --- | --- | --- | --- | --- |
| `v3-mutate-text-string` | `text_input` | `PF_EDIT_STRING` | `PF_EDIT_STRING_POST` | `final-after-string-committed-reset/` | candidate |
| `v3-mutate-number` | `number_input` | `PF_EDIT_NUMBER` | `PF_EDIT_NUMBER_POST` | `direct-text-input-after-textedit-fix-run/` plus final reset | candidate |
| `v3-mutate-date` | `date_input` | `PF_EDIT_DATE` | `PF_EDIT_DATE_POST` | `direct-text-input-after-textedit-fix-run/` plus final reset | candidate |
| `v3-toggle-checkbox-true` | `checkbox_toggle` | `PF_CHECKBOX_TRUE` | checkbox post-state marker in handler proof | `final-after-handler-resets/` | candidate |
| `v3-click-inert-button` | `inert_button` | `PF_BUTTON_INERT` | `PF_BUTTON_INERT_POST` | `final-after-handler-resets/` | candidate |

The number and date rows start from the positive normal Vanessa/TestClient
route retained after the `TextEdit` metadata fix. The earlier VanessaExt and
clipboard/keyboard probes remain negative research evidence and are not part of
the accepted delivery route.

## Frame Isolation Boundary

No row is accepted from marker evidence alone. Candidate action frame ranges
must be recorded separately from bootstrap, background refresh and reset
traffic before any row can be promoted:

- `action_frame_range` describes only the selected mutation attempt;
- `background_frame_ranges` keeps adjacent active-window, form, idle and
  refresh frames visible;
- `recovery_frame_range` describes reset or recovery traffic and is not reused
  as the action request shape.

The current retained V3 surface proof is marker and reset evidence. It does not
yet retain mutation action frame ranges, normalized hashes, replay proof, direct
Python-manager proof or typed contract proof for the action request shape.

## Decision

Decision counts: `{"candidate": 5, "accepted": 0}`.

Rows remain candidate because `accepted_replay_probe_or_typed_contract_proof`
and isolated mutation action-frame proof are not yet retained. The reviewed
bundle is sufficient to start manifest publication and future frame-isolation
work, but it does not add accepted protocol mappings.

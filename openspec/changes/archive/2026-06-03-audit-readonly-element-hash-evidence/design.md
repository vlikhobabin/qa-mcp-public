## Context

The previous direct-probe acceptance work promoted only
`active-window-context` and `active-form-context` to accepted mappings.
`form-element-details` and `typed-input-field-readonly` remain useful direct
Python-manager probe paths but still need reviewed request-frame hashes before
they can become accepted wire mappings. The current repository already has
compact corpus, comparison, accepted-mapping and Python-manager probe evidence
for the relevant captures.

## Goals / Non-Goals

**Goals:**

- Inventory every existing compact evidence source that mentions the two
  element rows.
- Check each row against the accepted corpus evidence fields: capture id, frame
  ranges, request/response sizes, normalized hash, dynamic fields, operation
  token, response markers and replay or direct Python-manager status.
- Produce an audit decision that feeds the capture/extraction change without
  changing the row status.
- Preserve a clear reason when current evidence is insufficient.

**Non-Goals:**

- Do not run a live 1C TestClient or start capture processes in this change.
- Do not update `qa_mcp.protocol` descriptors.
- Do not change corpus comparison or normalizer tooling.
- Do not introduce safe-action, click, input, write or business-data mutation
  behavior.

## Decisions

### Audit Reviewed Evidence, Not Runtime Output

The audit should use committed compact artifacts first:

- `docs/protocol-research/evidence/corpus/20260602-193802-expanded-readonly/`
- `docs/protocol-research/evidence/corpus/20260602-195407-expanded-readonly/`
- `docs/protocol-research/evidence/corpus-comparison/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`
- `docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/`
- `docs/protocol-research/evidence/corpus/20260602-084433-readonly-smoke/`
- `docs/protocol-research/evidence/corpus/20260602-172319-readonly-smoke/`

Raw `runtime/protocol-research/` data can be named as a possible source for a
later extraction pass, but raw payloads are not copied into the audit.

### Use A Fixed Gap Taxonomy

Each row should receive one primary audit outcome:

- `already_reviewed_hash`: the row already has a complete reviewed hash set.
- `extractable_existing_capture`: committed evidence names enough capture/frame
  source data for the next change to extract a reviewed hash.
- `missing_request_frames`: useful probe data exists, but no request frame
  slice is available for hashing.
- `ambiguous_operation_join`: probe output cannot be joined to one operation
  shape or response marker set.
- `unsupported_fixture_state`: the current fixture cannot exercise the target
  element in a read-only way.
- `incomplete_normalizer_coverage`: frames exist, but dynamic fields are not
  normalized enough for a stable hash.

This taxonomy is audit output only; comparison tooling can adopt it in the
later classification change.

### Keep Status Changes Out Of The Audit

The audit can recommend a next action, but it must not promote rows or change
package descriptors. Promotion requires the later capture/classification and
publication changes to complete the accepted evidence contract.

## Risks / Trade-offs

- Existing evidence may contain accepted historical element rows while the
  current expanded read-only comparison still marks the target rows
  `incomplete_hash`; mitigate by naming source capture ids and explaining
  whether the operation shape matches the current descriptor path.
- The audit could overfit to one fixture form; mitigate by recording semantic
  sources and response markers separately from byte-level acceptance.
- A docs-only audit can feel redundant, but it prevents the next change from
  mixing evidence discovery with live capture and tool changes.

## Migration Plan

No runtime migration is needed. The output is a compact audit report and, if
appropriate, an evidence-index entry. Later changes consume the audit result
to decide whether to extract existing frames, run fresh capture/probe evidence
or preserve a precise unresolved status.

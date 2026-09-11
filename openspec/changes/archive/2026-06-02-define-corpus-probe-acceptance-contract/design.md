## Context

The current corpus contract already requires `replay_status`, but it does not
spell out how a direct Python-manager probe is attached to a corpus row or how
that probe evidence affects repeatability classification. The latest expanded
matrix therefore has useful stable normalized hashes for active-window and
active-form rows, but the comparison correctly keeps them out of stable
accepted dictionary entries because the proof is not represented in the row
contract.

## Goals / Non-Goals

**Goals:**

- Define a compact `probe_evidence` shape or equivalent row fields for
  direct Python-manager confirmation.
- Define the accepted read-only mapping rule: stable repeated normalized hash,
  matching operation identity, expected response markers and accepted
  replay/probe evidence.
- Define how unsupported, pending, partial, rejected, timeout and incomplete
  direct-probe rows remain visible.
- Keep raw probe output and raw TCP captures out of reviewed artifacts.

**Non-Goals:**

- Do not implement corpus runner or comparison logic in this contract change.
- Do not accept safe UI actions, clicks, text input or business-data mutation.
- Do not make EDT/meta semantic labels sufficient for protocol acceptance.

## Decisions

### Probe Evidence Is A Supporting Reviewed Link

Corpus rows should link to compact probe evidence under
`docs/protocol-research/evidence/` and may summarize sanitized facts such as
probe id, query, frame mode, status, response marker count and supported case
ids. They should not embed raw response payloads or full runtime logs.

### Accepted Means Stable And Confirmed

`accepted` should require both repeatability and confirmation. A row with a
stable hash but no accepted probe/replay evidence remains non-accepted. A row
with useful direct-probe output but no reviewed request-frame hash remains
`partial` or `incomplete_hash` until the gap is explained.

### Explicit Gaps Are First-Class Evidence

Rows for unavailable element families and incomplete direct-probe mappings
should stay in the corpus as reviewed gaps. This prevents the dictionary from
silently implying that unsupported families were tested.

## Risks / Trade-offs

- Requiring both stable hashes and probe evidence slows promotion, but avoids
  turning Vanessa noise into protocol knowledge.
- Probe-backed rows may not always have the same frame slicing as
  Vanessa-captured rows; unresolved rows must keep explicit limitations.
- Too much probe metadata in corpus rows could duplicate evidence; mitigate by
  linking compact evidence and summarizing only acceptance-critical fields.

## Migration Plan

Existing corpus rows remain valid. New or regenerated rows may add
probe-evidence fields and stricter accepted status rules. Older pending rows
should not be rewritten unless a delivery change regenerates reviewed evidence
from the recorded captures and compact probe outputs.

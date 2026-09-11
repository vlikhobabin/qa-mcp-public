## Context

The lab already has a baseline capture, generated manager-frame templates and a
direct Python manager probe. The next research phase needs breadth across many
1C testing API calls, but broad capture without a stable evidence contract would
make later comparisons hard to audit.

Existing source-of-truth boundaries remain unchanged:

- raw captures and generated replay output stay under `runtime/`;
- compact reviewed evidence stays under `docs/protocol-research/evidence/`;
- exploratory tooling stays under `tools/protocol-research/`;
- promoted runtime/provider code stays under `src/qa_mcp/`.

## Goals / Non-Goals

**Goals:**

- Define a corpus case row that can describe one marked protocol case.
- Require dynamic-field normalization before comparing request shapes.
- Require replay/probe confirmation before treating a mapping as working
  protocol knowledge.
- Keep metadata/help/EDT information as semantic enrichment, not proof by
  itself.

**Non-Goals:**

- Do not implement a corpus runner in this change.
- Do not promote Python manager code into `src/qa_mcp`.
- Do not decode action/write protocol semantics yet.
- Do not commit raw capture payloads or 1C binaries.

## Decisions

### Use A Normalized Case Row

Each corpus case should have one reviewed row with stable fields:
`case_id`, `scenario`, `api_call`, `ui_target`, `expected_state`,
`frame_range`, request/response sizes, `normalized_hash`, dynamic fields,
`operation_token`, `response_markers`, `replay_status` and `evidence_path`.

Alternative considered: keep per-run Markdown notes only. That is too hard to
aggregate or compare across repeated captures.

### Keep Capture Evidence Separate From Semantic Enrichment

The protocol claim is proved by captured bytes, normalization and replay. MCP
providers such as `help-mcp`, `meta-mcp` and `edt-mcp` may label object-model
semantics, but they do not replace TCP evidence.

Alternative considered: derive expected protocol mappings from metadata and
platform help first. That is useful for planning case matrices, but it cannot
prove wire behavior.

### Start With Read-Only Cases

The first corpus contract is optimized for read-only queries over
`TestedApplication`, `TestedClientApplicationWindow`, `TestedForm` and form
elements.

Alternative considered: include click/input/command execution immediately.
Those operations have higher recovery and data-mutation risk, so they should
wait until read-only classification is repeatable.

## Risks / Trade-offs

- Case rows may miss a dynamic field at first - mitigate by requiring repeated
  captures and replay status before marking a mapping accepted.
- A normalized hash can hide meaningful bytes if the normalizer is too broad -
  mitigate by recording replacement ranges and original byte classes.
- Semantic labels may contain encoding ambiguity - mitigate by retaining raw
  UTF-16/ASCII marker summaries in compact evidence.

## Migration Plan

No runtime migration is required. Existing evidence remains valid. Future
corpus output should add compact evidence under a new reviewed evidence folder
and link from `docs/protocol-research/evidence-index.md`.

## Open Questions

- Whether the first corpus schema should be documented only in Markdown or also
  backed by a JSON schema file.
- Whether `operation_token` should be one field or a list when a request has
  multiple command-like byte ranges.

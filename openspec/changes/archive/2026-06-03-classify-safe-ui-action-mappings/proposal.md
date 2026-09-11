## Why

Captured safe-action traffic is useful only after frame ranges, dynamic fields
and replay/probe outcomes are classified. The final action layer must publish
accepted mappings separately from unsupported or unresolved action evidence.

## What Changes

- Compare and classify safe UI-action evidence rows, including background
  refresh separation, normalized hash stability and action result markers.
- Attempt replay or direct Python-manager probing for at least one supported
  non-mutating action where the current protocol package can do so safely.
- Publish compact accepted-mapping or unresolved-action evidence under
  `docs/protocol-research/evidence/`.
- Keep unsupported, pending, partial, timeout and rejected statuses visible
  instead of treating them as accepted mappings.
- This change touches protocol research tools, Python manager probing where
  supported, protocol docs and compact evidence. It may require live 1C
  runtime for replay/probe confirmation after offline checks pass.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require classification and replay/probe status before
  safe UI-action mappings can be used as working protocol knowledge.

## Impact

- `tools/protocol-research/compare_corpus_runs.py` or action-specific
  comparison helpers.
- `src/qa_mcp/protocol/` only if a safe non-mutating descriptor or probe path
  is promoted with evidence.
- `docs/protocol-research/evidence-index.md` and action evidence directories.
- Live replay/probe evidence remains optional unless the selected action
  family is supported and safe to exercise.

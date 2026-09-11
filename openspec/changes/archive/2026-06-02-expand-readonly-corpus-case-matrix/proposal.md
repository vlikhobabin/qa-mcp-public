## Why

The first corpus runner proved three read-only smoke cases, but the protocol
dictionary is still too narrow to describe common form-element reads. Expanding
the case matrix now gives the normalizer and Python manager broader evidence
before any action/write semantics are attempted.

## What Changes

- Add an expanded read-only corpus case matrix for additional form element
  families such as `Button`, `Table`, `CommandBar`, `Page`, `Label`,
  `CheckBox` and typed input fields.
- Define the expected evidence rows, response markers and replay/probe
  expectations for those element families.
- Update protocol research docs and reviewed evidence locations when new
  mappings are accepted.
- This change touches protocol tools, protocol research docs and runtime lab
  evidence. It requires live 1C runtime through the existing Vanessa
  attach-running capture path for final acceptance.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for expanded read-only corpus case
  coverage and accepted evidence for additional form element families.

## Impact

- `tools/protocol-research/protocol_corpus_runner.py` case manifest handling
  and seeded case definitions.
- Optional supporting docs under `docs/protocol-research/`.
- Compact reviewed evidence under `docs/protocol-research/evidence/`.
- Raw captures remain under ignored `runtime/protocol-research/`.

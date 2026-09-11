## 1. Classification Inputs

- [x] 1.1 Confirm compact capture evidence from
  `capture-safe-ui-action-evidence`.
- [x] 1.2 Select classification and accepted-mapping evidence directories
  under `docs/protocol-research/evidence/`.
- [x] 1.3 Confirm which action rows have enough frame, hash and marker data
  for replay or direct Python-manager probing.

## 2. Classification And Replay

- [x] 2.1 Compare safe action rows and separate action frame ranges from
  background refresh ranges.
- [x] 2.2 Classify every row as `accepted`, `pending`, `unsupported`,
  `partial`, `timeout`, `rejected` or `blocked` with reason values.
- [x] 2.3 Attempt replay or direct Python-manager probing for at least one
  supported non-mutating action where current tooling can do so safely.
- [x] 2.4 Keep rows without accepted replay/probe proof out of accepted
  mapping output.

## 3. Publication

- [x] 3.1 Publish compact classification evidence and accepted or unresolved
  mapping evidence under a new evidence id.
- [x] 3.2 Update `docs/protocol-research/evidence-index.md` and related
  protocol docs without rewriting historical evidence.
- [x] 3.3 Update package descriptors only if accepted evidence supports a
  safe non-mutating action descriptor.

## 4. Verification

- [x] 4.1 Run focused classification/replay tests.
- [x] 4.2 Run `scripts\check.ps1`.
- [x] 4.3 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.4 Run `bin\openspec.cmd validate classify-safe-ui-action-mappings --strict`.
- [x] 4.5 Run `git diff --check -- openspec/changes/classify-safe-ui-action-mappings docs/protocol-research tools/protocol-research src tests`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Safe action classification, replay/probe and optional descriptor publication | Classification command plan, replay/probe safety check and accepted/unresolved evidence layout | Focused tests, comparison summary, replay/probe summary, OpenSpec validation | `docs/protocol-research/evidence/corpus-comparison/<comparison-id>/`; `docs/protocol-research/evidence/accepted-mappings/<evidence-id>/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` | required | `project:qa-mcp` | N/A | High: replay/probe support may not exist for action frames |
| Managed form layout | Safe action target rows with pre/post state and action markers | Action/result marker review and refresh-frame separation | Classification report, optional Vanessa UI evidence bundle, accepted or unresolved row summary | `.artifacts/openspec/classify-safe-ui-action-mappings/<run-id>/`; `docs/protocol-research/evidence/corpus-comparison/<comparison-id>/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: ambiguous refresh may block acceptance |
| Python manager protocol API | Optional safe non-mutating action descriptor or probe path | Descriptor gate tied to accepted evidence only | Focused package tests and accepted evidence link when descriptor changes | `src/qa_mcp/protocol/`; `tests/`; `docs/protocol-research/evidence/accepted-mappings/<evidence-id>/` | required | `project:qa-mcp` | N/A if no descriptor is promoted | Medium: package may stay read-only until action replay is accepted |
| Form module or command | Business command execution, input and write handlers | N/A | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Mutating command/input behavior is excluded and needs a separate rollback card | Medium: no write/action command semantics are learned |

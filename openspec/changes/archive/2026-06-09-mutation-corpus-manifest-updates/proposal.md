## Why

V3 mutation work needs a machine-readable manifest and evidence contract so
rows can be reviewed, isolated and published without relying on informal notes.
The state model, handlers and recovery proof are not enough unless the corpus
rows themselves declare the required fields and the evidence index records the
resulting compact proof bundle.

## What Changes

- Define the V3 mutation manifest row shape with `target_marker`,
  `mutation_family`, `pre_state`, `action`, `post_state`,
  `recovery_expectation`, `mutates_business_data=false` and
  `expected_action_result_markers`.
- Require fail-closed validation for incomplete or unsupported mutation rows.
- Update the corpus evidence contract so reviewed mutation rows are published
  as compact evidence bundles instead of raw captures.
- Keep the manifest and evidence links aligned with the reviewed V3 mutation
  proof paths.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V3 mutation rows gain explicit manifest and evidence
  contract requirements.

## Impact

- Protocol research docs, evidence index entries and later corpus publication
  workflow.
- OpenSpec artifacts for V3 mutation planning and review.
- Requires live 1C runtime evidence for verification of the underlying rows,
  but the change itself is docs and contract focused.

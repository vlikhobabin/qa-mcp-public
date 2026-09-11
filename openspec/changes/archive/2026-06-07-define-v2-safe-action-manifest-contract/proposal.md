## Why

The safe UI action scope already separates non-mutating action research from
read-only evidence and later mutation work. V2 now needs a concrete manifest
contract so client fixture, manager runner and tooling cards consume the same
fail-closed row shape before any capture or implementation starts.

## What Changes

- Document required V2 safe-action manifest fields:
  `action_id`, `target_id`, `target_marker`, `pre_state`, `action`,
  `post_state`, `recovery_expectation`, `mutates_business_data=false`,
  `allowed_action_family` and `expected_action_result_markers`.
- Allow only the first V2 action families: focus or activate an existing
  element, activate an existing window/form, switch a fixture page, select a
  local table row, and expand/collapse a menu or group without executing a
  command.
- Explicitly reject text input, checkbox/value toggles, business command
  clicks, object writes, save, post, delete, fill, import, export and external
  side effects from V2.
- Keep action rows as candidate/planned evidence until later replay or direct
  Python-manager proof accepts them.

This change touches protocol research docs, evidence contract wording and
OpenSpec requirements. It does not edit the fixture or manager harness and does
not run live 1C captures.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: V2 safe-action manifests are defined as an explicit
  fail-closed contract before implementation cards consume them.

## Impact

- `docs/protocol-research/safe-ui-action-scope.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `openspec/specs/qa-mcp-protocol-lab/spec.md` delta requirements
- No client fixture, manager harness, Python package or runtime lab config
  changes.

# Server SSH workspace policy-gated QA proof receipts

## Status
4.done

## Series
`S60-074` subordinate follow-up from root.

## Owner
unassigned

## OpenSpec Stage
archived

## Policy Gate
Not required by default. Activate only when a project card requires QA/TestClient
proof for a server SSH workspace delivery phase.

## Source
- `../openspec/board/2.todo/s60-forgejo-team-development-074-server-ssh-workspace-component-receipts.md`
- `../docs/server-ssh-workspace-lifecycle.md`

## Summary
When project policy requires QA proof, bind QA/TestClient evidence to the same
pushed source identity used by metadata, BSL, config and admin receipts.

## Acceptance
- QA proof receipts report workspace id when provided, project/repository
  identity, commit SHA, tree SHA, source scope, source generation or snapshot
  id, scenario/evidence reference and freshness state.
- Missing QA proof is reported as not-required unless an active project policy
  or card makes QA proof mandatory.
- QA diagnostics are bounded and do not retain screenshots, raw protocol logs,
  customer data, infobase dumps or source bodies in the workspace receipt.
- QA proof never parses mutable server SSH workspace paths or receives XML/BSL
  source through MCP, host bridge or retained evidence.

## Scope
- Policy-gated QA proof receipt contracts only.
- No runtime action implementation in this root-routed card.
- Any business-data mutation or UI action still requires explicit project
  policy and qa-mcp safety rules.

## Receipt Field Checklist
- Owns: QA proof correlation, scenario evidence reference and policy-gated
  required/not-required status.
- Consumes: root workspace identity and source/provider readiness receipts.
- Reports gaps: missing policy, missing QA proof, stale source identity or
  unavailable TestClient contour.

## Verify
- `uv run pytest -q tests/test_workspace_proof_receipts.py`
- `uv run pytest -q`
- `uv run python -m compileall -q src tests`
- `openspec validate qa-server-ssh-workspace-proof-receipts --strict`
- `openspec validate qa-mcp-workspace-proof-receipts --strict`
- `openspec validate --all --strict`
- `git diff --check`

## Verification Evidence
- RED: `uv run pytest -q tests/test_workspace_proof_receipts.py` failed before
  implementation with `ModuleNotFoundError: No module named
  'qa_mcp.workspace_proof_receipts'`.
- PASS: `uv run pytest -q tests/test_workspace_proof_receipts.py` - 5 passed.
  The tests observe policy status transitions, source identity freshness
  comparison, forbidden-route rejection and raw proof body omission.
- PASS: `uv run pytest -q` - 900 passed before review; 903 passed after the
  cycle-1 rescue; 906 passed after the cycle-2 rescue.
- PASS: `uv run python -m compileall -q src tests`.
- PASS: `openspec validate qa-server-ssh-workspace-proof-receipts --strict`.
- PASS: `openspec validate qa-mcp-workspace-proof-receipts --strict`.
- PASS: `openspec validate --all --strict` - 22 passed, 0 failed after archive.
- PASS: `git diff --check`.
- NOT APPLICABLE: Windows-native/live TestClient verification. This change is a
  pure offline receipt contract and does not execute UI, protocol replay, COM,
  infobase access or platform startup.

## Result
Implemented an offline qa-mcp server SSH workspace proof receipt helper and
spec. QA proof remains policy-gated: missing proof reports `not-required` by
default, required missing proof reports `missing`, matching proof reports
`current`, mismatched proof reports `stale`, and forbidden source/evidence routes
report `unavailable` without retaining rejected values. Review rescue now
requires project id, repository id and non-empty source scope before required
proof can be marked `current`, and rejects URL-like, Windows-drive, backslash,
home and traversal `source_scope` routes without retaining those values.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Change Set
- `qa-server-ssh-workspace-proof-receipts` -
  `openspec/changes/archive/2026-08-04-qa-server-ssh-workspace-proof-receipts/`

## Archive
- `openspec/changes/archive/2026-08-04-qa-server-ssh-workspace-proof-receipts/`

## Related
- `openspec/changes/archive/2026-08-04-qa-server-ssh-workspace-proof-receipts/`
- `openspec/specs/qa-mcp-workspace-proof-receipts/spec.md`

## Next
- done

## Change 1: `qa-server-ssh-workspace-proof-receipts`

### Why
Root S60 server SSH workspace routing needs a qa-mcp-owned receipt contract that
binds optional QA/TestClient proof to immutable source identity only when
project policy requires runtime proof.

### Goal
Publish an offline-tested QA proof receipt helper that reports `not-required` by
default, `missing` when required proof is absent, `current` when proof matches
the selected commit/tree identity, `stale` when it does not, and `unavailable`
for forbidden source/evidence routes.

### Scope
- Add qa-mcp proof receipt contract code and tests.
- Add OpenSpec requirements for policy-gated receipt behavior, source identity
  freshness and bounded diagnostics.
- Keep runtime QA actions, TestClient launch, UI automation, protocol replay,
  COM, screenshots and source-body handling out of this change.

### Acceptance
- QA proof receipts report workspace id when provided, project/repository
  identity, commit SHA, tree SHA, source scope, source generation or snapshot
  id, scenario/evidence reference and freshness state.
- Missing QA proof is reported as `not-required` unless an active project policy
  or card makes QA proof mandatory.
- QA diagnostics are bounded and do not retain screenshots, raw protocol logs,
  customer data, infobase dumps or source bodies in the workspace receipt.
- QA proof never parses mutable server SSH workspace paths or receives XML/BSL
  source through MCP, host bridge or retained evidence.

### Depends On
- root S60-074 published routing and receipt handoff contracts.

### Related
- `openspec/changes/archive/2026-08-04-qa-server-ssh-workspace-proof-receipts/`

## Log
- 2026-08-04T07:05:00Z created as policy-gated optional route from root S60-074.
- 2026-08-04T09:45:00Z `$changerail-deliver` treated the operator request as
  activation for the contract-only receipt surface; runtime QA proof remains
  policy-gated and not required by default.
- 2026-08-04T09:45:00Z `$changerail-ff` created one apply-ready OpenSpec
  change for policy-gated QA proof receipts.
- 2026-08-04T09:51:00Z `$changerail-do` implemented the offline receipt helper,
  synced specs, verified focused/OpenSpec/whitespace checks and archived the
  change for independent review.
- 2026-08-04T09:57:12Z independent review cycle 1 returned `no-go` for blocker
  `R1`: required QA proof could be marked `current` without project/repository
  identity or `source_scope`.
- 2026-08-04T10:01:14Z same-card rescue fixed `R1` by requiring project id,
  repository id and non-empty source scope before current required proof,
  added regression tests and reran focused/full verification.
- 2026-08-04T10:07:00Z independent review cycle 2 returned `no-go` for blocker
  `R1`: URL-like, Windows-drive and traversal `source_scope` values could be
  retained while required QA proof reported `current`.
- 2026-08-04T10:11:13Z same-card rescue fixed cycle 2 `R1` by rejecting and
  omitting unsafe `source_scope` routes, added regression tests and reran
  focused/full verification.
- 2026-08-04T10:18:06Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

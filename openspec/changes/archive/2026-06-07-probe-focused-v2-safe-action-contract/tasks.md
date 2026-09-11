## 1. Proof Route Selection

- [x] 1.1 Consume isolated candidate rows from
  `isolate-focused-v2-safe-action-frames`.
- [x] 1.2 Choose the feasible proof route for each focused row: replay, direct
  Python-manager probe or typed contract validation.
- [x] 1.3 Record when a proof route is infeasible, blocked or unsafe and keep
  the row non-accepted.

## 2. Proof Attempt

- [x] 2.1 Run the selected proof attempt for the focused row or rows.
- [x] 2.2 Retain compact proof evidence with normalized hash, dynamic fields,
  operation token, request/response sizes and action result markers where
  available.
- [x] 2.3 Keep raw replay/probe payloads, generated request series and platform
  logs under ignored runtime paths.
- [x] 2.4 Decide accepted versus candidate or another non-accepted status per
  row.

## 3. Verification

- [x] 3.1 Retain proof summaries under
  `.artifacts/openspec/probe-focused-v2-safe-action-contract/<run-id>/proof/`.
- [x] 3.2 Run `bin\openspec.cmd validate probe-focused-v2-safe-action-contract --strict`.
- [x] 3.3 Run `git diff --check -- openspec/changes/probe-focused-v2-safe-action-contract docs/protocol-research tools/protocol-research tests openspec/board`.

## Evidence

- Source corpus:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/corpus_cases.jsonl`
- Proof decision:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-proof-decision/proof_summary.md`
- Proof decisions JSONL:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-proof-decision/proof_decisions.jsonl`
- Handoff artifact:
  `.artifacts/openspec/probe-focused-v2-safe-action-contract/20260607-first-focused-v2-safe-action-live-runner-2/proof/proof_summary.md`
- Decision: 2 candidate rows, 0 accepted rows.
- Route result: replay and direct Python-manager probes are infeasible for the
  current same-action V2 semantics; typed contract is insufficient because it
  cannot independently prove the isolated wire shape reproduces the same
  action.
- Verification:
  `pytest -q tests/test_v2_safe_action_proof_summary.py tests/test_manager_fixture_v2_safe_action_report.py tests/test_v2_safe_action_tooling.py tests/test_v2_safe_action_live_runner.py -p no:cacheprovider --basetemp runtime/tmp/pytest`
  passed with 14 tests.

## 4. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Replay/probe or typed contract proof route for focused V2 row | Proof route decision and command plan that avoids mutation | Proof summary; accepted/candidate decision; OpenSpec strict validation | `.artifacts/openspec/probe-focused-v2-safe-action-contract/<run-id>/proof/` | required | `project:qa-mcp`, `/opt/ai-tools-1c` | N/A | Medium: replay/probe route can be infeasible against current live session |
| Form module or command | Focused manager safe-action row and action result markers | Same-action proof comparing isolated frames to replay/probe or typed contract result | Action marker comparison; normalized hash summary; dynamic-field summary | `.artifacts/openspec/probe-focused-v2-safe-action-contract/<run-id>/action-proof/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: typed contract may be weaker than live replay if markers are incomplete |
| Managed form layout | Client fixture visual/marker state after proof attempt | N/A unless proof route opens or inspects the form live | N/A or retained form/marker summary if live proof is used | N/A | N/A | `project:qa-mcp`, `vanessa-mcp` | The proof change may use replay or typed contract evidence without a new form layout interaction | Low: latest live form state remains covered by the capture change |

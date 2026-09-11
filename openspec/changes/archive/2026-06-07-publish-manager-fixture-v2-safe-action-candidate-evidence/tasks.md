## 1. Evidence Publication

- [x] 1.1 Publish compact manager fixture V2 safe-action candidate evidence
  with action, background and recovery ranges separated.
- [x] 1.2 Record normalized hash fields, action result markers, replay/probe
  or typed-contract status and non-accepted reasons.
- [x] 1.3 Update docs or evidence index with compact retained evidence paths.
- [x] 1.4 Keep raw captures, platform logs and generated replay payloads under
  ignored runtime paths.

## 2. Verification

- [x] 2.1 Retain publication proof under
  `.artifacts/openspec/publish-manager-fixture-v2-safe-action-candidate-evidence/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate
  publish-manager-fixture-v2-safe-action-candidate-evidence --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/publish-manager-fixture-v2-safe-action-candidate-evidence docs/protocol-research tools/protocol-research tests openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | V2 reporter, comparison output and evidence docs | Compact candidate evidence publication and accepted/non-accepted status review | Reporter output; comparison summary; OpenSpec strict validation; diff check | `.artifacts/openspec/publish-manager-fixture-v2-safe-action-candidate-evidence/<run-id>/publication-proof/` | required | `project:qa-mcp`, `/opt/ai-tools-1c` | N/A | Medium: candidate rows can be misread as accepted without clear status |
| Form module or command | Manager runner implementation | N/A for this publication change; runner behavior is covered by earlier changes | N/A | N/A | N/A | `project:qa-mcp` | This change publishes reviewed evidence and docs after runner proof exists | Low: implementation verification remains required upstream |

## 1. Manifest And Evidence Contract

- [x] 1.1 Define the V4 manifest row shape for warning, question, modal,
  expected-error and bounded-wait scenario families.
- [x] 1.2 Require family-specific safety fields such as expected text marker,
  expected diagnostic marker and bounded wait duration.
- [x] 1.3 Update corpus evidence docs or reporter contracts so expected errors
  stay separate from infrastructure failures.
- [x] 1.4 Keep raw captures, platform logs and generated replay payloads under
  ignored runtime paths.

## 2. Verification

- [x] 2.1 Retain V4 manifest samples and compact evidence examples under
  `.artifacts/openspec/v4-dialog-corpus-manifest-updates/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate v4-dialog-corpus-manifest-updates
  --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/v4-dialog-corpus-manifest-
  updates docs/protocol-research tools/protocol-research tests openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | V4 manifest docs, reporter contract and compact evidence publication | Fail-closed row shape, sample rows and evidence publication plan | OpenSpec strict validation; manifest sample validation or dry-run reporter proof; diff check | `.artifacts/openspec/v4-dialog-corpus-manifest-updates/20260609-v4-static-contract/manifest-proof/` | done | `project:qa-mcp`, `/opt/ai-tools-1c` | N/A | Low: V4 fields are documented as scoped candidate-only manifest fields |
| Form module or command | Fixture runtime handlers | N/A for this change; runtime handlers are covered by earlier V4 scenario changes | N/A | N/A | N/A | `project:qa-mcp` | This change defines manifest/publication contracts only | Low: handler evidence remains required by scenario and recovery changes |

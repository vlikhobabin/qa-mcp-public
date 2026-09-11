## 1. Publication

- [x] 1.1 Update the fixture target-map or evidence index docs so the V2
  safe-action rows reference the new marker set and reset hook.
- [x] 1.2 Record the allowed families and excluded controls as reviewed
  publication text, not accepted protocol mapping.

## 2. Verification

- [x] 2.1 Run the Windows-native publication review and retain compact
  evidence for the target-map updates.
- [x] 2.2 Run `bin\openspec.cmd validate
  publish-client-fixture-v2-safe-action-manifest-updates --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/publish-client-fixture-v2-safe-action-manifest-updates docs/protocol-research openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Docs and evidence index | V2 safe-action target rows and evidence paths | Reviewed target map and manifest notes | Compact reviewed docs links; no raw runtime payloads | `docs/protocol-research/evidence/`; `.artifacts/openspec/publish-client-fixture-v2-safe-action-manifest-updates/<run-id>/review-notes/` | required | `project:qa-mcp` | N/A for live runtime: this change publishes documentation only | Medium: target rows can drift if the fixture markers change |
| Runtime apply | Documentation publication | OpenSpec validation and diff check | Strict validation and whitespace check | `openspec/changes/publish-client-fixture-v2-safe-action-manifest-updates/` | required | `project:qa-mcp` | N/A | Low: no fixture code is modified here |

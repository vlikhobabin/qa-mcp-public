## 1. Manifest Carve-Out

- [x] 1.1 Update self-hosted release docs to state the qa-mcp `_bundled/` P5 carve-out.
- [x] 1.2 Ensure generated `ai1c.component-release.manifest.v1` manifests include no separate qa data asset for `_bundled/`.
- [x] 1.3 Include protected bundled-data metadata without secrets or raw capture payloads.

## 2. Protected Verification

- [x] 2.1 Keep `docker/verify_protected_image.py` as a publish gate in the self-hosted manifest contract.
- [x] 2.2 Record verifier output as release evidence when Docker is available.

## 3. Verification

- [x] 3.1 Generate or inspect a sample manifest.
- [x] 3.2 Run `openspec validate protected-bundle-release-manifest --strict`.
- [x] 3.3 Run `git diff --check`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | self-hosted manifest and protected image | Manifest inspection plus protected verifier | sample manifest, verifier output or Docker provider-gap diagnostic | `.artifacts/openspec/protected-bundle-release-manifest/20260703T101126Z/manifest.sample.json` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient runtime | `_bundled` decrypt/read path | Protected verifier exercises packaged bundled reads | verifier output | `.artifacts/openspec/suite-base-proxy-transport/20260703T101126Z/verification-summary.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Managed form layout | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No 1C managed form behavior changes. | Live release E2E remains required before external handoff. |

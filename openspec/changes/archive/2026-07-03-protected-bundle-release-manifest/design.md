## Context

`src/qa_mcp/_bundled/` contains genuine captures, templates and accepted mappings.
Prior protected-build changes compile protocol code and encrypt `_bundled/` in
the image using an AES-GCM key embedded in compiled code. The suite architecture
normally moves data assets out of provider images, but doing that for qa-mcp
would expose the most sensitive protocol corpus as a standalone release artifact.

## Design

- Keep `_bundled/` inside the code image and encrypted at rest.
- Add a manifest field or metadata block that records:
  - `component: qa-mcp`
  - image type/tag/asset/sha256/size
  - `data_assets: []`
  - `protected_bundled_data.carve_out: true`
  - rationale that `_bundled/` is small encrypted protocol IP, not large swappable
    customer/project data.
- Treat `docker/verify_protected_image.py` output as the acceptance proof that
  the baked corpus is encrypted and usable.
- Keep `BUNDLED_DATA_KEY` in ignored local release env or CI secret only. The
  manifest must not contain keys, internal capture paths or raw evidence.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Component release manifest and protected image | Manifest schema/field inspection; protected image verifier | manifest sample, sha256 sidecar, verifier output | `.artifacts/openspec/protected-bundle-release-manifest/<run-id>/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient runtime | Protocol corpus decrypt/read path | Existing protected verifier exercises bundled reads; no live UI action for manifest-only change | verifier output or deferred release-run evidence | `.artifacts/openspec/protected-bundle-release-manifest/<run-id>/verify-protected.txt` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Migration or data repair | External data asset extraction | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change intentionally does not extract or migrate `_bundled/` data. | Future data-asset tooling must preserve this carve-out. |

## Risks

- The carve-out can be mistaken for ignoring suite P5. Mitigation: docs and
  manifest explicitly state the reason and the absence of a qa data asset.
- A client-side encrypted corpus is still reverse-engineerable. Mitigation:
  this is cost-raising protection combined with the license gate, not absolute
  DRM.

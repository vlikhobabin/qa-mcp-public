## 1. Thin Image Transport

- [x] 1.1 Parameterize `docker/Dockerfile.thin` with matching builder/final Python base image args.
- [x] 1.2 Change the final stage to inherit the suite provider base.
- [x] 1.3 Remove final-image vendored broker copying and use the suite base broker path.
- [x] 1.4 Replace qa-mcp's in-process HTTP transport defaults with `ai-mcp-proxy serve-http` on port 8080.
- [x] 1.5 Update thin compose/bootstrap docs for port 8080 inside the container and bearer-token MCP access.

## 2. Root Compose Handoff

- [x] 2.1 Update or document the root `ai-suite-qa` service handoff so it uses the published qa-mcp provider image instead of a placeholder.
- [x] 2.2 Ensure the service passes `AI1C_MCP_PROXY_HTTP_TOKEN` from the suite east-west token.

## 3. Verification

- [x] 3.1 Run `uv run pytest -q -ra -m "not live"`.
- [x] 3.2 Build the protected thin image or run an equivalent Dockerfile/static proxy smoke when Docker is unavailable.
- [x] 3.3 Run `docker/verify_protected_image.py` against the built image when the image build is available.
- [x] 3.4 Run `openspec validate suite-base-proxy-transport --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `docker/Dockerfile.thin`, proxy command, root compose handoff | Docker build/proxy smoke and static compose review | build log, verifier output, proxy `/health` result or provider-gap diagnostic | `.artifacts/openspec/suite-base-proxy-transport/20260703T101126Z/verification-summary.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient runtime | Model B env contract | Static env inspection, no live TestClient action during packaging change | env inspection summary | `.artifacts/openspec/suite-base-proxy-transport/20260703T101126Z/model-b-env.txt` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Managed form layout | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No 1C form or metadata behavior changes. | Released bundle still needs live Windows E2E before customer handoff. |

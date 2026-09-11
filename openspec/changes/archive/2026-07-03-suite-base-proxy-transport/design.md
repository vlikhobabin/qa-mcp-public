## Context

The current `docker/Dockerfile.thin` compiles protected native modules in a
Python builder stage, then installs the package into a `python:3.13-slim` final
stage and runs `qa-native-mcp` with `QA_MCP_TRANSPORT=http`. The suite base image
already contains `ai-mcp-proxy`, `uv`, the suite broker executable and the
standard provider HTTP proxy contract.

The native `.so` modules produced by Nuitka are Python-ABI specific, so the
builder and final runtime must use the same Python ABI. The change must avoid
building against Python 3.13 and then running under an unrelated suite base.

## Design

- Add Docker args for the final suite base and matching builder Python image:
  - `ARG SUITE_BASE_IMAGE=ai-suite-base:latest`
  - `ARG PYTHON_IMAGE=python:3.12-slim`
- Use `FROM ${PYTHON_IMAGE}` for the Nuitka builder and `FROM ${SUITE_BASE_IMAGE}`
  for the final stage. Release builds can override both if the suite base moves
  Python versions.
- Remove `QA_MCP_TRANSPORT=http`, `QA_MCP_HTTP_HOST`, `QA_MCP_HTTP_PORT` and
  `QA_MCP_HTTP_ALLOW_UNSAFE_BIND` from the final image defaults. With no transport
  env set, `qa-native-mcp` runs stdio.
- Set `QA_MCP_LICENSE_BROKER` to the suite base broker path and remove the final
  image `COPY delivery/broker/ai1c-license` step.
- Expose `8080`, use a `curl` healthcheck against `http://127.0.0.1:8080/health`,
  and run:
  `ai-mcp-proxy --provider-id qa-mcp --owner-path /opt/ai-dev-suite-for-1c/qa-mcp serve-http --host 0.0.0.0 --port 8080 -- qa-native-mcp`
- Keep model B defaults:
  - `QA_MCP_REMOTE_CLIENT=1`
  - `QA_MCP_CLIENT_HOST=host.docker.internal`
  - `QA_MCP_CLIENT_PORT=15381`
  - `QA_MCP_PLATFORM_VERSION=8.3.27.2130`
- Root compose coordination should point the `ai-suite-qa` service at the published
  qa image and pass `AI1C_MCP_PROXY_HTTP_TOKEN` from the suite east-west token.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Thin image final stage and startup command | Docker build/static inspection; proxy health smoke | `docker build`, `docker/verify_protected_image.py`, proxy `/health` result | `.artifacts/openspec/suite-base-proxy-transport/<run-id>/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient runtime | Model B remote TestClient path | Confirm env defaults unchanged; no live tool action required for this packaging change | static env inspection and existing offline tests | `.artifacts/openspec/suite-base-proxy-transport/<run-id>/model-b-env.txt` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Managed form layout | Runtime UI behavior | N/A: no form, metadata or UI automation behavior changes | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | Packaging transport only; no managed form surface changes. | A later E2E release run still needs live UI proof for the released bundle. |

## Risks

- Python ABI mismatch would break compiled protected modules. Mitigation: builder
  and final stage are parameterized together and the image verifier imports the
  protected package.
- Direct standalone bootstrap now needs a bearer token for `/mcp`. Mitigation:
  bootstrap will generate/pass an MCP proxy token and print client config with
  authorization headers.

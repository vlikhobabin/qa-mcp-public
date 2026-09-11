# Standalone source runbook

This is a pre-release source runbook. It does not depend on a private download
portal and does not claim that signed public release artifacts exist.

The standalone source topology supports one
Windows workstation only. Team deployment is not supported; use a separately
reviewed shared deployment process for a shared server or multiple developer
workstations.

1. Obtain the reviewed public source snapshot.
2. Run `uv sync --extra dev --locked` and `uv run pytest -q -m "not live"`.
3. Build the package with `uv build --offline` or the thin image with
   `docker build -f docker/Dockerfile.thin -t qa-mcp-standalone .`.
4. Generate a strong `QA_MCP_BEARER_TOKEN`; keep it outside Git and logs.
5. For live Windows operation, build and install the public bridge by following
   [host-agent/README.md](../host-agent/README.md), then bind it to a disposable
   test target and interactive desktop.
6. Connect the agent to `http://127.0.0.1:8000/mcp` with the bearer header.

The source contains no 1C platform or license. The operator must provide a
legal supported 1C installation and a test infobase. Never use business data as
a fixture and never publish 1C credentials, bridge tokens, private paths,
infobases or captures.

Updates and rollback use immutable reviewed source commits until OSS-08
publishes a release process. Rebuild from the selected commit; do not overwrite
an existing artifact directory.

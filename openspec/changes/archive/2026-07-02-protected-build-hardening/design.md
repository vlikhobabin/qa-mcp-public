## Context

The existing protected-image spec already requires non-protocol modules to ship as native code and source payloads to be encrypted. CR-06 closes gaps around readable docstrings, weaker standalone verification and container/release hygiene. The implementation should strengthen the shipped artifact without changing dev-source behavior.

## Design

Protected-image updates:

- Add `--python-flag=no_docstrings` to both Nuitka compile paths that produce shipped `.so` files.
- Extend `docker/verify_protected_image.py` to inspect the built image for:
  - absence of readable `protocol/*.py` sources except package initialization where intentionally allowed;
  - absence of `mcp_server.py` and `license_gate.py` as readable sources;
  - presence/loadability of compiled `.so` modules for `mcp_server` and `license_gate`;
  - `strings` scan over protected `.so` files for selected internal protocol prose/R&D tokens;
  - encrypted bundled data plus a decrypt/open round trip through the production loader;
  - expected tool count and server import smoke.
- Keep scan patterns specific enough to catch protocol prose without flagging legitimate binary/runtime metadata.

Container/runtime updates:

- Add a dedicated non-root user/group in both Dockerfiles and switch to it before runtime.
- Ensure writable runtime directories needed by the MCP server are owned by the runtime user.
- Add a lightweight healthcheck that probes the local MCP HTTP port or an equivalent server health endpoint without requiring secrets.
- Pin base images by digest. If the tag is retained for readability, use the `tag@sha256:<digest>` form.
- Update release workflow actions from mutable major tags to full commit SHAs, and keep action names/comments readable enough for maintenance.
- Preserve existing build behavior unless a change is needed to make non-root runtime work.

## Verification

Verification is container/build focused:

- Build the main and thin/protected images.
- Run the stronger `docker/verify_protected_image.py` against the built protected image.
- Run a `strings` scan that proves selected protocol docstrings are absent from compiled protocol modules.
- Inspect image metadata for `USER` and `HEALTHCHECK`.
- Check release workflow action references are pinned by SHA.
- Run OpenSpec validation and `git diff --check`.

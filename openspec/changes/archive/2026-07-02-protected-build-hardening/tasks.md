## 1. Compile And Verify Protected Modules

- [x] 1.1 Add `--python-flag=no_docstrings` to the Nuitka compile scripts for protocol and non-protocol protected modules.
- [x] 1.2 Strengthen `docker/verify_protected_image.py` to check compiled gate modules, protocol-string leakage and bundled-data decrypt/open behavior.
- [x] 1.3 Ensure the release workflow runs the strengthened verifier before publishing.

## 2. Container And Workflow Hardening

- [x] 2.1 Add non-root runtime users and required directory ownership to both Dockerfiles.
- [x] 2.2 Add lightweight Docker healthchecks to both images.
- [x] 2.3 Pin published base images by digest.
- [x] 2.4 Pin release workflow GitHub Actions by full commit SHA.
- [x] 2.5 Either consume `uv.lock` in the model-A build or remove misleading unused lockfile copying and keep dependencies constrained.

## 3. Verification

- [x] 3.1 Build the main and thin/protected Docker images.
- [x] 3.2 Run `docker/verify_protected_image.py` against the built protected image.
- [x] 3.3 Retain evidence that `strings qa_mcp/protocol/*.so` finds no selected protocol docstring prose.
- [x] 3.4 Inspect both images for non-root `USER` and `HEALTHCHECK`.
- [x] 3.5 Run `openspec validate protected-build-hardening --strict`.

## 1. Inject the encryption key as a CI secret

- [x] 1.1 `release.yml` passes `build-args: BUNDLED_DATA_KEY=${{ secrets.BUNDLED_DATA_KEY }}`
  into the thin-image build; the secret is masked (never echoed). FAIL-CLOSED: an unset
  secret forces the Dockerfile arg empty and aborts the build, so the public dev key
  cannot ship.
- [x] 1.2 Documented in the `release.yml` ONE-TIME SETUP header (the `BUNDLED_DATA_KEY`
  secret + how to generate it), next to `DIST_REPO_TOKEN` + the GHCR-public step.

## 2. Build the protected image in CI

- [x] 2.1 The build step uses the multi-stage `docker/Dockerfile.thin` protected path
  (compile + encrypt) with the injected key; it builds + LOADS locally, runs the
  pre-publish integrity gate, then pushes (build -> verify -> push).
- [x] 2.2 Local `docker build -f docker/Dockerfile.thin` still works without CI secrets —
  the Dockerfile `ARG BUNDLED_DATA_KEY` carries a documented dev/local default; CI
  overrides it with the real secret.

## 3. Verify the released image is protected

- [ ] 3.1 **DEFERRED to the first tagged release / `workflow_dispatch` run** (needs CI).
  The gate is in place: `docker/verify_protected_image.py` asserts no readable
  `protocol/*.py`, the 62-tool surface, and `_bundled` ciphertext (via the engine's
  `is_encrypted`), run on the locally-loaded image BEFORE push. Record the CI run URL
  under `.artifacts/openspec/ci-nuitka-release/<run-id>/` on the first run.
- [x] 3.2 Build-cost note added to the `release.yml` header (Nuitka compile + encrypt ~ a
  few minutes over an unprotected build; `ccache` deferred). Exact runner figure lands
  with the first CI run (3.1).

## 4. Verification

- [x] 4.1 Code-complete + composes with card 121: the build -> verify -> push path injects
  the key from the CI secret, local build still works, build cost documented. Card 121's
  `license-broker-in-image` adds its broker build/COPY to the SAME workflow without
  conflict (separate steps). Full end-to-end acceptance is confirmed by the first tagged
  run (3.1, deferred).

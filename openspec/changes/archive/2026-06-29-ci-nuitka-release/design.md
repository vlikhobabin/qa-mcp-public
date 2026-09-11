## Context

`.github/workflows/release.yml` builds + pushes `ghcr.io/vlikhobabin/qa-mcp-thin`
on a version tag (and `gh release create` to the dist repo). It currently builds
the **unprotected** thin image. The two prior changes add the compile + encrypt to
`docker/Dockerfile.thin`; this change makes CI use that path with a CI-injected key.

## Goals / Non-Goals

- **Goal:** the pushed GHCR image is the protected build; the key comes from a CI
  secret; local builds still work.
- **Non-Goal:** the broker-in-image / activation wiring (owned by card 121's
  `license-broker-in-image` change, which edits the same workflow separately).
- **Non-Goal:** changing the dist-repo release-asset flow.

## Decisions

- **D1 — Reuse the Dockerfile build path.** CI builds via the same multi-stage
  `docker/Dockerfile.thin`; the protection is already in the Dockerfile, so CI only
  supplies the key and (optionally) build args. Avoid a CI-only divergent build.
- **D2 — Key from a GitHub secret.** Add a secret (e.g. `BUNDLED_DATA_KEY`) passed
  as a `--build-arg` / secret file into the builder stage. Never commit the key; the
  compiled helper embeds the same value at build time. Document the one-time setup
  alongside the existing `DIST_REPO_TOKEN` + GHCR-public setup.
- **D3 — Keep local builds working.** Provide a documented default/dev key (or
  required build-arg) so `docker build` locally still produces a protected,
  functional image without CI secrets.
- **D4 — Document build time.** Record the Nuitka + encrypt overhead in the
  release/CI docs; consider `ccache` later (out of scope).

## Risks / Trade-offs

- **Key handling in CI:** keep the key out of logs (masked secret, no echo).
- **Build-time increase:** acceptable for tagged releases; measured + documented.
- **Coupling with card 121's workflow edit:** both touch `release.yml`; sequence so
  the edits compose (this change adds the protected build path + key secret; card
  121 adds the broker build/copy).

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CI/delivery | `release.yml` protected build + key secret | tagged build pushes a protected image | CI run log: image built via the protected path; key from secret | CI run URL in `tasks.md` §3 | planned | qa-mcp | — |
| Image integrity | published GHCR image | no `protocol/*.py`; `_bundled` ciphertext | image-pull checks (the prior changes' assertions) on the CI image | `.artifacts/openspec/ci-nuitka-release/<run-id>/` | planned | qa-mcp | — |
| QA/TestClient runtime | — | — | — | — | n/a | qa-mcp | parity already proven by the prior two changes' lab e2e; CI only wires the build |

Residual risk: a CI misconfiguration could publish an unprotected image; mitigated
by the image-integrity checks gating the release.

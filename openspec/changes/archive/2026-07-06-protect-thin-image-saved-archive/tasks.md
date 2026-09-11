## 1. Docker Layer Hygiene

- [x] 1.1 Rework `docker/Dockerfile.thin` so final-stage layers only receive sanitized installed artifacts and never receive `src/`, plaintext bundled data, or readable protected modules.
- [x] 1.2 Move bundled-data key injection to a BuildKit secret mount and fail closed when the secret is missing.
- [x] 1.3 Preserve the existing protected runtime import/tool/decrypt smoke in the built image.

## 2. Archive Scanner And Release Gate

- [x] 2.1 Extend `docker/verify_protected_image.py` with saved-archive scan mode covering layer tar entries plus image config/history metadata.
- [x] 2.2 Add scanner checks for readable protocol source, readable `mcp_server.py`/`license_gate.py`, plaintext `_bundled` captures/templates/mappings, and bundled-data key bytes.
- [x] 2.3 Update `tools/release/publish_self_hosted.sh` to pass `BUNDLED_DATA_KEY` through `--secret`, reject the development key, run the archive scanner after `docker save`, and block staging on failure.

## 3. Tests And Evidence

- [x] 3.1 Add focused offline tests proving the archive scanner fails on a synthetic bad archive and passes on a synthetic clean archive.
- [x] 3.2 Add focused tests or script assertions for publish-helper secret handling and archive-scan invocation.
- [x] 3.3 When Docker is available, build the old or intentionally leaky image/archive and prove the archive scanner fails.
- [x] 3.4 Build the fixed thin image, save it, and prove the archive scanner passes with zero protected plaintext/key hits in every layer/config/history. (2026-07-06: docker buildx 0.30.1 installed; real DOCKER_BUILDKIT --secret build rc=0, docker save 103M, verify_protected_image.py --key-env => "archive OK", independent grep => plaintext key ABSENT. Log: docs/retro/opsx-deliver-runs/20260706T*-qa-thin-layer-buildkit-PROOF-v2.log.)
- [x] 3.5 Run `uv run --with pytest --with pyyaml pytest`, `python3 scripts/check_suite_source_of_truth_drift.py`, and `uv run --with pytest --with pyyaml pytest -m smoke`, or record an explicit blocker for any unavailable gate.

## 4. Board And Release Handoff

- [x] 4.1 Sync the modified specs and archive the change after validation passes.
- [x] 4.2 Update the board card with archive paths, verification results, and the operator-owned v0.2.3 republish step.

## Verification Notes

- Focused scanner/publisher tests passed: `uv run --with pytest pytest -q tests/test_verify_protected_image_archive.py tests/test_self_hosted_release_scripts.py` (`10 passed`).
- Full suite passed: `uv run --with pytest --with pyyaml pytest` (`718 passed`).
- Suite drift fallback passed: `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/smoke_suite_source_of_truth_drift.py`.
- Smoke marker gate passed: `uv run --with pytest --with pyyaml pytest -m smoke` (`2 passed, 716 deselected`).
- `openspec validate protect-thin-image-saved-archive --strict` and `git diff --check` passed.
- Docker image proof is blocked on this host before Dockerfile execution: `docker buildx` is not installed, and `DOCKER_BUILDKIT=1 docker build ... --secret ...` exits with "BuildKit is enabled but the buildx component is missing or broken." Evidence: `.artifacts/openspec/protect-thin-image-saved-archive/20260706T144900Z/docker-build.log`.

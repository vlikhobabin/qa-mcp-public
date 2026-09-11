## Context

`docker/Dockerfile.thin` currently installs qa-mcp from copied source in the
final stage, then replaces/removes readable files and encrypts bundled data in
later `RUN` layers. Docker image archives include every layer blob, so deleting
or overwriting those paths later only changes the merged filesystem. A tester
with the published tarball can extract the earlier final-stage layer and recover
the plaintext protected source/data.

The bundled-data key is also supplied via `--build-arg BUNDLED_DATA_KEY`, which
is the wrong transport for a real release secret. Build args can leak through
history, provenance, cache exports, or intermediate build surfaces even when the
final merged filesystem is clean.

## Goals / Non-Goals

**Goals:**

- Ensure no final-image layer ever contains plaintext `qa_mcp/protocol/*.py`,
  readable `mcp_server.py` or `license_gate.py`, or unencrypted bundled capture
  and template payloads.
- Verify the saved Docker archive directly by walking all layer tar entries,
  whiteouts included, and by scanning image config/history metadata.
- Inject the bundled-data key with BuildKit `RUN --mount=type=secret`, not a
  Docker build arg, and reject the development key in release publishing.
- Keep the dev source tree unchanged; protection remains a build-time transform.

**Non-Goals:**

- Republish the external v0.2.3 artifact from this automated run.
- Change the protocol engine, capture corpus, TestClient runtime behavior, or
  license activation workflow.
- Guarantee resistance against native binary reverse engineering; this change
  only closes the plaintext layer/cache/key-transport leaks.

## Decisions

**D1 - Build the runtime package in a sanitized handoff stage.**
Create a stage that starts from the runtime base ABI, installs from source,
copies compiled `.so` modules from the builder, strips/removes readable
protected sources, encrypts `_bundled`, and then exports only the sanitized
site-packages/runtime assets. The final stage copies those sanitized assets
with `COPY --from=...`; it never receives `src/`, build directories, plaintext
bundled files, or readable gate modules.

Alternative considered: keep installing in the final stage and rely on `rm`.
That is rejected because it only cleans the merged filesystem and leaves layer
blobs recoverable from `docker save`.

**D2 - Make the verifier dual-mode.**
Preserve the existing in-container mode because it proves imports, tool count,
compiled gate modules, and decrypt round trips. Add an archive mode that accepts
the `docker save` tar path and scans layer contents plus config/history without
importing qa-mcp.

**D3 - Detect archive leaks by path and content.**
The scanner should fail on protected path names when layer entries expose
readable source locations and on content signatures for unencrypted bundled
payloads or the bundled-data key. It should tolerate package `__init__.py`
source, compiled `.so` files, encrypted bundled payloads, and expected Docker
metadata.

**D4 - Use BuildKit secrets for the bundled-data key.**
The Dockerfile reads `/run/secrets/bundled_data_key` inside the compile/encrypt
stage. `publish_self_hosted.sh` sets `DOCKER_BUILDKIT=1` and passes
`--secret id=bundled_data_key,env=BUNDLED_DATA_KEY`. The release helper rejects
the documented development key before build/save.

**D5 - Keep release activation as an operator action.**
The change can produce a safe staged image and manifest. Actually replacing the
already-published v0.2.3 artifact remains an explicit operator release action
and is recorded on the card.

## Risks / Trade-offs

- BuildKit dependency -> Mitigation: fail closed with a clear error and use
  standard Docker `--secret` syntax supported by modern Docker BuildKit.
- False positives in archive scanning -> Mitigation: combine path rules with
  narrowly scoped content probes and keep package `__init__.py` files allowed.
- Docker may be unavailable in CI/local verification -> Mitigation: keep offline
  unit tests for archive-scanner failure modes and record Docker build/save as
  the retained release-evidence gate when available.
- Existing published tarball remains vulnerable until republished -> Mitigation:
  card result and final summary explicitly assign the republish step.

## Verification Matrix

This is not a 1C runtime/metadata card. No BSL diagnostics, source import,
runtime apply, managed form UI, role, posting, or live-read evidence is
applicable.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Docker protected image | `docker/Dockerfile.thin` final layers | final image copies only sanitized artifacts | `docker build`, `docker save`, archive scanner pass | `.artifacts/openspec/protect-thin-image-saved-archive/<run-id>/` | planned | qa-mcp | — | Docker unavailable locally can defer image proof to release runner |
| Release gate | `publish_self_hosted.sh` | publish path rejects dev key and runs archive scanner before staging | focused pytest plus shell syntax; image archive gate when Docker is available | `.artifacts/openspec/protect-thin-image-saved-archive/<run-id>/` | planned | qa-mcp | — | external v0.2.3 republish remains operator action |
| 1C runtime | none | no runtime behavior change | none | none | n/a | qa-mcp | Docker/release packaging only | no runtime parity proof from this card |

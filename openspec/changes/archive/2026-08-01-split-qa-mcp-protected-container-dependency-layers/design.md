## Context

Both shipped Dockerfiles currently copy `src/` before a single `pip install .` step. That makes the dependency-resolution layer depend on every source byte. The protected thin flow then sanitizes `/protected-prefix` and copies only that prefix into the final stage; that security boundary, BuildKit secret model, compiled modules, encrypted bundled data, 68-tool smoke, and saved-archive scanner must remain unchanged.

The project requires Python 3.11 or newer, so Docker build stages can use the standard-library `tomllib` parser already present in their Python runtimes. This change uses local Docker BuildKit evidence only. It has no protocol capture source, frame range, dynamic field, replay strategy, live 1C process, or runtime cleanup requirement.

## Goals / Non-Goals

**Goals:**

- Put runtime dependency resolution in a stable Docker layer that depends on package metadata but not `src/`.
- Keep the project installation in a later layer that does not re-resolve dependencies.
- Demonstrate cache reuse with a cold protected build followed by a source-only rebuild.
- Preserve every protected-image compilation, encryption, key-exclusion, import/tool-count, and saved-layer scanner gate.

**Non-Goals:**

- Changing Python dependencies or the public MCP/runtime behavior.
- Changing the protected source list, bundled-data key model, compilation strategy, final-stage sanitized-prefix copy, or archive scanner.
- Introducing a package lockfile or a registry cache policy.
- Running live 1C, Vanessa, EDT/meta, capture, or replay workflows.

## Decisions

### Parse dependency metadata before copying source

Each Dockerfile will copy `pyproject.toml` and the installed README first. A metadata-only `RUN` uses `tomllib` to materialize requirement files and install the declared build/runtime requirements. `src/` is copied only afterward.

This keeps `pyproject.toml` authoritative and avoids a second hand-maintained requirements file. A generated lockfile was considered, but dependency locking is a separate supply-chain decision and is not needed to establish the cache boundary.

### Install project source without dependency resolution

The later project install uses `--no-deps --no-build-isolation`. Build-system requirements are installed in the earlier stable layer, and runtime dependencies are already present in the appropriate global or protected prefix. This prevents a code-only edit from causing hidden dependency resolution during the mutable source step.

For the protected flow, runtime dependencies remain in `/protected-prefix` when they are not already supplied by the immutable suite base; the final image continues to use the same suite base and receives only the sanitized prefix.

### Prove the boundary with a cold/warm BuildKit pair

The first protected build uses a dedicated cache scope with `--no-cache`. The second build uses an otherwise identical temporary build context with one harmless source-only edit. Plain-progress output must show the dependency-install step as cached while a later source-copy/project-install path is evaluated again.

The bundled-data key is stored only in an ignored mode-0600 runtime evidence file and mounted as a BuildKit secret. The cold build avoids accepting an encryption layer populated with an unknown prior secret. The same key is supplied to runtime verification and the saved-archive scanner without being printed.

### Keep regression checks cheap and behavioral

Focused tests inspect Dockerfile instruction ordering and install flags for both image flows. They fail if `COPY src` moves before dependency installation or if the source install starts resolving dependencies again. The real BuildKit run supplies the acceptance evidence that static ordering alone cannot provide.

## Risks / Trade-offs

- **Dependency declarations use unsupported TOML shapes** -> The extractor reads the standard `build-system.requires` and `project.dependencies` arrays and fails the build if they are absent or invalid; focused tests pin the intended structure.
- **A base image already satisfies a dependency globally** -> Pip may leave it in the immutable suite base instead of duplicating it in `/protected-prefix`; the final stage uses the same base, and protected import/tool-count smoke verifies availability.
- **BuildKit cache output is mistaken for source reuse** -> The proof starts cold, makes a real source-only context edit, and checks both the cached dependency step and a non-cached downstream source step.
- **BuildKit secrets are not cache keys** -> The cold proof build and matching runtime decrypt check prevent acceptance of a layer encrypted with an unknown cached key.
- **Build time remains dominated by Nuitka after protected source edits** -> This change deliberately optimizes Python dependency layers only; compiler-layer optimization is separate scope.

## Migration Plan

1. Add the focused ordering/install regression test and observe it fail against the current Dockerfiles.
2. Split metadata dependency installation from source project installation in both Dockerfiles.
3. Run focused and broader offline release tests.
4. Run the cold/warm protected BuildKit pair, image smoke, `docker save`, and protected archive scanner.
5. Retain raw build/scanner output under ignored `.runtime/changerail/evidence/`; keep only concise command/outcome summaries in tracked artifacts.

Rollback is a normal scoped revert of the Dockerfile/test changes. No data, protocol, service, or runtime migration is involved.

## Open Questions

- None for this change. Lockfiles, remote registry cache export, and Nuitka cache optimization remain separate future decisions.

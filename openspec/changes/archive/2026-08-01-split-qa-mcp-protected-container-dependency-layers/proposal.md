## Why

The normal and protected container builds currently copy all mutable QA source before resolving Python dependencies, so every code-only edit invalidates the otherwise stable dependency layer. Separating dependency installation from project installation makes iterative and release rebuilds reuse the expensive dependency prefix while keeping the protected-image sanitization boundary intact.

## What Changes

- Materialize runtime Python dependencies from `pyproject.toml` before copying mutable `src/` in both shipped Dockerfiles.
- Install the qa-mcp project from source in a later, dependency-free step so code-only changes do not rebuild the stable dependency layer.
- Add focused regression checks for the dependency/source cache boundary and retain BuildKit cache-reuse evidence from consecutive protected-image builds.
- Re-run the protected build, 68-tool import smoke, encrypted bundled-data checks, saved-archive scanner, and no-key/no-readable-source gates.

## Capabilities

### New Capabilities

- `qa-mcp-container-build-cache`: Defines the dependency/source layer boundary and observable cache reuse for qa-mcp container builds.

### Modified Capabilities

- None. Existing protected-release and container-security requirements remain unchanged and are reverified as invariants.

## Impact

- Affected delivery code: `Dockerfile` and `docker/Dockerfile.thin`.
- Affected verification: focused Dockerfile regression tests plus real Docker BuildKit build/cache and saved-archive evidence.
- This change touches container delivery configuration and tests only; it does not change protocol tools, Python manager behavior, MCP provider setup, OpenSpec workflow, documentation contracts, or runtime lab configuration.
- No live 1C runtime, Vanessa MCP, EDT/meta snapshot, or protocol capture evidence is required. Verification uses offline tests and the local Docker/BuildKit runtime.

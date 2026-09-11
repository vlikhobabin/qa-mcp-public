## ADDED Requirements

### Requirement: Container dependency layers precede mutable qa-mcp source

Each shipped qa-mcp Dockerfile SHALL install the Python build and runtime dependencies declared by `pyproject.toml` in a layer whose inputs do not include mutable `src/` content. The Dockerfile SHALL copy mutable source only after that dependency layer.

#### Scenario: Normal image separates dependencies from source

- **WHEN** the normal `Dockerfile` is evaluated
- **THEN** its dependency-install instruction occurs before `COPY src`
- **AND** its later qa-mcp project install does not resolve dependencies again

#### Scenario: Protected image separates dependencies from source

- **WHEN** `docker/Dockerfile.thin` is evaluated through the `protected-package` stage
- **THEN** its dependency-prefix installation occurs before `COPY src`
- **AND** its later qa-mcp project install does not resolve dependencies again

### Requirement: Code-only protected rebuilds reuse the dependency layer

A protected thin-image rebuild whose only build-context difference is mutable qa-mcp source SHALL reuse the previously materialized Python dependency layer.

#### Scenario: BuildKit reports dependency cache reuse

- **WHEN** a cold protected-image build is followed by an otherwise identical build with one source-only edit
- **THEN** BuildKit plain-progress evidence reports the dependency-install step as cached
- **AND** evidence shows that a downstream source-copy or project-install step was evaluated for the changed source

### Requirement: Cache optimization preserves protected release invariants

The dependency/source layer split MUST NOT weaken the protected-package sanitization, compiled-module import, 68-tool surface, encrypted bundled-data, external runtime-key, or saved-layer archive-scanner requirements.

#### Scenario: Optimized protected image passes release gates

- **WHEN** the optimized protected thin image is built and saved with the bundled-data key supplied only as a BuildKit secret
- **THEN** the protected-package and final-stage import/tool-count smokes pass
- **AND** runtime bundled-data verification succeeds only with the external key
- **AND** the saved-archive scanner reports no readable protected source, plaintext bundled data, or key material in any shipped layer or image metadata

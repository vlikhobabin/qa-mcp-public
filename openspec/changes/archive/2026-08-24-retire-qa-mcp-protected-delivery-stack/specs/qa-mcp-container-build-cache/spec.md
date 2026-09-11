## MODIFIED Requirements

### Requirement: Container dependency layers precede mutable qa-mcp source

Each shipped qa-mcp Dockerfile SHALL install the Python build and runtime
dependencies declared by `pyproject.toml` in a layer whose inputs do not include
mutable `src/` content. The Dockerfile SHALL copy mutable readable source only
after that dependency layer.

#### Scenario: Source-visible image separates dependencies from source

- **WHEN** the standalone Dockerfile is evaluated
- **THEN** its dependency-install instruction occurs before `COPY src`
- **AND** its later qa-mcp project install does not resolve dependencies again.

## REMOVED Requirements

### Requirement: Code-only protected rebuilds reuse the dependency layer
**Reason**: The protected image no longer exists.
**Migration**: Use the source-visible cache requirement added below.

### Requirement: Cache optimization preserves protected release invariants
**Reason**: Compiled modules, encrypted data, runtime keys and archive secrecy
scanners are retired.
**Migration**: Preserve ordinary dependency locking, source/asset integrity and
runtime smoke gates.

## ADDED Requirements

### Requirement: Code-only source rebuilds reuse the dependency layer
A source-visible image rebuild MUST reuse the locked dependency layer when its
only build-context difference is mutable qa-mcp source.

#### Scenario: BuildKit reports dependency cache reuse
- **WHEN** a cold image build is followed by an otherwise identical build with
  one source-only edit
- **THEN** the dependency-install step is cached
- **AND** a downstream source-copy or package-install step is reevaluated.

### Requirement: Cache optimization preserves open release integrity
The dependency/source layer split MUST preserve locked dependency, readable
source, curated asset, import, tool-profile and release-manifest verification.

#### Scenario: Cached image passes public release gates
- **WHEN** the source-visible image is rebuilt with cached dependencies
- **THEN** package and asset integrity checks pass
- **AND** its source revision and image digest reconcile with the release
  manifest.

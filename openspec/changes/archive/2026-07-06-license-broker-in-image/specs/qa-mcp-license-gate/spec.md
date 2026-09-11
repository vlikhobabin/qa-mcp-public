## ADDED Requirements

### Requirement: The thin image ships the broker with a host-stable license anchor
The thin delivery image SHALL include the `ai1c-license` broker (built for
linux/amd64) at the path the gate invokes, and SHALL provide a **host-stable
fingerprint** and **persistent lease state** so the broker holds a per-host lease
across container recreations. The container SHALL fingerprint the **host** (via a
bind-mounted host machine-id / host-provided stable id), not the ephemeral
container, and SHALL persist the broker's activation/lease cache in a named volume.

#### Scenario: The broker is present and runnable in the image
- **WHEN** the thin image is built
- **THEN** the `ai1c-license` broker binary is present at the gate's configured path
  and is executable (`ai1c-license check --component qa-mcp --json` runs)

#### Scenario: The lease is host-stable across container restarts
- **WHEN** the container is run with the host machine-id bind-mounted and the
  `qa-mcp-license` lease volume mounted, then recreated
- **THEN** the broker computes the same host fingerprint and reads its cached lease
  from the volume, so the per-host lease + offline grace survive the restart
- **AND** the machine-id bind + lease volume are wired in `docker-compose.thin.yml`
  and documented in the run docs

#### Scenario: CI ships the broker with the image
- **WHEN** the release workflow builds the thin image
- **THEN** it builds the broker (linux/amd64) and includes it in the published
  image, composing with the protected-build (Nuitka + encrypt) path

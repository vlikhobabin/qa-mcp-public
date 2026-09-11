# qa-mcp

qa-mcp is an open-source Python manager and Model Context Protocol (MCP)
server for native 1C TestClient QA automation. It speaks the TestManager /
TestClient protocol directly, runs BDD/Gherkin scenarios, reads and verifies
managed forms, and exposes target-bound lifecycle and UI operations to AI
agents without requiring a Vanessa Automation manager runtime.

The public repository is [vlikhobabin/qa-mcp-public](https://github.com/vlikhobabin/qa-mcp-public).
[qa-mcp v0.1.0 (MVP prerelease)](https://github.com/vlikhobabin/qa-mcp-public/releases/tag/v0.1.0)
is published with the existing product unchanged; it is not Stable.
The immutable tag points to the fresh public root `ba576b752ebe2939d4c84d53a8b1732d7b641e36`,
imported from the prepared snapshot based on original commit
`b6ae33639d151e9b47bf0a1248f0be5309a72504`. Internal Git ancestors are excluded.
Only README/publication-policy documentation on `main` is updated after the tag.
The release includes full source `qa-mcp-b6ae336-source.tar.gz`, Python wheel
and package sdist, a Docker archive, Windows executable/ZIP and `SHA256SUMS`.
Download the assets together and run `sha256sum -c SHA256SUMS` before use.
No PyPI/GHCR publication was made; GitHub Actions is disabled for this initial import.
The broader OSS-08 release train and OSS-09 downstream cutover are not mandatory
MVP prerequisites. This release does not claim stable or live-native qualification.

## What is included

- Native TestClient protocol/session engine and curated, plaintext protocol
  fixtures for supported 8.3 and 8.5 families.
- Managed-form reads/actions, assertions, waits and target-bound lifecycle.
- Gherkin scenario parsing/execution and JUnit/Allure-compatible reporting.
- Standalone stdio and authenticated streamable-HTTP MCP transports.
- A public Windows host bridge for authenticated TestClient lifecycle, relay,
  screenshots and bounded desktop input.
- Offline tests, protocol research tools and curated reproducible evidence.

`open_external_processor` remains dormant research code and is omitted from the
declared stable standalone support surface pending separate target-bound
qualification. The current source catalog is pre-stable; see
[the tool reference](docs/qa-mcp-tool-reference.md).

## Architecture

```text
AI agent ── MCP stdio/HTTP ── qa-mcp Python server
                                │
                                ├─ native TestClient protocol
                                ├─ scenario/reporting engine
                                └─ optional authenticated Windows bridge
                                      └─ owned TestClient + desktop primitives
```

The public core owns protocol, scenario, operation/result and standalone
transport semantics. Private downstream products consume a released version
and provide their own relay, tenant, portal or telemetry integrations without
forking core behavior. See [the shared-core extension contract](docs/shared-core-extension.md).

## Install the release wheel

Download `qa_mcp-0.1.0-py3-none-any.whl` from the release linked above.
With Python 3.11+:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install ./qa_mcp-0.1.0-py3-none-any.whl
.venv/bin/qa-native-mcp
```

The last command starts the stdio server for an MCP client.
The Docker attachment can be loaded with `docker load --input qa-mcp-image.tar`;
use its retained tag `qa-mcp-mvp-b6ae336-20260911t105140z:local` with the
[Docker startup settings](docker/README.md).

## Install from a source snapshot

Prerequisites for offline development are Python 3.11+ and
[uv](https://docs.astral.sh/uv/). No 1C installation is needed for the offline
suite.

```sh
tar -xzf qa-mcp-b6ae336-source.tar.gz
cd qa-mcp-b6ae336
uv sync --extra dev --locked
uv run pytest -q -m "not live"
uv build --offline
```

Run the MCP server over stdio (the default):

```sh
uv run qa-native-mcp
```

An agent can launch that command as a local stdio MCP server. Live TestClient
operations additionally need an explicit supported platform and test target;
keep target paths and credentials in ignored local configuration.

## Authenticated HTTP

HTTP defaults to loopback. Generate a strong project-owned bearer token and do
not commit or print it:

```sh
export QA_MCP_TRANSPORT=http
export QA_MCP_HTTP_HOST=127.0.0.1
export QA_MCP_HTTP_PORT=8000
export QA_MCP_BEARER_TOKEN="$(openssl rand -hex 32)"
uv run qa-native-mcp
```

Connect at `http://127.0.0.1:8000/mcp` with
`Authorization: Bearer <QA_MCP_BEARER_TOKEN>`. A non-loopback bind is rejected
without bearer authentication. See [Docker delivery](docker/README.md) for the
thin container and Linux-host models.

## Windows TestClient bridge

The complete public bridge source is under `host-agent/windows-display-agent/`.
It is separate from private AI-for-1C components and exposes only authenticated,
target-bound lifecycle/relay and bounded display primitives.

Build it from Linux without running a Windows host:

```sh
./bin/ai-build-windows-host-agent build --output-dir .runtime/windows-host-agent
./bin/ai-build-windows-host-agent verify --bundle-dir .runtime/windows-host-agent
```

For v0.1.0, the attached Windows executable/ZIP is an unstamped Linux
cross-build (`-buildvcs=false`) inspected for PE/amd64/GUI and capability markers.
It has no Windows-native qualification or successful helper-bundle verification.
The existing helper above requires Git and fails in a Git-free source extraction.
No new live 1C qualification was performed for this release.

Installation and firewall guidance is in
[host-agent/README.md](host-agent/README.md). Live use requires a licensed 1C
platform and an interactive Windows test session. Never commit a bridge token,
1C password, infobase or generated executable.

## Development and verification

Fast focused loop:

```sh
uv run pytest -q tests/test_public_repository_readiness.py
python3 tools/public_readiness.py audit --history --json
python3 tools/public_readiness.py provenance --check --json
python3 tools/protocol-research/oss07_i2/verify_matrix.py --run-mutations
git diff --check
```

The complete non-live suite is:

```sh
uv run pytest -q -m "not live"
```

Tests marked `live` require an explicitly authorized TestClient/lab target and
are not part of ordinary public-source verification. Raw captures and runtime
evidence stay in ignored state.

## Safety model

- Use disposable test data for UI/mutation operations and retain recovery proof.
- Runtime target resolution is immutable for a session; target mismatches fail
  before lifecycle or UI work.
- HTTP and Windows bridge routes are authenticated; loopback is the safe default.
- Cleanup stops only exact processes and artifacts owned by the operation.
- Secrets, customer data, private endpoints, full infobases, proprietary 1C
  binaries and local captures do not belong in Git or issue reports.

Read [SECURITY.md](SECURITY.md) before reporting a vulnerability.

## Documentation

- [MCP tool reference](docs/qa-mcp-tool-reference.md)
- [Docker delivery](docker/README.md)
- [Windows bridge](host-agent/README.md)
- [Shared-core extension contract](docs/shared-core-extension.md)
- [Platform support](docs/platform-support.md)
- [Protocol research index](docs/protocol-research/README.md) — historical and
  current research evidence, not the installation guide
- [Public source publication policy](docs/publication-policy.md)

## Contributing and support

Read [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md),
[SUPPORT.md](SUPPORT.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
Generic core fixes go upstream first; private product integrations stay in their
own repositories.

## License and trademarks

qa-mcp is licensed under [Apache-2.0](LICENSE). See [NOTICE](NOTICE) for
attribution and nominative trademark use. This independent project is not
affiliated with or endorsed by the owners of the 1C trademarks.

## Project-local delivery

Validate canonical specs with the pinned project-local OpenSpec wrapper:

```bash
./bin/openspec validate --specs --strict --no-interactive
```

The installed ChangeRail runtime uses Astra/high for review and Terra/high for
implementation; the project Codex launcher defaults to Astra/high for planning.
See
[`docs/development/local-changerail-delivery.md`](docs/development/local-changerail-delivery.md)
for installation and command semantics. Delivery via `./bin/chrl-run` includes
commit/push and requires authority for that complete cycle. Sequential product
roadmap work is described in [OSS-00 orchestration](docs/development/oss-00-orchestration.md).
Stopped migration runs remain history and are not the ordinary delivery queue.

## Product test policy

Ordinary checks select changed qa-mcp modules: `uv run pytest --qa-changed --qa-lane offline`.
Subprocess/build/display checks use the separate `integration` lane. Full tests
require epic closure or explicit operator agreement; live Linux/Windows 1C checks
require target-specific authorization and preflight. See
[test policy](docs/development/test-policy.md) and
[test inventory](docs/development/test-inventory.md). ChangeRail is consumed only
as an executable distribution; its development and tests do not run here.

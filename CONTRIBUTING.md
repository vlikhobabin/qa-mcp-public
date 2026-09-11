# Contributing to qa-mcp

Thank you for improving qa-mcp. Contributions are accepted upstream under the
project's [Apache-2.0 license](LICENSE).

## Development setup

```sh
git clone <public-repository-url> qa-mcp
cd qa-mcp
uv sync --extra dev --locked
uv run pytest -q -m "not live"
uv build --offline
```

Offline tests must not require a 1C installation, customer data, credentials or
private services. A change that genuinely requires live 1C/TestClient evidence
must use an explicit test target and the repository safety policy; do not attach
raw captures or infobases to a pull request.

## Change discipline

1. Open or reference an issue for non-trivial work.
2. Keep one coherent capability change per pull request.
3. Add a regression test that would fail without the fix. For docs/config-only
   work, state why a RED test is not applicable.
4. Run focused tests, the non-live suite, `git diff --check`, and relevant
   OpenSpec validation.
5. Update user-facing docs and public provenance when assets change.

Generic protocol, scenario, result-model and executor fixes belong in public
qa-mcp first. Private products consume a released version; product-specific
relay, tenant, portal and telemetry integrations stay in their owning
repositories.

Do not submit secrets, customer identifiers, private endpoints, proprietary 1C
platform files, infobases, unreviewed captures or generated local runtime state.

Unless explicitly marked “Not a Contribution,” intentional submissions are
provided under Apache-2.0 as described in section 5 of the license.

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [GOVERNANCE.md](GOVERNANCE.md)
and [SECURITY.md](SECURITY.md).

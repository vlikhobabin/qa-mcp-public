## Why

The repository lacks standard public security, contribution, governance,
support and conduct documents, while its main entry points mix active source
usage with internal research/staging language. A public clone needs one
coherent route that matches the actual source without claiming OSS-08 release
publication or OSS-09 downstream cutover.

## What Changes

- Add SECURITY, CONTRIBUTING, GOVERNANCE, SUPPORT and CODE_OF_CONDUCT policies
  using only public/private-reporting UI routes and no personal contact data.
- Replace the README with a source-focused architecture, install, bearer-auth,
  Windows bridge, development, safety and upstream-first contribution guide.
- Make active delivery guidance source-clone based and clearly label retained
  research/planning/staging records as historical or pre-release.
- Add deterministic local-link and prohibited-terminology checks for the public
  documentation surface.

## Capabilities

### New Capabilities

- `qa-mcp-public-repository-docs`: Defines the required discoverable public
  documentation, contact, terminology and upstream-first contribution
  behavior of the qa-mcp source repository.

### Modified Capabilities

- none.

## Impact

This is a docs/OpenSpec change plus offline documentation checks. It does not
modify protocol tools, Python manager behavior, MCP setup, Windows bridge code,
runtime configuration or release automation. It requires no Windows, SSH, 1C,
TestClient, Vanessa, EDT/meta snapshot, live service or network work.
